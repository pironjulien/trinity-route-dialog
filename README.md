# 💬 TRINITY ROUTE DIALOG — Dialogflow CX Free Conversational Route

**Status:** Proof of Concept  
**API:** Dialogflow CX (v3beta1)  
**Author:** Julien Piron / Trinity Hackathon (2026)

---

## What This Proves

This project demonstrates using **Dialogflow CX** as a **free conversational AI route** with multi-project failover. Instead of paying for Vertex AI or AI Studio API calls, we leverage Dialogflow CX agents (which have a generous free tier) to handle conversational queries.

### Key Concepts
- **Multi-Project Failover:** 2 Google Cloud projects configured, automatic fallback
- **Service Account Auth:** Base64-encoded credentials in environment variables
- **Zero LLM Cost:** Dialogflow CX free tier handles the conversation
- **Language Support:** French (`fr`) by default, configurable

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
3. **Export the key** as JSON and base64-encode it:
   ```bash
   base64 -w0 service-account-key.json
   ```
4. **Configure `.env`:**
   ```bash
   cp .env.example .env
   # Fill in your values
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
├── .env.example        # Configuration template
├── requirements.txt    # Python dependencies
└── route_dialog.py     # Dialogflow CX integration
```

---
*Trinity Hackathon 2026 — Technical Demonstration*
