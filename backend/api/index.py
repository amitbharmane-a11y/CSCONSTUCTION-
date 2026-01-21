import os
import sys

from fastapi import FastAPI

# Ensure we can import the backend package (app.main) when running on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app as main_app


# Create a small wrapper app mounted at /api so that requests to
# /api/... on Vercel are correctly routed to the FastAPI application
# defined in app.main, whose routes are declared without the /api
# prefix (e.g. "/health", "/projects").
app = FastAPI()
app.mount("/api", main_app)