# 🚀 FastAPI Financial Data Backend

## 📖 Giới thiệu

FastAPI backend cho hệ thống dữ liệu tài chính, cung cấp API để truy xuất:

- **OHLC Data**: Dữ liệu candlestick (Open, High, Low, Close, Volume, VWAP)
- **Technical Indicators**: Chỉ báo kỹ thuật (SMA, EMA, RSI, MACD, Bollinger Bands)
- **Raw Trades**: Dữ liệu giao dịch thô từ Finnhub
- **Trading Signals**: Phân tích tín hiệu mua/bán
- **Real-time WebSocket**: Streaming dữ liệu thời gian thực

## 🛠️ Tech Stack

- **FastAPI**: Modern Python web framework
- **Cassandra**: NoSQL database cho big data
- **Pydantic**: Data validation và serialization
- **WebSocket**: Real-time data streaming
- **Docker**: Containerization

## 📁 Cấu trúc Project

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── core/
│   │   └── cassandra.py          # Database connection
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── ohlc.py          # OHLC data endpoints
│   │   │   ├── technical_indicators.py  # Technical indicators
│   │   │   └── trades.py        # Trades data endpoints
│   │   └── websocket/
│   │       └── realtime.py      # WebSocket streaming
├── requirements.txt              # Python dependencies
├── Dockerfile                   # Docker configuration
├── demo_api.py                 # API testing script
└── README.md                   # Documentation
```

## 🚀 Cách chạy

### 1. Standalone (Development)

```bash
# 1. Cài đặt dependencies
cd backend
pip install -r requirements.txt

# 2. Thiết lập environment variables
export CASSANDRA_HOSTS=localhost
export CASSANDRA_PORT=9042
export CASSANDRA_USERNAME=cassandra
export CASSANDRA_PASSWORD=cassandra

# 3. Chạy FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Truy cập API
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health check: http://localhost:8000/health
```

### 2. Docker (Production)

```bash
# Build và chạy container
docker build -t financial-api .
docker run -p 8000:8000 \
  -e CASSANDRA_HOSTS=cassandra \
  -e CASSANDRA_PORT=9042 \
  --name financial-api \
  financial-api
```

### 3. Với Docker Compose (Recommended)

```bash
# Thêm service vào docker-compose.yml của project chính
# Rồi chạy:
docker-compose up -d
```

## 📊 API Endpoints

### 🏠 Root Endpoints

- `GET /` - Thông tin API
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

### 📈 OHLC Data

- `GET /api/v1/ohlc/{symbol}` - Lấy OHLC data
- `GET /api/v1/ohlc/{symbol}/latest` - OHLC data mới nhất
- `GET /api/v1/ohlc/{symbol}/timeframe/{timeframe}` - OHLC theo timeframe

### 📊 Technical Indicators

- `GET /api/v1/indicators/{symbol}` - Chỉ báo kỹ thuật
- `GET /api/v1/indicators/{symbol}/latest` - Indicators mới nhất
- `GET /api/v1/indicators/{symbol}/signals` - Tín hiệu giao dịch

### 💰 Trades Data

- `GET /api/v1/trades/{symbol}` - Dữ liệu giao dịch
- `GET /api/v1/trades/{symbol}/latest` - Giao dịch mới nhất

### 🌐 WebSocket

- `WS /ws/{symbol}` - Real-time price streaming

## 🔧 Query Parameters

### Tham số chung:

- `start_date`: Ngày bắt đầu (YYYY-MM-DD)
- `end_date`: Ngày kết thúc (YYYY-MM-DD)
- `limit`: Số lượng records (max: 1000)

### Ví dụ:

```
GET /api/v1/ohlc/AAPL?start_date=2024-01-01&end_date=2024-01-07&limit=100
```

## 📱 Sử dụng API

### 1. Python Example

```python
import requests

# Lấy OHLC data
response = requests.get("http://localhost:8000/api/v1/ohlc/AAPL")
data = response.json()
print(data)

# Lấy trading signals
signals = requests.get("http://localhost:8000/api/v1/indicators/AAPL/signals")
print(signals.json())
```

### 2. JavaScript/WebSocket Example

```javascript
// Kết nối WebSocket
const ws = new WebSocket("ws://localhost:8000/ws/AAPL");

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("Real-time update:", data);

  if (data.type === "price_update") {
    console.log("Price:", data.data.price);
    console.log("Volume:", data.data.volume);
  }
};

ws.onopen = function () {
  console.log("Connected to AAPL stream");
};
```

### 3. cURL Examples

```bash
# Health check
curl http://localhost:8000/health

# Lấy OHLC data cho AAPL
curl "http://localhost:8000/api/v1/ohlc/AAPL?limit=10"

# Lấy technical indicators
curl http://localhost:8000/api/v1/indicators/AAPL/latest

# Lấy trading signals
curl http://localhost:8000/api/v1/indicators/AAPL/signals
```

## 🧪 Testing

### Chạy Demo Script

```bash
# Cài đặt dependencies cho demo
pip install requests websockets

# Chạy demo
python demo_api.py
```

Demo script sẽ test tất cả endpoints và WebSocket streaming.

### Test với Postman

Import API collection từ Swagger UI:

1. Mở http://localhost:8000/docs
2. Click "Download" để lấy OpenAPI spec
3. Import vào Postman

## 🐛 Troubleshooting

### Lỗi Connection tới Cassandra

```bash
# Kiểm tra Cassandra service
docker-compose ps cassandra

# Xem logs
docker-compose logs cassandra

# Test connection
cqlsh localhost 9042 -u cassandra -p cassandra
```

### Lỗi Port đã sử dụng

```bash
# Tìm process đang dùng port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Empty

```bash
# Kiểm tra data trong Cassandra
docker-compose exec cassandra cqlsh -e "SELECT COUNT(*) FROM finnhub.trades;"

# Restart producer nếu cần
docker-compose restart finnhub-producer
```

## 🔍 Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "cassandra": "connected",
    "api": "running"
  }
}
```

### Logs

```bash
# Xem logs của FastAPI
docker-compose logs financial-api

# Follow logs real-time
docker-compose logs -f financial-api
```

## 🚀 Performance

### Typical Response Times:

- **OHLC data (100 records)**: ~50-100ms
- **Technical indicators**: ~30-70ms
- **Trading signals**: ~40-80ms
- **WebSocket latency**: ~10-30ms

### Scaling:

- API hỗ trợ concurrent requests
- Cassandra auto-scale với cluster
- WebSocket connections được manage hiệu quả

## 📝 Environment Variables

```bash
# Cassandra connection
CASSANDRA_HOSTS=localhost        # Cassandra host(s)
CASSANDRA_PORT=9042             # Cassandra port
CASSANDRA_USERNAME=cassandra    # Username
CASSANDRA_PASSWORD=cassandra    # Password

# API settings
API_HOST=0.0.0.0               # API host
API_PORT=8000                  # API port
LOG_LEVEL=INFO                 # Logging level
```

## 🎯 Next Steps

1. **Authentication**: Thêm JWT authentication
2. **Rate Limiting**: Implement rate limiting
3. **Caching**: Add Redis caching layer
4. **Monitoring**: Setup Prometheus metrics
5. **Testing**: Add unit tests và integration tests

## 📞 Support

Nếu gặp vấn đề, hãy kiểm tra:

1. Cassandra database đã có data chưa
2. All services trong docker-compose đã running
3. Network connectivity giữa services
4. Logs của từng service

Happy coding! 🎉
