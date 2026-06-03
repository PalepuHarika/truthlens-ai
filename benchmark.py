import json
import time
from src.evaluator import TruthLensEvaluator

def run_benchmark():
    print("==========================================")
    print("TruthLens AI - Offline Validation Benchmark")
    print("==========================================\n")
    
    # Ground Truth Dataset (Prompt, Context, Response, Is_Hallucination)
    dataset = [
        {
            "prompt": "Who is the CEO of Tesla?",
            "context": "Elon Musk is the CEO of Tesla, Inc., an American electric vehicle and clean energy company.",
            "response": "The CEO of Tesla is Elon Musk.",
            "expected_risk": 0 # Factual
        },
        {
            "prompt": "Where is the Eiffel Tower located?",
            "context": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.",
            "response": "The Eiffel Tower is located in London, England.",
            "expected_risk": 1 # Hallucination
        },
        {
            "prompt": "What is the boiling point of water?",
            "context": "Water boils at 100 degrees Celsius (212 degrees Fahrenheit) at sea level.",
            "response": "Water boils at exactly 50 degrees Celsius.",
            "expected_risk": 1 # Hallucination
        },
        {
            "prompt": "Who wrote Romeo and Juliet?",
            "context": "Romeo and Juliet is a tragedy written by William Shakespeare early in his career.",
            "response": "William Shakespeare wrote the famous play Romeo and Juliet.",
            "expected_risk": 0 # Factual
        },
        {
            "prompt": "What is the capital of Japan?",
            "context": "Tokyo is the capital and largest city of Japan.",
            "response": "The capital of Japan is Kyoto.",
            "expected_risk": 1 # Hallucination
        }
    ]

    print(f"Loading TruthLens Evaluator Models...\n")
    evaluator = TruthLensEvaluator(use_mock=False)
    evaluator._load_models()

    correct_predictions = 0
    false_positives = 0
    false_negatives = 0
    
    # Validation loop
    start_time = time.time()
    for i, item in enumerate(dataset):
        print(f"Running sample {i+1}/{len(dataset)}...")
        
        # We explicitly supply context to disable stochastic live web searches for reproducible validation
        result = evaluator.evaluate(
            prompt=item["prompt"],
            response=item["response"],
            context=item["context"]
        )
        
        predicted_risk = result["overall_risk"]
        is_flagged = 1 if predicted_risk >= 0.50 else 0
        expected = item["expected_risk"]
        
        if is_flagged == expected:
            correct_predictions += 1
        elif is_flagged == 1 and expected == 0:
            false_positives += 1
        else:
            false_negatives += 1
            
        print(f"  Prompt:   {item['prompt']}")
        print(f"  Response: {item['response']}")
        print(f"  Score:    {predicted_risk*100:.1f}% Risk (Flagged: {'Yes' if is_flagged else 'No'})")
        print(f"  Expected: {'Hallucination' if expected else 'Factual'}")
        print(f"  Result:   {'[PASS]' if is_flagged == expected else '[FAIL]'}\n")
        
    end_time = time.time()
    
    # Calculate Metrics
    total = len(dataset)
    accuracy = (correct_predictions / total) * 100
    precision = (correct_predictions / (correct_predictions + false_positives)) if (correct_predictions + false_positives) > 0 else 0
    
    print("==========================================")
    print("BENCHMARK RESULTS")
    print("==========================================")
    print(f"Total Evaluated:  {total} samples")
    print(f"Time Taken:       {end_time - start_time:.2f} seconds")
    print(f"Accuracy:         {accuracy:.1f}%")
    print(f"Precision:        {precision*100:.1f}%")
    print("==========================================\n")
    print("Note: Weights have been calibrated based on ground-truth empirical testing.")

if __name__ == "__main__":
    run_benchmark()
