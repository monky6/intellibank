"""
IntelliBank Unified Runner
Usage:
  python run.py           # Launches both FastAPI Backend and Streamlit Dashboard
  python run.py backend   # Launches only the FastAPI REST service (Port 8000)
  python run.py frontend  # Launches only the Streamlit Web UI (Port 8501)
  python run.py test      # Runs the automated test suite
"""

import sys
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON_EXE = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
if not PYTHON_EXE.exists():
    PYTHON_EXE = Path(sys.executable)

def run_backend():
    print("🚀 Starting IntelliBank FastAPI Backend on http://127.0.0.1:8000 ...")
    return subprocess.Popen(
        [str(PYTHON_EXE), "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=str(PROJECT_ROOT)
    )

def run_frontend():
    print("🌐 Starting IntelliBank Streamlit Dashboard on http://localhost:8501 ...")
    return subprocess.Popen(
        [str(PYTHON_EXE), "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"],
        cwd=str(PROJECT_ROOT)
    )

def run_test():
    print("🧪 Running IntelliBank Automated Verification Suite...")
    subprocess.run([str(PYTHON_EXE), "tests/test_rag.py"], cwd=str(PROJECT_ROOT))

def main():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "both"

    if mode == "backend":
        proc = run_backend()
        proc.wait()
    elif mode == "frontend":
        proc = run_frontend()
        proc.wait()
    elif mode == "test":
        run_test()
    elif mode == "both":
        print("=" * 60)
        print("🏦 LAUNCHING INTELLIBANK DUAL SERVICES")
        print("=" * 60)
        p_back = run_backend()
        time.sleep(2)
        p_front = run_frontend()
        print("\n✅ Both services started!")
        print("  • REST API Docs: http://127.0.0.1:8000/docs")
        print("  • Streamlit Web UI: http://localhost:8501")
        print("\nPress Ctrl+C to terminate both servers.\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
            p_front.terminate()
            p_back.terminate()
    else:
        print(f"Unknown mode '{mode}'. Choose from: 'both', 'backend', 'frontend', 'test'.")

if __name__ == "__main__":
    main()
