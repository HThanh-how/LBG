# Quick Start - Chạy không cần Database

Hệ thống có thể chạy ngay mà **không cần cài đặt PostgreSQL** bằng cách sử dụng SQLite.

## Cách 1: Chạy với SQLite (Khuyến nghị cho development)

### Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server (sẽ tự động tạo file lbg.db)
uvicorn main:app --reload
```

Backend sẽ tự động:
- Tạo file `lbg.db` (SQLite database) nếu chưa có
- Tạo các bảng cần thiết
- Sẵn sàng sử dụng ngay!

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Truy cập: http://localhost:3000

## Cách 2: Chạy với Docker (không cần PostgreSQL)

```bash
# Chỉ chạy backend và frontend, không cần PostgreSQL
docker-compose up backend frontend
```

Hoặc chỉnh sửa `docker-compose.yml` để comment out service `db`:

```yaml
# db:
#   image: postgres:15-alpine
#   ...
```

## Cách 3: Sử dụng PostgreSQL (Production)

Nếu muốn dùng PostgreSQL, chỉ cần set environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/lbg_db"
export USE_SQLITE=false
```

Hoặc trong file `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/lbg_db
USE_SQLITE=false
```

## Cấu hình Database

Hệ thống tự động chọn database theo thứ tự:

1. **Nếu có `DATABASE_URL`**: Sử dụng PostgreSQL/MySQL/etc từ URL
2. **Nếu không có `DATABASE_URL` và `USE_SQLITE=true`**: Sử dụng SQLite
3. **SQLite file location**: Mặc định là `lbg.db` trong thư mục backend

### Thay đổi vị trí SQLite file

```bash
export SQLITE_DB_PATH="./data/lbg.db"
```

Hoặc trong `.env`:

```env
SQLITE_DB_PATH=./data/lbg.db
```

## Lưu ý

- **SQLite**: Phù hợp cho development, testing, và single-user production
- **PostgreSQL**: Khuyến nghị cho production với nhiều users
- File SQLite (`lbg.db`) sẽ được tạo tự động khi chạy lần đầu
- Database schema sẽ được tạo tự động khi start server

## Troubleshooting

### Lỗi: "Database locked"
- Đảm bảo chỉ có một instance của backend đang chạy
- Kiểm tra file `lbg.db` không bị lock

### Lỗi: "Permission denied"
- Kiểm tra quyền ghi trong thư mục chứa `lbg.db`
- Thử chạy với quyền admin hoặc thay đổi `SQLITE_DB_PATH`

### Muốn reset database
- Xóa file `lbg.db`
- Restart server, database sẽ được tạo lại


