from fastapi.testclient import TestClient
from GraphRAG.backend.main import app
import json

client = TestClient(app)

def test_baseline_crs():
    print("Testing Baseline Mode CRS...")
    response = client.post("/chat", json={
        "user_id": "test_user",
        "message": "Who is Harry Potter?",
        "mode": "baseline"
    })
    
    if response.status_code != 200:
        print(f"FAILED: Status {response.status_code}")
        print(response.text)
        return

    data = response.json()
    print("Response Keys:", data.keys())
    
    if "crs_scores" not in data:
        print("FAILED: crs_scores missing from response")
        return

    crs = data["crs_scores"]
    print(f"CRS Scores: {json.dumps(crs, indent=2)}")
    
    if crs is None:
        print("FAILED: crs_scores is None")
        return
        
    required_metrics = [
        "context_recall", "context_precision", 
        "temporal_stability", "dependency_resolution", 
        "context_decay_resistance", "composite_score"
    ]
    
    missing = [m for m in required_metrics if m not in crs]
    if missing:
        print(f"FAILED: Missing metrics: {missing}")
    else:
        print("PASSED: Baseline CRS structure valid.")

def test_graph_crs():
    print("\nTesting Graph Mode CRS (Expect potential graph connection error, but CRS should still exist)...")
    # Note: If Neo4j is not reachable, the backend returns a canned response.
    # CRS should still be calculated (likely with 0 context stats).
    
    response = client.post("/chat", json={
        "user_id": "test_user",
        "message": "Who is Harry Potter?",
        "mode": "graph"
    })

    if response.status_code != 200:
        print(f"FAILED: Status {response.status_code}")
        return

    data = response.json()
    
    if "crs_scores" not in data:
        print("FAILED: crs_scores missing from response")
        return
        
    crs = data["crs_scores"]
    print(f"CRS Scores: {json.dumps(crs, indent=2)}")
    print("PASSED: Graph CRS structure valid.")

if __name__ == "__main__":
    test_baseline_crs()
    test_graph_crs()
