import os
from dotenv import load_dotenv
load_dotenv()
import re
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from src.evaluator import TruthLensEvaluator, is_dynamic_fact_query, detect_query_intent, ddg_html_search, parse_structured_intent, is_answer_supported_by_evidence, is_valid_generated_response
from src.rag_engine import TruthLensRAG
from contextlib import asynccontextmanager

USE_MOCK = os.environ.get("USE_MOCK", "false").lower() == "true"
evaluator = TruthLensEvaluator(use_mock=USE_MOCK)

# detect_intent delegates to the single canonical detect_query_intent in evaluator.py
# This ensures intent detection is NEVER duplicated between main.py and evaluator.py.
def detect_intent(prompt: str) -> str:
    return detect_query_intent(prompt)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load evaluator models
    if not USE_MOCK:
        evaluator._load_models()
        
        # Load generation pipeline
        from transformers import pipeline
        import torch
        device_id = 0 if torch.cuda.is_available() else -1
        print(f"Loading generation model (Qwen 0.5B) on device {device_id}...")
        app.state.llm_pipeline = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct", device=device_id)
        
        # Initialize RAG Engine
        print("Initializing RAG Engine (FAISS + LangChain)...")
        app.state.rag_engine = TruthLensRAG()
    else:
        print("[TruthLens] USE_MOCK=True. Skipping heavy model initialization for low-memory environment.")
        app.state.llm_pipeline = None
        app.state.rag_engine = None
        
    yield

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TruthLens AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Secure SQLite User Store ────────────────────────────────────────────────
import uuid, hashlib, sqlite3, secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DB_PATH = os.path.join(BASE_DIR, "truthlens.db")

class NoCacheStaticFiles(StaticFiles):
    def is_not_modified(self, response_headers, request_headers) -> bool:
        return False
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.mount("/static", NoCacheStaticFiles(directory=STATIC_DIR), name="static")

from fastapi import UploadFile, File
import PyPDF2, docx, io

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    ext = filename.split(".")[-1].lower()
    content = await file.read()
    text = ""
    try:
        if ext == "pdf":
            reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        elif ext == "docx":
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext in ["txt", "csv"]:
            text = content.decode("utf-8")
        else:
            return {"error": f"Unsupported file type: {ext}"}
            
        # Index document into RAG engine
        if text and hasattr(app.state, 'rag_engine') and app.state.rag_engine is not None:
            app.state.rag_engine.index_text(text, metadata={"filename": filename})
            
        return {"filename": filename, "text": text[:10000], "status": "success"}
    except Exception as e:
        return {"error": f"Extraction failed: {str(e)}"}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY, name TEXT, salt HEX, password_hash HEX
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY, email TEXT
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS contact_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            inquiry_type TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            email TEXT,
            title TEXT,
            prompt TEXT,
            response TEXT,
            risk_score INTEGER,
            verdict TEXT,
            created_at TEXT,
            updated_at TEXT,
            is_saved INTEGER DEFAULT 0,
            evaluation_data TEXT,
            FOREIGN KEY(email) REFERENCES users(email)
        )''')
        conn.commit()

init_db()

def hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login", auto_error=False)

def verify_token(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT s.email, u.name FROM sessions s JOIN users u ON s.email = u.email WHERE s.token = ?", (token,))
        row = cursor.fetchone()
        if not row:
            return None # Or raise 401 if you want to be strict with provided tokens
        return {"email": row[0], "name": row[1]}



class EvaluationRequest(BaseModel):
    prompt: str
    response: str
    context: str = ""
    language: str = "English"

class GenerateRequest(BaseModel):
    prompt: str
    model: str = "tiny"
    history: list = []  # Added history for conversation memory
    evaluate: bool = False
    language: str = "English"

# ── Groq API Key ───────────────────────────────────────────────────────────────
# Get a FREE key at: https://console.groq.com  (takes 30 seconds)
# Or set it as an environment variable GROQ_API_KEY
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

def llama3_generate(prompt, context, history=None, language="English"):
    """
    Calls Llama-3.3-70B via Groq's free inference API with history support.
    """
    if not GROQ_API_KEY:
        print("[TruthLens] GROQ_API_KEY not set — falling back.")
        return None
        
    is_dynamic = is_dynamic_fact_query(prompt)
    if is_dynamic and (not context or len(context.strip()) < 50):
        print("[TruthLens] Dynamic query detected with insufficient context. Returning fallback.")
        return "Unable to verify this claim with available evidence."
        
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)

        if language and language.lower() != "english":
            lang_instruction = f" Respond in the language: {language}."
        else:
            lang_instruction = ""

        intent = detect_intent(prompt)
        intent_lower = intent.lower()
        struct_intent = parse_structured_intent(prompt)
        target = struct_intent.get("target")
        comp = struct_intent.get("competition") or ""
        yr = str(struct_intent.get("year") or "")
        
        intent_instruction = ""
        max_tokens = 200
        temperature = 0.5
        
        if target == "winner" or target == "champion":
            comp_str = f" {comp}" if comp else ""
            yr_str = f" {yr}" if yr else ""
            intent_instruction = (
                " Respond in EXACTLY this format and nothing else:"
                f" 'Winner of{comp_str}{yr_str}: [Name]'"
                " Example: 'Winner of IPL 2026: Royal Challengers Bengaluru'."
                " Do NOT include extra sentences or commentary."
            )
            max_tokens = 60
            temperature = 0.1
        elif target == "president":
            intent_instruction = (
                " Respond in EXACTLY this format and nothing else:"
                " 'President of [Place]: [Name]'"
                " Example: 'President of the USA: Donald Trump'."
                " Do NOT include extra sentences or commentary."
            )
            max_tokens = 60
            temperature = 0.1
        elif target == "prime minister":
            intent_instruction = (
                " Respond in EXACTLY this format and nothing else:"
                " 'Prime Minister of [Place]: [Name]'"
                " Example: 'Prime Minister of India: Narendra Modi'."
                " Do NOT include extra sentences or commentary."
            )
            max_tokens = 60
            temperature = 0.1
        elif target == "founder":
            ent_str = f" {comp}" if comp else " [Entity]"
            intent_instruction = (
                " Respond in EXACTLY this format and nothing else:"
                f" 'Founder of{ent_str}: [Name]'"
                " Example: 'Founder of WhatsApp: Jan Koum'."
                " Do NOT include extra sentences or commentary."
            )
            max_tokens = 60
            temperature = 0.1
        elif target == "inventor":
            intent_instruction = (
                " Respond in EXACTLY this format and nothing else:"
                " 'Inventor of [Entity]: [Name]'"
                " Example: 'Inventor of Telephone: Alexander Graham Bell'."
                " Do NOT include extra sentences or commentary."
            )
            max_tokens = 60
            temperature = 0.1
        elif target == "ceo":
            intent_instruction = (
                " Respond in EXACTLY this format and nothing else:"
                " 'CEO of [Company]: [Name]'"
                " Example: 'CEO of Apple: Tim Cook'."
                " Do NOT include extra sentences or commentary."
            )
            max_tokens = 60
            temperature = 0.1
        else:
            intent = detect_intent(prompt)
            intent_lower = intent.lower()
            if intent_lower == "person lookup":
                intent_instruction = (
                    " The query asks for a specific person or entity name."
                    " Respond in EXACTLY this format and nothing else:"
                    " '[Title/Role] of [Place/Organization]: [Full Name]'"
                    " Example: 'President of the United States: Donald Trump'."
                    " Do NOT include sentences, descriptions, or extra commentary."
                )
                max_tokens  = 60
                temperature = 0.1

            elif intent_lower == "date lookup":
                intent_instruction = (
                    " The query asks for a specific date, year, or time period."
                    " Respond with the date/year concisely in one line."
                    " Do NOT add prose descriptions or background information."
                )
                max_tokens  = 60
                temperature = 0.1

            elif intent_lower == "definition":
                intent_instruction = (
                    " The query asks for a definition or explanation of a concept."
                    " Respond with 3 to 6 clear, informative sentences."
                    " Start with a concise one-line definition, then expand with key details,"
                    " use cases, and relevance. Do NOT bullet-point the answer."
                )
                max_tokens  = 350
                temperature = 0.6

            elif intent_lower == "explanation":
                intent_instruction = (
                    " The query asks for an in-depth explanation."
                    " Respond with well-structured paragraphs covering: what it is,"
                    " how it works, why it matters, and a practical example."
                    " Use clear, natural language. Do NOT use bullet points or headers."
                )
                max_tokens  = 500
                temperature = 0.7

            else:  # fact_lookup / general
                intent_instruction = (
                    " Answer the factual question directly and accurately."
                    " Provide the key fact first, then 1–2 supporting sentences of context."
                    " Do NOT write an essay or include unrelated information."
                )
                max_tokens  = 200
                temperature = 0.5

        if context and len(context.strip()) > 50:
            if is_dynamic:
                system_msg = (
                    "You are an expert factual assistant."
                    " Answer the user's question using the provided Context ONLY."
                    " CRITICAL: If the Context does not contain the answer, or if there is no mention of the requested entities in the Context,"
                    " reply exactly with the following string: 'Unable to verify this claim with available evidence.'"
                    " Do NOT use your own knowledge, guess, or output outdated information."
                    f" Current Year: 2026.{lang_instruction}{intent_instruction}"
                )
            else:
                system_msg = (
                    "You are an expert factual assistant."
                    " Answer the user's question using the provided Context."
                    " If the context is insufficient, supplement with your own knowledge."
                    " CRITICAL: Do not mention the context, add disclaimers, or include metadata."
                    f" Current Year: 2026.{lang_instruction}{intent_instruction}"
                )
            user_msg = f"Context:\n{context[:2000]}\n\nQuestion: {prompt}"
        else:
            system_msg = (
                "You are TruthLens AI. Provide grounded, accurate information."
                " Answer the user's question using your internal knowledge."
                f" Current Year: 2026.{lang_instruction}{intent_instruction}"
            )
            user_msg = f"Question: {prompt}"

        messages = [{"role": "system", "content": system_msg}]
        if history:
            messages.extend(history[-6:])
        messages.append({"role": "user", "content": user_msg})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        answer = completion.choices[0].message.content.strip()
        print(f"[TruthLens] Groq Llama-3.3-70B (intent={intent}) -> {answer[:80]}")
        return answer
    except Exception as e:
        print(f"[TruthLens] Groq API error: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    with open(os.path.join(STATIC_DIR, "dashboard.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/chat", response_class=HTMLResponse)
async def serve_chat():
    with open(os.path.join(STATIC_DIR, "chat.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/analysis", response_class=HTMLResponse)
async def serve_analysis():
    with open(os.path.join(STATIC_DIR, "analysis.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/features", response_class=HTMLResponse)
async def serve_features():
    with open(os.path.join(STATIC_DIR, "features.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/contact", response_class=HTMLResponse)
async def serve_contact():
    with open(os.path.join(STATIC_DIR, "contact.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/settings", response_class=HTMLResponse)
async def serve_settings():
    with open(os.path.join(STATIC_DIR, "settings.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/login", response_class=HTMLResponse)
async def serve_login():
    with open(os.path.join(STATIC_DIR, "login.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/about", response_class=HTMLResponse)
async def serve_about():
    with open(os.path.join(STATIC_DIR, "about.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/logout")
async def logout_redirect():
    return RedirectResponse(url="/")

@app.get("/features/nli", response_class=HTMLResponse)
async def serve_features_nli():
    with open(os.path.join(STATIC_DIR, "features_nli.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/features/grounding", response_class=HTMLResponse)
async def serve_features_grounding():
    with open(os.path.join(STATIC_DIR, "features_grounding.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/features/crosscheck", response_class=HTMLResponse)
async def serve_features_crosscheck():
    with open(os.path.join(STATIC_DIR, "features_crosscheck.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/features/heatmap", response_class=HTMLResponse)
async def serve_features_heatmap():
    with open(os.path.join(STATIC_DIR, "features_heatmap.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/evaluate")
def evaluate_response(req: EvaluationRequest, user: str = Depends(verify_token)):
    try:
        print(f"[TruthLens] Incoming evaluation request for prompt: {req.prompt[:50]}...")
        
        # Grounding with local RAG if context is empty, and always returning matching chunks
        context_text = req.context
        local_chunks = []
        is_dynamic = is_dynamic_fact_query(req.prompt)
        if not is_dynamic and hasattr(app.state, 'rag_engine') and app.state.rag_engine.vector_store is not None:
            try:
                local_chunks = app.state.rag_engine.query_detailed(req.prompt, k=5)
                if not context_text and local_chunks:
                    context_text = "\n\n".join([chunk["page_content"] for chunk in local_chunks])
                    print(f"[TruthLens] Local RAG grounding context retrieved ({len(local_chunks)} chunks).")
            except Exception as e:
                print(f"[TruthLens] RAG evaluation query failed: {e}")

        result = evaluator.evaluate(prompt=req.prompt, response=req.response, context=context_text, language=req.language)
        if result is None:
            return {
                "status": "error",
                "overall_risk": 0.0,
                "trust_score": 0,
                "trust_verdict": "N/A",
                "trust_reasoning": "Cannot evaluate an invalid/failed response.",
                "components": {"Consistency": 0.0, "Logical NLI": 0.0, "HHEM Factor": 0.0},
                "details": {"Consistency": "N/A", "Logical NLI": "N/A", "HHEM Factor": "N/A"},
                "rag_chunks": local_chunks
            }
        result["rag_chunks"] = local_chunks
        
        print(f"[TruthLens] Evaluation complete. Risk: {result.get('overall_risk')}")
        return result
    except Exception as e:
        print(f"[TruthLens] EVALUATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class RAGProcessor:
    """
    Implements a professional RAG pipeline using Vector Search (Cosine Similarity).
    """
    def __init__(self, embed_model):
        self.embed_model = embed_model

    def process(self, query: str, snippets: list, top_k: int = 4):
        if not snippets:
            return ""
        
        import torch
        import numpy as np
        from sentence_transformers import util

        # 1. Semantic Chunking: Split long snippets into smaller, focused factual chunks
        chunks = []
        for s in snippets:
            # split by sentences or small paragraphs
            parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', s) if len(p.strip()) > 30]
            chunks.extend(parts)
        
        if not chunks:
            return " ".join(snippets[:3])

        # 2. Vector Embedding & Ranking
        query_emb = self.embed_model.encode(query, convert_to_tensor=True)
        chunk_embs = self.embed_model.encode(chunks, convert_to_tensor=True)
        
        # Calculate cosine similarity
        cos_scores = util.cos_sim(query_emb, chunk_embs)[0]
        
        # 3. Retrieve Top-K most relevant factual chunks
        top_results = torch.topk(cos_scores, k=min(top_k, len(chunks)))
        
        selected_chunks = []
        for score, idx in zip(top_results[0], top_results[1]):
            if score > 0.35: # Only include chunks with decent semantic relevance
                selected_chunks.append(chunks[idx])
        
        return "\n".join(selected_chunks)

def verify_and_resolve_response(prompt: str, generated_response: str, context_text: str, is_dynamic: bool, local_chunks: list, model_name: str, language: str = "English", retrieval_count: int = 0) -> dict:
    eval_data = None
    final_response = generated_response
    
    # 5 & 6. Run NLI verification and hallucination evaluation, reject contradicted responses
    try:
        eval_data = evaluator.evaluate(prompt=prompt, response=generated_response, context=context_text, language=language)
        if eval_data:
            eval_data['model_name'] = model_name
            status = eval_data.get("status")
            corrected = eval_data.get("corrected_answer")
            
            if status == "Contradicted" and "unable to verify" not in generated_response.lower():
                print(f"[TruthLens] Verification rejected hallucinated response: '{generated_response}'")
                if corrected and corrected not in ("No correction required", "") and "unable to verify" not in corrected.lower():
                    final_response = corrected
                    print(f"[TruthLens] Replacing with verified/corrected answer: '{final_response}'")
                else:
                    final_response = "Unable to verify with current evidence."
                    print(f"[TruthLens] No valid correction found. Falling back to: '{final_response}'")
    except Exception as e:
        print(f"[TruthLens] Post-verification evaluation check failed: {e}")
        import traceback
        traceback.print_exc()

    # If it is dynamic, apply extra strict NLI/hallucination verification
    if is_dynamic:
        if "tata cricket" in final_response.lower():
            final_response = "Unable to verify this claim with available evidence."
            
        # Programmatic answer validation against retrieved evidence
        if context_text and not is_answer_supported_by_evidence(final_response, context_text):
            final_response = "Unable to verify this claim with available evidence."
            print(f"[TruthLens] Answer validation failed: final answer not supported by retrieved evidence.")
            
        if eval_data:
            status = eval_data.get("status")
            trust_score = eval_data.get("trust_score", 100)
            corrected = eval_data.get("corrected_answer")
            
            if status == "Contradicted" or trust_score < 50:
                if corrected and "unable to verify" not in corrected.lower() and corrected != "No correction required":
                    if is_answer_supported_by_evidence(corrected, context_text):
                        final_response = corrected
                        print(f"[TruthLens] Enforcing corrected answer: '{final_response}'")
                    else:
                        final_response = "Unable to verify this claim with available evidence."
                        print(f"[TruthLens] Corrected answer not supported by evidence. Fallback.")
                else:
                    final_response = "Unable to verify this claim with available evidence."
                    print(f"[TruthLens] Rejecting unsupported/contradicted dynamic answer. Fallback: '{final_response}'")

    if is_dynamic and (not final_response or final_response.strip() == ""):
        final_response = "Unable to verify this claim with available evidence."

    # 7. Add debug logging (wrapped in try-except with repr to avoid Windows CP1252 UnicodeEncodeErrors)
    try:
        evidence_sources = []
        if eval_data and eval_data.get("evidence"):
            evidence_sources = [e.get("src", "Web Source") for e in eval_data["evidence"]]
        elif local_chunks:
            evidence_sources = [chunk.get("metadata", {}).get("filename", "Local Doc") for chunk in local_chunks]

        struct_intent = parse_structured_intent(prompt)

        print(f"\n====================== DEBUG LOG ======================")
        print(f"Original Query:     {repr(prompt)}")
        print(f"Parsed Intent:      {repr(struct_intent)}")
        print(f"Retrieved Sources:   {repr(evidence_sources)}")
        print(f"Retrieved Evidence:  {repr(context_text[:500])}...")
        print(f"Generated Answer:    {repr(final_response)}")
        print(f"Verification Result: {repr(eval_data.get('status') if eval_data else 'Unknown/Bypassed')}")
        print(f"Risk Score:          {eval_data.get('overall_risk', 0.0) if eval_data else 0.0}")
        print(f"=======================================================\n")
    except Exception as print_err:
        print(f"[TruthLens] Debug print failed due to encoding: {print_err}")

    # Add logging for Requirement 4
    verification_confidence = eval_data.get("confidence", 0.0) if eval_data else 0.0
    print(f"[TruthLens LOG] Retrieval Results Count: {retrieval_count}")
    print(f"[TruthLens LOG] LLM Response: {generated_response}")
    print(f"[TruthLens LOG] Verification Confidence: {verification_confidence}")

    status_val = "error" if not is_valid_generated_response(generated_response) else (eval_data.get("status") if eval_data else "success")

    return {
        "status": status_val,
        "generated_response": final_response, 
        "model": model_name, 
        "prompt": prompt, 
        "context": context_text,
        "evaluation": eval_data,
        "rag_chunks": local_chunks
    }


@app.post("/api/generate")
def generate_response(req: GenerateRequest, user: str = Depends(verify_token)):
    """
    Live LLM response generator using TinyLlama and RAG.
    """
    # 0. AI QUERY REFINER: Normalize and expand the search query for better RAG
    prompt = req.prompt.strip()
    local_chunks = []
    refined_query = prompt
    try:
        # Use Groq for a split-second query optimization
        if GROQ_API_KEY:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            refiner_messages = [
                {"role": "system", "content": "You are a search query optimizer. Extract the core entities. CRITICAL: Distinguish between 'Jupyter' (the coding notebook) and 'Jupiter' (the planet). If moons, space, or gravity are mentioned, always use 'Jupiter planet'. Output keywords only."},
                {"role": "user", "content": f"Optimize this for web search: {prompt}"}
            ]
            refine_resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=refiner_messages,
                temperature=0.0,
                max_tokens=40
            )
            refined_query = refine_resp.choices[0].message.content.strip()
            print(f"[TruthLens] Refined Search Query: '{prompt}' -> '{refined_query}'")
        else:
            print("[TruthLens] No Groq API Key found; skipping query optimization.")
    except Exception as e:
        print(f"[TruthLens] Query refiner failed, using original: {e}")

    is_dynamic = is_dynamic_fact_query(prompt)
    print(f"[TruthLens] is_dynamic_fact_query('{prompt}') -> {is_dynamic}")

    search_query = refined_query
    context_text = ""
    filtered_snippets = []
    retrieval_count = 0
    
    # 1. LOCAL RAG: Search indexed documents (FAISS) - Bypassed for dynamic queries
    if not is_dynamic:
        try:
            if hasattr(app.state, 'rag_engine') and app.state.rag_engine.vector_store is not None:
                local_chunks = app.state.rag_engine.query_detailed(search_query, k=5)
                if local_chunks:
                    context_text = "\n\n".join([chunk["page_content"] for chunk in local_chunks])
                    retrieval_count = len(local_chunks)
                    print(f"RAG: Found relevant local context ({len(local_chunks)} chunks).")
        except Exception as e:
            print(f"RAG: Local search failed: {e}")

    # 2. WEB RAG: Fallback to web search if local context is sparse or specifically requested, or forced for dynamic query
    if is_dynamic or not context_text or len(context_text) < 200:
        try:
            print(f"RAG: Consolidated HTML search for '{search_query}'...")
            all_results = ddg_html_search(search_query, max_results=10)
            print(f"RAG: Total HTML search results retrieved: {len(all_results)}")

            # 3. Filter noise
            seen = set()
            for r in all_results:
                body = r.get('body', r.get('snippet', '')).strip()
                if len(body) < 40:
                    continue
                noise_words = ['cookie', 'javascript', 'subscribe', 'log in', 'sign up', 'newsletter', 'privacy policy', 'terms of service', 'captcha']
                if any(noise in body.lower() for noise in noise_words):
                    continue
                key = body[:40]
                if key in seen:
                    continue
                seen.add(key)
                filtered_snippets.append(body)

        except Exception as e:
            print(f"RAG: Search failed: {e}")

        # Wikipedia Fallback
        if not filtered_snippets:
            print("RAG: DuckDuckGo search yielded no results. Trying Wikipedia Fallback...")
            try:
                import urllib.request, urllib.parse, json as _json
                clean_wiki_query = search_query
                for prefix in ["who is ", "who was ", "what is ", "what was ", "where is ", "where was ", "tell me about ", "about ", "who are "]:
                    if clean_wiki_query.lower().startswith(prefix):
                        clean_wiki_query = clean_wiki_query[len(prefix):]
                
                ua = {'User-Agent': 'Mozilla/5.0'}
                wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_wiki_query)}&format=json"
                with urllib.request.urlopen(urllib.request.Request(wiki_url, headers=ua), timeout=5) as resp:
                    s_data = _json.loads(resp.read().decode())
                    search_results = s_data.get("query", {}).get("search", [])
                    if search_results:
                        top_title = search_results[0]["title"]
                        print(f"RAG: Found Wikipedia page: {top_title}")
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top_title.replace(' ', '_'))}"
                        with urllib.request.urlopen(urllib.request.Request(sum_url, headers=ua), timeout=5) as sum_resp:
                            wiki_data = _json.loads(sum_resp.read().decode())
                            if wiki_data.get("extract"):
                                filtered_snippets.append(wiki_data["extract"])
                                print("RAG: Wikipedia summary successfully added to snippets.")
            except Exception as wiki_err:
                print(f"RAG: Wikipedia fallback failed: {wiki_err}")

        try:
            if filtered_snippets:
                # Use the new Vector RAG Processor to select the most relevant context
                print(f"RAG: Performing Vector Search on {len(filtered_snippets)} snippets...")
                
                # Lazy-load the embedder if not already in state
                _embed_model = getattr(app.state, 'embed_model', None)
                if _embed_model is None:
                    from sentence_transformers import SentenceTransformer
                    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
                    app.state.embed_model = _embed_model
                
                rag = RAGProcessor(_embed_model)
                context_text = rag.process(search_query, filtered_snippets)
                retrieval_count = len(filtered_snippets)
                print(f"RAG: Vector Search complete. Grounding context prepared.")
            else:
                print(f"RAG: No usable snippets found for: {prompt}")
        except Exception as vec_err:
            print(f"RAG: Vector selection process failed: {vec_err}")

    # ── Nested LLM generator helper ──
    def run_generation(context: str) -> str:
        nonlocal used_model
        gen_res = None

        # Priority 1: Groq Llama-3 (if API key is set) — most accurate
        if not gen_res and (req.model == "llama" or GROQ_API_KEY):
            try:
                print("[TruthLens] Attempting Groq Llama-3 generation with memory...")
                res = llama3_generate(prompt, context, history=req.history, language=req.language)
                if res and res.strip() != "":
                    gen_res = res
                    used_model = "Groq / Llama-3.3-70B"
            except Exception as e:
                print(f"[TruthLens] Groq generation failed: {e}")

        # Priority 2: Direct Answer Extractor
        if not gen_res:
            question_words = ["who", "what", "where", "when", "why", "how", "name", "list", "identify", "tell me", "whose", "which"]
            is_active_question = any(word in prompt.lower() for word in question_words) or prompt.strip().endswith('?')
            
            if context and not is_active_question:
                try:
                    from sentence_transformers import SentenceTransformer, util
                    import torch

                    _embed_model = getattr(app.state, 'embed_model', None)
                    if _embed_model is None:
                        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
                        app.state.embed_model = _embed_model

                    raw_snippets = [s.strip() for s in filtered_snippets] if filtered_snippets else [context[:500]]
                    candidate_sentences = []
                    for snip in raw_snippets[:6]:
                        parts = [p.strip() for p in snip.replace('!', '.').replace('?', '.').split('.') if len(p.strip()) > 20]
                        candidate_sentences.extend(parts[:4])

                    if candidate_sentences:
                        q_emb  = _embed_model.encode(prompt, convert_to_tensor=True)
                        s_embs = _embed_model.encode(candidate_sentences, convert_to_tensor=True)
                        scores = util.cos_sim(q_emb, s_embs)[0]
                        best_idx = int(scores.argmax())
                        best_score = float(scores[best_idx])

                        best_sentence = candidate_sentences[best_idx]

                        if best_score > 0.60:
                            answer = best_sentence.strip().rstrip(',').strip()
                            if answer:
                                answer = answer[0].upper() + answer[1:]
                            print(f"[TruthLens] Direct Extractor -> score={best_score:.2f}: {answer[:80]}")
                            gen_res = answer
                            used_model = "TruthLens Direct Extractor (RAG)"
                except Exception as e:
                    print(f"[TruthLens] Direct Extractor failed: {e}")

        # Priority 3: Qwen fallback (last resort)
        if not gen_res:
            try:
                print("[TruthLens] Attempting Qwen fallback generation...")
                if req.language and req.language.lower() != "english":
                    lang_instruction = f" Respond ONLY in {req.language}."
                else:
                    lang_instruction = ""

                intent = detect_intent(prompt)
                intent_lower = intent.lower()
                struct_intent = parse_structured_intent(prompt)
                target = struct_intent.get("target")
                comp = struct_intent.get("competition") or ""
                yr = str(struct_intent.get("year") or "")
                
                intent_instruction = ""
                qwen_max_tokens = 150
                
                if target == "winner" or target == "champion":
                    comp_str = f" {comp}" if comp else ""
                    yr_str = f" {yr}" if yr else ""
                    intent_instruction = (
                        " Respond in EXACTLY this format and nothing else:"
                        f" 'Winner of{comp_str}{yr_str}: [Name]'"
                        " Example: 'Winner of IPL 2026: Royal Challengers Bengaluru'."
                    )
                    qwen_max_tokens = 40
                elif target == "president":
                    intent_instruction = (
                        " Respond in EXACTLY this format and nothing else:"
                        " 'President of [Place]: [Name]'"
                        " Example: 'President of the USA: Donald Trump'."
                    )
                    qwen_max_tokens = 40
                elif target == "prime minister":
                    intent_instruction = (
                        " Respond in EXACTLY this format and nothing else:"
                        " 'Prime Minister of [Place]: [Name]'"
                        " Example: 'Prime Minister of India: Narendra Modi'."
                    )
                    qwen_max_tokens = 40
                elif target == "founder":
                    ent_str = f" {comp}" if comp else " [Entity]"
                    intent_instruction = (
                        " Respond in EXACTLY this format and nothing else:"
                        f" 'Founder of{ent_str}: [Name]'"
                        " Example: 'Founder of WhatsApp: Jan Koum'."
                    )
                    qwen_max_tokens = 40
                elif target == "inventor":
                    intent_instruction = (
                        " Respond in EXACTLY this format and nothing else:"
                        " 'Inventor of [Entity]: [Name]'"
                        " Example: 'Inventor of Telephone: Alexander Graham Bell'."
                    )
                    qwen_max_tokens = 40
                elif target == "ceo":
                    intent_instruction = (
                        " Respond in EXACTLY this format and nothing else:"
                        " 'CEO of [Company]: [Name]'"
                        " Example: 'CEO of Apple: Tim Cook'."
                    )
                    qwen_max_tokens = 40
                else:
                    intent = detect_intent(prompt)
                    intent_lower = intent.lower()
                    if intent_lower == "person lookup":
                        intent_instruction = (
                            " Respond ONLY with the entity name in the format:"
                            " '[Title/Role] of [Place]: [Name]'."
                            " No extra sentences."
                        )
                        qwen_max_tokens = 40

                    elif intent_lower == "date lookup":
                        intent_instruction = (
                            " Respond with only the date or year. No prose."
                        )
                        qwen_max_tokens = 30

                    elif intent_lower == "definition":
                        intent_instruction = (
                            " Provide a definition in 3 to 5 sentences."
                            " Start with a one-line definition, then add key details."
                        )
                        qwen_max_tokens = 250

                    elif intent_lower == "explanation":
                        intent_instruction = (
                            " Provide a detailed explanation in paragraphs."
                            " Cover what it is, how it works, and give an example."
                        )
                        qwen_max_tokens = 300

                    else:  # fact_lookup
                        intent_instruction = (
                            " Answer factually. Give the key fact first,"
                            " then 1-2 sentences of supporting context."
                        )
                        qwen_max_tokens = 150

                if context:
                    if is_dynamic:
                        system_prompt = (
                            f"You are a factual assistant.{lang_instruction}{intent_instruction}"
                            " Answer using the context below ONLY. Do NOT guess or use external knowledge."
                            " If the context does not contain the answer, reply exactly: 'Unable to verify this claim with available evidence.'"
                            " Current Year: 2026."
                        )
                    else:
                        system_prompt = (
                            f"You are a factual assistant.{lang_instruction}{intent_instruction}"
                            " Answer using the context below. If the context is insufficient, use your knowledge."
                            " Current Year: 2026."
                        )
                    input_text = (
                        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                        f"<|im_start|>user\nContext: {context[:800]}\n\nQuestion: {prompt}<|im_end|>\n<|im_start|>assistant\n"
                    )
                else:
                    if is_dynamic:
                        system_prompt = (
                            f"You are a factual assistant.{lang_instruction}{intent_instruction}"
                            " Answer using your best internal knowledge."
                            " Current Year: 2026."
                        )
                        input_text = (
                            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                            f"<|im_start|>user\nQuestion: {prompt}<|im_end|>\n<|im_start|>assistant\n"
                        )
                    else:
                        input_text = (
                            f"<|im_start|>system\nYou are a factual assistant.{lang_instruction}{intent_instruction}"
                            f" Current Year: 2026.<|im_end|>\n"
                            f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
                        )

                if input_text and hasattr(app.state, 'llm_pipeline') and app.state.llm_pipeline is not None:
                    out = app.state.llm_pipeline(
                        input_text,
                        max_new_tokens=qwen_max_tokens,
                        do_sample=(intent_lower in ("definition", "explanation", "fact lookup")),
                        temperature=0.6 if intent_lower in ("definition", "explanation") else 0.3,
                    )
                    generated = out[0]['generated_text'][len(input_text):].strip()
                    if generated.lower().startswith("context:"):
                        generated = generated.split("\n")[-1].strip()
                    if generated:
                        gen_res = generated
                        used_model = "TruthLens Tiny (Local 1.1B)"
            except Exception as e:
                print(f"[TruthLens] Qwen fallback failed: {e}")

        return gen_res

    used_model = "None"
    performed_fallback_search = False

    # Check if retrieval returned no documents *before* first generation
    if not context_text or len(context_text.strip()) < 50:
        print("RAG: Retrieval returned no documents. Performing fallback web search using prompt...")
        performed_fallback_search = True
        fallback_snippets = []
        try:
            all_results = ddg_html_search(prompt, max_results=10)
            seen = set()
            for r in all_results:
                body = r.get('body', r.get('snippet', '')).strip()
                if len(body) < 40:
                    continue
                noise_words = ['cookie', 'javascript', 'subscribe', 'log in', 'sign up', 'newsletter', 'privacy policy', 'terms of service', 'captcha']
                if any(noise in body.lower() for noise in noise_words):
                    continue
                key = body[:40]
                if key in seen:
                    continue
                seen.add(key)
                fallback_snippets.append(body)
        except Exception as e:
            print(f"RAG: Fallback search failed: {e}")

        if not fallback_snippets:
            try:
                import urllib.request, urllib.parse, json as _json
                clean_wiki_query = prompt
                for prefix in ["who is ", "who was ", "what is ", "what was ", "where is ", "where was ", "tell me about ", "about ", "who are "]:
                    if clean_wiki_query.lower().startswith(prefix):
                        clean_wiki_query = clean_wiki_query[len(prefix):]
                
                ua = {'User-Agent': 'Mozilla/5.0'}
                wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_wiki_query)}&format=json"
                with urllib.request.urlopen(urllib.request.Request(wiki_url, headers=ua), timeout=5) as resp:
                    s_data = _json.loads(resp.read().decode())
                    search_results = s_data.get("query", {}).get("search", [])
                    if search_results:
                        top_title = search_results[0]["title"]
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top_title.replace(' ', '_'))}"
                        with urllib.request.urlopen(urllib.request.Request(sum_url, headers=ua), timeout=5) as sum_resp:
                            wiki_data = _json.loads(sum_resp.read().decode())
                            if wiki_data.get("extract"):
                                fallback_snippets.append(wiki_data["extract"])
            except: pass

        if fallback_snippets:
            try:
                _embed_model = getattr(app.state, 'embed_model', None)
                if _embed_model is None:
                    from sentence_transformers import SentenceTransformer
                    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
                    app.state.embed_model = _embed_model
                rag = RAGProcessor(_embed_model)
                context_text = rag.process(prompt, fallback_snippets)
                retrieval_count = len(fallback_snippets)
                print(f"RAG: Fallback web search retrieved context: {len(context_text)} chars.")
            except Exception as vec_err:
                print(f"RAG: Fallback vector selection failed: {vec_err}")

    # Generate response
    final_response = run_generation(context_text)

    # ── Fallback Web Search and Retry if first generation was invalid and fallback search was not run yet ──
    if not is_valid_generated_response(final_response) and not performed_fallback_search:
        print("RAG: First generation was invalid. Performing fallback web search using prompt...")
        fallback_snippets = []
        try:
            all_results = ddg_html_search(prompt, max_results=10)
            seen = set()
            for r in all_results:
                body = r.get('body', r.get('snippet', '')).strip()
                if len(body) < 40:
                    continue
                noise_words = ['cookie', 'javascript', 'subscribe', 'log in', 'sign up', 'newsletter', 'privacy policy', 'terms of service', 'captcha']
                if any(noise in body.lower() for noise in noise_words):
                    continue
                key = body[:40]
                if key in seen:
                    continue
                seen.add(key)
                fallback_snippets.append(body)
        except Exception as e:
            print(f"RAG: Fallback search failed: {e}")

        if not fallback_snippets:
            try:
                import urllib.request, urllib.parse, json as _json
                clean_wiki_query = prompt
                for prefix in ["who is ", "who was ", "what is ", "what was ", "where is ", "where was ", "tell me about ", "about ", "who are "]:
                    if clean_wiki_query.lower().startswith(prefix):
                        clean_wiki_query = clean_wiki_query[len(prefix):]
                
                ua = {'User-Agent': 'Mozilla/5.0'}
                wiki_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_wiki_query)}&format=json"
                with urllib.request.urlopen(urllib.request.Request(wiki_url, headers=ua), timeout=5) as resp:
                    s_data = _json.loads(resp.read().decode())
                    search_results = s_data.get("query", {}).get("search", [])
                    if search_results:
                        top_title = search_results[0]["title"]
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top_title.replace(' ', '_'))}"
                        with urllib.request.urlopen(urllib.request.Request(sum_url, headers=ua), timeout=5) as sum_resp:
                            wiki_data = _json.loads(sum_resp.read().decode())
                            if wiki_data.get("extract"):
                                fallback_snippets.append(wiki_data["extract"])
            except: pass

        if fallback_snippets:
            try:
                _embed_model = getattr(app.state, 'embed_model', None)
                if _embed_model is None:
                    from sentence_transformers import SentenceTransformer
                    _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
                    app.state.embed_model = _embed_model
                rag = RAGProcessor(_embed_model)
                context_text = rag.process(prompt, fallback_snippets)
                retrieval_count = len(fallback_snippets)
                print(f"RAG: Fallback web search retrieved context: {len(context_text)} chars. Retrying generation...")
                # Retry generation
                final_response = run_generation(context_text)
            except Exception as vec_err:
                print(f"RAG: Fallback vector selection failed: {vec_err}")

    # ── Requirement 2 & 6: If generation fails ──
    if not final_response or final_response.strip() == "" or not is_valid_generated_response(final_response):
        print(f"[TruthLens LOG] Retrieval Results Count: {retrieval_count}")
        print(f"[TruthLens LOG] LLM Response: {final_response if final_response else '[Generation Failed]'}")
        print(f"[TruthLens LOG] Verification Confidence: 0.0")
        return {
            "status": "error",
            "generated_response": "Knowledge source unavailable. Please try again.",
            "model": used_model,
            "prompt": prompt,
            "context": context_text,
            "evaluation": None,
            "rag_chunks": local_chunks
        }

    return verify_and_resolve_response(
        prompt=prompt,
        generated_response=final_response,
        context_text=context_text,
        is_dynamic=is_dynamic,
        local_chunks=local_chunks,
        model_name=used_model,
        language=req.language,
        retrieval_count=retrieval_count
    )

@app.post("/api/compare")
def compare_llms(req: GenerateRequest, user: str = Depends(verify_token)):
    """
    Multi-LLM Comparison Engine.
    Simulates GPT, Gemini, Claude, and Llama using specialized personas.
    """
    from duckduckgo_search import DDGS
    prompt = req.prompt.strip()
    context_text = ""
    
    # Retrieval step with improved accuracy
    try:
        with DDGS() as ddgs:
            search_query = f"latest verified facts: {prompt}"
            results = list(ddgs.text(search_query, max_results=5))
        if results:
            keywords = prompt.lower().split()
            filtered = [r.get('body', '') for r in results if any(kw in r.get('body', '').lower() for kw in keywords)]
            context_text = " ".join(filtered[:3]) if filtered else " ".join([r.get('body', '') for r in results[:2]])
    except: pass

    if req.language and req.language.lower() != "english":
        lang_instruction = f" Respond ONLY in {req.language}."
    else:
        lang_instruction = ""

    models = [
        {"name": "OpenAI GPT-4o", "persona": f"You are OpenAI GPT-4o. Provide a detailed, structured, and factual response.{lang_instruction}"},
        {"name": "Google Gemini Pro", "persona": f"You are Google Gemini. Provide a concise response with clear bullet points.{lang_instruction}"},
        {"name": "Anthropic Claude 3.5", "persona": f"You are Anthropic Claude. Provide a helpful, honest, and harmless response with a slightly formal tone.{lang_instruction}"},
        {"name": "Meta Llama 3", "persona": f"You are Meta Llama 3. Provide a direct, plain-text response without any fluff.{lang_instruction}"}
    ]

    responses = []
    for m in models:
        try:
            # We use the same TinyLlama backbone but with different system instructions to simulate 'diversity'
            sys_msg = m["persona"]
            if context_text:
                input_text = f"<|system|>\n{sys_msg} Use this context: {context_text[:1000]}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
            else:
                input_text = f"<|system|>\n{sys_msg}</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
            
            # Slightly vary temperature for 'diversity' in simulation
            temp = 0.7 if "GPT" in m["name"] else 0.2
            if hasattr(app.state, 'llm_pipeline') and app.state.llm_pipeline is not None:
                out = app.state.llm_pipeline(input_text, max_new_tokens=150, do_sample=True, temperature=temp)
                text = out[0]['generated_text'][len(input_text):].strip()
            else:
                text = f"[Simulation Response for {m['name']}]"
            responses.append({"model": m["name"], "text": text})
        except:
            responses.append({"model": m["name"], "text": "[Simulation Error]"})

    # Find disagreements (unstable facts) using NLI if possible, or simple overlap check
    # For now, we return the responses and let the UI handle the 'diff' highlighting
    return {
        "prompt": prompt,
        "responses": responses,
        "context": context_text
    }

@app.get("/api/me")
def get_me(user: dict = Depends(verify_token)):
    return {"status": "success", "user": user}


# ── Chat Management System API ───────────────────────────────────────────────

class ChatCreateRequest(BaseModel):
    id: str
    title: str
    prompt: str
    response: str
    risk_score: int
    verdict: str
    created_at: str
    updated_at: str
    is_saved: bool = False
    evaluation_data: str = "" # serialized JSON string of evaluation details

class ChatUpdateRequest(BaseModel):
    title: str = None
    is_saved: bool = None
    updated_at: str = None

class BulkDeleteRequest(BaseModel):
    ids: list

class BulkSaveRequest(BaseModel):
    ids: list
    is_saved: bool

@app.get("/api/chats")
def get_chats(user: dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    email = user["email"]
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, prompt, response, risk_score, verdict, created_at, updated_at, is_saved, evaluation_data FROM chats WHERE email = ? ORDER BY created_at DESC",
            (email,)
        )
        rows = cursor.fetchall()
        
        chats_list = []
        for r in rows:
            chats_list.append({
                "id": r["id"],
                "title": r["title"],
                "prompt": r["prompt"],
                "response": r["response"],
                "risk_score": r["risk_score"],
                "verdict": r["verdict"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
                "is_saved": bool(r["is_saved"]),
                "evaluation_data": r["evaluation_data"]
            })
        return chats_list

@app.post("/api/chats")
def create_chat(req: ChatCreateRequest, user: dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    email = user["email"]
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Check if chat already exists
        cursor.execute("SELECT id FROM chats WHERE id = ? AND email = ?", (req.id, email))
        exists = cursor.fetchone()
        
        is_saved_int = 1 if req.is_saved else 0
        
        if exists:
            # Update existing
            cursor.execute(
                """UPDATE chats SET 
                    title = ?, prompt = ?, response = ?, risk_score = ?, verdict = ?, 
                    updated_at = ?, is_saved = ?, evaluation_data = ?
                   WHERE id = ? AND email = ?""",
                (req.title, req.prompt, req.response, req.risk_score, req.verdict,
                 req.updated_at, is_saved_int, req.evaluation_data, req.id, email)
            )
        else:
            # Insert new
            cursor.execute(
                """INSERT INTO chats 
                    (id, email, title, prompt, response, risk_score, verdict, created_at, updated_at, is_saved, evaluation_data)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (req.id, email, req.title, req.prompt, req.response, req.risk_score, req.verdict,
                 req.created_at, req.updated_at, is_saved_int, req.evaluation_data)
            )
        conn.commit()
        return {"status": "success", "chat_id": req.id}

@app.put("/api/chats/{chat_id}")
def update_chat(chat_id: str, req: ChatUpdateRequest, user: dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    email = user["email"]
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Build dynamic query based on what is provided
        updates = []
        params = []
        
        if req.title is not None:
            updates.append("title = ?")
            params.append(req.title)
        if req.is_saved is not None:
            updates.append("is_saved = ?")
            params.append(1 if req.is_saved else 0)
        if req.updated_at is not None:
            updates.append("updated_at = ?")
            params.append(req.updated_at)
            
        if not updates:
            return {"status": "ignored"}
            
        params.extend([chat_id, email])
        query = f"UPDATE chats SET {', '.join(updates)} WHERE id = ? AND email = ?"
        
        cursor.execute(query, tuple(params))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")
            
        return {"status": "success"}

@app.delete("/api/chats/{chat_id}")
def delete_chat(chat_id: str, user: dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    email = user["email"]
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats WHERE id = ? AND email = ?", (chat_id, email))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")
            
        return {"status": "success"}

@app.post("/api/chats/bulk-delete")
def bulk_delete_chats(req: BulkDeleteRequest, user: dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    email = user["email"]
    
    if not req.ids:
        return {"status": "success", "count": 0}
        
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(req.ids))
        query = f"DELETE FROM chats WHERE email = ? AND id IN ({placeholders})"
        cursor.execute(query, [email] + req.ids)
        conn.commit()
        
        return {"status": "success", "count": cursor.rowcount}

@app.post("/api/chats/bulk-save")
def bulk_save_chats(req: BulkSaveRequest, user: dict = Depends(verify_token)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    email = user["email"]
    
    if not req.ids:
        return {"status": "success", "count": 0}
        
    is_saved_int = 1 if req.is_saved else 0
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(req.ids))
        query = f"UPDATE chats SET is_saved = ? WHERE email = ? AND id IN ({placeholders})"
        cursor.execute(query, [is_saved_int, email] + req.ids)
        conn.commit()
        
        return {"status": "success", "count": cursor.rowcount}

class AuthRequest(BaseModel):
    email: str
    password: str
    name: str = ""

@app.post("/api/register")
def register(req: AuthRequest):
    if len(req.password) < 6:
        return {"status": "error", "message": "Password must be at least 6 characters."}
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = ?", (req.email,))
        if cursor.fetchone():
            return {"status": "error", "message": "An account with this email already exists."}
        
        salt = secrets.token_hex(16)
        pw_hash = hash_password(req.password, bytes.fromhex(salt))
        name = req.name or req.email.split("@")[0]
        
        cursor.execute("INSERT INTO users (email, name, salt, password_hash) VALUES (?, ?, ?, ?)",
                       (req.email, name, salt, pw_hash))
        
        token = str(uuid.uuid4())
        cursor.execute("INSERT INTO sessions (token, email) VALUES (?, ?)", (token, req.email))
        conn.commit()
        return {"status": "success", "token": token, "name": name}

@app.post("/api/login")
def login(req: AuthRequest):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, salt, password_hash FROM users WHERE email = ?", (req.email,))
        row = cursor.fetchone()
        if not row:
            return {"status": "error", "message": "No account found with this email."}
        
        name, salt, pw_hash = row
        if hash_password(req.password, bytes.fromhex(salt)) != pw_hash:
            return {"status": "error", "message": "Incorrect password. Please try again."}
            
        token = str(uuid.uuid4())
        cursor.execute("INSERT INTO sessions (token, email) VALUES (?, ?)", (token, req.email))
        conn.commit()
        return {"status": "success", "token": token, "name": name}


class ContactRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    inquiry_type: str
    message: str
    honeypot: str = ""

contact_rate_limits = {}

def send_contact_email(first_name: str, last_name: str, email: str, inquiry_type: str, message: str):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import urllib.request
    import urllib.parse
    import json as _json

    subject = f"TruthLens Inquiry: {inquiry_type.capitalize()} from {first_name} {last_name}"
    body_text = f"""
New Inquiry Received from TruthLens Contact Form:

Name: {first_name} {last_name}
Email: {email}
Inquiry Type: {inquiry_type}
Message:
{message}
"""
    
    # 1. Resend API
    resend_key = os.environ.get("RESEND_API_KEY")
    if resend_key:
        try:
            print("[Email] Sending via Resend API...")
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json"
            }
            data = {
                "from": "TruthLens Form <onboarding@resend.dev>",
                "to": "truthlens.verify@gmail.com",
                "subject": subject,
                "text": body_text
            }
            req = urllib.request.Request(
                url, 
                data=_json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"[Email] Resend success: {response.read().decode('utf-8')}")
                return True
        except Exception as e:
            print(f"[Email] Resend failed: {e}")

    # 2. SendGrid API
    sendgrid_key = os.environ.get("SENDGRID_API_KEY")
    if sendgrid_key:
        try:
            print("[Email] Sending via SendGrid API...")
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {sendgrid_key}",
                "Content-Type": "application/json"
            }
            data = {
                "personalizations": [{"to": [{"email": "truthlens.verify@gmail.com"}]}],
                "from": {"email": "truthlens.verify@gmail.com"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body_text}]
            }
            req = urllib.request.Request(
                url,
                data=_json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                print(f"[Email] SendGrid success: status={response.status}")
                return True
        except Exception as e:
            print(f"[Email] SendGrid failed: {e}")

    # 3. SMTP
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = os.environ.get("SMTP_PORT")
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    if smtp_host:
        try:
            print(f"[Email] Sending via SMTP {smtp_host}...")
            msg = MIMEMultipart()
            msg["From"] = smtp_user or "truthlens.verify@gmail.com"
            msg["To"] = "truthlens.verify@gmail.com"
            msg["Subject"] = subject
            msg.attach(MIMEText(body_text, "plain"))
            
            port = int(smtp_port) if smtp_port else 587
            if port == 465:
                server = smtplib.SMTP_SSL(smtp_host, port, timeout=5)
            else:
                server = smtplib.SMTP(smtp_host, port, timeout=5)
                server.starttls()
                
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
                
            server.sendmail(msg["From"], [msg["To"]], msg.as_string())
            server.quit()
            print("[Email] SMTP sent successfully.")
            return True
        except Exception as e:
            print(f"[Email] SMTP failed: {e}")

    # Fallback
    print(f"""
==================================================
[EMAIL SIMULATION] (No credentials configured)
To: truthlens.verify@gmail.com
Subject: {subject}
{body_text}
==================================================
""")
    return False

@app.post("/api/contact")
async def contact_submit(req: ContactRequest, request: Request):
    import time
    
    # 1. Rate Limiting (1 request per 30 seconds per IP)
    ip = request.client.host
    now = time.time()
    if ip in contact_rate_limits:
        elapsed = now - contact_rate_limits[ip]
        if elapsed < 30:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait 30 seconds.")
    
    # 2. Honeypot check (anti-spam)
    if req.honeypot.strip():
        # Silent success for bots
        print(f"[Contact] Honeypot triggered by IP {ip}. Silent success.")
        return {"status": "success", "message": "Your message has been sent successfully. Our team will contact you soon."}

    # 3. Backend validation
    if not req.first_name.strip() or not req.last_name.strip():
        raise HTTPException(status_code=400, detail="First name and last name are required.")
    
    if len(req.message.strip()) < 10:
        raise HTTPException(status_code=400, detail="Message must be at least 10 characters long.")
        
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, req.email):
        raise HTTPException(status_code=400, detail="Invalid email format.")

    valid_types = {"enterprise", "research", "support", "partners", "feedback"}
    if req.inquiry_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid inquiry type.")

    # Apply rate limit after validation to avoid blocking invalid attempts
    contact_rate_limits[ip] = now

    # 4. Save to Database
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO contact_submissions (first_name, last_name, email, inquiry_type, message) VALUES (?, ?, ?, ?, ?)",
                (req.first_name.strip(), req.last_name.strip(), req.email.strip(), req.inquiry_type, req.message.strip())
            )
            conn.commit()
    except Exception as e:
        print(f"[Contact] DB Insert failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to save submission to database.")

    # 5. Send Email
    send_contact_email(
        first_name=req.first_name.strip(),
        last_name=req.last_name.strip(),
        email=req.email.strip(),
        inquiry_type=req.inquiry_type,
        message=req.message.strip()
    )

    return {"status": "success", "message": "Your message has been sent successfully. Our team will contact you soon."}


app.mount("/", NoCacheStaticFiles(directory=STATIC_DIR), name="static_root")

if __name__ == "__main__":
    print("Starting TruthLens AI Backend...")
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
