import express from 'express';
import cors from 'cors';

const app = express();
const port = process.env.PORT || 3000;

const ollamaBaseUrl = (process.env.OLLAMA_BASE_URL || 'http://127.0.0.1:11434').replace(/\/$/, '');
const allowedOriginsRaw = process.env.FRONTEND_ORIGIN || '*';
const allowedOrigins = allowedOriginsRaw.split(',').map((s) => s.trim()).filter(Boolean);

app.use(express.json({ limit: '1mb' }));
app.use(
  cors({
    origin: allowedOrigins.includes('*') ? true : allowedOrigins
  })
);

app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'one-more-question-backend' });
});

app.post('/api/ask', async (req, res) => {
  try {
    const prompt = (req.body?.prompt || '').trim();
    const model = (req.body?.model || process.env.OLLAMA_MODEL || 'llama3.2').trim();

    if (!prompt) {
      return res.status(400).json({ error: 'Missing prompt' });
    }

    const ollamaResponse = await fetch(`${ollamaBaseUrl}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        stream: false
      })
    });

    if (!ollamaResponse.ok) {
      const text = await ollamaResponse.text();
      return res.status(502).json({ error: `Ollama request failed: ${text}` });
    }

    const data = await ollamaResponse.json();
    return res.json({ response: data.response || '' });
  } catch (err) {
    return res.status(500).json({ error: err.message || 'Unknown server error' });
  }
});

app.listen(port, () => {
  console.log(`Backend listening on port ${port}`);
});
