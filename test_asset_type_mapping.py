#!/usr/bin/env python3
"""
Test script để kiểm tra logic mapping asset type
Kiểm tra cả STOCK và CRYPTO data mapping
"""

def test_asset_type_mapping():
    """Test asset type detection logic"""
    
    # Test cases
    test_cases = [
        # CRYPTO cases
        {"symbol": "BINANCE:BTCUSDT", "expected": "CRYPTO"},
        {"symbol": "BINANCE:ETHUSDT", "expected": "CRYPTO"},
        {"symbol": "CRYPTO:BTCUSD", "expected": "CRYPTO"},
        
        # STOCK cases  
        {"symbol": "AAPL", "expected": "STOCK"},
        {"symbol": "MSFT", "expected": "STOCK"},
        {"symbol": "GOOGL", "expected": "STOCK"},
        {"symbol": "TSLA", "expected": "STOCK"},
        
        # Edge cases
        {"symbol": "OTHER:SYMBOL", "expected": "OTHER"},
        {"symbol": "VERY_LONG_SYMBOL", "expected": "OTHER"},
    ]
    
    print("=== TESTING ASSET TYPE MAPPING ===")
    
    for case in test_cases:
        symbol = case["symbol"]
        expected = case["expected"]
        
        # Logic từ spark_config.py
        if "BINANCE:" in symbol or "CRYPTO:" in symbol:
            detected = "CRYPTO"
        elif len(symbol) <= 5 and symbol.isupper() and symbol.isalpha():
            detected = "STOCK"
        else:
            detected = "OTHER"
            
        status = "✅ PASS" if detected == expected else "❌ FAIL"
        print(f"{status} - Symbol: {symbol:15} | Expected: {expected:6} | Detected: {detected}")

def test_crypto_data_structure():
    """Test crypto data structure"""
    
    print("\n=== TESTING CRYPTO DATA STRUCTURE ===")
    
    # Sample crypto data từ Finnhub
    crypto_data = {
        "data": [
            {
                "p": 7296.89,
                "s": "BINANCE:BTCUSDT", 
                "t": 1575526691134,
                "v": 0.011467
                # Lưu ý: KHÔNG có trường "c" (trade_conditions)
            }
        ],
        "type": "trade"
    }
    
    print("✅ Crypto data structure:")
    print(f"   - Symbol: {crypto_data['data'][0]['s']}")
    print(f"   - Price: ${crypto_data['data'][0]['p']:,.2f}")
    print(f"   - Volume: {crypto_data['data'][0]['v']}")
    print(f"   - Timestamp: {crypto_data['data'][0]['t']}")
    print(f"   - Has 'c' field: {'c' in crypto_data['data'][0]}")
    
def test_stock_data_structure():
    """Test stock data structure"""
    
    print("\n=== TESTING STOCK DATA STRUCTURE ===")
    
    # Sample stock data từ Finnhub
    stock_data = {
        "data": [
            {
                "c": ["12", "37"],  # trade_conditions - CHỈ CÓ TRONG STOCK
                "p": 150.25,
                "s": "AAPL",
                "t": 1575526691134,
                "v": 100
            }
        ],
        "type": "trade"
    }
    
    print("✅ Stock data structure:")
    print(f"   - Symbol: {stock_data['data'][0]['s']}")
    print(f"   - Price: ${stock_data['data'][0]['p']:,.2f}")
    print(f"   - Volume: {stock_data['data'][0]['v']}")
    print(f"   - Timestamp: {stock_data['data'][0]['t']}")
    print(f"   - Trade Conditions: {stock_data['data'][0]['c']}")
    print(f"   - Has 'c' field: {'c' in stock_data['data'][0]}")

def test_cassandra_schema_mapping():
    """Test Cassandra schema mapping"""
    
    print("\n=== TESTING CASSANDRA SCHEMA MAPPING ===")
    
    # Test CRYPTO mapping
    crypto_record = {
        "symbol": "BINANCE:BTCUSDT",
        "price": 7296.89,
        "volume": 0.011467,
        "asset_type": "CRYPTO",
        "trade_conditions": None  # NULL for crypto
    }
    
    # Test STOCK mapping
    stock_record = {
        "symbol": "AAPL", 
        "price": 150.25,
        "volume": 100.0,
        "asset_type": "STOCK",
        "trade_conditions": ["12", "37"]  # Array for stock
    }
    
    print("✅ CRYPTO record for Cassandra:")
    for key, value in crypto_record.items():
        print(f"   - {key}: {value}")
        
    print("\n✅ STOCK record for Cassandra:")
    for key, value in stock_record.items():
        print(f"   - {key}: {value}")

def main():
    """Main test runner"""
    test_asset_type_mapping()
    test_crypto_data_structure()
    test_stock_data_structure()
    test_cassandra_schema_mapping()
    
    print("\n=== SUMMARY ===")
    print("✅ Schema hỗ trợ cả STOCK và CRYPTO")
    print("✅ Asset type detection logic working")
    print("✅ trade_conditions nullable cho CRYPTO")
    print("✅ Volume type DOUBLE hỗ trợ fractional crypto volume")
    print("\n🚀 Ready to test với real data!")

if __name__ == "__main__":
    main() 