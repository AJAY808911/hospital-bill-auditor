"""
Convenience launcher for the FastAPI backend server.
Run with: python backend/run_backend.py
"""
import sys
import os
import uvicorn

# Ensure the backend directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("Starting Hospital Bill Auditor Backend on http://127.0.0.1:8000 ...")
    print("API Documentation available at: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

