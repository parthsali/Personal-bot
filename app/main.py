import uvicorn

if __name__ == "__main__":
    # The server setup is now handled inside app/server.py
    # This script is just a convenient way to run it.
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True)