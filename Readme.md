# 🎙️ AI Hotline Backend

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An AI-powered hotline platform that processes Arabic (Egyptian dialect) voice calls with real-time transcription, LLM processing, and text-to-speech synthesis. Built with modern Python async architecture and designed for scalability.

## 🌟 Key Features

### 🎯 Core Capabilities
- **🗣️ Arabic Speech Processing**: Specialized for Egyptian dialect using Munsit-1 STT
- **🤖 Multi-LLM Support**: Dynamic response generation via GPT-4, Claude, and Mistral
- **🔊 Voice Synthesis**: High-quality Arabic TTS via ElevenLabs
- **📚 Knowledge Integration**: User-uploaded documents with vector search
- **⚡ Real-time Processing**: Async-first architecture for low latency
- **🏢 Multi-tenant Architecture**: Complete data isolation between organizations

### 🛠️ Technical Excellence
- **🎯 Domain-Driven Design**: Modular monolith ready for microservice extraction
- **🔒 Enterprise Security**: JWT authentication, rate limiting, input validation
- **📊 Database Migrations**: Alembic-powered schema evolution
- **🧪 Comprehensive Testing**: Unit and integration test coverage
- **📈 Observability**: Structured logging and error tracking

## 🛠️ Technical Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI | REST API and business logic |
| **Database** | PostgreSQL | Data storage and management |
| **Cache** | Redis | Session management and caching |
| **Frontend** | Next.js | User interface and dashboard |
| **Language** | Python 3.11+ | Backend development |
| **Deployment** | Docker | Containerization |

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **PostgreSQL**: 14+ 
- **Redis**: 6+
- **Node.js**: 18+ (for frontend)
- **Git**: For version control

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-phone-call-system.git
cd ai-phone-call-system
```

### 2. Environment Setup

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/phone_ai_system
REDIS_URL=redis://localhost:6379/0

# Application
SECRET_KEY=your-secret-key-here
DEBUG=True
ENVIRONMENT=development

# AI Services (add when ready to integrate)
# OPENAI_API_KEY=your_openai_api_key
# ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### 4. Database Setup

```bash
# Create database and run migrations
python -m alembic upgrade head
```

### 5. Start the Application

Development mode:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
ai-phone-call-system/
├── 📁 app/                  # Application core (to be created)
│   ├── 📁 api/             # API endpoints
│   ├── 📁 models/          # Database models  
│   ├── 📁 schemas/         # Pydantic schemas
│   ├── 📁 services/        # Business logic
│   └── 📁 core/            # Core configurations
├── 📁 frontend/            # Next.js frontend (to be created)
├── 📁 tests/               # Test files
├── 🐳 docker-compose.yml   # Docker services
├── 🐳 Dockerfile          # Container definition
├── 📋 requirements.txt     # Python dependencies
├── ⚙️ .env.example        # Environment template
└── 📝 main.py             # Application entry point
```

## 🔧 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Features (To Be Implemented)

- **Phone Management**: Register and manage phone numbers
- **Firm Management**: Multi-tenant support for different businesses
- **Call Processing**: Handle incoming calls with AI
- **Analytics**: Basic call statistics and reporting

## 🐳 Docker Support

Run with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- FastAPI application
- PostgreSQL database
- Redis cache

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `DEBUG` | Enable debug mode | No |
├── ⚙️ .env.example         # Environment template
└── 📝 main.py              # Application entry point
```

## 🔧 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/calls/process` - Process voice call
- `POST /api/v1/knowledge/upload` - Upload knowledge documents
- `GET /api/v1/calls/{call_id}` - Get call details
- `POST /api/v1/auth/login` - User authentication

## 🧪 Testing

Run tests:

```bash
## 🧪 Testing

Run tests (when implemented):

```bash
pytest
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 coding standards
- Write tests for new features
- Use async/await for database operations
- Keep it simple and maintainable

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚀 Roadmap

- [ ] Basic phone number management
- [ ] Simple call processing
- [ ] Multi-firm support
- [ ] Basic AI integration
- [ ] Call analytics dashboard
- [ ] Frontend interface

---

**Built with ❤️ for automated phone call processing**