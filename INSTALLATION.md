# Hướng dẫn Cài đặt và Chạy Hệ thống

## Yêu cầu hệ thống

- Docker và Docker Compose (khuyến nghị)
- Hoặc:
  - Python 3.11+
  - Node.js 20+
  - PostgreSQL 15+

## Cách 1: Chạy bằng Docker (Khuyến nghị)

### Bước 1: Clone hoặc tải dự án

```bash
cd /Users/huythanh/Code/LBG
```

### Bước 2: Khởi động các service

```bash
docker-compose up -d
```

Lệnh này sẽ tự động:
- Tạo và khởi động PostgreSQL database
- Build và chạy Backend API (port 8000)
- Build và chạy Frontend (port 3000)

### Bước 3: Truy cập ứng dụng

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Bước 4: Dừng các service

```bash
docker-compose down
```

## Cách 2: Chạy thủ công (Development)

### Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env từ .env.example
cp .env.example .env

# Chỉnh sửa .env với thông tin database của bạn

# Khởi động PostgreSQL (nếu chưa có)
# Hoặc sử dụng Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Chạy server
uvicorn main:app --reload
```

Backend sẽ chạy tại: http://localhost:8000

### Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install

# Tạo file .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Chạy development server
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

## Sử dụng lần đầu

1. Truy cập http://localhost:3000
2. Đăng ký tài khoản mới
3. Đăng nhập
4. Upload file Excel TKB (xem TEMPLATE_TKB.md)
5. Upload file Excel CTGD (xem TEMPLATE_CTGD.md)
6. Chọn tuần và xem bảng báo giảng tự động
7. Chỉnh sửa trực tiếp trên bảng nếu cần
8. Xuất PDF hoặc Excel

## Troubleshooting

### Lỗi kết nối database

- Kiểm tra PostgreSQL đã chạy chưa
- Kiểm tra DATABASE_URL trong file .env
- Đảm bảo database `lbg_db` đã được tạo

### Lỗi CORS

- Kiểm tra CORS settings trong `backend/main.py`
- Đảm bảo frontend URL được thêm vào `allow_origins`

### Lỗi upload file

- Kiểm tra định dạng file (.xlsx hoặc .xls)
- Kiểm tra cấu trúc file theo template
- Xem logs trong backend console


