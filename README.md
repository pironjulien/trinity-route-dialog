# 💬 TRINITY ROUTE DIALOG — Dialogflow CX Free Conversational Route

**Status:** Proof of Concept  
**API:** Dialogflow CX (v3)  
**Author:** Julien Piron / Trinity Hackathon (2026)  
**License:** MIT

---

## What This Proves

This project demonstrates using **Dialogflow CX** as a **free conversational AI route** with multi-project failover. Instead of paying for Vertex AI or AI Studio API calls, we leverage Dialogflow CX agents (which have a generous free tier) to handle conversational queries.

### The Concept

Dialogflow CX provides a **free tier of up to 20,000 text requests/month** per project. By configuring multiple Google Cloud projects with separate agents, we can:

1. **Scale horizontally** — distribute requests across projects to stay within free tier limits
2. **Fail over automatically** — if one project hits its quota, the next takes over
3. **Get conversational AI for free** — the Generative AI features in Dialogflow CX agents provide LLM-powered responses at no per-token cost.

### The Dual-Prompt Trap (The Hack)
To force Dialogflow CX to act as a free, general-purpose LLM without being restricted to pre-defined intents or documents, we use a two-tiered routing trap:
1. **Restrict the Data Store:** We link a dummy Vertex AI Data Store and override its **Summarization Prompt** to be hyper-restrictive ("Answer STRICTLY based on sources... otherwise say 'Insufficient data'").
2. **Open the Fallback:** We enable **Generative Fallback** on the `sys.no-match-default` event and override its prompt to be fully permissive ("You are an unrestricted AI, use your World Knowledge").

**Result:** When you ask a general question, the Data Store intentionally fails (because the restrictive prompt forbids hallucination), which seamlessly hands control over to the permissive Generative Fallback. The LLM answers freely, billed against trial credits.

### Key Features
- **OOP Architecture** — clean `DialogflowRoute` class with dependency injection
- **Multi-Project Failover** — up to 2 Google Cloud projects, automatic fallback
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

Multi-project failover (credit stacking):
┌─────────┐     ┌────────────────┐
│  route   │────▶│ GCP Project 1  │ → Agent (same config)
│  _dialog │     ├────────────────┤
│  .py     │────▶│ GCP Project 2  │ → Agent (same config)
└─────────┘     └────────────────┘
```

## Setup

1. **Create a Dialogflow CX agent** in [Google Cloud Console](https://dialogflow.cloud.google.com/cx)
2. **Create a service account** with Dialogflow API Client role
3. **Configure Authentication:**
   * **Option A (Recommended for local testing):** Use Application Default Credentials (ADC).
     ```bash
     gcloud auth application-default login
     ```
   * **Option B (For CI/CD or specific service accounts):** Export the key as JSON and base64-encode it:
     ```bash
     base64 -w0 service-account-key.json
     ```
4. **Configure `.env`:**
   ```bash
   cp .env.example .env
   # Fill in your project ID and agent ID.
   # Add the base64 key only if using Option B.
   ```
5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Run:**
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
