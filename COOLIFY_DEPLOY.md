# Hướng dẫn Deploy lên Coolify

## Vấn đề thường gặp

Coolify sử dụng Nixpacks để tự động detect loại ứng dụng. Với monorepo có cả backend (Python) và frontend (Node.js), Nixpacks không thể tự động detect được.

## Giải pháp

### Cách 1: Deploy Backend (Khuyến nghị)

1. **Trong Coolify, chọn Build Pack**: Chọn "Dockerfile" thay vì "Nixpacks"
2. **Dockerfile Path**: Để mặc định là `Dockerfile` (file ở root)
3. **Port**: Đặt port là `8000`
4. **Environment Variables**:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   USE_SQLITE=false
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Cách 2: Deploy với Nixpacks (Backend)

1. **Trong Coolify, chọn Build Pack**: Chọn "Nixpacks"
2. **Root Directory**: Để mặc định hoặc set là `/`
3. **Port**: Đặt port là `8000`
4. File `nixpacks.toml` sẽ được sử dụng tự động

### Cách 3: Deploy Frontend riêng

Nếu muốn deploy frontend, cần tạo application riêng:

1. **Tạo application mới trong Coolify**
2. **Build Pack**: Chọn "Dockerfile"
3. **Dockerfile Path**: `frontend/Dockerfile`
4. **Root Directory**: `frontend/`
5. **Port**: `3000`
6. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```

## Cấu hình Database

### Option 1: Sử dụng PostgreSQL từ Coolify

1. Tạo PostgreSQL service trong Coolify
2. Lấy connection string và set vào `DATABASE_URL`
3. Set `USE_SQLITE=false`

### Option 2: Sử dụng SQLite (không khuyến nghị cho production)

1. Set `USE_SQLITE=true`
2. Set `SQLITE_DB_PATH=/app/data/lbg.db`
3. Đảm bảo có volume mount cho `/app/data`

## Lưu ý quan trọng

1. **Port**: Coolify sẽ tự động set biến môi trường `PORT`. Nếu backend không đọc từ `PORT`, có thể cần chỉnh sửa Dockerfile để sử dụng `$PORT` thay vì hardcode `8000`.

2. **CORS**: Đảm bảo backend cho phép CORS từ domain của frontend. Kiểm tra file `backend/main.py` để cấu hình CORS.

3. **Volumes**: Nếu cần lưu trữ file exports, cần cấu hình volumes trong Coolify.

4. **Health Check**: Coolify sẽ tự động tạo health check endpoint. Backend đã có endpoint `/health` sẵn.

## Troubleshooting

### Lỗi: "Nixpacks failed to detect the application type"

**Nguyên nhân**: Nixpacks không thể detect được loại ứng dụng trong monorepo.

**Giải pháp**: 
- Chọn "Dockerfile" thay vì "Nixpacks" trong Coolify
- Hoặc tạo file `nixpacks.toml` ở root (đã có sẵn)

### Lỗi: "Port already in use"

**Nguyên nhân**: Port đã được sử dụng.

**Giải pháp**: 
- Đổi port trong Coolify settings
- Hoặc chỉnh sửa Dockerfile để sử dụng biến môi trường `PORT`

### Lỗi: "Cannot connect to database"

**Nguyên nhân**: Database connection string không đúng hoặc database chưa sẵn sàng.

**Giải pháp**: 
- Kiểm tra `DATABASE_URL` trong environment variables
- Đảm bảo PostgreSQL service đã chạy và accessible
- Kiểm tra network connectivity giữa services

