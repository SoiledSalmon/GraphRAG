from GraphRAG.backend.rag.extractor import extract_entities
from GraphRAG.backend.evaluation.crs_evaluator import CRSEvaluator
import json

def debug_crs(query, response, context=""):
    print(f"\n--- Debugging CRS ---")
    print(f"Query: {query}")
    print(f"Response: {response}")
    print(f"Context: {context}")

    evaluator = CRSEvaluator()
    results = evaluator.evaluate(query, response, context, extract_entities)
    
    print("\nExtraction:")
    print(f"Query Ext: {extract_entities(query)}")
    print(f"Response Ext: {extract_entities(response)}")
    print(f"Context Ext: {extract_entities(context)}")
    
    print("\nScores:")
    print(json.dumps(results.dict(), indent=2))

if __name__ == "__main__":
    # Scenario 1: Likely user scenario
    # Query: "Who is Harry Potter?"
    # Response: "Harry Potter is a wizard in the series by J.K. Rowling." (Ideal)
    debug_crs(
        "Who is Harry Potter?",
        "Harry Potter is a protagonist in the series by J.K. Rowling."
    )

    # Scenario 2: Minimal response
    # Response: "He is a wizard."
    debug_crs(
        "Who is Harry Potter?",
        "He is a wizard."
    )

    # Scenario 3: Response triggers topic but not entity? 
    # (Checking for Stability 0.0 cause)
    debug_crs(
        "Who is Harry Potter?",
        "As an AI language model, I can tell you about Harry Potter."
    )
