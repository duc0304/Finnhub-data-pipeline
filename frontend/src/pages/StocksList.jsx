import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './StocksList.css';

const StocksList = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('stocks'); // 'stocks' hoặc 'crypto'
  const [stocksData, setStocksData] = useState([]);
  const [cryptoData, setCryptoData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState('');

  // Mock data cho stocks
  const mockStocksData = [
        {
          id: 1, 
      symbol: 'AAPL',
      name: 'Apple Inc.',
      currentPrice: 193.85,
      openPrice: 192.30,
      change: 1.55,
      changePercent: 0.81,
      volume: 45876320,
      high: 195.12,
      low: 191.78,
      ceiling: 211.53,
      floor: 173.07,
      reference: 192.30,
      marketCap: 2980.5,
      peRatio: 29.8,
      dividend: 0.95,
      type: 'stock'
        },
        {
          id: 2, 
      symbol: 'NVDA',
      name: 'NVIDIA Corporation',
      currentPrice: 875.42,
      openPrice: 870.15,
      change: 5.27,
      changePercent: 0.61,
      volume: 32145890,
      high: 882.35,
      low: 868.90,
      ceiling: 957.17,
      floor: 783.14,
      reference: 870.15,
      marketCap: 2145.8,
      peRatio: 74.2,
      dividend: 0.16,
      type: 'stock'
        },
        {
          id: 3, 
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      currentPrice: 248.50,
      openPrice: 252.80,
      change: -4.30,
      changePercent: -1.70,
      volume: 78932140,
      high: 254.60,
      low: 245.20,
      ceiling: 278.08,
      floor: 227.52,
      reference: 252.80,
      marketCap: 788.9,
      peRatio: 62.4,
      dividend: 0.00,
      type: 'stock'
        },
        {
          id: 4, 
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      currentPrice: 420.15,
      openPrice: 420.15,
      change: 0.00,
      changePercent: 0.00,
      volume: 23456780,
      high: 423.45,
      low: 417.90,
      ceiling: 462.17,
      floor: 378.14,
      reference: 420.15,
      marketCap: 3120.4,
      peRatio: 34.7,
      dividend: 3.00,
      type: 'stock'
        },
        {
          id: 5, 
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      currentPrice: 168.24,
      openPrice: 165.80,
      change: 2.44,
      changePercent: 1.47,
      volume: 28934567,
      high: 169.15,
      low: 165.30,
      ceiling: 182.38,
      floor: 149.37,
      reference: 165.80,
      marketCap: 2089.7,
      peRatio: 25.3,
      dividend: 0.00,
      type: 'stock'
        },
        {
          id: 6, 
      symbol: 'AMZN',
      name: 'Amazon.com Inc.',
      currentPrice: 155.89,
      openPrice: 158.20,
      change: -2.31,
      changePercent: -1.46,
      volume: 41256789,
      high: 159.45,
      low: 154.12,
      ceiling: 174.02,
      floor: 142.38,
      reference: 158.20,
      marketCap: 1634.2,
      peRatio: 43.8,
      dividend: 0.00,
      type: 'stock'
        },
        {
          id: 7, 
      symbol: 'META',
      name: 'Meta Platforms Inc.',
      currentPrice: 512.78,
      openPrice: 510.25,
      change: 2.53,
      changePercent: 0.50,
      volume: 19847563,
      high: 516.90,
      low: 508.40,
      ceiling: 561.28,
      floor: 459.23,
      reference: 510.25,
      marketCap: 1298.4,
      peRatio: 24.7,
      dividend: 2.40,
      type: 'stock'
        },
        {
          id: 8, 
      symbol: 'NFLX',
      name: 'Netflix Inc.',
      currentPrice: 685.34,
      openPrice: 682.10,
      change: 3.24,
      changePercent: 0.47,
      volume: 8934567,
      high: 689.75,
      low: 679.80,
      ceiling: 750.31,
      floor: 613.89,
      reference: 682.10,
      marketCap: 304.8,
      peRatio: 31.9,
      dividend: 0.00,
      type: 'stock'
        },
        {
          id: 9, 
      symbol: 'AMD',
      name: 'Advanced Micro Devices',
      currentPrice: 142.67,
      openPrice: 145.30,
      change: -2.63,
      changePercent: -1.81,
      volume: 52847391,
      high: 146.85,
      low: 141.20,
      ceiling: 159.83,
      floor: 130.77,
      reference: 145.30,
      marketCap: 230.5,
      peRatio: 189.6,
      dividend: 0.00,
      type: 'stock'
        },
        {
          id: 10, 
      symbol: 'JPM',
      name: 'JPMorgan Chase & Co.',
      currentPrice: 219.84,
      openPrice: 218.50,
      change: 1.34,
      changePercent: 0.61,
      volume: 15673842,
      high: 221.45,
      low: 217.90,
      ceiling: 240.35,
      floor: 196.65,
      reference: 218.50,
      marketCap: 634.7,
      peRatio: 11.8,
      dividend: 4.20,
      type: 'stock'
    }
  ];

  // Mock data cho crypto
  const mockCryptoData = [
        {
          id: 11, 
      symbol: 'BTC',
      name: 'Bitcoin',
      currentPrice: 67420.50,
      openPrice: 65890.30,
      change: 1530.20,
      changePercent: 2.32,
      volume: 28456789000,
      high: 68150.75,
      low: 65234.80,
      ceiling: 72479.33,
      floor: 59301.27,
      reference: 65890.30,
      marketCap: 1334.2,
      circulatingSupply: 19.8,
      maxSupply: 21.0,
      type: 'crypto'
        },
        {
          id: 12, 
      symbol: 'ETH',
      name: 'Ethereum',
      currentPrice: 3542.85,
      openPrice: 3610.40,
      change: -67.55,
      changePercent: -1.87,
      volume: 15678923000,
      high: 3625.90,
      low: 3485.20,
      ceiling: 3971.44,
      floor: 3249.36,
      reference: 3610.40,
      marketCap: 426.8,
      circulatingSupply: 120.4,
      maxSupply: null,
      type: 'crypto'
        },
        {
          id: 13, 
      symbol: 'USDT',
      name: 'Tether',
      currentPrice: 1.0001,
      openPrice: 1.0001,
      change: 0.0000,
      changePercent: 0.00,
      volume: 45789123000,
      high: 1.0003,
      low: 0.9998,
      ceiling: 1.1001,
      floor: 0.9001,
      reference: 1.0001,
      marketCap: 119.8,
      circulatingSupply: 119.8,
      maxSupply: null,
      type: 'crypto'
        },
        {
          id: 14, 
      symbol: 'BNB',
      name: 'Binance Coin',
      currentPrice: 592.45,
      openPrice: 578.30,
      change: 14.15,
      changePercent: 2.45,
      volume: 1234567000,
      high: 598.75,
      low: 575.80,
      ceiling: 636.13,
      floor: 520.47,
      reference: 578.30,
      marketCap: 86.2,
      circulatingSupply: 145.5,
      maxSupply: 200.0,
      type: 'crypto'
    },
    {
      id: 15,
      symbol: 'ADA',
      name: 'Cardano',
      currentPrice: 0.6845,
      openPrice: 0.6520,
      change: 0.0325,
      changePercent: 4.98,
      volume: 891234567,
      high: 0.6920,
      low: 0.6485,
      ceiling: 0.7172,
      floor: 0.5868,
      reference: 0.6520,
      marketCap: 24.1,
      circulatingSupply: 35.2,
      maxSupply: 45.0,
      type: 'crypto'
    },
    {
      id: 16,
      symbol: 'SOL',
      name: 'Solana',
      currentPrice: 189.34,
      openPrice: 192.80,
      change: -3.46,
      changePercent: -1.79,
      volume: 2847563901,
      high: 195.67,
      low: 186.25,
      ceiling: 212.08,
      floor: 173.52,
      reference: 192.80,
      marketCap: 89.7,
      circulatingSupply: 473.8,
      maxSupply: null,
      type: 'crypto'
    },
    {
      id: 17,
      symbol: 'XRP',
      name: 'Ripple',
      currentPrice: 0.5234,
      openPrice: 0.5180,
      change: 0.0054,
      changePercent: 1.04,
      volume: 1567892340,
      high: 0.5289,
      low: 0.5145,
      ceiling: 0.5698,
      floor: 0.4662,
      reference: 0.5180,
      marketCap: 29.8,
      circulatingSupply: 56.9,
      maxSupply: 100.0,
      type: 'crypto'
    },
    {
      id: 18,
      symbol: 'DOGE',
      name: 'Dogecoin',
      currentPrice: 0.1789,
      openPrice: 0.1825,
      change: -0.0036,
      changePercent: -1.97,
      volume: 3456789012,
      high: 0.1842,
      low: 0.1765,
      ceiling: 0.2008,
      floor: 0.1643,
      reference: 0.1825,
      marketCap: 26.3,
      circulatingSupply: 147.0,
      maxSupply: null,
      type: 'crypto'
    },
    {
      id: 19,
      symbol: 'MATIC',
      name: 'Polygon',
      currentPrice: 0.8945,
      openPrice: 0.8720,
      change: 0.0225,
      changePercent: 2.58,
      volume: 456789123,
      high: 0.9078,
      low: 0.8685,
      ceiling: 0.9592,
      floor: 0.7848,
      reference: 0.8720,
      marketCap: 8.7,
      circulatingSupply: 9.7,
      maxSupply: 10.0,
      type: 'crypto'
    },
    {
      id: 20,
      symbol: 'AVAX',
      name: 'Avalanche',
      currentPrice: 42.67,
      openPrice: 43.85,
      change: -1.18,
      changePercent: -2.69,
      volume: 678912345,
      high: 44.32,
      low: 41.95,
      ceiling: 48.24,
      floor: 39.47,
      reference: 43.85,
      marketCap: 17.2,
      circulatingSupply: 403.4,
      maxSupply: 720.0,
      type: 'crypto'
    }
  ];

  useEffect(() => {
    // Giả lập thời gian load
    setTimeout(() => {
      setStocksData(mockStocksData);
      setCryptoData(mockCryptoData);
      
      // Cập nhật thời gian dữ liệu
      const now = new Date();
      setLastUpdated(`${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`);
      
      setLoading(false);
    }, 800);
  }, []);

  const handleItemClick = (itemId) => {
    navigate(`/stock/${itemId}`);
  };

  const formatPrice = (price, isCrypto = false) => {
    if (isCrypto && price < 10) {
      return price.toFixed(4);
    }
    return price.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  };

  const formatVolume = (volume, isCrypto = false) => {
    if (isCrypto) {
      if (volume >= 1000000000) {
        return (volume / 1000000000).toFixed(2) + 'B';
      } else if (volume >= 1000000) {
        return (volume / 1000000).toFixed(2) + 'M';
      }
    } else {
    if (volume >= 1000000) {
      return (volume / 1000000).toFixed(2) + 'M';
    } else if (volume >= 1000) {
      return (volume / 1000).toFixed(0) + 'K';
    }
    }
    return volume.toLocaleString('en-US');
  };

  const formatMarketCap = (marketCap) => {
    if (marketCap >= 1000) {
      return (marketCap / 1000).toFixed(1) + 'T';
    }
    return marketCap.toFixed(1) + 'B';
  };
    
  const getRowClassName = (changePercent) => {
    if (changePercent > 0) return 'row-positive';
    if (changePercent < 0) return 'row-negative';
    return 'row-neutral';
  };

  const getPriceChangeIcon = (changePercent) => {
    if (changePercent > 0) {
      return <span className="price-icon icon-up">▲</span>;
    } else if (changePercent < 0) {
      return <span className="price-icon icon-down">▼</span>;
    }
    return <span className="price-icon icon-neutral">●</span>;
  };

  const currentData = activeTab === 'stocks' ? stocksData : cryptoData;
  const isCryptoTab = activeTab === 'crypto';


  return (
    <div className="news-page">
      <div className="news-header">
        <div className="news-header-content">
          <h1 className="impact-title">
            Thị trường tài chính
            <span className="title-glow"></span>
          </h1>
          <p className="news-subtitle">Theo dõi và phân tích các cơ hội đầu tư tốt nhất với dữ liệu thời gian thực.</p>
        </div>
        <div className="header-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>
      
      <div className="market-tabs">
        <button 
          className={`tab-button ${activeTab === 'stocks' ? 'active' : ''}`}
          onClick={() => setActiveTab('stocks')}
        >
          <svg className="tab-icon" viewBox="0 0 24 24" fill="none">
            <path d="M3 3H21V21H3V3Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M9 9H15M9 13H15M9 17H15" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
          Chứng khoán
        </button>
        <button 
          className={`tab-button ${activeTab === 'crypto' ? 'active' : ''}`}
          onClick={() => setActiveTab('crypto')}
        >
          <svg className="tab-icon" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
            <path d="M8 12H16M10 8H14M10 16H14" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
          Tiền điện tử
        </button>
      </div>

      <div className="market-content">
        {loading ? (
          <div className="loading-container">
            <div className="loader"></div>
            <p>Đang tải dữ liệu...</p>
          </div>
        ) : (
          <div className="market-table-container">
            <table className="market-table">
                  <thead>
                    <tr>
                  <th className="col-symbol">Ký hiệu</th>
                  <th className="col-name">Tên</th>
                  <th className="col-price">Giá hiện tại</th>
                  <th className="col-change">Thay đổi</th>
                  <th className="col-volume">Khối lượng</th>
                  <th className="col-high">Cao nhất</th>
                  <th className="col-low">Thấp nhất</th>
                  <th className="col-ceiling">Giá trần</th>
                  <th className="col-floor">Giá sàn</th>
                  <th className="col-reference">TC</th>
                  <th className="col-marketcap">Vốn hóa</th>
                  {isCryptoTab ? (
                    <th className="col-supply">Lưu hành</th>
                  ) : (
                    <>
                      <th className="col-pe">P/E</th>
                      <th className="col-dividend">Cổ tức</th>
                    </>
                  )}
                    </tr>
                  </thead>
                  <tbody>
                {currentData.map(item => (
                  <tr 
                    key={item.id} 
                    className={`market-row ${getRowClassName(item.changePercent)}`}
                    onClick={() => handleItemClick(item.id)}
                  >
                    <td className="col-symbol">
                      <div className="symbol-container">
                        <div className="symbol-avatar">
                          {item.symbol.charAt(0)}
                        </div>
                        <span className="symbol-text">{item.symbol}</span>
                      </div>
                    </td>
                    <td className="col-name">
                      <span className="item-name">{item.name}</span>
                    </td>
                    <td className="col-price">
                      <span className="price-value">
                        ${formatPrice(item.currentPrice, isCryptoTab)}
                      </span>
                    </td>
                    <td className="col-change">
                      <div className="change-container">
                        {getPriceChangeIcon(item.changePercent)}
                        <div className="change-details">
                          <span className="change-amount">
                            {item.change > 0 ? '+' : ''}{formatPrice(Math.abs(item.change), isCryptoTab)}
                          </span>
                          <span className="change-percent">
                            ({item.changePercent > 0 ? '+' : ''}{item.changePercent.toFixed(2)}%)
                          </span>
                        </div>
                          </div>
                        </td>
                    <td className="col-volume">
                      <span className="volume-value">
                        {formatVolume(item.volume, isCryptoTab)}
                      </span>
                    </td>
                    <td className="col-high">
                      <span className="high-value">
                        ${formatPrice(item.high, isCryptoTab)}
                      </span>
                    </td>
                    <td className="col-low">
                      <span className="low-value">
                        ${formatPrice(item.low, isCryptoTab)}
                      </span>
                    </td>
                    <td className="col-ceiling">
                      <span className="ceiling-value">
                        ${formatPrice(item.ceiling, isCryptoTab)}
                      </span>
                    </td>
                    <td className="col-floor">
                      <span className="floor-value">
                        ${formatPrice(item.floor, isCryptoTab)}
                      </span>
                    </td>
                    <td className="col-reference">
                      <span className="reference-value">
                        ${formatPrice(item.reference, isCryptoTab)}
                      </span>
                    </td>
                    <td className="col-marketcap">
                      <span className="marketcap-value">
                        ${formatMarketCap(item.marketCap)}
                      </span>
                    </td>
                    {isCryptoTab ? (
                      <td className="col-supply">
                        <span className="supply-value">
                          {item.circulatingSupply.toFixed(1)}M
                          {item.maxSupply && ` / ${item.maxSupply.toFixed(0)}M`}
                        </span>
                      </td>
                    ) : (
                      <>
                        <td className="col-pe">
                          <span className="pe-value">
                            {item.peRatio.toFixed(1)}
                          </span>
                        </td>
                        <td className="col-dividend">
                          <span className="dividend-value">
                            {item.dividend > 0 ? `${item.dividend.toFixed(2)}%` : 'N/A'}
                          </span>
                        </td>
                      </>
                    )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
        )}
      </div>
    </div>
  );
};

export default StocksList;