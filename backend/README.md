# One More Question Backend

Small proxy server so `question.html` on GitHub Pages can call Ollama on your Mac (via a public URL such as ngrok).

## Easiest: Python (macOS has this already)

```bash
cd backend
python3 server.py
```

Health check:

```bash
curl http://127.0.0.1:3000/health
```

Ask:

```bash
curl -X POST http://127.0.0.1:3000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Say hi to a kid in one sentence","model":"llama3.2"}'
```

Then expose port 3000 (example):

```bash
ngrok http 3000
```

On the live site: **Parent Portal** → **Kid Explainer (AI)** → paste `https://YOUR-NGROK-HOST/api` → **Save** → **Test connection**.

## Alternative: Node

```bash
cd backend
npm install
npm start
```

(Same `/health` and `/api/ask` paths.)

## Environment Variables

- `PORT` - default `3000`
- `OLLAMA_BASE_URL` - default `http://127.0.0.1:11434`
- `OLLAMA_MODEL` - default `llama3.2`
- `FRONTEND_ORIGIN` - CORS: `*` or comma-separated origins (e.g. `https://carrie-s-dev.github.io`)

## Frontend config

The question page reads `localStorage.omqApiBase`. It must end with **`/api`** (e.g. `https://abc.ngrok-free.app/api`). You can set this in **Parent Portal** without using the console.
