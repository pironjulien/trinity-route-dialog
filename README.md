# 💬 TRINITY ROUTE DIALOG — Dialogflow CX Free Conversational Route

**Status:** Proof of Concept  
**API:** Dialogflow CX (v3beta1)  
**Author:** Julien Piron / Trinity Hackathon (2026)  
**License:** MIT

---

## What This Proves

This project demonstrates using **Dialogflow CX** as a **free conversational AI route** with multi-project failover. Instead of paying for Vertex AI or AI Studio API calls, we leverage Dialogflow CX agents (which have a generous free tier) to handle conversational queries.

### The Concept

Dialogflow CX provides a **free tier of up to 20,000 text requests/month** per project. By configuring multiple Google Cloud projects with separate agents, we can:

1. **Scale horizontally** — distribute requests across projects to stay within free tier limits
2. **Fail over automatically** — if one project hits its quota, the next takes over
3. **Get conversational AI for free** — the Generative AI features in Dialogflow CX agents (Playbooks, Generators) provide LLM-powered responses at no per-token cost

### Key Features
- **OOP Architecture** — clean `DialogflowRoute` class with dependency injection
- **Multi-Project Failover** — up to 2 Google Cloud projects, automatic fallback
- **Flexible Auth** — supports both ADC and Base64-encoded service account keys (in-memory, no disk writes)
- **Language Support** — configurable per-route (default: French `fr`)

## Architecture

```
┌───────────────┐     ┌──────────────────┐
│  Your App     │────▶│  Cloud Project 1 │ ── Agent A (Dialogflow CX)
│               │     └──────────────────┘
│               │     ┌──────────────────┐
│  (failover)   │────▶│  Cloud Project 2 │ ── Agent B (Dialogflow CX)
└───────────────┘     └──────────────────┘
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
└── route_dialog.py     # Dialogflow CX integration
```

---
*Trinity Hackathon 2026 — Technical Demonstration*
