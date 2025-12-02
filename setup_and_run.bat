@echo off
echo ========================================
echo Installing required packages...
echo ========================================
pip install --upgrade pip
pip install streamlit>=1.39.0
pip install pandas>=2.2.0
pip install plotly>=5.22.0
echo.
echo ========================================
echo Starting Streamlit application...
echo ========================================
streamlit run app.py
pause

