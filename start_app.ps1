$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python -m streamlit run app.py --server.headless true --server.port 8501
