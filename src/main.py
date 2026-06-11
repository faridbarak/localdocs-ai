from fastapi import FastAPI
app = FastAPI(title="LocalDocs AI", version="1.0.0")

@app.get("/")
def read_root(): return {"message": "LocalDocs AI is running!", "docs": "/docs"}

@app.get("/health")
def health(): return {"status": "healthy"}

