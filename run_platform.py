import subprocess
import time
import webbrowser
import os
import sys

def main():
    print("🚀 Starting Quant Platform Ecosystem...")
    
    # 1. Start API Backend
    print("Starting API (FastAPI) on port 8000...")
    # api_process = subprocess.Popen(["uvicorn", "api.main:app", "--reload", "--port", "8000"])
    api_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--reload", "--port", "8000"])
    
    time.sleep(3) # Wait for API to boot
    
    # 2. Start Frontend
    print("Starting Dashboard (Streamlit) on port 8501...")
    # frontend_process = subprocess.Popen(["streamlit", "run", "dashboard/app.py"])
    frontend_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard/app.py"])
    
    print("\n✅ System Running!")
    print("API: http://127.0.0.1:8000")
    print("Dashboard: http://127.0.0.1:8501")
    print("Press Ctrl+C to stop both servers.")
    
    try:
        api_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        api_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
