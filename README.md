# 🎓 Admissions Counseling Chatbot

AI-powered chatbot system for university admissions counseling using **LangGraph**, **LangChain**, **Elasticsearch**, and **React**.

**Disclaimer:** This project was designed by a student and is for reference and learning purposes only.


## 📋 Features

- ✅ Conversational AI using LangGraph workflow
- ✅ RAG (Retrieval-Augmented Generation) with Elasticsearch
- ✅ Vietnamese language support
- ✅ Hybrid search (BM25 + Vector similarity)
- ✅ Conversation history management
- ✅ Real-time streaming responses
- ✅ User authentication & authorization
- ✅ Modern React UI

## 🏗️ Architecture

```
Frontend (React + Vite)
    ↓
Backend (FastAPI + LangGraph)
    ↓
├── Elasticsearch (Document Retrieval)
├── MongoDB (Conversation Storage)
└── Gemini API (LLM)
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **LangChain** - LLM orchestration
- **LangGraph** - Conversational workflow engine
- **Elasticsearch** - Hybrid search engine
- **MongoDB** - NoSQL database
- **Sentence-Transformers** - Vietnamese embeddings

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management

### AI/ML
- **Google Gemini Pro** - Large Language Model
- **Vietnamese SBERT** - Embeddings model

## 📦 Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for MongoDB)
- Elastic Cloud account (or local Elasticsearch)
- Google Gemini API key

### 1. Clone Repository

```bash
git clone <repository-url>
cd Langgragh
```

### 2. Environment Setup

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

**Important variables to configure:**
- `GOOGLE_API_KEY` - Your Gemini API key
- `ELASTICSEARCH_URL` - Your Elasticsearch endpoint
- `ELASTICSEARCH_API_KEY` - Your Elasticsearch API key
- `MONGODB_URL` - MongoDB connection string

### 3. Start MongoDB

```bash
docker-compose up -d mongodb
```

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend
python -m app.main
```

Backend will run on: `http://localhost:8000`

### 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on: `http://localhost:5173`

## 📊 Data Ingestion

Load your admissions Q&A data into Elasticsearch:

```bash
cd backend
python scripts/ingest_data.py
```

This will:
1. Read `train.csv`
2. Generate Vietnamese embeddings
3. Index documents to Elasticsearch
4. Create necessary indexes

## 🚀 Usage

### Start All Services

```bash
# Terminal 1: Start MongoDB
docker-compose up -d

# Terminal 2: Start Backend
cd backend
python -m app.main

# Terminal 3: Start Frontend
cd frontend
npm run dev
```

### Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
Langgragh/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Configuration
│   │   ├── database/            # DB connections
│   │   │   ├── mongodb.py
│   │   │   └── elasticsearch.py
│   │   ├── models/              # Pydantic models
│   │   ├── api/                 # API routes
│   │   ├── services/            # Business logic
│   │   ├── langgraph/           # LangGraph workflows
│   │   └── utils/               # Utilities
│   ├── scripts/                 # Data ingestion scripts
│   ├── tests/                   # Unit tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── store/               # State management
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── train.csv                    # Training data
├── docker-compose.yml           # Docker services
├── .env                         # Environment variables
└── README.md
```

## 🔧 Configuration

### Elasticsearch Setup

Your Elasticsearch is configured with:
- **URL**: `https://e28a57d7f3774266a59618be9edcc050.us-gov-east-1.aws.elastic-cloud.com:443`
- **Index**: `admissions_qa`
- **Features**: Vietnamese analyzer, vector search, hybrid search

### MongoDB Setup

Collections:
- `users` - User accounts
- `conversations` - Chat history
- `feedback` - User feedback

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 API Endpoints

### Chat
- `POST /api/chat` - Send message
- `GET /api/conversations` - List conversations
- `GET /api/conversations/{id}` - Get conversation

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

### Admin
- `POST /api/admin/ingest` - Trigger data ingestion
- `GET /api/admin/stats` - Get system statistics

## 🔐 Security Notes

⚠️ **IMPORTANT**: Never commit `.env` file to version control!

Your credentials are configured in `.env`:
- Gemini API key
- Elasticsearch credentials
- JWT secret key

## 🐛 Troubleshooting

### Elasticsearch Connection Issues
```bash
# Test connection
curl -X GET "https://your-elasticsearch-url:443" \
  -H "Authorization: ApiKey your-api-key"
```

### MongoDB Connection Issues
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# View logs
docker logs admissions_mongodb
```

### Backend Issues
```bash
# Check logs
tail -f backend/logs/app.log

# Verify dependencies
pip list
```

## 📚 Documentation

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- LangChain team for amazing tools
- Elastic for search infrastructure
- Google for Gemini API

