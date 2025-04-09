import os
import json
import websocket
from kafka import KafkaProducer
from dotenv import load_dotenv
from finnhub import Client as FinnhubClient

# Load environment variables
load_dotenv()

class FinnhubProducer:
    def __init__(self):
        # Initialize Finnhub client
        self.finnhub_client = FinnhubClient(api_key=os.getenv('FINNHUB_API_TOKEN'))
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=f"{os.getenv('KAFKA_SERVER')}:{os.getenv('KAFKA_PORT')}",
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        # Get tickers from environment
        self.tickers = json.loads(os.getenv('FINNHUB_STOCKS_TICKERS'))
        self.validate = os.getenv('FINNHUB_VALIDATE_TICKERS')
        
        # Initialize websocket
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            f'wss://ws.finnhub.io?token={os.getenv("FINNHUB_API_TOKEN")}',
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.on_open = self.on_open

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            self.producer.send(os.getenv('KAFKA_TOPIC_NAME'), data)
            print(f"Sent message: {data}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket connection closed with status {close_status_code}: {close_msg}")

    def on_open(self, ws):
        for ticker in self.tickers:
            if self.validate == "1":
                try:
                    # Validate ticker
                    quote = self.finnhub_client.quote(ticker)
                    if quote:
                        self.ws.send(json.dumps({"type": "subscribe", "symbol": ticker}))
                        print(f"Subscription for {ticker} succeeded")
                    else:
                        print(f"Subscription for {ticker} failed - ticker not found")
                except Exception as e:
                    print(f"Error validating ticker {ticker}: {e}")
            else:
                self.ws.send(json.dumps({"type": "subscribe", "symbol": ticker}))

    def run(self):
        self.ws.run_forever()

if __name__ == "__main__":
    producer = FinnhubProducer()
    producer.run() 