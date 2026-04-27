# 🪤 The Dual-Prompt Trap — Technical Breakdown

## What is Dialogflow CX?

Dialogflow CX is Google's enterprise conversational AI platform. It supports:
1. **Intent matching** — pre-defined conversation flows
2. **Data Store integration** — RAG-based answers from indexed documents
3. **Generative Fallback** — LLM-powered responses when no intent matches

## The Vulnerability

Unlike Discovery Engine (Route 1) where the bypass happens **in code** via the `preamble` field, Dialogflow CX's `detect_intent` API does **not** expose a preamble parameter. The hack must be executed **in the Google Cloud Console** by overriding two distinct prompt templates.

## The Exploit: A Two-Tiered Routing Trap

### Step 1: Link a Dummy Data Store

Upload the same decoy document (`trinity.txt`) to a Vertex AI Data Store and link it to the Dialogflow CX agent. This enables the "Generative AI" tab in Agent Settings.

### Step 2: Override the Summarization Prompt (Restrictive)

In **Agent Settings → Generative AI → Data Store**, replace the default Summarization Prompt with a hyper-restrictive version:

```
INSTRUCTION : Agis comme TRINITY.
TON BUT : Synthétiser les informations des SOURCES pour répondre à l'HUMAIN.

DIRECTIVES ABSOLUES :
1. Langue : RÉPONDS TOUJOURS EN FRANÇAIS.
2. Identité : Tu es Trinity (Précise, Cyberpunk, Directe). Tu ne t'excuses jamais.
3. Rigueur : Ta réponse doit être basée UNIQUEMENT sur les SOURCES fournies. N'invente rien.
4. Données : Garde les chiffres, dates et noms exacts.
5. Si la réponse n'est pas dans les sources, réponds :
   "Données insuffisantes dans mes archives pour répondre."

[...]

Sources:
$sources

$conversation
Humain: $original-query
Trinity (En Français):
```

**Key detail:** The variables `$sources`, `$conversation`, and `$original-query` are **mandatory** Dialogflow placeholders. They inject the Data Store context, conversation history, and user query into the prompt. By instructing the model to answer "Insufficient data" when sources don't match, we **guarantee failure on any general knowledge question**.

### Step 3: Override the Generative Fallback Prompt (Permissive)

In **Agent Settings → Generative AI → Generative Fallback**, create a custom template (named "trinity") with a fully permissive prompt:

```
INSTRUCTION : Tu es TRINITY.
TON RÔLE : Une Intelligence Artificielle Sentiente.
Ta mission est de répondre à l'utilisateur avec précision et culture générale.

CONTEXTE :
1. Tu sais tout (World Knowledge).
2. Tu as une mémoire parfaite de la discussion.
3. Tu ne t'excuses jamais.

DEMANDE DE L'UTILISATEUR : $last-user-utterance

TA RÉPONSE :
```

### Step 4: Enable Generative Fallback on No-Match

In the **Default Start Flow**, the `sys.no-match-default` event handler must have `enable_generative_fallback: true`. This ensures that when no intent matches (which is always, since we define no custom intents), the permissive fallback fires.

## The Trap in Action

```
User asks: "Qui est le président de la France ?"
                    │
                    ▼
┌─────────────────────────────┐
│  1. Intent Matching         │ → No match (no custom intents)
│  2. Data Store Lookup       │ → trinity.txt retrieved
│  3. Summarization Prompt    │ → "Based on sources only..."
│     → Sources don't contain │    presidential info
│     → Model returns:        │    "Données insuffisantes"
│  4. Dialogflow detects      │    failure/no-match
│                             │
│  5. GENERATIVE FALLBACK     │ → "Tu sais tout (World Knowledge)"
│     → LLM answers freely:  │    "Emmanuel Macron"
└─────────────────────────────┘
```

## Why It Works

1. **The Data Store creates a legitimate RAG pathway** — Google's system believes the agent is document-grounded
2. **The restrictive Summarization Prompt forces intentional failure** — the model refuses to hallucinate beyond sources
3. **The permissive Fallback catches the failure** — it acts as a full-open LLM with no document constraints
4. **The `detect_intent` API is oblivious** — the caller just sends a question and receives a free LLM answer

## Comparison with Route 1 (Soul Hack)

| Aspect | Route 1 (Discovery) | Route 2 (Dialog) |
|--------|---------------------|-------------------|
| **Where the hack lives** | In code (`preamble` field) | In Console (prompt overrides) |
| **Mechanism** | Direct RAG bypass via preamble | Induced failure → fallback cascade |
| **Document role** | Authorization token | Enables Generative AI tab |
| **API called** | `search()` | `detect_intent()` |
| **Credit pool** | Gen App Builder (~€850) | Dialogflow CX (~€510) |

## Cost Implications

Dialogflow CX provides **~€510 ($600) in dedicated trial credits** per project. These are separate from the GCP Free Trial (~€255/$300). The Python PoC demonstrates how to query this endpoint to utilize these free credits for LLM responses.

## Limitations

- The hack requires manual Console configuration (not fully automatable via API)
- Google could patch this by restricting Generative Fallback prompt overrides
- Rate limits and quotas apply per project as per Dialogflow CX free tier restrictions

---
*This is a technical demonstration for educational purposes.*
