# Hướng dẫn Cài đặt và Chạy Frontend

## Vấn đề: Node.js chưa được cài đặt

Frontend cần Node.js để chạy. Dưới đây là các cách cài đặt:

## Cách 1: Cài Node.js trực tiếp (Khuyến nghị)

### macOS:

1. **Tải Node.js từ website chính thức:**
   - Truy cập: https://nodejs.org/
   - Tải bản LTS (Long Term Support)
   - Cài đặt file .pkg

2. **Hoặc dùng Homebrew:**
   ```bash
   brew install node
   ```

### Kiểm tra sau khi cài:
```bash
node --version
npm --version
```

## Cách 2: Dùng nvm (Node Version Manager)

```bash
# Cài nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Restart terminal hoặc chạy:
source ~/.zshrc

# Cài Node.js
nvm install --lts
nvm use --lts
```

## Sau khi cài Node.js:

```bash
cd frontend
npm install
npm run dev
```

Frontend sẽ chạy tại: **http://localhost:3000**

## Lưu ý:

- Cần Node.js version 18+ hoặc 20+
- Backend đang chạy tại http://127.0.0.1:8000
- Frontend sẽ tự động kết nối với backend

## Troubleshooting:

### Lỗi: "command not found: node"
→ Node.js chưa được cài hoặc chưa có trong PATH

### Lỗi: "Port 3000 already in use"
```bash
# Tìm và kill process
lsof -ti:3000 | xargs kill -9
```

### Lỗi khi npm install
```bash
# Xóa node_modules và cài lại
rm -rf node_modules package-lock.json
npm install
```

