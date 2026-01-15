@echo off
REM Quick setup script for GraphRAG system
REM This installs dependencies and prepares environment

echo ================================================================================
echo GRAPHRAG SYSTEM - QUICK SETUP
echo ================================================================================
echo.

echo [1/4] Installing Python dependencies...
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Installing spaCy language model...
python -m spacy download en_core_web_sm
if %ERRORLEVEL% neq 0 (
    echo WARNING: Failed to install spaCy model - you may need to install manually
)

echo.
echo [3/4] Running environment check...
python check_environment.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo WARNING: Environment check found issues
    echo Please review the output above and configure missing items
    echo.
)

echo.
echo [4/4] Setup complete!
echo.
echo ================================================================================
echo NEXT STEPS:
echo ================================================================================
echo 1. Set environment variables:
echo    set GEMINI_API_KEY=your_api_key_here
echo    set NEO4J_PASSWORD=your_password
echo.
echo 2. Start Neo4j database
echo.
echo 3. Start backend server:
echo    cd backend
echo    uvicorn main:app --reload
echo.
echo 4. Run validation tests:
echo    python test_validation.py
echo.
echo 5. (Optional) Start frontend:
echo    streamlit run frontend/ui.py
echo ================================================================================
echo.

pause
