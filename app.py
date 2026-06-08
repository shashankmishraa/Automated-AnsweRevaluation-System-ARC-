"""
Entry point for the Answer Evaluation System.
Run this file to start the FastAPI backend server.
"""

from main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Answer Evaluation API Server...")
    print("📍 Server running at: http://127.0.0.1:8000")
    print("📚 API Docs available at: http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
# Quick push (if git already initialized)
