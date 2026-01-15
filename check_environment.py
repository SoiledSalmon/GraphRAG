"""
Pre-Flight Check Script

This script performs basic checks BEFORE running the full validation suite.
It verifies that all dependencies are installed and environment is configured.

Usage:
    python check_environment.py
"""

import sys
import os


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠ WARNING: Python 3.8+ recommended")
        return False
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "neo4j",
        "spacy",
        "requests",
        "streamlit"
    ]
    
    missing = []
    installed = []
    
    for package in required:
        try:
            __import__(package)
            installed.append(package)
            print(f"✓ {package}")
        except ImportError:
            missing.append(package)
            print(f"✗ {package} - NOT INSTALLED")
            
    return missing, installed


def check_spacy_model():
    """Check if spaCy language model is installed"""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("✓ spaCy model 'en_core_web_sm'")
            return True
        except OSError:
            print("✗ spaCy model 'en_core_web_sm' - NOT INSTALLED")
            return False
    except ImportError:
        print("⚠ Cannot check spaCy model (spaCy not installed)")
        return False


def check_environment_variables():
    """Check required environment variables"""
    required_vars = {
        "GEMINI_API_KEY": True,  # Required
        "NEO4J_URI": False,      # Optional (has default)
        "NEO4J_USERNAME": False, # Optional (has default)
        "NEO4J_PASSWORD": False  # Optional (has default)
    }
    
    missing_required = []
    
    for var, is_required in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var:
                display = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display = value
            print(f"✓ {var} = {display}")
        else:
            if is_required:
                print(f"✗ {var} - NOT SET (REQUIRED)")
                missing_required.append(var)
            else:
                print(f"⚠ {var} - NOT SET (using default)")
                
    return missing_required


def check_backend_structure():
    """Verify backend directory structure"""
    required_files = [
        "backend/main.py",
        "backend/graph/graph.py",
        "backend/graph/retriever.py",
        "backend/llm/gemini_client.py",
        "backend/rag/baseline.py",
        "backend/rag/extractor.py",
        "backend/rag/prompt_builder.py",
        "frontend/ui.py"
    ]
    
    missing = []
    
    for filepath in required_files:
        if os.path.exists(filepath):
            print(f"✓ {filepath}")
        else:
            print(f"✗ {filepath} - NOT FOUND")
            missing.append(filepath)
            
    return missing


def main():
    """Run all pre-flight checks"""
    print("=" * 80)
    print("GRAPHRAG SYSTEM - PRE-FLIGHT CHECKS")
    print("=" * 80)
    
    print("\n[1/5] Checking Python Version...")
    python_ok = check_python_version()
    
    print("\n[2/5] Checking Python Dependencies...")
    missing_deps, installed_deps = check_dependencies()
    
    print("\n[3/5] Checking spaCy Language Model...")
    spacy_ok = check_spacy_model()
    
    print("\n[4/5] Checking Environment Variables...")
    missing_env = check_environment_variables()
    
    print("\n[5/5] Checking Project Structure...")
    missing_files = check_backend_structure()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_ok = True
    
    if not python_ok:
        print("⚠ Python version should be 3.8+")
        
    if missing_deps:
        print(f"✗ Missing dependencies: {', '.join(missing_deps)}")
        print(f"\n  Install with: python -m pip install -r requirements.txt")
        all_ok = False
    else:
        print(f"✓ All dependencies installed ({len(installed_deps)} packages)")
        
    if not spacy_ok and "spacy" in installed_deps:
        print("✗ spaCy model not installed")
        print("  Install with: python -m spacy download en_core_web_sm")
        all_ok = False
        
    if missing_env:
        print(f"✗ Missing required environment variables: {', '.join(missing_env)}")
        all_ok = False
    else:
        print("✓ All required environment variables set")
        
    if missing_files:
        print(f"✗ Missing project files: {', '.join(missing_files)}")
        all_ok = False
    else:
        print("✓ All project files present")
        
    print("\n" + "=" * 80)
    
    if all_ok:
        print("✓ ENVIRONMENT READY")
        print("\nNext steps:")
        print("  1. Start Neo4j database")
        print("  2. Start backend: cd backend && uvicorn main:app --reload")
        print("  3. Run validation: python test_validation.py")
        print("  4. Start frontend: streamlit run frontend/ui.py")
        return 0
    else:
        print("✗ ENVIRONMENT NOT READY")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
