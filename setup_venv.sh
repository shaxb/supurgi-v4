#!/bin/bash
python -m venv venv
# Windows-specific activation path
source venv/Scripts/activate
pip install -r requirements-dev.txt
echo "Virtual environment created and activated."
echo "Use 'source venv/Scripts/activate' to activate it in the future."


#python -m uvicorn services.market_data.app:app --reload --host 0.0.0.0 --port 8001
