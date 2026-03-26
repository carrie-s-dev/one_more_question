# One More Question Backend

Small proxy server that lets `question.html` call Ollama safely from a hosted site.

## Environment Variables

- `PORT` - Provided by host (default `3000`)
- `OLLAMA_BASE_URL` - URL for Ollama API (default `http://127.0.0.1:11434`)
- `OLLAMA_MODEL` - Model name (default `llama3.2`)
- `FRONTEND_ORIGIN` - Allowed CORS origins, comma-separated, or `*`

## Local Run

```bash
cd backend
npm install
npm start
```

Health check:

```bash
curl http://localhost:3000/health
```

Ask endpoint:

```bash
curl -X POST http://localhost:3000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain rainbows for kids","model":"llama3.2"}'
```

## Point Frontend To Backend

In browser console on your deployed site:

```js
localStorage.setItem('omqApiBase', 'https://YOUR-BACKEND-URL')
```

Then refresh.
