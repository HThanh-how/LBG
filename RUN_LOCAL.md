# Hướng dẫn Chạy Local

## ✅ Backend đã chạy thành công!

Backend đang chạy tại: **http://127.0.0.1:8000**

### Kiểm tra Backend:

```bash
# Health check
curl http://127.0.0.1:8000/health

# API Documentation
open http://127.0.0.1:8000/docs
```

### Dừng Backend:

```bash
pkill -f "uvicorn main:app"
```

## 🚀 Chạy Frontend

### Yêu cầu:
- Node.js 18+ và npm

### Cài đặt và chạy:

```bash
cd frontend
npm install
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

## 📝 Lưu ý

1. **Backend đang dùng SQLite** (file `lbg.db` tự động tạo)
2. **Không cần PostgreSQL** để chạy local
3. **API Base URL**: `http://127.0.0.1:8000/api/v1`
4. **Frontend cần Node.js** - nếu chưa có, cài từ https://nodejs.org

## 🔍 Kiểm tra nhanh

```bash
# Backend health
curl http://127.0.0.1:8000/health

# API root
curl http://127.0.0.1:8000/

# API docs (mở trong browser)
open http://127.0.0.1:8000/docs
```


