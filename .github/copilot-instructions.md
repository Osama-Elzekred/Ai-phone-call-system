# Project Overview

This repository hosts an AI-powered hotline application designed to process Arabic (Egyptian dialect) voice calls. The system transcribes audio inputs, generates context-aware responses using various LLMs, and synthesizes reply audio for playback. It supports multi-tenant configurations, allowing users to upload and manage their own knowledge bases and define custom action triggers.

# Technical Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with JSONB and pgvector extensions
- **Caching & Queueing**: Redis
- **Frontend**: Next.js
- **Asynchronous Tasks**: Celery
- **Speech-to-Text (STT)**: Munsit-1 API
- **Text-to-Speech (TTS)**: ElevenLabs API
- **LLMs**: GPT-4, Claude, Mistral (interchangeable via abstraction layer)

# Coding Standards

- Utilize asynchronous programming paradigms (`async`/`await`) throughout the FastAPI application.
- Employ SQLAlchemy for ORM interactions with PostgreSQL.
- Define data models using Pydantic for validation and serialization.
- Organize code into modular components: `api`, `services`, `models`, `schemas`, `core`, and `workers`.
- Implement environment-based configurations using `pydantic.BaseSettings`.
- Adhere to PEP 8 coding style guidelines.

# Functional Requirements

- Develop endpoints to handle audio uploads, transcription via Munsit-1, response generation through selected LLMs, and TTS synthesis using ElevenLabs.
- Enable users to upload various document formats (e.g., PDFs, CSVs) as knowledge sources.
- Implement a retrieval-augmented generation (RAG) system for context-aware responses.
- Allow users to define custom actions triggered by specific intents, such as updating a Google Sheet or sending data to a CRM.
- Ensure the system can dynamically switch between different LLM APIs based on user preferences or availability.

# Security and Best Practices

- Validate and sanitize all user inputs to prevent injection attacks.
- Secure API endpoints using JWT-based authentication.
- Store sensitive information, such as API keys and database credentials, in environment variables; never hard-code them.
- Implement rate limiting to prevent abuse and ensure fair usage.
- Log all operations with appropriate log levels and ensure logs do not contain sensitive information.

# Development and Deployment

- Use Docker and Docker Compose for containerization and orchestration of services.
- Write unit and integration tests for all critical components.
- Set up continuous integration and deployment (CI/CD) pipelines to automate testing and deployment processes.
- Monitor application performance and errors using appropriate monitoring tools.

# Interaction with Copilot

- When generating code, follow the project's modular structure and coding standards.
- For new features, create corresponding Pydantic models, SQLAlchemy schemas, and FastAPI routes.
- When integrating with external APIs (e.g., Munsit-1, ElevenLabs), encapsulate interactions within dedicated service classes.
- For user-defined actions, design a plugin-like architecture that allows easy addition and management of custom triggers.

# Notes

- Always seek clarification if a task description lacks sufficient detail.
- Prioritize code readability, maintainability, and scalability in all implementations.
