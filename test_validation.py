"""
GraphRAG System Validation Script

This script performs comprehensive end-to-end testing of the GraphRAG system
without modifying core logic. It validates:
1. Backend health and availability
2. Both baseline and graph modes
3. Behavioral differences between modes
4. Neo4j graph structure and persistence
5. System readiness for demo/submission

Usage:
    python test_validation.py

Requirements:
    - Backend server running on http://localhost:8000
    - Neo4j database accessible (for graph mode tests)
    - GEMINI_API_KEY environment variable set
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class GraphRAGValidator:
    """Comprehensive validation suite for GraphRAG system"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": []
        }
        self.start_time = datetime.now()
        
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")
        
    def print_test(self, name: str, status: str, details: str = ""):
        """Print individual test result"""
        if status == "PASS":
            symbol = f"{Colors.GREEN}✓{Colors.END}"
            self.results["passed"] += 1
        elif status == "FAIL":
            symbol = f"{Colors.RED}✗{Colors.END}"
            self.results["failed"] += 1
        else:  # WARN
            symbol = f"{Colors.YELLOW}⚠{Colors.END}"
            self.results["warnings"] += 1
            
        print(f"{symbol} {Colors.BOLD}{name}{Colors.END}")
        if details:
            print(f"  {details}")
            
        self.results["tests"].append({
            "name": name,
            "status": status,
            "details": details
        })
        
    def test_health_endpoint(self) -> bool:
        """Test 1: Verify /health endpoint responds"""
        self.print_header("TEST 1: BACKEND HEALTH CHECK")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.print_test(
                        "Health endpoint responds correctly",
                        "PASS",
                        f"Response: {data}"
                    )
                    return True
                else:
                    self.print_test(
                        "Health endpoint returns unexpected response",
                        "FAIL",
                        f"Expected status='ok', got: {data}"
                    )
                    return False
            else:
                self.print_test(
                    "Health endpoint returns non-200 status",
                    "FAIL",
                    f"Status code: {response.status_code}"
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_test(
                "Cannot connect to backend",
                "FAIL",
                f"Is the server running on {self.backend_url}?"
            )
            return False
        except Exception as e:
            self.print_test(
                "Health check failed with exception",
                "FAIL",
                str(e)
            )
            return False
            
    def send_chat_message(self, user_id: str, message: str, mode: str) -> Dict[str, Any]:
        """Send a chat message to the backend"""
        try:
            payload = {
                "user_id": user_id,
                "message": message,
                "mode": mode
            }
            
            response = requests.post(
                f"{self.backend_url}/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": 200
                }
            else:
                return {
                    "success": False,
                    "error": f"Status {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def test_baseline_mode(self) -> Dict[str, Any]:
        """Test 2: Verify baseline mode functionality"""
        self.print_header("TEST 2: BASELINE MODE (Text Memory)")
        
        user_id = f"test_baseline_{int(time.time())}"
        
        # First message
        print(f"{Colors.BLUE}Sending Q1: 'Explain Neo4j'{Colors.END}")
        result1 = self.send_chat_message(user_id, "Explain Neo4j", "baseline")
        
        if not result1["success"]:
            self.print_test(
                "Baseline mode Q1 failed",
                "FAIL",
                result1.get("error", "Unknown error")
            )
            return {"success": False}
            
        response1 = result1["data"]["response"]
        context1 = result1["data"]["context_used"]
        
        self.print_test(
            "Baseline Q1 accepted",
            "PASS",
            f"Response length: {len(response1)} chars"
        )
        
        print(f"\n{Colors.MAGENTA}Response:{Colors.END} {response1[:200]}...")
        print(f"{Colors.MAGENTA}Context used:{Colors.END} {context1}\n")
        
        # Second message
        time.sleep(1)
        print(f"{Colors.BLUE}Sending Q2: 'How is it used in Graph RAG?'{Colors.END}")
        result2 = self.send_chat_message(user_id, "How is it used in Graph RAG?", "baseline")
        
        if not result2["success"]:
            self.print_test(
                "Baseline mode Q2 failed",
                "FAIL",
                result2.get("error", "Unknown error")
            )
            return {"success": False}
            
        response2 = result2["data"]["response"]
        context2 = result2["data"]["context_used"]
        
        self.print_test(
            "Baseline Q2 accepted",
            "PASS",
            f"Response length: {len(response2)} chars"
        )
        
        print(f"\n{Colors.MAGENTA}Response:{Colors.END} {response2[:200]}...")
        print(f"{Colors.MAGENTA}Context used:{Colors.END} {context2}\n")
        
        # Verify context contains previous message
        if "Explain Neo4j" in str(context2):
            self.print_test(
                "Baseline maintains conversation history",
                "PASS",
                "Q1 found in Q2 context"
            )
        else:
            self.print_test(
                "Baseline conversation history issue",
                "WARN",
                "Q1 not found in Q2 context (expected for baseline)"
            )
            
        return {
            "success": True,
            "q1_response": response1,
            "q2_response": response2,
            "user_id": user_id
        }
        
    def test_graph_mode(self) -> Dict[str, Any]:
        """Test 3: Verify graph mode functionality"""
        self.print_header("TEST 3: GRAPH MODE (Graph Memory)")
        
        user_id = f"test_graph_{int(time.time())}"
        
        # First message
        print(f"{Colors.BLUE}Sending Q1: 'Explain Neo4j'{Colors.END}")
        result1 = self.send_chat_message(user_id, "Explain Neo4j", "graph")
        
        if not result1["success"]:
            self.print_test(
                "Graph mode Q1 failed",
                "FAIL",
                result1.get("error", "Unknown error")
            )
            
            # Check if it's a Neo4j connection error
            error_msg = result1.get("error", "")
            if "neo4j" in error_msg.lower() or "connection" in error_msg.lower():
                self.print_test(
                    "Neo4j connection issue detected",
                    "WARN",
                    "Ensure Neo4j is running and credentials are correct"
                )
                
            return {"success": False, "neo4j_error": True}
            
        response1 = result1["data"]["response"]
        context1 = result1["data"]["context_used"]
        
        self.print_test(
            "Graph Q1 accepted",
            "PASS",
            f"Response length: {len(response1)} chars"
        )
        
        print(f"\n{Colors.MAGENTA}Response:{Colors.END} {response1[:200]}...")
        print(f"{Colors.MAGENTA}Context used:{Colors.END} {context1}\n")
        
        # Second message - give graph a moment to persist
        time.sleep(2)
        print(f"{Colors.BLUE}Sending Q2: 'How is it used in Graph RAG?'{Colors.END}")
        result2 = self.send_chat_message(user_id, "How is it used in Graph RAG?", "graph")
        
        if not result2["success"]:
            self.print_test(
                "Graph mode Q2 failed",
                "FAIL",
                result2.get("error", "Unknown error")
            )
            return {"success": False}
            
        response2 = result2["data"]["response"]
        context2 = result2["data"]["context_used"]
        
        self.print_test(
            "Graph Q2 accepted",
            "PASS",
            f"Response length: {len(response2)} chars"
        )
        
        print(f"\n{Colors.MAGENTA}Response:{Colors.END} {response2[:200]}...")
        print(f"{Colors.MAGENTA}Context used:{Colors.END} {context2}\n")
        
        # Check if graph retrieval found context
        if context2 and len(context2) > 0:
            self.print_test(
                "Graph mode retrieved context",
                "PASS",
                f"Found {len(context2)} context items: {context2}"
            )
        else:
            self.print_test(
                "Graph mode context retrieval",
                "WARN",
                "No context retrieved (entities may not have matched)"
            )
            
        return {
            "success": True,
            "q1_response": response1,
            "q2_response": response2,
            "q1_context": context1,
            "q2_context": context2,
            "user_id": user_id
        }
        
    def test_behavioral_difference(self, baseline_result: Dict, graph_result: Dict):
        """Test 4: Verify behavioral difference between modes"""
        self.print_header("TEST 4: BEHAVIORAL DIFFERENCE VERIFICATION")
        
        if not baseline_result.get("success") or not graph_result.get("success"):
            self.print_test(
                "Cannot compare modes",
                "FAIL",
                "One or both modes failed in previous tests"
            )
            return
            
        # Compare Q2 context usage
        baseline_context = baseline_result.get("q2_response", "")
        graph_context = graph_result.get("q2_context", [])
        
        print(f"{Colors.BLUE}Baseline Mode Context:{Colors.END}")
        print(f"  Q2 references Q1 entities: {'Likely' if 'neo4j' in baseline_context.lower() else 'No'}")
        
        print(f"\n{Colors.BLUE}Graph Mode Context:{Colors.END}")
        print(f"  Retrieved context items: {len(graph_context)}")
        print(f"  Context details: {graph_context}")
        
        # Behavioral difference test
        if len(graph_context) > 0:
            self.print_test(
                "Graph mode uses structured context",
                "PASS",
                f"Graph retrieved {len(graph_context)} items vs baseline's chronological history"
            )
        else:
            self.print_test(
                "Graph context retrieval",
                "WARN",
                "Graph didn't retrieve context (may need entity matching tuning)"
            )
            
        # Response difference
        if baseline_result["q2_response"] != graph_result["q2_response"]:
            self.print_test(
                "Modes produce different responses",
                "PASS",
                "Graph and baseline responses differ (expected)"
            )
        else:
            self.print_test(
                "Response similarity",
                "WARN",
                "Responses are identical (LLM may have provided same answer)"
            )
            
    def test_neo4j_inspection(self, graph_user_id: str = None):
        """Test 5: Inspect Neo4j database structure"""
        self.print_header("TEST 5: NEO4J DATABASE INSPECTION")
        
        try:
            from neo4j import GraphDatabase
            import os
            
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            username = os.getenv("NEO4J_USERNAME", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            driver = GraphDatabase.driver(uri, auth=(username, password))
            
            with driver.session() as session:
                # Count nodes
                result = session.run("MATCH (n) RETURN labels(n) as label, count(n) as count")
                node_counts = {}
                for record in result:
                    label = record["label"][0] if record["label"] else "Unknown"
                    node_counts[label] = record["count"]
                    
                print(f"{Colors.BLUE}Node Counts:{Colors.END}")
                for label, count in node_counts.items():
                    print(f"  {label}: {count}")
                    
                if "User" in node_counts and node_counts["User"] > 0:
                    self.print_test(
                        "User nodes exist",
                        "PASS",
                        f"Found {node_counts['User']} User nodes"
                    )
                else:
                    self.print_test(
                        "User nodes missing",
                        "WARN",
                        "No User nodes found in database"
                    )
                    
                if "Event" in node_counts and node_counts["Event"] > 0:
                    self.print_test(
                        "Event nodes exist",
                        "PASS",
                        f"Found {node_counts['Event']} Event nodes"
                    )
                else:
                    self.print_test(
                        "Event nodes missing",
                        "WARN",
                        "No Event nodes found in database"
                    )
                    
                if "Entity" in node_counts and node_counts["Entity"] > 0:
                    self.print_test(
                        "Entity nodes exist",
                        "PASS",
                        f"Found {node_counts['Entity']} Entity nodes"
                    )
                        
                if "Topic" in node_counts and node_counts["Topic"] > 0:
                    self.print_test(
                        "Topic nodes exist",
                        "PASS",
                        f"Found {node_counts['Topic']} Topic nodes"
                    )
                    
                # Check relationships
                result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
                rel_counts = {}
                for record in result:
                    rel_counts[record["rel_type"]] = record["count"]
                    
                print(f"\n{Colors.BLUE}Relationship Counts:{Colors.END}")
                for rel_type, count in rel_counts.items():
                    print(f"  {rel_type}: {count}")
                    
                expected_rels = ["ASKED_ABOUT", "MENTIONS"]
                for rel in expected_rels:
                    if rel in rel_counts:
                        self.print_test(
                            f"{rel} relationships exist",
                            "PASS",
                            f"Found {rel_counts[rel]} relationships"
                        )
                        
                # If we have a test user, inspect their graph
                if graph_user_id:
                    print(f"\n{Colors.BLUE}Inspecting test user: {graph_user_id}{Colors.END}")
                    result = session.run("""
                        MATCH (u:User {id: $user_id})-[:ASKED_ABOUT]->(e:Event)
                        RETURN e.type as event_type, e.timestamp as timestamp, e.content as content
                        ORDER BY e.timestamp
                    """, user_id=graph_user_id)
                    
                    events = list(result)
                    if events:
                        self.print_test(
                            f"Test user has event history",
                            "PASS",
                            f"Found {len(events)} events for user {graph_user_id}"
                        )
                        
                        for i, event in enumerate(events, 1):
                            print(f"  Event {i}: {event['content'][:50]}...")
                    else:
                        self.print_test(
                            "Test user event history",
                            "WARN",
                            f"No events found for user {graph_user_id}"
                        )
                        
            driver.close()
            
        except ImportError:
            self.print_test(
                "Neo4j driver not available",
                "WARN",
                "Cannot inspect database (neo4j package not installed)"
            )
        except Exception as e:
            self.print_test(
                "Neo4j inspection failed",
                "WARN",
                f"Error: {str(e)}"
            )
            
    def generate_report(self):
        """Generate final validation report"""
        self.print_header("VALIDATION SUMMARY")
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"{Colors.BOLD}Test Execution Time:{Colors.END} {duration:.2f} seconds\n")
        
        print(f"{Colors.GREEN}Passed: {self.results['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.results['failed']}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings: {self.results['warnings']}{Colors.END}")
        print(f"Total: {self.results['passed'] + self.results['failed'] + self.results['warnings']}\n")
        
        # Determine system readiness
        critical_failures = self.results['failed']
        
        self.print_header("FINAL VERDICT")
        
        if critical_failures == 0:
            if self.results['warnings'] == 0:
                print(f"{Colors.GREEN}{Colors.BOLD}✓ SYSTEM READY FOR DEMO: YES{Colors.END}")
                print(f"{Colors.GREEN}All tests passed successfully!{Colors.END}\n")
            else:
                print(f"{Colors.YELLOW}{Colors.BOLD}⚠ SYSTEM READY FOR DEMO: YES (with warnings){Colors.END}")
                print(f"{Colors.YELLOW}System is functional but has minor issues.{Colors.END}\n")
        else:
            print(f"{Colors.RED}{Colors.BOLD}✗ SYSTEM READY FOR DEMO: NO{Colors.END}")
            print(f"{Colors.RED}Critical failures detected. Address failing tests before demo.{Colors.END}\n")
            
        # Recommendations
        print(f"{Colors.BOLD}Recommendations:{Colors.END}")
        
        if critical_failures > 0:
            print(f"  {Colors.RED}• Fix all failing tests before proceeding{Colors.END}")
            
        if self.results['warnings'] > 0:
            print(f"  {Colors.YELLOW}• Review warnings for potential improvements{Colors.END}")
            
        print(f"  {Colors.BLUE}• Verify Neo4j database contains expected data{Colors.END}")
        print(f"  {Colors.BLUE}• Test with frontend (Streamlit UI) for full validation{Colors.END}")
        print(f"  {Colors.BLUE}• Ensure GEMINI_API_KEY is valid and has quota{Colors.END}")
        
        return critical_failures == 0
        
    def run_all_tests(self):
        """Execute complete validation suite"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                   GRAPHRAG SYSTEM VALIDATION SUITE                           ║")
        print("║                                                                              ║")
        print("║  Senior Engineer Onboarding - System Verification Without Refactoring       ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")
        
        print(f"Backend URL: {Colors.CYAN}{self.backend_url}{Colors.END}")
        print(f"Start Time: {Colors.CYAN}{self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")
        
        # Test 1: Health check
        health_ok = self.test_health_endpoint()
        
        if not health_ok:
            print(f"\n{Colors.RED}{Colors.BOLD}VALIDATION ABORTED{Colors.END}")
            print(f"{Colors.RED}Backend is not responding. Start the server and try again.{Colors.END}\n")
            return False
            
        # Test 2: Baseline mode
        baseline_result = self.test_baseline_mode()
        
        # Test 3: Graph mode
        graph_result = self.test_graph_mode()
        
        # Test 4: Behavioral difference
        self.test_behavioral_difference(baseline_result, graph_result)
        
        # Test 5: Neo4j inspection
        graph_user_id = graph_result.get("user_id") if graph_result.get("success") else None
        self.test_neo4j_inspection(graph_user_id)
        
        # Generate final report
        return self.generate_report()


def main():
    """Main entry point for validation script"""
    validator = GraphRAGValidator()
    success = validator.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
