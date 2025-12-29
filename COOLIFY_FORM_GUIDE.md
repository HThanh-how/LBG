# Hướng dẫn Điền Form Coolify

## ⚠️ Lưu ý quan trọng

Dự án có **2 services**:
- **Backend**: Port `8000` (Python FastAPI)
- **Frontend**: Port `3000` (Next.js)

Trong Coolify, bạn cần tạo **2 applications riêng biệt**:
1. Application 1: Deploy Backend (port 8000)
2. Application 2: Deploy Frontend (port 3000) - sau khi backend đã chạy

---

## 📝 Cấu hình cho BACKEND (Application 1)

### Docker Registry Section
- **Docker Image**: Để trống (không cần push lên registry)
- **Docker Image Tag**: Để trống

### Build Section
- **Base Directory**: `/`
- **Dockerfile Location**: `/Dockerfile` hoặc `Dockerfile`
- **Docker Build Stage Target**: Để trống
- **Custom Docker Options**: Để trống (hoặc xóa hết nội dung hiện tại)
- **Use a Build Server?**: Không tích (unchecked)

### Network Section
- **Ports Exposes**: `8000` ⚠️ (bắt buộc - có dấu *)
- **Ports Mappings**: `8000:8000` (hoặc để Coolify tự động)
- **Network Aliases**: Để trống

### Environment Variables (Settings → Environment Variables)
Thêm các biến sau:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
USE_SQLITE=false
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 📝 Cấu hình cho FRONTEND (Application 2) - Sau khi backend đã chạy

### Build Section
- **Base Directory**: `/frontend`
- **Dockerfile Location**: `/Dockerfile` hoặc `Dockerfile`
- **Docker Build Stage Target**: Để trống
- **Custom Docker Options**: Để trống
- **Use a Build Server?**: Không tích

### Network Section
- **Ports Exposes**: `3000` ⚠️ (bắt buộc)
- **Ports Mappings**: `3000:3000`
- **Network Aliases**: Để trống

### Environment Variables
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

**Lưu ý**: Thay `your-backend-url.com` bằng URL thực tế của backend đã deploy trên Coolify.

---

## 🎯 Thứ tự Deploy

1. **Deploy Backend trước** (port 8000)
   - Đảm bảo backend chạy thành công
   - Lấy URL của backend (ví dụ: `https://backend.yourdomain.com`)

2. **Deploy Frontend sau** (port 3000)
   - Set `NEXT_PUBLIC_API_URL` = URL của backend
   - Frontend sẽ gọi API từ backend

---

## 🔍 Kiểm tra sau khi deploy

### Backend
- Health check: `https://your-backend-url/health`
- API docs: `https://your-backend-url/docs`

### Frontend
- Truy cập: `https://your-frontend-url`
- Kiểm tra console browser để xem có lỗi API không

