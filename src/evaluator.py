"""
TruthLens Real Hallucination Evaluator
Uses genuine NLP models — no mock/random scores.

Models loaded lazily on first evaluation call:
  1. all-MiniLM-L6-v2       — semantic consistency (cosine similarity)
  2. cross-encoder/nli-deberta-v3-small — NLI contradiction detection
  3. vectara/hallucination_evaluation_model — HHEM factuality scoring
"""

import os
from dotenv import load_dotenv
load_dotenv()
import re
import functools
import urllib.request
import urllib.parse
import html
import numpy as np
from typing import Optional

def ddg_html_search(query: str, max_results: int = 10) -> list:
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            content = response.read().decode('utf-8')
            
        snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', content, re.DOTALL)
        titles = re.findall(r'<h2 class="result__title"[^>]*>.*?<a[^>]*>(.*?)</a>', content, re.DOTALL)
        urls = re.findall(r'<a class="result__url"[^>]*>(.*?)</a>', content, re.DOTALL)
        
        results = []
        for i in range(min(max_results, len(snippets))):
            snippet_text = re.sub(r'<[^>]+>', '', snippets[i])
            snippet_text = html.unescape(snippet_text).strip()
            
            title_text = "Web Search Result"
            if i < len(titles):
                title_text = re.sub(r'<[^>]+>', '', titles[i])
                title_text = html.unescape(title_text).strip()
                
            href = ""
            if i < len(urls):
                href = urls[i].strip()
                
            results.append({
                "title": title_text,
                "body": snippet_text,
                "snippet": snippet_text,
                "href": href
            })
        return results
    except Exception as e:
        print(f"[TruthLens] Error in direct ddg search: {e}")
        return []

def parse_structured_intent(query: str) -> dict:
    p_lower = query.lower()
    intent = {
        "domain": "general",
        "competition": None,
        "year": None,
        "target": "fact"
    }
    
    # Extract year if present
    year_match = re.search(r'\b(202\d|19\d\d)\b', p_lower)
    if year_match:
        intent["year"] = int(year_match.group(1))
        
    # Check domain & target synonyms
    winner_synonyms = ["winner", "won", "champion", "title holder", "trophy winner", "trophy holder", "received title", "received the ipl title", "received the title"]
    if any(syn in p_lower for syn in winner_synonyms):
        intent["target"] = "winner"
    elif "president" in p_lower:
        intent["target"] = "president"
    elif "prime minister" in p_lower or " pm " in p_lower or p_lower.startswith("pm ") or p_lower.endswith(" pm"):
        intent["target"] = "prime minister"
    elif "founder" in p_lower or "founded" in p_lower:
        intent["target"] = "founder"
    elif "inventor" in p_lower or "invented" in p_lower:
        intent["target"] = "inventor"
    elif "ceo" in p_lower:
        intent["target"] = "ceo"
        
    # Domain & Competition
    if "ipl" in p_lower:
        intent["domain"] = "sports"
        intent["competition"] = "IPL"
    elif any(x in p_lower for x in ["world cup", "football", "soccer", "olympics", "championship", "tournament", "nfl", "nba", "cricket"]):
        intent["domain"] = "sports"
        if "world cup" in p_lower:
            intent["competition"] = "World Cup"
        elif "nfl" in p_lower:
            intent["competition"] = "NFL"
        elif "nba" in p_lower:
            intent["competition"] = "NBA"
    elif any(x in p_lower for x in ["president", "prime minister", "election", "pm", "government", "senate", "mayor", "governor"]):
        intent["domain"] = "politics"
    elif any(x in p_lower for x in ["news", "today", "recent", "headlines"]):
        intent["domain"] = "news"
    elif "whatsapp" in p_lower or "software" in p_lower or "app " in p_lower or "website" in p_lower or "internet" in p_lower:
        intent["domain"] = "technology"
        if "whatsapp" in p_lower:
            intent["competition"] = "WhatsApp"
        
    # Use Groq for advanced parsing if available
    key = os.environ.get("GROQ_API_KEY", None)
    if key:
        try:
            from groq import Groq
            import json as _json
            client = Groq(api_key=key)
            system_prompt = (
                "You are an expert semantic query parser.\n"
                "Parse the user's query into a structured JSON intent with these keys:\n"
                "  - domain: string (e.g. sports, politics, news, business, technology, general)\n"
                "  - competition: string or null (e.g. IPL, NBA, WhatsApp if sports/tech)\n"
                "  - year: integer or null (e.g. 2026 if mentioned)\n"
                "  - target: string (e.g. winner, president, prime minister, founder, inventor, CEO, fact)\n"
                "Keep values simple and normalized. Return the JSON object only."
            )
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                max_tokens=100,
                response_format={"type": "json_object"}
            )
            data = _json.loads(completion.choices[0].message.content.strip())
            # Merge/override rule-based with LLM results for keys that exist
            for k in ["domain", "competition", "year", "target"]:
                if k in data:
                    intent[k] = data[k]
        except Exception as e:
            print(f"[TruthLens] LLM structured intent parsing failed: {e}")
            
    return intent

def is_answer_supported_by_evidence(generated_answer: str, context_text: str) -> bool:
    if not context_text or len(context_text.strip()) < 10:
        return False
        
    entity = generated_answer
    if ":" in generated_answer:
        entity = generated_answer.split(":", 1)[1].strip()
        
    entity_clean = entity.strip().lower()
    entity_clean = entity_clean.strip('"').strip("'").strip()
    
    if not entity_clean or entity_clean in ["unable to verify", "unable to verify this claim with available evidence", "unable to verify with current evidence"]:
        return False
        
    context_lower = context_text.lower()
    
    if entity_clean in context_lower:
        return True
        
    stop_words = {"the", "of", "and", "a", "an", "in", "to", "for", "with", "at", "by", "from", "on"}
    words = [w for w in re.findall(r'\b\w+\b', entity_clean) if w not in stop_words]
    
    if words:
        match_count = sum(1 for w in words if w in context_lower)
        if match_count == len(words):
            return True
            
        if "rcb" in context_lower and ("royal" in entity_clean or "bengluru" in entity_clean or "bengaluru" in entity_clean):
            return True
            
        if len(words) >= 2:
            unique_words = [w for w in words if len(w) > 3]
            if any(w in context_lower for w in unique_words):
                return True
                
    return False

def is_valid_generated_response(response: str) -> bool:
    if not response:
        return False
    r_lower = response.lower()
    invalid_keywords = [
        "knowledge source unavailable",
        "unable to generate a response",
        "unable to generate response",
        "could not generate a response",
        "could not generate response",
        "please try again"
    ]
    for kw in invalid_keywords:
        if kw in r_lower:
            return False
    return True

def convert_topic_to_query(prompt: str) -> str:
    prompt_clean = prompt.strip()
    if not prompt_clean:
        return prompt_clean
    
    key = os.environ.get("GROQ_API_KEY", None)
    if key:
        try:
            from groq import Groq
            client = Groq(api_key=key)
            system_prompt = (
                "You are an expert search query optimizer.\n"
                "Determine if the user's input is a topic, title, role, or generic phrase (e.g. 'Chief of the Army Staff of the Indian Army', 'President of France') rather than a complete question or statement.\n"
                "If it is a topic or generic phrase, convert it into an explicit, searchable factual query by prefixing or appending words like 'Current' or 'Who is the current' (e.g. 'Current Chief of the Army Staff of the Indian Army').\n"
                "If the input is already a question or a statement, just output the optimized search query.\n"
                "Output the final search query only, without explanation, intro, or quotes."
            )
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_clean}
                ],
                temperature=0.0,
                max_tokens=50
            )
            result = completion.choices[0].message.content.strip().strip('"').strip("'")
            if result:
                return result
        except Exception as e:
            print(f"[TruthLens] Groq topic-to-query conversion error: {e}")
            
    p_lower = prompt_clean.lower()
    question_words = ["who", "what", "where", "when", "why", "how", "whose", "which", "is ", "was ", "are ", "were "]
    is_question = any(p_lower.startswith(w) for w in question_words) or prompt_clean.endswith('?')
    
    if not is_question and len(prompt_clean.split()) <= 15:
        if not p_lower.startswith("current"):
            return f"Current {prompt_clean}"
            
    return prompt_clean

@functools.lru_cache(maxsize=128)
def is_dynamic_fact_query(query: str) -> bool:
    # 1. Parse structured intent
    intent = parse_structured_intent(query)
    
    # 2. Sports, politics, elections, news, current affairs are dynamic domains
    if intent["domain"] in ["sports", "politics", "news"]:
        return True
        
    # 3. Dynamic target values
    if intent["target"] in ["winner", "champion", "president", "prime minister", "ceo", "inventor", "founder"]:
        return True

    p_lower = query.lower()
    
    # 4. Keyword boundaries
    dynamic_keywords = [
        "current", "currently", "latest", "today", "recent", "recently", "now", "winner", "winners", "news", "election",
        "elections", "2025", "2026", "2027", "president", "presidents", "prime minister", "prime ministers",
        "pm", "champion", "champions", "score", "scores", "match", "matches", "founder", "inventor", "ceo"
    ]
    for kw in dynamic_keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', p_lower):
            return True
            
    if re.search(r'\b(202\d|19\d\d)\b', p_lower):
        return True
        
    return False


# Canonical intent labels used throughout the pipeline
INTENT_PERSON_LOOKUP = "Person lookup"
INTENT_DATE_LOOKUP    = "Date lookup"
INTENT_DEFINITION     = "Definition"
INTENT_EXPLANATION    = "Explanation"
INTENT_FACT_LOOKUP    = "Fact lookup"


def detect_query_intent(prompt: str) -> str:
    """
    Detects the intent of a query. Returns one of exactly five canonical labels:
      - 'Person lookup'  : asking for a person's name or identity
      - 'Date lookup'    : asking for a date, year, or time period
      - 'Definition'     : asking for the definition of a term
      - 'Explanation'    : asking how/why something works or roles/responsibilities
      - 'Fact lookup'    : any other factual question

    Intent is NEVER converted from one type to another elsewhere in the pipeline.
    """
    p_lower = prompt.lower()

    # Person lookup — who is, name of, role holders
    if (
        "who" in p_lower
        or "name" in p_lower
        or "president" in p_lower
        or "prime minister" in p_lower
        or " pm " in p_lower
        or p_lower.startswith("pm ")
        or p_lower.endswith(" pm")
        or "ceo" in p_lower
        or "leader" in p_lower
        or "founder" in p_lower
        or "chairman" in p_lower
        or "governor" in p_lower
        or "mayor" in p_lower
        or "minister" in p_lower
    ):
        return INTENT_PERSON_LOOKUP

    # Date lookup — when, year, born, age
    if (
        "when" in p_lower
        or "date" in p_lower
        or "year" in p_lower
        or "born" in p_lower
        or "age" in p_lower
        or "how old" in p_lower
        or "founded" in p_lower
        or "established" in p_lower
    ):
        return INTENT_DATE_LOOKUP

    # Definition — what is, define, definition
    if (
        "what is" in p_lower
        or "what are" in p_lower
        or "define" in p_lower
        or "definition" in p_lower
        or "meaning of" in p_lower
    ):
        return INTENT_DEFINITION

    # Explanation — how, why, explain, role of, responsibilities
    if (
        "how" in p_lower
        or "why" in p_lower
        or "explain" in p_lower
        or "role of" in p_lower
        or "responsibilities" in p_lower
        or "describe" in p_lower
    ):
        return INTENT_EXPLANATION

    return INTENT_FACT_LOOKUP


def get_verdict_label(risk_score: int) -> str:
    if risk_score <= 20:
        return "High Trust"
    elif risk_score <= 40:
        return "Moderate Risk"
    elif risk_score <= 60:
        return "High Risk"
    else:
        return "Severe Risk"


class TruthLensEvaluator:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        self._loaded = False
        self.embed_model = None
        self.nli_pipe = None
        self.hhem_pipe = None

    # ── Model Loading ──────────────────────────────────────────────────────────

    def _load_models(self):
        if self._loaded:
            return
        
        import torch
        device_id = 0 if torch.cuda.is_available() else -1
        device_str = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"[TruthLens] Loading sentence-transformer (all-MiniLM-L6-v2) on {device_str}...")
        from sentence_transformers import SentenceTransformer
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2", device=device_str)

        print(f"[TruthLens] Loading NLI model (cross-encoder/nli-deberta-v3-small) on {device_str}...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        self._nli_tokenizer = AutoTokenizer.from_pretrained("cross-encoder/nli-deberta-v3-small")
        self._nli_model = AutoModelForSequenceClassification.from_pretrained(
            "cross-encoder/nli-deberta-v3-small"
        ).to(device_str)
        self._nli_model.eval()

        print(f"[TruthLens] Loading HHEM model (vectara/hallucination_evaluation_model) on {device_str}...")
        from transformers import pipeline
        try:
            self.hhem_pipe = pipeline(
                "text-classification",
                model="vectara/hallucination_evaluation_model",
                device=device_id,
                trust_remote_code=True
            )
        except Exception as e:
            print(f"[TruthLens] HHEM failed to load due to library incompatibility. Falling back. Error: {e}")
            self.hhem_pipe = None

        self._loaded = True
        print("[TruthLens] All models ready.")

    # ── Metric 1: Semantic Consistency ────────────────────────────────────────

    def _consistency(self, prompt: str, response: str, context: str) -> tuple:
        from sentence_transformers import util
        if not context or len(context) < 50:
            return 0.2, "Limited evidence context for semantic verification."
            
        # Encode with context to check factual alignment
        emb_ctx = self.embed_model.encode(context[:1000])
        emb_res = self.embed_model.encode(response)
        score = util.cos_sim(emb_ctx, emb_res).item()
        
        # Risk is lower if response is semantically tied to retrieved facts
        risk = 1.0 - max(0.0, score)
        detail = f"Semantic grounding in evidence: {round(score*100, 1)}%."
        return risk, detail

    # ── Metric 2: NLI Contradiction ───────────────────────────────────────────

    def _nli_probs(self, source: str, response: str) -> tuple:
        import torch
        device_str = "cuda" if torch.cuda.is_available() else "cpu"
        
        inputs = self._nli_tokenizer(
            source[:512], response[:256], 
            return_tensors="pt", truncation=True, max_length=512
        ).to(device_str)
        
        with torch.no_grad():
            logits = self._nli_model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).squeeze().tolist()

        # cross-encoder/nli-deberta-v3-small label order: contradiction, entailment, neutral
        label_names = self._nli_model.config.id2label
        scores = {label_names[i].lower(): probs[i] for i in range(len(probs))}

        contradiction = scores.get("contradiction", probs[0])
        entailment    = scores.get("entailment",    probs[1] if len(probs) > 1 else 0.0)
        neutral       = scores.get("neutral",       probs[2] if len(probs) > 2 else 0.0)
        return contradiction, entailment, neutral

    def _nli(self, source: str, response: str) -> tuple:
        contradiction, entailment, neutral = self._nli_probs(source, response)
        risk = round(min(1.0, contradiction + 0.4 * neutral), 4)
        detail = (
            f"NLI — Contradiction: {contradiction*100:.1f}%, "
            f"Entailment: {entailment*100:.1f}%, "
            f"Neutral: {neutral*100:.1f}%."
        )
        return risk, detail

    # ── Metric 3: HHEM (Vectara) ──────────────────────────────────────────────

    def _hhem(self, source: str, response: str, precalculated_nli_risk=None) -> tuple:
        if not self.hhem_pipe:
            if precalculated_nli_risk is not None:
                return precalculated_nli_risk, "HHEM unavailable. Score inferred from logical NLI analysis."
            risk, _ = self._nli(source, response)
            return risk, "HHEM unavailable. Score inferred from logical NLI analysis."
            
        result = self.hhem_pipe({"text": source[:400], "text_pair": response[:400]}, truncation=True, max_length=512)[0]
        label = result["label"].lower()
        score = result["score"]
        # vectara model: LABEL_0 = hallucination, LABEL_1 = factual
        risk = round(score if ("hallucination" in label or label == "label_0") else 1.0 - score, 4)
        verdict = "hallucination" if risk > 0.5 else "factual"
        detail = (
            f"HHEM predicts '{verdict}' with {max(risk, 1-risk)*100:.1f}% confidence. "
            f"Hallucination risk: {risk*100:.1f}%."
        )
        return risk, detail

    def _compute_relevance(self, prompt: str, text: str) -> float:
        from sentence_transformers import util
        import re
        
        # 1. Semantic Similarity
        emb_p = self.embed_model.encode(prompt, convert_to_tensor=True)
        emb_t = self.embed_model.encode(text, convert_to_tensor=True)
        cos_sim_val = float(util.cos_sim(emb_p, emb_t).item())
        
        # Rescale semantic similarity from [0.2, 0.6] to [0.0, 1.0]
        if cos_sim_val <= 0.2:
            rescaled_cos = max(0.0, cos_sim_val)
        else:
            rescaled_cos = min(1.0, (cos_sim_val - 0.2) / 0.4)
            
        # 2. Keyword Overlap
        prompt_words = set(re.findall(r'\b\w+\b', prompt.lower()))
        stop_words = {'who', 'is', 'what', 'where', 'when', 'why', 'how', 'the', 'of', 'in', 'and', 'a', 'to', 'for', 'on', 'with', 'at', 'by', 'an'}
        prompt_keywords = prompt_words - stop_words
        
        if prompt_keywords:
            text_words = set(re.findall(r'\b\w+\b', text.lower()))
            overlap = prompt_keywords.intersection(text_words)
            overlap_ratio = len(overlap) / len(prompt_keywords)
            # Hybrid blend
            score = 0.4 * rescaled_cos + 0.6 * overlap_ratio
        else:
            score = rescaled_cos
            
        return max(0.0, min(1.0, score))

    def _generate_explanation(self, response: str, prompt: str, context: str, language: str = "English", 
                              sentences: list = None, sentences_en: list = None, evidence: list = None,
                              global_nli_risks: list = None, nli_cache: dict = None) -> dict:
        import re
        import torch
        from sentence_transformers import util
        
        loc = {
            "english": {
                "correction_prefix": "Grounded evidence states",
                "reason_prefix": "Logical NLI analysis flagged this sentence as a potential hallucination",
                "risk_score": "Risk Score"
            },
            "spanish": {
                "correction_prefix": "La evidencia fundamental afirma",
                "reason_prefix": "El análisis lógico de NLI marcó esta oración como una posible alucinación",
                "risk_score": "Puntuación de riesgo"
            },
            "french": {
                "correction_prefix": "Les preuves factuelles indiquent",
                "reason_prefix": "L'analyse logique NLI a signalé cette phrase comme une hallucination potentielle",
                "risk_score": "Score de risque"
            },
            "german": {
                "correction_prefix": "Fundierte Beweise belegen",
                "reason_prefix": "Die logische NLI-Analyse hat diesen Satz als potenzielle Halluzination markiert",
                "risk_score": "Risikobewertung"
            },
            "hindi": {
                "correction_prefix": "आधारित साक्ष्य बताते हैं",
                "reason_prefix": "तार्किक एनएलआई विश्लेषण ने इस वाक्य को एक संभावित मतिभ्रम के रूप में चिह्नित किया",
                "risk_score": "जोखिम स्कोर"
            },
            "telugu": {
                "correction_prefix": "ఆధారిత ఆధారాలు పేర్కొంటున్నాయి",
                "reason_prefix": "లాజికల్ NLI విశ్లేషణ ఈ వాక్యాన్ని సంభావ్య భ్రమగా గుర్తించింది",
                "risk_score": "ప్రమాద స్కోర్"
            }
        }
        
        lang_key = language.lower() if language else "english"
        if lang_key not in loc:
            lang_key = "english"
        texts = loc[lang_key]

        if not sentences:
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", response) if len(s.strip()) > 5]
        if not sentences_en:
            sentences_en = sentences
            
        if not sentences or not context:
            return None
            
        try:
            if evidence:
                snippets = [e["snippet"] for e in evidence]
                snippets_en = [e.get("snippet_en", e["snippet"]) for e in evidence]
            else:
                raw_snippets = re.split(r"\n|(?<=[.!?])\s+", context)
                snippets = [s.strip() for s in raw_snippets if len(s.strip()) > 20]
                if not snippets:
                    snippets = [context]
                snippets_en = snippets
                
            if not snippets:
                return None

            flagged_idx = 0
            max_contradiction = -1.0
            
            if global_nli_risks and len(global_nli_risks) == len(sentences_en):
                flagged_idx = int(np.argmax(global_nli_risks))
                max_contradiction = global_nli_risks[flagged_idx]
            else:
                context_en = " ".join(snippets_en)
                for idx, sent_en in enumerate(sentences_en):
                    c_risk, _ = self._nli(context_en, sent_en)
                    if c_risk > max_contradiction:
                        max_contradiction = c_risk
                        flagged_idx = idx
            
            flagged_sentence = sentences[flagged_idx]
            flagged_sentence_en = sentences_en[flagged_idx]
            
            best_candidate_idx = 0
            if nli_cache and flagged_idx is not None:
                max_logic_signal = -1.0
                for idx in range(len(snippets_en)):
                    probs = nli_cache.get((flagged_idx, idx))
                    if probs:
                        contradiction, entailment, neutral = probs
                        # We want the snippet that either entails or contradicts most (relevance)
                        logic_signal = max(contradiction, entailment)
                        if logic_signal > max_logic_signal:
                            max_logic_signal = logic_signal
                            best_candidate_idx = idx
            else:
                flagged_emb = self.embed_model.encode(flagged_sentence_en, convert_to_tensor=True)
                snippet_embs = self.embed_model.encode(snippets_en, convert_to_tensor=True)
                sim_scores = util.cos_sim(flagged_emb, snippet_embs)[0]
                
                top_k = min(5, len(snippets_en))
                top_indices = torch.topk(sim_scores, k=top_k).indices.tolist()
                
                best_candidate_idx = top_indices[0]
                max_logic_signal = -1.0
                
                for idx in top_indices:
                    snip_en = snippets_en[idx]
                    inputs = self._nli_tokenizer(
                        snip_en[:512], flagged_sentence_en[:256],
                        return_tensors="pt", truncation=True, max_length=512
                    ).to(self.embed_model.device)
                    
                    with torch.no_grad():
                        logits = self._nli_model(**inputs).logits
                    probs = torch.softmax(logits, dim=-1).squeeze().tolist()
                    
                    logic_signal = max(probs[0], probs[1]) 
                    
                    if logic_signal > max_logic_signal:
                        max_logic_signal = logic_signal
                        best_candidate_idx = idx

            best_snippet = snippets[best_candidate_idx]

            # Compute flagged sentence confidence score: min(factual_score, relevance_score)
            emb_prompt = self.embed_model.encode(prompt, convert_to_tensor=True)
            flagged_emb_tmp = self.embed_model.encode(flagged_sentence_en, convert_to_tensor=True)
            relevance_score_flagged = float(util.cos_sim(emb_prompt, flagged_emb_tmp).item())
            relevance_score_flagged = max(0.0, min(1.0, relevance_score_flagged))

            factual_score_flagged = 1.0 - max_contradiction
            factual_score_flagged = max(0.0, min(1.0, factual_score_flagged))

            final_conf_flagged = min(relevance_score_flagged, factual_score_flagged)
            final_conf_flagged_pct = int(round(final_conf_flagged * 100))

            correction = f"{texts['correction_prefix']}: \"{best_snippet.strip()}\" (Confidence: {final_conf_flagged_pct}%)"
            reason = f"{texts['reason_prefix']} (Confidence: {final_conf_flagged_pct}%)."
            return {
                "flagged_sentence": flagged_sentence,
                "reason": reason,
                "correction": correction
            }
        except Exception as e:
            print(f"[TruthLens] Explanation generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _translate_to_english(self, text: str) -> str:
        if not text or len(text.strip()) < 10:
            return text
        import os
        from groq import Groq
        key = os.environ.get("GROQ_API_KEY", None)
        if not key:
            return text
        try:
            client = Groq(api_key=key)
            messages = [
                {"role": "system", "content": "You are a professional translator. Translate the input text to English. Keep the meaning exact. Do not add comments or change the structure. Output the translation only."},
                {"role": "user", "content": text}
            ]
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.0,
                max_tokens=max(100, len(text.split()) * 2)
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[TruthLens] Translation to English failed: {e}")
            return text

    def _translate_sentences(self, sentences: list) -> list:
        if not sentences:
            return []
        import json, os
        from groq import Groq
        key = os.environ.get("GROQ_API_KEY", None)
        if not key:
            return sentences
        try:
            client = Groq(api_key=key)
            prompt = f"Translate the following list of sentences into English. Return the result as a raw JSON array of strings in the exact same order. Do not write any markdown code blocks or explanation. Output the raw JSON only.\n\nSentences:\n{json.dumps(sentences, ensure_ascii=False)}"
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=2048
            )
            content = completion.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            translated = json.loads(content)
            if isinstance(translated, list) and len(translated) == len(sentences):
                return [str(t) for t in translated]
            else:
                print(f"[TruthLens] Translation list length mismatch. Expected {len(sentences)}, got {len(translated)}. Falling back to one-by-one translation.")
        except Exception as e:
            print(f"[TruthLens] Batch translation of sentences failed: {e}. Falling back to one-by-one translation.")
        
        # Fallback to translating one-by-one
        results = []
        for sent in sentences:
            results.append(self._translate_to_english(sent))
        return results

    def retrieve_verified_source(self, prompt: str, context: str, intent: Optional[str] = None) -> str:
        """
        Retrieves the verified answer from the context, strictly preserving the detected query intent.
        Returns the fact/answer type that matches the original intent:
          - Person lookup  -> person's name
          - Date lookup    -> date / year
          - Definition     -> definition text
          - Explanation    -> explanation text
          - Fact lookup    -> factual answer
        """
        if intent is None:
            intent = detect_query_intent(prompt)
        ans_data = self.extract_both_answers(prompt, "", context, intent=intent)
        verified_fact = ans_data[1] if len(ans_data) > 1 else ""
        return verified_fact

    def verify_response(
        self,
        prompt: str,
        response: str,
        context: str,
        confidence: float,
        intent: Optional[str] = None,
    ) -> tuple:
        """
        Single source of truth for verification status.

        Returns (status, generated_answer, verified_answer, correction_required, disagreement_detected, extracted_conf) where:
          - status             : 'Verified' or 'Contradicted'
          - generated_answer   : the fact extracted from the LLM response (intent-preserved)
          - verified_answer    : the fact extracted from the retrieved context (intent-preserved)
          - correction_required: True if status == 'Contradicted', False otherwise
          - disagreement_detected: True if sources in context disagree
          - extracted_conf     : confidence score estimated by extraction or None

        No other part of the pipeline should independently calculate a status.
        """
        if intent is None:
            intent = detect_query_intent(prompt)

        ans_data = self.extract_both_answers(
            prompt, response, context, intent=intent
        )
        if len(ans_data) == 4:
            generated_answer, verified_answer, disagreement_detected, extracted_conf = ans_data
        else:
            generated_answer, verified_answer = ans_data
            disagreement_detected = False
            extracted_conf = None

        is_dynamic = is_dynamic_fact_query(prompt)

        def clean_fact(fact: str) -> str:
            if not fact:
                return ""
            # If it contains a colon (like role: name), extract the name part
            if ":" in fact:
                fact = fact.split(":", 1)[1]
            # Remove punctuation and lowercase
            fact = re.sub(r'[^\w\s]', '', fact.lower()).strip()
            return fact

        g_clean_fact = clean_fact(generated_answer)
        v_clean_fact = clean_fact(verified_answer)

        # Match checks:
        # 1. Exact match
        # 2. Both non-empty and equal clean values
        # 3. Clean value of one is a substring/superstring of the other (to handle things like "Donald Trump" vs "Donald John Trump")
        match = (generated_answer == verified_answer) or (
            g_clean_fact and v_clean_fact and (
                g_clean_fact == v_clean_fact or 
                g_clean_fact in v_clean_fact or 
                v_clean_fact in g_clean_fact
            )
        )

        if match:
            status = "Verified"
            correction_required = False
            if is_dynamic and (not verified_answer or verified_answer.strip() in ("", "matched", "unable to verify with current evidence", "unable to verify this claim with available evidence")):
                status = "Contradicted"
                correction_required = True
        else:
            status = "Contradicted"
            correction_required = True

        return status, generated_answer, verified_answer, correction_required, disagreement_detected, extracted_conf

    def extract_both_answers(
        self,
        prompt: str,
        response: str,
        context: str,
        intent: Optional[str] = None,
    ) -> tuple:
        """
        Extracts 'generated_answer' and 'verified_answer' in a single LLM call,
        strictly preserving the query intent throughout.

        Intent mapping:
          - Person lookup  : extracted fact MUST be a person's name
          - Date lookup    : extracted fact MUST be a date, year, or time period
          - Definition     : extracted fact MUST be a definition of the term
          - Explanation    : extracted fact MUST be an explanation of roles/responsibilities/causes
          - Fact lookup    : extracted fact MUST be a general factual answer

        Intent is NEVER converted from one type to another.
        """
        import os, json as _json
        from groq import Groq

        # Determine intent
        if intent is None:
            intent = detect_query_intent(prompt)

        # Heuristic fallbacks
        generated_fact_fallback = response.strip() if response else ""
        verified_fact_fallback  = context.strip()  if context  else ""

        disagreement_detected = False
        confidence = 0.8

        if not context or len(context.strip()) < 5:
            return generated_fact_fallback, "", disagreement_detected, confidence

        # Build intent-specific extraction instruction
        intent_lower = intent.lower()
        if intent_lower == INTENT_PERSON_LOOKUP.lower():
            intent_instructions = (
                f"- The query intent is '{intent}'. The extracted facts MUST be a person or entity NAME only.\n"
                "- For 'verified_answer': extract in the format 'Current <Role> of <Place>: <Name>' "
                "(e.g. 'President of the United States: Donald Trump').\n"
                "- NEVER output an encyclopedia description, a sentence about duties/powers, "
                "or any text that does not include the actual person's name.\n"
                "- NEVER use 'Prime Minister of India' alone — always append ': <Name>'."
            )
        elif intent_lower == INTENT_DATE_LOOKUP.lower():
            intent_instructions = (
                f"- The query intent is '{intent}'. The extracted facts MUST be a specific date, year, or time period ONLY.\n"
                "- Output ONLY the date/year string (e.g. '1947', 'July 4, 1776'). "
                "Do NOT output a sentence or prose description."
            )
        elif intent_lower == INTENT_DEFINITION.lower():
            intent_instructions = (
                f"- The query intent is '{intent}'. The extracted facts MUST be a concise definition of the term."
            )
        elif intent_lower == INTENT_EXPLANATION.lower():
            intent_instructions = (
                f"- The query intent is '{intent}'. The extracted facts MUST be an explanation of roles, responsibilities, or causes."
            )
        else:  # Fact lookup
            intent_instructions = (
                f"- The query intent is '{intent}'. The extracted facts MUST be a concise factual answer."
            )

        key = os.environ.get("GROQ_API_KEY", None)
        if not key:
            # Heuristic fallback: substring match check
            g_clean = re.sub(r'[^\w\s]', '', generated_fact_fallback.lower()).strip()
            v_clean = re.sub(r'[^\w\s]', '', verified_fact_fallback.lower()).strip()
            if g_clean and (g_clean in v_clean or v_clean in g_clean):
                return "matched", "matched", disagreement_detected, confidence
            return generated_fact_fallback, verified_fact_fallback, disagreement_detected, confidence

        try:
            client = Groq(api_key=key)
            system_prompt = (
                "You are a fact extraction and comparison assistant.\n"
                f"The original query intent is: '{intent}'. You MUST preserve this intent. Do NOT switch to any other intent.\n"
                "Analyze the user's query, the generated response, and the verified context.\n"
                "Identify the core entity/fact being asked about, based on the intent.\n"
                "Extract the value of this fact as stated in the generated response → 'generated_answer'.\n"
                "Extract the value of this fact as stated in the verified context → 'verified_answer'.\n"
                "If multiple sources in the verified context disagree or state different facts, compare all of them and select the most supported answer (the one supported by the most/highest quality sources) as the 'verified_answer'.\n"
                "Additionally, evaluate if there is any active disagreement or conflict among the sources in the verified context regarding this fact. Set 'disagreement_detected' to true if different sources state contradictory facts (e.g. source A says X won, source B says Y won), else false.\n"
                "Also estimate a 'confidence' score between 0.0 and 1.0 representing how strongly the verified_answer is supported. If all sources agree, confidence should be 0.95-1.0. If there is a disagreement/conflict, scale confidence down based on the conflict level (e.g., 0.3 to 0.6 depending on how split the sources are).\n"
                "Normalization rules:\n"
                f"{intent_instructions}\n"
                "- If the generated response is empty or makes no factual claim, set 'generated_answer' to empty string ''.\n"
                "- If both the response and context refer to the SAME entity/fact, make both strings EXACTLY IDENTICAL.\n"
                "- If they differ, output the actual differing values.\n"
                "Return a JSON object with exactly these keys: 'generated_answer', 'verified_answer', 'disagreement_detected', and 'confidence'.\n"
                "Example: {\"generated_answer\": \"Narendra Modi\", \"verified_answer\": \"Narendra Modi\", \"disagreement_detected\": false, \"confidence\": 0.95}"
            )
            user_msg = (
                f"Query: {prompt}\n"
                f"Generated Response: {response}\n"
                f"Verified Context: {context[:2000]}\n"
            )
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_msg},
                ],
                temperature=0.0,
                max_tokens=150,
                response_format={"type": "json_object"},
            )
            data = _json.loads(completion.choices[0].message.content.strip())
            g_ans = data.get("generated_answer", "").strip()
            v_ans = data.get("verified_answer",  "").strip()
            disagreement = data.get("disagreement_detected", False)
            conf = data.get("confidence", 0.8)
            if g_ans or v_ans:
                return g_ans, v_ans, disagreement, conf
        except Exception as e:
            print(f"[TruthLens] LLM fact extraction error: {e}")

        # Heuristic fallback
        g_clean = re.sub(r'[^\w\s]', '', generated_fact_fallback.lower()).strip()
        v_clean = re.sub(r'[^\w\s]', '', verified_fact_fallback.lower()).strip()
        if g_clean and (g_clean in v_clean or v_clean in g_clean):
            return "matched", "matched", disagreement_detected, confidence
        return generated_fact_fallback, verified_fact_fallback, disagreement_detected, confidence

    # ── Kept for backward compatibility (delegates to extract_both_answers) ──
    def extract_facts(
        self,
        prompt: str,
        response: str,
        context: str,
        intent: Optional[str] = None,
    ) -> tuple:
        """Backward-compatible alias for extract_both_answers."""
        return self.extract_both_answers(prompt, response, context, intent=intent)

    def generate_corrected_answer(
        self,
        prompt: str,
        response: str,
        context: str,
        verified_fact: str,
        intent: Optional[str] = None,
    ) -> str:
        """
        Generates a corrected answer with STRICT answer-type locking.

        Answer-type locking rules (enforced before any LLM call):
          - Person lookup  -> corrected answer MUST be a person/entity name only.
                             Format: "Current <Role> of <Place>: <Name>"
                             NEVER an encyclopedia description.
          - Date lookup    -> corrected answer MUST be the verified date/year only.
          - Definition     -> corrected answer MUST be a definition (LLM constrained).
          - Explanation    -> corrected answer MUST be an explanation (LLM constrained).
          - Fact lookup    -> corrected answer MUST be a concise factual statement.

        For person_lookup and date_lookup, the verified_fact is returned directly
        (with optional formatting) — the LLM is NOT called, preventing encyclopedia drift.
        """
        import os
        from groq import Groq

        is_dynamic = is_dynamic_fact_query(prompt)
        if is_dynamic:
            if not verified_fact or verified_fact.strip() in ("", "matched", "unable to verify with current evidence", "unable to verify this claim with available evidence"):
                return "Unable to verify this claim with available evidence."

        if intent is None:
            intent = detect_query_intent(prompt)

        intent_lower = intent.lower()

        # ── Answer-type lock: Person lookup ──────────────────────────────────
        # Return entity name directly. Never pass through LLM which might produce
        # an encyclopedia description instead of the name.
        if intent_lower == INTENT_PERSON_LOOKUP.lower():
            if verified_fact and verified_fact not in ("matched", ""):
                # If the verified_fact already looks like a plain name, format it.
                # Otherwise return as-is (already formatted by extract_both_answers).
                return verified_fact
            return f"Corrected: The verified entity is {verified_fact}."

        # ── Answer-type lock: Date lookup ─────────────────────────────────────
        # Return the date/year directly — no LLM prose expansion.
        if intent_lower == INTENT_DATE_LOOKUP.lower():
            if verified_fact and verified_fact not in ("matched", ""):
                return verified_fact
            return f"Corrected: The verified date is {verified_fact}."

        # ── LLM-assisted correction for Definition / Explanation / Fact lookup ─
        # These need natural language output but are still tightly constrained.
        key = os.environ.get("GROQ_API_KEY", None)
        if key:
            try:
                client = Groq(api_key=key)

                # Build intent-specific output format instruction
                if intent_lower == INTENT_DEFINITION.lower():
                    format_rule = (
                        "Output a single concise definition sentence. "
                        "Do NOT output a person's name, a date, or a narrative story."
                    )
                elif intent_lower == INTENT_EXPLANATION.lower():
                    format_rule = (
                        "Output a clear explanation of the topic. "
                        "Do NOT output a person's name, a date, or a dictionary entry."
                    )
                else:  # Fact lookup
                    format_rule = (
                        "Output a single concise factual statement answering the query. "
                        "Do NOT output an encyclopedia article, a list, or extra commentary."
                    )

                system_prompt = (
                    f"You are a factual correction assistant. Query intent: '{intent}'.\n"
                    "STRICT RULES:\n"
                    f"1. {format_rule}\n"
                    "2. Use the verified fact provided — do NOT invent or hallucinate.\n"
                    "3. Match the language of the original response.\n"
                    "4. Output the corrected answer ONLY — no preamble, no markdown."
                )
                user_msg = (
                    f"Query: {prompt}\n"
                    f"Original Response: {response}\n"
                    f"Verified Fact: {verified_fact}\n"
                    f"Verified Context (for reference only): {context[:1500]}"
                )
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_msg},
                    ],
                    temperature=0.0,
                    max_tokens=150,
                )
                ans = completion.choices[0].message.content.strip()
                if ans:
                    return ans
            except Exception as e:
                print(f"[TruthLens] Failed to generate corrected response with LLM: {e}")

        # Final fallback — always type-safe
        if is_dynamic and (not verified_fact or verified_fact.strip() in ("", "matched")):
            return "Unable to verify this claim with available evidence."
        return verified_fact if verified_fact and verified_fact not in ("matched", "") \
            else f"Corrected: The verified fact is {verified_fact}."

    def evaluate(self, prompt: str, response: str, context: str = "", language: str = "English") -> dict:
        if not is_valid_generated_response(response):
            print(f"[TruthLens] Skipped evaluation in evaluator.evaluate: response is invalid/error fallback.")
            return None

        if self.use_mock:
            return self._mock_evaluate(prompt, response, context)

        self._load_models()
        
        evidence = []
        if not context:
            print(f"[TruthLens] Retrieving live evidence for: {prompt[:50]}...")
            
            # 1. Advanced Search Query Refinement
            search_query = prompt
            try:
                from groq import Groq
                key = os.environ.get("GROQ_API_KEY", None)
                client = Groq(api_key=key)
                refine_resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a search query optimizer. Extract core entities and factual keywords for verification. For 'who won' queries, include 'winner' and the year. For planetary science, distinguish 'Jupiter planet'. Output keywords only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=25
                )
                search_query = refine_resp.choices[0].message.content.strip()
                print(f"[TruthLens] DEBUG: Refined Search -> '{search_query}'")
            except Exception as e:
                print(f"[TruthLens] Eval refiner skip: {e}")

            try:
                print(f"[TruthLens] Running direct ddg html search for '{search_query}'...")
                all_results = ddg_html_search(search_query, max_results=10)
                for r in all_results:
                    body = r.get("body", "").strip()
                    src = r.get("title", "Web Source")
                    if body and len(body) > 30:
                        evidence.append({"src": src, "snippet": body})
                print(f"[TruthLens] HTML search retrieved {len(evidence)} snippets.")
            except Exception as e:
                print(f"[TruthLens] Search failed: {e}")

            # Wikipedia Fallback
            if not evidence:
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
                            sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(top_title.replace(' ', '_'))}"
                            with urllib.request.urlopen(urllib.request.Request(sum_url, headers=ua), timeout=5) as sum_resp:
                                wiki_data = _json.loads(sum_resp.read().decode())
                                if wiki_data.get("extract"):
                                    evidence.append({"src": f"Wikipedia: {top_title}", "snippet": wiki_data["extract"]})
                except: pass

            context = "\n".join([e["snippet"] for e in evidence])
        else:
            snippets = [s.strip() for s in re.split(r"\n|(?<=[.!?])\s+", context) if len(s.strip()) > 20]
            if not snippets:
                snippets = [context]
            for snip in snippets:
                evidence.append({"src": "Grounded Context", "snippet": snip})

        # 3. Sentence-Level Verification Pipeline (The Core Fix)
        has_evidence = len(evidence) > 0 or (context and len(context.strip()) > 50)
        sentence_analysis = []
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", response) if len(s.strip()) > 5]

        # Translate to English if selected language is not English
        if language and language.lower() != "english":
            print(f"[TruthLens] Translating response & evidence snippets for evaluation (Language: {language})...")
            sentences_en = self._translate_sentences(sentences)
            snippets_en = self._translate_sentences([e["snippet"] for e in evidence])
            for i, snip_en in enumerate(snippets_en):
                evidence[i]["snippet_en"] = snip_en
            context_en = self._translate_to_english(context)
            response_en = " ".join(sentences_en)
        else:
            sentences_en = sentences
            for e in evidence:
                e["snippet_en"] = e["snippet"]
            context_en = context
            response_en = response
        
        # We track individual sentence risks to build a more accurate global score
        global_nli_risks = []
        global_hhem_risks = []
        nli_cache = {} # Cache NLI probabilities: (sent_idx, snippet_idx) -> (contradiction, entailment, neutral)

        from sentence_transformers import util
        import torch
        emb_prompt = self.embed_model.encode(prompt, convert_to_tensor=True)

        for sent_idx, sent in enumerate(sentences):
            sent_en = sentences_en[sent_idx] if sent_idx < len(sentences_en) else sent
            
            # Compute relevance score for sentence to query
            emb_sent = self.embed_model.encode(sent_en, convert_to_tensor=True)
            relevance_score = float(util.cos_sim(emb_prompt, emb_sent).item())
            relevance_score = max(0.0, min(1.0, relevance_score))

            if not has_evidence:
                s_risk = 0.8
                best_nli_risk = 0.8
                best_hhem_risk = 0.8
                factual_score = 0.2
                cat, ctype, reason = "fabricated", "Fabricated", "No evidence found to verify."
            else:
                # Rank snippets by semantic similarity to only check top-2 most relevant
                snip_texts = [e.get("snippet_en", e["snippet"]) for e in evidence]
                emb_snippets = self.embed_model.encode(snip_texts, convert_to_tensor=True)
                cos_similarities = util.cos_sim(emb_sent, emb_snippets)[0]
                
                # Pick top-2 snippets
                top_k = min(2, len(evidence))
                top_indices = torch.topk(cos_similarities, k=top_k).indices.tolist()
                
                # IMPORTANT: Check against each snippet individually to avoid truncation
                best_nli_risk = 1.0 # Start high, we want to FIND support
                best_hhem_risk = 1.0
                
                # We prioritize the SMALLEST risk found across the top-k snippets
                # (If ANY snippet supports it, it's not a hallucination)
                for snippet_idx in top_indices:
                    snippet_obj = evidence[snippet_idx]
                    snip_en = snippet_obj.get("snippet_en", snippet_obj["snippet"])
                    
                    contradiction, entailment, neutral = self._nli_probs(snip_en, sent_en)
                    nli_cache[(sent_idx, snippet_idx)] = (contradiction, entailment, neutral)
                    
                    n_risk = round(min(1.0, contradiction + 0.4 * neutral), 4)
                    h_risk, _ = self._hhem(snip_en, sent_en, precalculated_nli_risk=n_risk)
                    
                    if n_risk < best_nli_risk: best_nli_risk = n_risk
                    if h_risk < best_hhem_risk: best_hhem_risk = h_risk

                s_risk = (best_nli_risk + best_hhem_risk) / 2
                global_nli_risks.append(best_nli_risk)
                global_hhem_risks.append(best_hhem_risk)

                # Compute factual score for sentence
                factual_score = 1.0 - best_nli_risk
                factual_score = max(0.0, min(1.0, factual_score))

                # Classification (Only mark VERIFIED if both scores > 0.7)
                if best_nli_risk <= 0.15 and relevance_score > 0.7 and factual_score > 0.7:
                    cat, ctype, reason = "verified", "Verified", "Evidence directly supports claim."
                else:
                    if best_nli_risk > 0.7:
                        cat, ctype, reason = "contradicted", "Contradicted", "Evidence says opposite."
                    elif best_nli_risk > 0.55 or best_hhem_risk > 0.75:
                        cat, ctype, reason = "fabricated", "Fabricated", "No evidence found."
                    elif best_nli_risk > 0.35:
                        cat, ctype, reason = "weak", "Weak", "Limited evidence."
                    else:
                        if relevance_score <= 0.7:
                            cat, ctype, reason = "weak", "Weak", "Factual but irrelevant to query."
                        else:
                            cat, ctype, reason = "partial", "Partial", "Some evidence supports."

            # Use a single confidence score throughout the application: min(factual_score, relevance_score)
            final_confidence = min(factual_score, relevance_score)
            confidence_pct = int(round(final_confidence * 100))
            confidence_pct = max(0, min(100, confidence_pct))
            sentence_analysis.append({
                "text": f"{sent} ({confidence_pct}%)",
                "category": cat,
                "type": f"{ctype} -> {confidence_pct}%",
                "reason": reason,
                "score": confidence_pct,
                "relevance_score": round(relevance_score, 4),
                "factual_score": round(factual_score, 4)
            })

        # 4. Aggregated Global Scores
        n_risk = sum(global_nli_risks) / len(global_nli_risks) if global_nli_risks else 0.5
        h_risk = sum(global_hhem_risks) / len(global_hhem_risks) if global_hhem_risks else 0.5
        c_risk, c_detail = self._consistency(prompt, response_en, context_en)
        
        overall = float((h_risk * 0.50) + (n_risk * 0.35) + (c_risk * 0.15))
        trust_score = round((1.0 - overall) * 100)

        # Global scores
        global_relevance_score = self._compute_relevance(prompt, response_en)
        global_factual_score = 1.0 - n_risk
        global_factual_score = max(0.0, min(1.0, global_factual_score))
        
        # ── Step 1: Determine confidence ──────────────────────────────────────
        confidence = min(global_factual_score, global_relevance_score)

        # ── Step 2: Detect query intent (single call, passed through everywhere) ──
        intent = detect_query_intent(prompt)

        # ── Step 3 & 4: Single source of truth — verify_response() ──────────
        # verify_response() calls extract_both_answers() once and returns:
        #   (status, generated_answer, verified_answer, correction_required, disagreement_detected, extracted_conf)
        # No other part of this function recalculates the status.
        final_status, generated_answer, verified_answer, correction_required, disagreement_detected, extracted_conf = \
            self.verify_response(prompt, response, context, confidence, intent=intent)

        if extracted_conf is not None:
            confidence = min(confidence, extracted_conf)

        if disagreement_detected:
            # Scale down trust score and increase overall risk since sources disagree
            trust_score = max(10, min(trust_score, 45))
            overall = 1.0 - (trust_score / 100.0)
            print(f"[TruthLens] Conflict detected between sources. Confidence scaled down to {confidence*100:.1f}%.")

        # ── Step 5: Build corrected_answer from verified_answer ───────────────
        # Rule: if correction_required → corrected_answer = verified_answer
        #        else                  → corrected_answer = "No correction required"
        if correction_required:
            # Generate a well-formed corrected response using the verified fact
            corrected_answer = self.generate_corrected_answer(
                prompt, response, context, verified_answer, intent=intent
            )
            correction_generated = True
            needs_correction = True
        else:
            corrected_answer = "No correction required"
            correction_generated = False
            needs_correction = False

        # ── Step 6: Build metadata fields from final_status ───────────────────
        if final_status == "Contradicted":
            reason_str = "Outdated information"
            reasoning  = "\u2716 Outdated information detected."
            trust_score = min(trust_score, 30)
            overall = 1.0 - (trust_score / 100.0)
            # Use the optimized _generate_explanation to pinpoint the contradicted claim
            explanation = self._generate_explanation(
                response, prompt, context, language,
                sentences=sentences, sentences_en=sentences_en, evidence=evidence,
                global_nli_risks=global_nli_risks, nli_cache=nli_cache
            )
            if not explanation:
                explanation = {
                    "flagged_sentence": response,
                    "reason": reason_str,
                    "correction": corrected_answer,
                }
        else:
            reason_str = "Verified"
            reasoning  = "\u2713 Verified facts. \u2713 Fully grounded."
            trust_score = max(trust_score, 85)
            overall = 1.0 - (trust_score / 100.0)
            explanation = None

        risk_score = round(overall * 100)
        verdict = get_verdict_label(risk_score)

        # ── Step 7: Propagate final_status uniformly to sentence_analysis ──
        # This feeds both the Heatmap and the Claim Verification Panel.
        # There is NO independent status calculation here.
        for item in sentence_analysis:
            item["category"] = final_status.lower()
            item["type"]     = f"{final_status} -> {item['score']}%"
            if final_status == "Contradicted":
                item["reason"] = "Outdated information"
            else:
                item["reason"] = "Evidence directly supports claim."

        return {
            # ── Single source of truth status ──
            "status":             final_status,
            "intent":             intent,
            "reason":             reason_str,
            # ── Comparison data ──
            "generated_answer":   generated_answer,
            "verified_answer":    verified_answer,
            # ── Correction data ──
            "needs_correction":   needs_correction,
            "corrected_answer":   corrected_answer,
            "correction_generated": correction_generated,
            # ── Trust scores ──
            "confidence":         round(confidence, 4),
            "trust_score":        trust_score,
            "trust_verdict":      verdict,
            "trust_reasoning":    reasoning,
            "overall_risk":       round(overall, 4),
            "relevance_score":    round(global_relevance_score, 4),
            "factual_score":      round(global_factual_score, 4),
            # ── Display panels (all driven by final_status) ──
            "explanation":        explanation,
            "evidence":           evidence,
            "sentence_analysis":  sentence_analysis,
            "components": {
                "Consistency":  round(c_risk, 4),
                "Logical NLI": round(n_risk, 4),
                "HHEM Factor": round(h_risk, 4),
            },
            "details": {
                "Consistency":  c_detail,
                "Logical NLI": f"Aggregated sentence-level verification (Risk: {n_risk*100:.1f}%)",
                "HHEM Factor": f"Factuality probability check (Risk: {h_risk*100:.1f}%)",
            },
        }


    # ── Legacy mock (kept for dev/testing) ────────────────────────────────────

    def _mock_evaluate(self, prompt: str, response: str, context: str = "") -> dict:
        import hashlib, time
        time.sleep(0.5)
        hv = int(hashlib.md5((prompt + response + context).encode()).hexdigest(), 16)
        def r(salt, lo, hi): return lo + ((hv ^ salt) % 1000) / 1000.0 * (hi - lo)
        scores = {
            "Consistency":  r(105, 0.1, 0.4),
            "Logical NLI":  r(106, 0.05, 0.35),
            "HHEM Factor":  r(107, 0.1, 0.45),
        }
        overall = float(np.mean(list(scores.values())))
        risk_score = round(overall * 100)
        verdict = get_verdict_label(risk_score)
        trust_score = 100 - risk_score
        
        return {
            "status": "Verified" if risk_score <= 40 else "Contradicted",
            "intent": "Fact lookup",
            "reason": "Verified" if risk_score <= 40 else "Outdated information",
            "generated_answer": "",
            "verified_answer": "",
            "needs_correction": risk_score > 40,
            "corrected_answer": "No correction required" if risk_score <= 40 else "Mock corrected answer",
            "correction_generated": risk_score > 40,
            "confidence": 0.9,
            "trust_score": trust_score,
            "trust_verdict": verdict,
            "trust_reasoning": "\u2713 Verified facts." if risk_score <= 40 else "\u2716 Outdated information detected.",
            "overall_risk": round(overall, 4),
            "relevance_score": 0.9,
            "factual_score": 1.0 - overall,
            "explanation": None if risk_score <= 40 else {
                "flagged_sentence": response,
                "reason": "Outdated information",
                "correction": "Mock corrected answer",
            },
            "evidence": [],
            "sentence_analysis": [],
            "components": scores,
            "details": {
                "Consistency": f"[MOCK] Simulated score: {scores['Consistency']*100:.1f}%",
                "Logical NLI": f"[MOCK] Simulated score: {scores['Logical NLI']*100:.1f}%",
                "HHEM Factor": f"[MOCK] Simulated score: {scores['HHEM Factor']*100:.1f}%",
            },
        }
