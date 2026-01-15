"""
Quick Import Test - Verify Core Modules Load Without Errors

This script tests that all backend modules can be imported without
syntax errors or missing dependencies. It does NOT test functionality,
only that code is syntactically valid.

Usage:
    python test_imports.py
"""

import sys
import importlib


def test_import(module_path, description):
    """Test importing a module"""
    try:
        # Try importing
        importlib.import_module(module_path)
        print(f"✓ {description}: {module_path}")
        return True
    except SyntaxError as e:
        print(f"✗ SYNTAX ERROR in {description}")
        print(f"  Module: {module_path}")
        print(f"  Error: {e}")
        return False
    except ImportError as e:
        print(f"⚠ IMPORT ERROR in {description} (missing dependency)")
        print(f"  Module: {module_path}")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"⚠ ERROR in {description}")
        print(f"  Module: {module_path}")
        print(f"  Error: {type(e).__name__}: {e}")
        return False


def main():
    """Test all backend module imports"""
    print("=" * 80)
    print("GRAPHRAG IMPORT TEST - Syntax & Basic Import Verification")
    print("=" * 80)
    print()
    
    # Add current directory to path
    sys.path.insert(0, '.')
    
    modules_to_test = [
        # Core backend
        ("backend.main", "FastAPI Main Application"),
        
        # Graph layer
        ("backend.graph.graph", "Graph Memory (Neo4j Write)"),
        ("backend.graph.retriever", "Graph Retriever (Neo4j Read)"),
        
        # RAG layer
        ("backend.rag.extractor", "Entity & Topic Extractor"),
        ("backend.rag.prompt_builder", "Prompt Builder"),
        ("backend.rag.baseline", "Baseline Memory"),
        ("backend.rag.pipeline", "RAG Pipeline (unused)"),
        
        # LLM layer
        ("backend.llm.gemini_client", "Gemini LLM Client"),
        
        # Frontend
        ("frontend.ui", "Streamlit Frontend"),
    ]
    
    results = {
        "syntax_ok": 0,
        "import_ok": 0,
        "import_failed": 0,
        "total": len(modules_to_test)
    }
    
    for module_path, description in modules_to_test:
        success = test_import(module_path, description)
        
        if success:
            results["import_ok"] += 1
            results["syntax_ok"] += 1
        else:
            results["import_failed"] += 1
    
    # Summary
    print()
    print("=" * 80)
    print("IMPORT TEST SUMMARY")
    print("=" * 80)
    print(f"Total modules tested: {results['total']}")
    print(f"✓ Syntax valid (no SyntaxError): {results['syntax_ok']}/{results['total']}")
    print(f"✓ Import successful: {results['import_ok']}/{results['total']}")
    print(f"✗ Import failed (missing deps): {results['import_failed']}/{results['total']}")
    print()
    
    if results["import_failed"] > 0:
        print("⚠ Some imports failed due to missing dependencies.")
        print("  This is expected if you haven't run: python -m pip install -r requirements.txt")
        print()
        print("  However, if you see SYNTAX ERROR above, that indicates a code problem.")
        print()
        return 1
    elif results["import_ok"] == results["total"]:
        print("✓ ALL IMPORTS SUCCESSFUL!")
        print("  All modules are syntactically valid and dependencies are installed.")
        print()
        return 0
    else:
        print("? Partial success")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
