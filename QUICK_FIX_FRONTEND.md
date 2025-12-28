# Quick Fix: Chạy Frontend

## Vấn đề hiện tại:
- Node.js chưa được cài đặt
- Frontend không thể chạy

## Giải pháp nhanh:

### Bước 1: Cài Node.js

**Option A - Tải trực tiếp (Dễ nhất):**
1. Mở browser, vào: https://nodejs.org/
2. Click "Download" (bản LTS)
3. Cài đặt file .pkg
4. Mở Terminal mới và chạy:
   ```bash
   node --version
   ```

**Option B - Dùng Homebrew:**
```bash
brew install node
```

### Bước 2: Cài dependencies và chạy

```bash
cd /Users/huythanh/Code/LBG/frontend
npm install
npm run dev
```

### Bước 3: Truy cập

Mở browser: **http://localhost:3000**

## Tạm thời chỉ dùng Backend:

Nếu chưa muốn cài Node.js ngay, bạn có thể:
- Test API trực tiếp tại: http://127.0.0.1:8000/docs
- Upload file và xuất PDF/Excel qua API

## Kiểm tra Backend:

```bash
curl http://127.0.0.1:8000/health
```

Backend đang chạy OK! Chỉ cần cài Node.js để chạy frontend.

