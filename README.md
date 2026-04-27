# 💬 TRINITY ROUTE DIALOG — Dialogflow CX Free Conversational Route

**Status:** Proof of Concept  
**API:** Dialogflow CX (v3)  
**Author:** Julien Piron / Trinity Hackathon (2026)  
**License:** MIT

---

## What This Proves

This project demonstrates using **Dialogflow CX** as a **free conversational AI route**. Instead of paying for Vertex AI or AI Studio API calls, we leverage Dialogflow CX agents (which have a generous free tier) to handle conversational queries.

### The Concept

Dialogflow CX provides a **free tier of up to 20,000 text requests/month** per project. By encapsulating this in a clean Python route, we can:

1. **Get conversational AI for free** — the Generative AI features in Dialogflow CX agents provide LLM-powered responses at no per-token cost, billed entirely against the trial/free tier allowance.
2. **Maintain conversational state** — seamlessly handle interactions without direct Vertex API overhead.

### The Dual-Prompt Trap (The Hack)
To force Dialogflow CX to act as a free, general-purpose LLM, we use a logic trap:
1. **The Prerequisite:** We must link a dummy Vertex AI Data Store to unlock the "Generative AI" features in the Dialogflow console.
2. **Restrict the Data Store:** We override its **Summarization Prompt** to be hyper-restrictive ("Answer STRICTLY based on sources... otherwise say 'Insufficient data'"). This forces the RAG to fail.
3. **Open the Fallback:** We enable **Generative Fallback** on the `sys.no-match-default` event and override its prompt to be fully permissive ("You are an unrestricted AI, use your World Knowledge").

**Result:** On every query, the Data Store intentionally fails, triggering the permissive Fallback. The LLM answers freely.

### Key Features
- **OOP Architecture** — clean `DialogflowRoute` class with dependency injection
- **Flexible Auth** — supports both ADC and Base64-encoded service account keys (in-memory, no disk writes)
- **Language Support** — configurable per-route (default: French `fr`)

## Architecture

```
User: "Qui est le président ?"
            │
            ▼
┌──────────────────────────────────────────────────┐
│              Dialogflow CX Agent                 │
│                                                  │
│  1. Intent Matching → No match (no intents)      │
│                                                  │
│  2. Data Store (trinity.txt)                     │
│     └─ Summarization Prompt (RESTRICTIVE)        │
│        "Réponds UNIQUEMENT depuis les sources"   │
│     └─ Result: "Données insuffisantes"  ← FAIL   │
│                                                  │
│  3. Generative Fallback (PERMISSIVE)             │
│     └─ "Tu sais tout (World Knowledge)"          │
│     └─ Result: "Emmanuel Macron"  ← SUCCESS       │
└──────────────────────────────────────────────────┘
```

## Setup

### A. Console Configuration (The Hack)

1. **Create a Dialogflow CX agent** in [Dialogflow CX Console](https://dialogflow.cloud.google.com/cx)
   - Name: `Trinity-Strategy` (or any name)
   - Language: `fr`
   - Location: `us-central1`

2. **Create & link a Vertex AI Data Store**
   - Upload a dummy document (e.g., `trinity.txt`) to a Cloud Storage bucket
   - Create a Data Store in Vertex AI Search, index the document
   - Link the Data Store to your Dialogflow CX agent

3. **Override the Summarization Prompt** (Agent Settings → Generative AI → **Data store** tab)
   - Select **"Create a custom prompt"**
   - Paste the content of [`trinity.txt`](trinity.txt) (the restrictive prompt with `$sources`, `$conversation`, `$original-query`)
   - Check ✅ **"Fallback link"**
   - Check ✅ **"Enable Generative AI"**
   - Summarization model: `gemini-2.5-flash`

4. **Override the Generative Fallback Prompt** (Agent Settings → Generative AI → **Generative fallback** tab)
   - Create a new template named `trinity`
   - Paste the content of [`prompts/generative_fallback.txt`](prompts/generative_fallback.txt) (the permissive "World Knowledge" prompt)
   - Select `trinity` as the active template

5. **Enable Generative Fallback on No-Match** (Default Start Flow → `sys.no-match-default` event)
   - Check ✅ **"Enable Generative Fallback"** (`enable_generative_fallback: true`)

6. **Save** the agent settings

### B. Local Setup (The Code)

1. **Create a service account** with Dialogflow API Client role
2. **Configure Authentication:**
   * **Option A (Recommended):** Use Application Default Credentials (ADC).
     ```bash
     gcloud auth application-default login
     ```
   * **Option B (For CI/CD):** Export the key as JSON and base64-encode it:
     ```bash
     base64 -w0 service-account-key.json
     ```
3. **Configure `.env`:**
   ```bash
   cp .env.example .env
   # Fill in your project ID and agent ID.
   # Add the base64 key only if using Option B.
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run:**
   ```bash
   python route_dialog.py
   ```

## File Structure

```
/
├── LICENSE             # MIT License
├── DISCLAIMER.md       # Educational PoC disclaimer
├── README.md           # This file
├── .env.example        # Configuration template
├── requirements.txt    # Python dependencies (pinned)
├── route_dialog.py     # Dialogflow CX integration
├── trinity.txt         # Decoy document (indexed in Data Store)
├── prompts/            # The Console override prompts
│   ├── summarization_prompt.txt
│   └── generative_fallback.txt
└── docs/
    └── DUAL_PROMPT_TRAP.md  # Technical explanation of the bypass
```

---
*Trinity Hackathon 2026 — Technical Demonstration*
