# 🚀 Các Cách Deploy Đơn Giản (Không Dùng Coolify)

## Cách 1: Deploy bằng Docker Compose trên VPS (Đơn giản nhất) ⭐

### Yêu cầu:
- VPS/Server có Docker và Docker Compose
- SSH access vào server

### Các bước:

#### 1. Clone code lên server
```bash
# SSH vào server
ssh user@your-server-ip

# Clone repository
git clone https://github.com/HThanh-how/LBG.git
cd LBG
```

#### 2. Chỉnh sửa docker-compose.yml cho production
```bash
# Tạo file docker-compose.prod.yml
nano docker-compose.prod.yml
```

#### 3. Chạy một lệnh duy nhất
```bash
docker-compose -f docker-compose.prod.yml up -d
```

**Xong!** Backend chạy ở port 8000, Frontend chạy ở port 3000.

---

## Cách 2: Deploy bằng Script Tự Động

Tạo script tự động deploy chỉ với 1 lệnh:

```bash
./deploy.sh
```

---

## Cách 3: Deploy trên Railway/Render (Đơn giản hơn Coolify)

### Railway (Railway.app)
1. Kết nối GitHub repo
2. Railway tự động detect docker-compose.yml
3. Click Deploy → Xong!

### Render (Render.com)
1. Kết nối GitHub repo
2. Chọn "Web Service"
3. Chọn docker-compose.yml
4. Deploy → Xong!

---

## Cách 4: Chỉ Deploy Backend (Đơn giản nhất cho Coolify)

Nếu vẫn muốn dùng Coolify nhưng đơn giản hơn:

1. **Chỉ deploy Backend** (bỏ qua Frontend)
2. Frontend chạy local hoặc deploy riêng sau

**Cấu hình Coolify cho Backend:**
- Base Directory: `/`
- Dockerfile Location: `Dockerfile`
- Port: `8000`
- Environment Variables: Copy từ docker-compose.yml

**Xong!** Chỉ cần điền 3 trường, không cần lo về Frontend.

