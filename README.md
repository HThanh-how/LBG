# Hệ thống Quản lý Lịch Báo Giảng

Hệ thống web quản lý lịch báo giảng cho giáo viên với khả năng upload TKB/CTGD từ Excel và chỉnh sửa linh hoạt như Excel.

## 🎯 Tính năng chính

- ✅ **Đăng ký/Đăng nhập** - Quản lý nhiều người dùng riêng biệt
- ✅ **Upload Excel TKB** - Tải lên thời khóa biểu từ file Excel
- ✅ **Upload Excel CTGD** - Tải lên chương trình giảng dạy cả năm
- ✅ **Tự động khớp dữ liệu** - Hệ thống tự động điền bài dạy dựa trên TKB và CTGD
- ✅ **Chỉnh sửa trực tiếp** - Click vào ô để sửa như Excel
- ✅ **Xuất PDF/Excel** - Tải về file báo giảng theo mẫu chuẩn
- ✅ **Quản lý theo tuần** - Xem và chỉnh sửa báo giảng từng tuần

## 🏗️ Kiến trúc

- **Frontend**: Next.js 14 + React + Tailwind CSS + TanStack Table
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **File Processing**: Pandas, Openpyxl
- **Export**: XlsxWriter, ReportLab

## 📁 Cấu trúc dự án

```
LBG/
├── backend/              # FastAPI backend
│   ├── main.py           # API endpoints
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # Authentication logic
│   ├── excel_processor.py # Excel processing
│   ├── export_service.py # PDF/Excel export
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js frontend
│   ├── app/              # Next.js app directory
│   ├── components/       # React components
│   ├── lib/              # Utilities & API client
│   └── package.json      # Node dependencies
├── docker-compose.yml    # Docker orchestration
├── INSTALLATION.md       # Hướng dẫn cài đặt chi tiết
├── TEMPLATE_TKB.md       # Hướng dẫn tạo file TKB
├── TEMPLATE_CTGD.md      # Hướng dẫn tạo file CTGD
└── README.md             # File này
```

## 🚀 Cài đặt nhanh

### Cách 1: Chạy không cần Database (SQLite - Khuyến nghị cho development)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (terminal khác)
cd frontend
npm install
npm run dev
```

Hệ thống sẽ tự động tạo file SQLite (`lbg.db`) và sẵn sàng sử dụng!

Xem [QUICK_START.md](./QUICK_START.md) để biết chi tiết.

### Cách 2: Sử dụng Docker với PostgreSQL

```bash
# Khởi động tất cả services
docker-compose up -d

# Truy cập ứng dụng
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

Xem [INSTALLATION.md](./INSTALLATION.md) để biết hướng dẫn chi tiết.

## 📖 Hướng dẫn sử dụng

1. **Đăng ký tài khoản** - Tạo tài khoản mới hoặc đăng nhập
2. **Upload TKB** - Tải file Excel thời khóa biểu (xem [TEMPLATE_TKB.md](./TEMPLATE_TKB.md))
3. **Upload CTGD** - Tải file Excel chương trình giảng dạy (xem [TEMPLATE_CTGD.md](./TEMPLATE_CTGD.md))
4. **Chọn tuần** - Chọn tuần cần xem/chỉnh sửa
5. **Chỉnh sửa** - Click vào ô để sửa trực tiếp
6. **Lưu** - Nhấn "Lưu thay đổi" để lưu
7. **Xuất file** - Nhấn "Xuất PDF" hoặc "Xuất Excel"

## 🔧 Development

Xem [INSTALLATION.md](./INSTALLATION.md) để biết cách setup môi trường development.

## 📝 License

Dự án này được phát triển cho mục đích giáo dục.

