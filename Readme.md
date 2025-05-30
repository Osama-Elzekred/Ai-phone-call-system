# 🎙️ AI Phone Call Processing System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)

A simple yet powerful AI-powered phone call processing system that allows businesses to link phone numbers to AI agents for automated sales, customer service, and food ordering calls. Built with FastAPI, PostgreSQL, Redis, and Next.js.

## 🌟 Features

### Core Capabilities
- **📞 Phone Number Linking**: Connect phone numbers to AI agents for automated call handling
- **🏢 Multi-Firm Support**: Multiple businesses can use the system with isolated data
- **🤖 AI Call Processing**: Automated handling of sales, customer service, and ordering calls
- **💬 Intelligent Responses**: Context-aware AI responses based on call type and business needs
- **📊 Call Analytics**: Track and analyze call performance and outcomes
- **🔧 Simple Configuration**: Easy setup for different business types and call scenarios

### Technical Features
- **🚀 FastAPI Backend**: Modern, fast Python web framework
- **🗄️ PostgreSQL Database**: Reliable data storage with JSONB support
- **⚡ Redis Caching**: Fast response times and session management
- **🌐 Next.js Frontend**: Modern React-based user interface
- **🔒 Secure**: Basic authentication and data isolation
- **📱 RESTful API**: Clean, documented API endpoints

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