# Kiến trúc Hệ thống - Enterprise Grade

## Tổng quan

Hệ thống được xây dựng theo chuẩn **Clean Architecture** và **Enterprise Best Practices** với các nguyên tắc:

- **Separation of Concerns**: Tách biệt rõ ràng giữa các layers
- **Dependency Injection**: Sử dụng dependency injection pattern
- **Repository Pattern**: Tách biệt data access logic
- **Service Layer**: Business logic được tập trung trong service layer
- **Rate Limiting**: Bảo vệ API khỏi abuse
- **Comprehensive Logging**: Logging đầy đủ cho monitoring và debugging
- **Error Handling**: Xử lý lỗi nhất quán và thân thiện

## Cấu trúc Backend

```
backend/
├── api/                    # API Layer
│   ├── routes/            # API endpoints
│   │   ├── auth.py        # Authentication routes
│   │   ├── upload.py      # File upload routes
│   │   └── weekly_report.py # Weekly report routes
│   └── dependencies.py    # Shared dependencies
├── core/                   # Core Infrastructure
│   ├── config.py          # Configuration management
│   ├── database.py        # Database setup
│   ├── security.py        # Security utilities
│   ├── logging_config.py  # Logging setup
│   ├── exceptions.py     # Custom exceptions
│   ├── middleware.py      # Custom middleware
│   └── rate_limit.py      # Rate limiting
├── repositories/          # Data Access Layer
│   ├── user_repository.py
│   ├── timetable_repository.py
│   ├── teaching_program_repository.py
│   └── weekly_log_repository.py
├── services/              # Business Logic Layer
│   ├── auth_service.py
│   ├── excel_service.py
│   ├── weekly_report_service.py
│   └── export_service.py
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── utils/                 # Utilities
│   └── validators.py
└── main.py                # Application entry point
```

## Layers

### 1. API Layer (`api/`)
- **Responsibility**: Xử lý HTTP requests/responses, validation input
- **Dependencies**: Services, Dependencies
- **Features**:
  - Rate limiting per endpoint
  - Request validation
  - Response formatting

### 2. Service Layer (`services/`)
- **Responsibility**: Business logic, orchestration
- **Dependencies**: Repositories
- **Features**:
  - Business rules enforcement
  - Transaction management
  - Error handling

### 3. Repository Layer (`repositories/`)
- **Responsibility**: Data access, database operations
- **Dependencies**: SQLAlchemy models
- **Features**:
  - CRUD operations
  - Query optimization
  - Data mapping

### 4. Core Infrastructure (`core/`)
- **Configuration**: Centralized config management
- **Database**: Connection pooling, session management
- **Security**: Password hashing, JWT tokens
- **Logging**: Structured logging với JSON format
- **Middleware**: Request logging, error handling
- **Rate Limiting**: API protection với Redis support

## Design Patterns

### Repository Pattern
Tách biệt data access logic khỏi business logic, dễ dàng test và maintain.

### Service Pattern
Tập trung business logic trong service layer, dễ dàng reuse và test.

### Dependency Injection
Sử dụng FastAPI's Depends để inject dependencies, dễ dàng mock trong testing.

## Security Features

1. **Password Hashing**: Bcrypt với salt
2. **JWT Authentication**: Secure token-based auth
3. **Rate Limiting**: Bảo vệ API khỏi abuse
4. **Input Validation**: Pydantic schemas
5. **File Upload Validation**: Size và format checking
6. **CORS**: Configurable CORS settings

## Logging Strategy

- **Structured Logging**: JSON format cho production
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Request Logging**: Tất cả requests được log với timing
- **Error Logging**: Full stack traces cho errors

## Rate Limiting

- **Per Endpoint**: Mỗi endpoint có rate limit riêng
- **Storage**: Redis (nếu available) hoặc in-memory
- **Configurable**: Có thể config qua environment variables

## Error Handling

- **Custom Exceptions**: Domain-specific exceptions
- **Consistent Format**: Tất cả errors có format nhất quán
- **HTTP Status Codes**: Đúng status codes cho từng loại error
- **Error Messages**: User-friendly error messages

## Database

- **Connection Pooling**: Tối ưu performance
- **Transactions**: Automatic transaction management
- **Migrations**: Alembic cho database migrations

## Testing Strategy (Recommended)

1. **Unit Tests**: Test từng service/repository riêng biệt
2. **Integration Tests**: Test API endpoints
3. **E2E Tests**: Test full user flows

## Performance Optimizations

1. **Database Connection Pooling**: Reuse connections
2. **Bulk Operations**: Bulk insert cho large datasets
3. **Caching**: Redis cho frequently accessed data (future)
4. **Async Operations**: Async file processing (future)

## Monitoring & Observability

1. **Health Check Endpoint**: `/health`
2. **Request Metrics**: Process time trong response headers
3. **Structured Logs**: Dễ dàng parse và analyze
4. **Error Tracking**: Comprehensive error logging

