# LocalDocs AI 🤖

**Privacy-focused local documentation generator using AI**

## Features

- ✅ 100% Local - No API keys, no cloud
- ✅ Privacy-First - Code stays on your machine
- ✅ Multi-Language - Python, JavaScript, TypeScript
- ✅ CLI + API - Terminal or HTTP interface
- ✅ Open Source - MIT License

## Quick Start

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run API
PYTHONPATH=src uvicorn localdocs.main:app --reload --host 0.0.0.0 --port 8000

# 4. Open docs
# http://localhost:8000/docs
