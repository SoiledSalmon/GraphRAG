import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file if it exists.
# OS-level environment variables will take precedence over .env file values.
load_dotenv()

def check_env_vars():
    """Checks for required environment variables."""
    missing = []
    required_vars = ["GEMINI_API_KEY", "NEO4J_PASSWORD"]
    
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing)}")
        return False
    print(f"✓ Environment variables checked ({len(required_vars)}/{len(required_vars)} present)")
    return True

def check_imports():
    """Checks if required Python modules can be imported."""
    modules = ["requests", "fastapi", "neo4j", "spacy"]
    missing = []
    
    for mod in modules:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    
    if missing:
        print(f"❌ Error: Missing required Python packages: {', '.join(missing)}")
        print("  Tip: Run 'pip install -r requirements.txt'")
        return False
    print(f"✓ Python dependencies checked ({len(modules)}/{len(modules)} installed)")
    return True

def check_spacy_model():
    """Checks if the spaCy model is available."""
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
            print("✓ spaCy model 'en_core_web_sm' available")
        except OSError:
            print("❌ Error: spaCy model 'en_core_web_sm' not found.")
            print("  Tip: Run 'python -m spacy download en_core_web_sm'")
            return False
    except ImportError:
        # Should be caught by check_imports, but safe fallback
        print("❌ Error: spacy not installed.")
        return False
    return True

def main():
    print("Starting environment verification...\n")
    
    checks = [
        check_env_vars,
        check_imports,
        check_spacy_model
    ]
    
    for check in checks:
        if not check():
            print("\nEnvironment check FAILED.")
            sys.exit(1)
            
    print("\n✓ ENVIRONMENT READY")

if __name__ == "__main__":
    main()