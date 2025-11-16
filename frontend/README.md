# Admissions Counseling Chatbot - Frontend

Giao diện chatbot tư vấn tuyển sinh đại học sử dụng React + Next.js 14.

## 🚀 Tính năng

- ✅ **Giao diện chat hiện đại** - UI/UX đẹp mắt, responsive
- ✅ **Real-time messaging** - Gửi và nhận tin nhắn ngay lập tức
- ✅ **Markdown support** - Hiển thị định dạng văn bản phong phú
- ✅ **Typing indicators** - Hiển thị trạng thái đang trả lời
- ✅ **Message history** - Lưu trữ lịch sử trò chuyện
- ✅ **Source references** - Hiển thị nguồn tham khảo
- ✅ **Dark mode ready** - Hỗ trợ chế độ tối
- ✅ **Vietnamese optimized** - Tối ưu cho tiếng Việt
- ✅ **TypeScript** - Type-safe development
- ✅ **State management** - Zustand với persistence

## 🛠️ Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **HTTP Client:** Axios
- **Markdown:** react-markdown
- **Icons:** Lucide React

## 📦 Installation

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Backend API running on http://localhost:8000

### Install Dependencies

```bash
cd frontend
npm install
```

## 🚀 Development

### Start Development Server

```bash
npm run dev
```

Server sẽ chạy tại: http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

### Type Check

```bash
npm run type-check
```

### Lint

```bash
npm run lint
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   └── chat/              # Chat components
│   │       ├── ChatInterface.tsx   # Main chat interface
│   │       ├── ChatMessage.tsx     # Message component
│   │       └── ChatInput.tsx       # Input component
│   ├── lib/                   # Utilities
│   │   └── api.ts            # API client
│   └── store/                 # State management
│       └── chatStore.ts      # Chat store (Zustand)
├── public/                    # Static files
├── package.json              # Dependencies
├── tsconfig.json            # TypeScript config
├── tailwind.config.ts       # Tailwind config
├── next.config.js           # Next.js config
└── .env.local              # Environment variables
```

## 🔧 Configuration

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Tư vấn tuyển sinh
NEXT_PUBLIC_APP_DESCRIPTION=Chatbot tư vấn tuyển sinh đại học thông minh
```

### API Integration

API client được cấu hình trong `src/lib/api.ts`:

- Base URL: `http://localhost:8000`
- Timeout: 60 seconds
- Auto-retry on failure
- Token authentication support

## 🎨 Customization

### Colors

Edit `tailwind.config.ts` để thay đổi màu sắc:

```typescript
colors: {
  primary: {
    500: '#0ea5e9',  // Main color
    600: '#0284c7',  // Hover color
    // ...
  },
}
```

### Suggested Questions

Edit `src/components/chat/ChatInterface.tsx`:

```typescript
const SUGGESTED_QUESTIONS = [
  'Điều kiện xét tuyển vào đại học là gì?',
  'Học phí đại học bao nhiêu?',
  // Add more...
]
```

## 📱 Features

### Chat Interface

- **Message Display:** User và assistant messages với avatar
- **Markdown Rendering:** Hỗ trợ bold, italic, lists, code blocks, tables
- **Copy to Clipboard:** Copy nội dung tin nhắn
- **Source References:** Hiển thị nguồn tham khảo từ backend
- **Metadata:** Hiển thị thời gian xử lý và token usage

### Input

- **Auto-resize:** Textarea tự động điều chỉnh chiều cao
- **Keyboard Shortcuts:**
  - `Enter`: Gửi tin nhắn
  - `Shift + Enter`: Xuống dòng
- **Loading State:** Disable input khi đang xử lý

### State Management

- **Persistent Storage:** Lưu conversation ID và user ID
- **Message History:** Lưu trữ toàn bộ lịch sử chat
- **Error Handling:** Xử lý lỗi và hiển thị thông báo

## 🔌 API Endpoints

### Chat API

```typescript
// Send query
POST /api/chat/query
{
  "query": "Điều kiện xét tuyển là gì?",
  "conversation_id": "optional",
  "user_id": "optional"
}

// Get history
GET /api/chat/history/{conversation_id}

// Submit feedback
POST /api/chat/feedback
{
  "conversation_id": "...",
  "message_id": "...",
  "rating": 5,
  "comment": "optional"
}
```

### Health Check

```typescript
GET /api/health
```

## 🐛 Troubleshooting

### Cannot connect to backend

```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Start backend
cd ../backend
python run.py --mode single
```

### Port 3000 already in use

```bash
# Use different port
PORT=3001 npm run dev
```

### TypeScript errors

```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
```

## 📝 Development Tips

1. **Hot Reload:** Code changes auto-reload in development
2. **Console Logs:** Check browser console for errors
3. **Network Tab:** Monitor API calls in DevTools
4. **React DevTools:** Install for component debugging
5. **Zustand DevTools:** Use Redux DevTools for state inspection

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t chatbot-frontend .

# Run container
docker run -p 3000:3000 chatbot-frontend
```

### Static Export

```bash
# Build static files
npm run build

# Files in .next/static/
```

## 📄 License

MIT

## 👥 Contributors

- Your Name

## 🙏 Acknowledgments

- Next.js team
- Tailwind CSS
- Zustand
- React Markdown

