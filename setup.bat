@echo off
echo Setting up the AgriShield AI Environment...
call venv\Scripts\activate.bat
echo Upgrading pip...
python -m pip install --upgrade pip
echo Installing required libraries (this might take a few minutes)...
pip install streamlit pandas numpy scikit-learn matplotlib plotly
echo.
echo Installation Complete!
echo You can now run the app by typing:
echo streamlit run app.py
pause
