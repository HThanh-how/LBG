# Hướng dẫn Deploy lên Coolify

## Vấn đề thường gặp

Coolify sử dụng Nixpacks để tự động detect loại ứng dụng. Với monorepo có cả backend (Python) và frontend (Node.js), Nixpacks không thể tự động detect được.

## ⚠️ QUAN TRỌNG: Dự án có 2 Port

Dự án có **2 services riêng biệt**:
- **Backend**: Port `8000` (Python FastAPI) 
- **Frontend**: Port `3000` (Next.js)

Bạn cần tạo **2 applications riêng** trong Coolify:
1. **Application 1**: Deploy Backend (port 8000)
2. **Application 2**: Deploy Frontend (port 3000) - sau khi backend đã chạy

Xem file [COOLIFY_FORM_GUIDE.md](./COOLIFY_FORM_GUIDE.md) để biết cách điền form chi tiết.

## Cấu hình Repository trong Coolify

### Bước 1: Commit và Push code lên GitHub

Trước tiên, bạn cần commit các file mới và push lên repository:

```bash
# Kiểm tra các file đã thay đổi
git status

# Thêm các file mới
git add Dockerfile nixpacks.toml .dockerignore COOLIFY_DEPLOY.md

# Commit
git commit -m "Add Coolify deployment configuration"

# Push lên GitHub
git push origin main
```

### Bước 2: Cấu hình Repository trong Coolify

1. **Vào ứng dụng của bạn trong Coolify**
2. **Settings → Source**: 
   - **Repository**: `HThanh-how/LBG` (hoặc URL đầy đủ của repository)
   - **Branch**: `main`
   - **Build Pack**: Chọn **"Dockerfile"** (không chọn Nixpacks)
   - **Dockerfile Path**: `Dockerfile` (để mặc định)
   - **Root Directory**: `/` (để mặc định)

### Bước 3: Trigger Deployment

Coolify có 2 cách để pull và deploy code:

#### Cách 1: Tự động (Auto Deploy)
- Coolify sẽ tự động pull và deploy khi có commit mới lên branch `main`
- Đảm bảo trong Settings → Source → **Auto Deploy** đã được bật

#### Cách 2: Manual (Thủ công)
- Vào trang ứng dụng trong Coolify
- Click nút **"Deploy"** hoặc **"Redeploy"**
- Coolify sẽ tự động pull code mới nhất từ repository và build lại

### Bước 4: Kiểm tra Deployment Logs

Sau khi trigger deployment, bạn có thể xem logs trong Coolify để theo dõi quá trình:
- Build logs: Xem quá trình build Docker image
- Runtime logs: Xem logs khi ứng dụng chạy

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

