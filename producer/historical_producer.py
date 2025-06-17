import os
import json
import time
import random
import datetime
import finnhub
import pandas as pd
import numpy as np
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HistoricalDataProducer:
    def __init__(self):
        # Khởi tạo Finnhub client
        self.api_token = os.getenv('FINNHUB_API_TOKEN')
        print(f"Initializing with Finnhub API token: {self.api_token[:5]}...{self.api_token[-5:]}")
        self.finnhub_client = finnhub.Client(api_key=self.api_token)
        
        # Khởi tạo Kafka producer
        kafka_server = os.getenv('KAFKA_SERVER', 'kafka')
        kafka_port = os.getenv('KAFKA_PORT', '29092')
        self.kafka_topic = os.getenv('KAFKA_TOPIC_NAME', 'finnhub_trades')
        print(f"Connecting to Kafka at {kafka_server}:{kafka_port}")
        self.producer = KafkaProducer(
            bootstrap_servers=f"{kafka_server}:{kafka_port}",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Kafka producer initialized successfully")
        
        # Lấy danh sách tickers từ biến môi trường
        self.tickers = json.loads(os.getenv('FINNHUB_STOCKS_TICKERS', '["AAPL", "MSFT", "GOOGL"]'))
        print(f"Configured to simulate data for tickers: {self.tickers}")
        
        # Cấu hình cho dữ liệu lịch sử
        self.resolution = os.getenv('HISTORICAL_RESOLUTION', '1')  # 1 minute candles
        self.days_back = int(os.getenv('HISTORICAL_DAYS_BACK', '7'))  # 7 days of data
        self.speed_factor = float(os.getenv('SIMULATION_SPEED', '1000'))  # 1000x speed (1 day in ~1.5 minutes)
        self.trades_per_candle = int(os.getenv('TRADES_PER_CANDLE', '5'))  # Số giao dịch mô phỏng cho mỗi nến
        
        # Các biến đếm
        self.message_count = 0
        self.last_status_time = time.time()
        
        # Dữ liệu lịch sử cho mỗi ticker
        self.historical_data = {}
        
    def fetch_historical_data(self):
        """Lấy dữ liệu lịch sử cho mỗi mã chứng khoán"""
        end_timestamp = int(time.time())
        start_timestamp = end_timestamp - (self.days_back * 24 * 60 * 60)
        
        for ticker in self.tickers:
            try:
                print(f"Fetching historical data for {ticker}...")
                candles = self.finnhub_client.stock_candles(
                    symbol=ticker,
                    resolution=self.resolution,
                    _from=start_timestamp,
                    to=end_timestamp
                )
                
                if candles['s'] == 'ok' and len(candles['t']) > 0:
                    # Convert to pandas DataFrame for easier manipulation
                    df = pd.DataFrame({
                        'timestamp': candles['t'],
                        'open': candles['o'],
                        'high': candles['h'],
                        'low': candles['l'],
                        'close': candles['c'],
                        'volume': candles['v']
                    })
                    
                    self.historical_data[ticker] = df
                    print(f"Successfully fetched {len(df)} candles for {ticker}")
                else:
                    print(f"No data returned for {ticker} or error in response")
            except Exception as e:
                print(f"Error fetching data for {ticker}: {e}")
                
        # Check if we have any data
        if not self.historical_data:
            raise Exception("No historical data could be fetched for any ticker!")
            
        print(f"Fetched historical data for {len(self.historical_data)} tickers")
        
    def generate_trades_from_candle(self, ticker, candle_data):
        """Tạo giao dịch giả từ dữ liệu nến"""
        timestamp = candle_data['timestamp']
        open_price = candle_data['open']
        close_price = candle_data['close']
        high_price = candle_data['high']
        low_price = candle_data['low']
        volume = candle_data['volume']
        
        # Chia khối lượng thành nhiều giao dịch
        trade_volume_parts = np.random.dirichlet(np.ones(self.trades_per_candle), size=1)[0]
        trade_volumes = [int(volume * part) for part in trade_volume_parts]
        
        # Tính thời gian cho mỗi giao dịch (phân bố đều trong khoảng thời gian của nến)
        minute_start = timestamp
        minute_end = timestamp + 60  # Nến 1 phút
        trade_timestamps = sorted([random.randint(minute_start, minute_end) for _ in range(self.trades_per_candle)])
        
        # Tính giá cho mỗi giao dịch (kết hợp giữa open và close, có yếu tố ngẫu nhiên)
        if open_price <= close_price:  # Nến tăng
            price_range = np.linspace(open_price, close_price, self.trades_per_candle)
            # Thêm yếu tố ngẫu nhiên, có thể vượt qua high hoặc thấp hơn low
            trade_prices = [min(high_price, max(low_price, p + random.uniform(-0.5, 0.5))) for p in price_range]
        else:  # Nến giảm
            price_range = np.linspace(open_price, close_price, self.trades_per_candle)
            # Thêm yếu tố ngẫu nhiên, có thể vượt qua high hoặc thấp hơn low
            trade_prices = [min(high_price, max(low_price, p + random.uniform(-0.5, 0.5))) for p in price_range]
        
        # Tạo danh sách giao dịch
        trades = []
        for i in range(self.trades_per_candle):
            # Tạo điều kiện giao dịch
            conditions = ["@", "T"]
            if random.random() > 0.7:
                conditions.append("I")  # Thêm điều kiện I (ISO) cho 30% giao dịch
                
            trade = {
                "c": conditions,
                "p": round(trade_prices[i], 2),  # Làm tròn giá đến 2 chữ số thập phân
                "s": ticker,
                "t": trade_timestamps[i] * 1000,  # convert to milliseconds
                "v": max(1, trade_volumes[i])  # Đảm bảo khối lượng tối thiểu là 1
            }
            trades.append(trade)
            
        return trades
        
    def simulate_realtime_stream(self):
        """Giả lập dữ liệu thời gian thực từ dữ liệu lịch sử"""
        print(f"Starting data replay at {self.speed_factor}x speed...")
        print(f"Processing approximately {self.trades_per_candle} trades per candle")
        
        # Tạo danh sách tất cả nến từ tất cả ticker và sắp xếp theo thời gian
        all_candles = []
        for ticker, df in self.historical_data.items():
            for _, row in df.iterrows():
                all_candles.append({
                    'ticker': ticker,
                    'timestamp': row['timestamp'],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume']
                })
        
        # Sắp xếp theo thời gian
        all_candles = sorted(all_candles, key=lambda x: x['timestamp'])
        
        if not all_candles:
            print("No candles to process!")
            return
            
        print(f"Total candles to process: {len(all_candles)}")
        
        # Thời gian bắt đầu mô phỏng
        sim_start_time = time.time()
        data_start_time = all_candles[0]['timestamp']
        
        for i, candle in enumerate(all_candles):
            # Tính thời gian đã trôi qua trong dữ liệu
            data_elapsed = candle['timestamp'] - data_start_time
            
            # Tính thời gian nên trôi qua trong mô phỏng
            sim_elapsed = data_elapsed / self.speed_factor
            
            # Thời gian nên chờ
            target_sim_time = sim_start_time + sim_elapsed
            current_time = time.time()
            
            # Nếu chưa đến thời gian, chờ
            if current_time < target_sim_time:
                time.sleep(target_sim_time - current_time)
            
            # Tạo giao dịch từ nến
            ticker = candle['ticker']
            trades = self.generate_trades_from_candle(ticker, candle)
            
            # Gửi giao dịch tới Kafka
            self.send_trades_to_kafka(trades)
            
            # Hiển thị trạng thái
            if i % 100 == 0 or time.time() - self.last_status_time > 10:
                print(f"Progress: {i+1}/{len(all_candles)} candles processed "
                      f"({((i+1)/len(all_candles))*100:.1f}%)")
                print(f"Currently at: {datetime.datetime.fromtimestamp(candle['timestamp'])}")
                self.last_status_time = time.time()
                
        print("Data processing completed!")
            
    def send_trades_to_kafka(self, trades):
        """Gửi giao dịch tới Kafka"""
        if not trades:
            return
            
        # Tạo message theo định dạng Finnhub WebSocket
        message = {
            "type": "trade",
            "data": trades
        }
        
        # Gửi tới Kafka
        self.producer.send(self.kafka_topic, message)
        self.message_count += 1
        
        # Hiển thị thông tin giao dịch
        if len(trades) > 0:
            sample_trade = trades[0]
            print(f"Sent {len(trades)} trades for {sample_trade['s']} at "
                  f"{datetime.datetime.fromtimestamp(sample_trade['t']/1000)}")
    
    def run(self):
        """Chạy producer dữ liệu lịch sử"""
        try:
            print("Fetching historical data...")
            self.fetch_historical_data()
            
            print("Starting data processing...")
            self.simulate_realtime_stream()
            
        except KeyboardInterrupt:
            print("\nData processing interrupted by user.")
        except Exception as e:
            print(f"Error in data processing: {e}")
        finally:
            print(f"Data processing ended. Sent {self.message_count} messages to Kafka.")
            

if __name__ == "__main__":
    print("\n=== HISTORICAL DATA PRODUCER STARTING ===\n")
    producer = HistoricalDataProducer()
    producer.run() 