/**
 * routes/chat.rag.js — version RAG de la route Yasmine.
 *
 * Au lieu de coller un bloc figé dans le prompt (buildSystemContext) et d'appeler
 * Claude, cette route transmet la question au service RAG Python (FastAPI, api.py)
 * qui fait la récupération sémantique + la génération, et renvoie { reply }.
 *
 * On garde la même sécurité que la route d'origine : limite de débit, validation,
 * journalisation dans chatLog. Le widget Angular Yasmine n'a RIEN à changer.
 *
 * Pré-requis :
 *   - Node 18+ (fetch global). Sinon : npm i node-fetch et l'importer.
 *   - Le service Python tourne :  uvicorn api:app --port 8001
 *   - .env (Node) :  RAG_URL=http://localhost:8001/chat
 *
 * Montage (server.js) :
 *   app.use(express.json({ limit: '1mb' }));
 *   app.use('/api/chat', require('./routes/chat.rag'));   // remplace ./routes/chat
 */
const express = require('express');
const rateLimit = require('express-rate-limit');
const models = require('../models/chatModels'); // fourni par le package yasmine-integration

const router = express.Router();

const RAG_URL = process.env.RAG_URL || 'http://localhost:8001/chat';
const MAX_MESSAGES = 30;
const MAX_CHARS = 2000;

// Même limite de débit qu'avant : 10 / IP / minute
const chatLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  handler: (_req, res) => res.status(429).json({ error: 'rate_limited' }),
});

function validateMessages(req, res, next) {
  const { messages } = req.body || {};
  if (!Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'invalid_messages' });
  }
  if (messages.length > MAX_MESSAGES) {
    return res.status(400).json({ error: 'too_many_messages', max: MAX_MESSAGES });
  }
  for (const m of messages) {
    if (!m || (m.role !== 'user' && m.role !== 'assistant') || typeof m.content !== 'string') {
      return res.status(400).json({ error: 'invalid_message' });
    }
    if (m.content.length > MAX_CHARS) {
      return res.status(400).json({ error: 'message_too_long', max: MAX_CHARS });
    }
  }
  next();
}

router.post('/', chatLimiter, validateMessages, async (req, res) => {
  try {
    const { messages, sessionId } = req.body;

    // Le service RAG est single-turn : on lui envoie la dernière question de l'utilisateur.
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (!lastUser) return res.status(400).json({ error: 'invalid_messages' });

    const r = await fetch(RAG_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: lastUser.content }),
    });
    if (!r.ok) throw new Error(`RAG service répond ${r.status}`);

    const data = await r.json();
    const reply =
      (data && data.reply) ||
      "Désolée, je n'ai pas de réponse pour le moment. En cas d'urgence, composez le 19.";

    // Journalisation (sans bloquer la réponse)
    models.ChatLog.create({
      sessionId: sessionId || `anon-${Date.now()}`,
      messages: [
        ...messages.map((m) => ({ role: m.role, content: m.content, ts: Date.now() })),
        { role: 'assistant', content: reply, ts: Date.now() },
      ],
    }).catch((e) => console.error('[chat] log échoué:', e?.message));

    return res.json({ reply });
  } catch (err) {
    console.error('[chat] erreur RAG:', err?.message || err);
    // Le widget affiche son message de repli (avec les numéros d'urgence) sur toute erreur.
    return res.status(502).json({ error: 'upstream_error' });
  }
});

module.exports = router;
