# Quick Start Guide

Hướng dẫn nhanh để chạy toàn bộ hệ thống chatbot tư vấn tuyển sinh.

## 📋 Yêu cầu hệ thống

### Backend
- Python >= 3.11
- Conda hoặc venv
- MongoDB (local hoặc cloud)
- Elasticsearch Cloud
- OpenAI API Key

### Frontend
- Node.js >= 18.0.0
- npm >= 9.0.0

## 🚀 Cài đặt nhanh (5 phút)

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd Langgragh
```

### Bước 2: Setup Backend

```bash
# Tạo conda environment
conda create -n LGR python=3.11 -y
conda activate LGR

# Cài đặt dependencies
cd backend
pip install -r requirements.txt

# Quay lại root directory
cd ..
```

### Bước 3: Setup Frontend

```bash
cd frontend
npm install
cd ..
```

### Bước 4: Cấu hình Environment Variables

File `.env` đã được tạo sẵn ở root directory. Kiểm tra và cập nhật nếu cần:

```env
# OpenAI API Key (BẮT BUỘC)
OPENAI_API_KEY=your-api-key-here

# MongoDB (mặc định: localhost)
MONGODB_URL=mongodb://localhost:27017

# Elasticsearch Cloud (đã cấu hình sẵn)
ELASTICSEARCH_CLOUD_ID=...
ELASTICSEARCH_API_KEY=...
```

## 🎯 Chạy hệ thống

### Option 1: Chạy từng service riêng lẻ

#### Terminal 1: Backend

```bash
# Từ root directory
python run.py --mode single
```

Server backend sẽ chạy tại: **http://localhost:8000**

#### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

### Option 2: Chạy production với multi-workers

#### Backend (Production)

```bash
# Auto-calculate optimal workers
python run.py --mode prod

# Hoặc custom workers
python run.py --mode prod --workers 4
```

#### Frontend (Production)

```bash
cd frontend
npm run build
npm start
```

## 🧪 Kiểm tra hệ thống

### 1. Kiểm tra Backend Health

```bash
curl http://localhost:8000/api/health
```

Kết quả mong đợi:
```json
{
  "status": "healthy",
  "services": {
    "elasticsearch": { "status": "connected" },
    "mongodb": { "status": "connected" },
    "openai": { "status": "configured" }
  }
}
```

### 2. Test API

```bash
cd backend
python scripts/test_api.py
```

### 3. Test Concurrent Requests

```bash
cd backend
python scripts/test_concurrent.py
```

### 4. Mở Frontend

Truy cập: **http://localhost:3000**

Thử hỏi:
- "Điều kiện xét tuyển vào đại học là gì?"
- "Học phí đại học bao nhiêu?"
- "Thời gian đăng ký xét tuyển khi nào?"

## 📊 Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                        │
│  - React + TypeScript                                        │
│  - Tailwind CSS                                              │
│  - Zustand (State Management)                                │
│  Port: 3000                                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  - Python 3.11                                               │
│  - LangGraph Workflow                                        │
│  - Multi-worker support                                      │
│  Port: 8000                                                  │
└─────┬──────────────┬──────────────┬────────────────────────┘
      │              │              │
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ MongoDB  │  │Elasticsearch│  │   OpenAI    │
│  Local   │  │   Cloud    │  │ GPT-4o-mini │
└──────────┘  └──────────┘  └──────────────┘
```

## 🔄 Workflow

```
User Query
    │
    ▼
┌─────────────────────┐
│  Input Validation   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Hybrid Search      │
│  (BM25 + Vector)    │
│  Elasticsearch      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Reranking          │
│  (Cross-Encoder)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Answer Generation  │
│  (GPT-4o-mini)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Format Output      │
└──────────┬──────────┘
           │
           ▼
      Response
```

## ⚡ Performance

### Current Performance (GPT-4o-mini)

- **Response Time:** 1.5-2.5 seconds per request
- **Throughput:** 
  - Single worker: ~20 req/min
  - 4 workers: ~80 req/min
  - 8 workers: ~160 req/min
- **Cost:** $0.0008-0.0012 per request

### Bottlenecks

1. **OpenAI API:** 60-70% of total time
2. **Reranking:** 15-25% of total time
3. **Elasticsearch:** 10-15% of total time

## 🛠️ Troubleshooting

### Backend không start được

```bash
# Kiểm tra Python version
python --version  # Phải >= 3.11

# Kiểm tra dependencies
pip list | grep -E "fastapi|langgraph|openai"

# Reinstall dependencies
pip install -r backend/requirements.txt --force-reinstall
```

### Frontend không start được

```bash
# Kiểm tra Node version
node --version  # Phải >= 18.0.0

# Clear cache và reinstall
cd frontend
rm -rf node_modules .next
npm install
```

### MongoDB connection error

```bash
# Kiểm tra MongoDB có đang chạy không
# Windows:
net start MongoDB

# Linux/Mac:
sudo systemctl start mongod

# Hoặc sử dụng MongoDB Atlas (cloud)
```

### Elasticsearch connection error

```bash
# Kiểm tra credentials trong .env
ELASTICSEARCH_CLOUD_ID=...
ELASTICSEARCH_API_KEY=...

# Test connection
curl -X GET "https://your-elasticsearch-url" \
  -H "Authorization: ApiKey your-api-key"
```

### OpenAI API error

```bash
# Kiểm tra API key
echo $OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## 📚 Documentation

- **Backend:** `backend/STRUCTURE.md`
- **Frontend:** `docs/FRONTEND_GUIDE.md`
- **Performance:** `docs/PERFORMANCE_ANALYSIS.md`
- **API:** http://localhost:8000/docs (Swagger UI)

## 🎓 Next Steps

1. **Customize UI:** Edit `frontend/src/components/chat/`
2. **Add Features:** Extend `backend/app/api/routes/`
3. **Optimize Performance:** Implement caching (Redis)
4. **Deploy:** Vercel (frontend) + Railway/Render (backend)

## 💡 Tips

- **Development:** Use `--mode single` for easier debugging
- **Production:** Use `--mode prod` for better performance
- **Testing:** Run `test_concurrent.py` to verify multi-user support
- **Monitoring:** Check logs in `backend/logs/`

## 🆘 Support

Nếu gặp vấn đề, kiểm tra:
1. Logs: `backend/logs/app.log`
2. Browser console (F12)
3. Network tab (F12 → Network)
4. Backend terminal output

## 🎉 Success!

Nếu mọi thứ hoạt động:
- ✅ Backend: http://localhost:8000/docs
- ✅ Frontend: http://localhost:3000
- ✅ Health check: http://localhost:8000/api/health

Bạn đã sẵn sàng sử dụng chatbot! 🚀

