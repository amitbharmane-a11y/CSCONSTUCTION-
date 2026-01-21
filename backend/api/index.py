import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from fastapi import FastAPI

# Vercel expects the FastAPI app to be named 'app'
app = app