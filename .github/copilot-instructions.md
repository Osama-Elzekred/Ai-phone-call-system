# 📞 Project Overview

This repository contains an AI-powered hotline platform that processes Arabic (Egyptian dialect) voice calls. The system performs the following key functions:

- Transcribes spoken audio using **Munsit-1 STT**
- Passes transcripts to **multiple LLM APIs** (GPT-4, Claude, Mistral) for dynamic response generation
- Synthesizes reply audio via **ElevenLabs TTS**
- Supports **user-uploaded knowledge sources** and **custom automation actions**
- Enables **multi-tenant operations**, with clear user isolation and document separation

The architecture is a modular monolith, designed to be future-ready for microservice extraction.

---

# 🧱 Technical Stack

- **Backend**: FastAPI (Python, async-first)
- **Frontend**: Next.js (React + SSR)
- **Database**: PostgreSQL (with `JSONB` and `pgvector`)
- **Cache & Queue**: Redis (via Celery)
- **LLMs**: OpenAI GPT-4, Anthropic Claude, Mistral — interchangeable via abstraction layer
- **STT**: Munsit-1 API (Arabic dialect-optimized)
- **TTS**: ElevenLabs API

---

# ✅ Architectural Guidelines

- Follow a **modular, domain-driven structure**, using folders like `modules/{domain}/routers, services, schemas, integrations`
- Design each module to be **isolated, independently testable**, and optionally extractable into a microservice
- Encapsulate external API access (e.g., ElevenLabs, OpenAI) inside `integrations/` folders
- Use `shared/` for cross-cutting concerns (e.g., config, events, logging, exceptions)

---

# 🔐 Security & Resilience

- Use **JWT-based authentication** and ensure all user data is **tenant-isolated**
- **Never** hard-code API keys or credentials; load from `.env` via `pydantic.BaseSettings`
- Validate all external input and **sanitize against injection**
- Add fallback handling for failures in LLM, STT, or TTS services
- Rate-limit public endpoints to prevent abuse
- Store audio/text logs carefully and respect privacy constraints
- **Implement graceful degradation** - applications should start and provide basic functionality even when external dependencies (database, Redis, external APIs) are unavailable
- Use comprehensive exception handling with custom exception classes for different error types

---

# 🧪 Testing & DevOps

- Write **unit tests** per module and **integration tests** for cross-cutting workflows
- Include a robust `conftest.py` with DB/session fixtures
- Ensure compatibility with `docker-compose` and use `.env.example` for shared configs
- **Create application startup tests** to verify endpoints and basic functionality work correctly
- Test error scenarios and fallback behaviors when external services are unavailable
- CI/CD should run `pytest`, `ruff`/`black`, and build Docker images
- Monitor API performance and service uptime using Prometheus or equivalent

---

# 🧠 Copilot Usage Instructions

When writing or completing code, **prioritize these behaviors**:

### ✅ Generate code that:
- Uses **async/await** consistently in API and service layers
- Uses **SQLAlchemy ORM** with PostgreSQL + pgvector
- Defines Pydantic models for all request/response schemas
- Respects the existing modular structure and file placement
- Uses `Depends()` for dependency injection of DB, current user, etc.
- Uses `logging` from `shared/utils/logging.py` for logs
- Names functions and variables **explicitly** — avoid vague names like `process()`
- **Implements proper error handling** with try-catch blocks and graceful fallbacks
- **Includes proper lifespan management** for FastAPI applications with startup/shutdown handlers

### ❌ Avoid code that:
- Writes logic directly inside routers (always call a service layer)
- Uses blocking I/O in async routes (e.g. `open()`, `requests`)
- Hard-codes file paths, secrets, or service endpoints
- Assumes single-user context or stores global state
- **Fails catastrophically when external services are unavailable**
- **Lacks proper exception handling or logs errors inadequately**

---

# 🧩 Functional Considerations

- STT, LLM, and TTS are orchestrated in a single flow, which should be broken into **service layers**
- LLM provider should be **selectable per tenant or per request**, with fallbacks if one fails
- Document upload (PDF, CSV, DOCX) must support **Arabic text extraction**, clean chunking, and embedding via pgvector
- Automation actions (e.g., "update CRM", "write to Sheet") should be implemented as **plugin handlers** with clear interfaces
- Consider memory and performance constraints when chaining LLM + TTS responses — keep logs for diagnostics

---

# 🌍 Language and Localization

- Ensure accurate processing and generation for **Egyptian Arabic**
- Support TTS/STT behavior testing with realistic dialectal samples
- Use UTF-8 and `dir="rtl"` when needed for frontend integration

---

# 🧑‍💻 Developer Notes

- I have a .NET background — C#-style modularity and separation of concerns are familiar, but please follow Python idioms (PEP8, async context, explicit dependency injection)
- Use type hints and docstrings throughout the codebase
- Prefer readability and testability over one-liners or premature optimization
- Be thoughtful about interfaces — code should be extensible and cleanly layered

---

# ✅ Summary Goals for Copilot

- Respect multi-layered modular design
- Use clean naming and typing conventions
- Favor isolated business logic in services
- Handle async I/O properly
- Consider security, fallback, and multilingual behavior in all responses

