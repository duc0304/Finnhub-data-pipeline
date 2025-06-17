import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './News.css';
import './Recommendations.css';

const Recommendations = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [filter, setFilter] = useState('all'); // all, buy, sell, hold
  const [confidenceFilter, setConfidenceFilter] = useState('all'); // all, high, medium, low
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [showPopup, setShowPopup] = useState(false);

  // Mock recommendations data
  const mockRecommendations = [
    {
      id: 1,
      symbol: 'BTC',
      name: 'Bitcoin',
      signal: 'buy',
      confidence: 92,
      currentPrice: 67420.50,
      entryMin: 67420,
      entryMax: 67800,
      takeProfit: 72500,
      stopLoss: 64200,
      riskReward: 1.56,
      profitPercent: 7.5,
      riskPercent: 4.8,
      timeframe: '4H',
      timestamp: '2 phút trước',
      indicators: {
        macd: { status: 'bullish', signal: 'Bullish Crossover' },
        rsi: { value: 45.2, status: 'neutral', signal: 'Neutral' },
        sma20: { status: 'bullish', signal: 'SMA20 > EMA12' },
        volume: { status: 'bullish', signal: 'Volume Spike +156%' }
      }
    },
    {
      id: 2,
      symbol: 'AAPL',
      name: 'Apple Inc.',
      signal: 'sell',
      confidence: 78,
      currentPrice: 193.85,
      entryMin: 193.50,
      entryMax: 194.20,
      takeProfit: 185.00,
      stopLoss: 198.50,
      riskReward: 2.09,
      profitPercent: 4.8,
      riskPercent: 2.3,
      timeframe: '1H',
      timestamp: '5 phút trước',
      indicators: {
        rsi: { value: 78.5, status: 'bearish', signal: 'Overbought' },
        macd: { status: 'bearish', signal: 'Bearish Divergence' },
        sma20: { status: 'bearish', signal: 'Price < SMA20' },
        volume: { status: 'neutral', signal: 'Normal Volume' }
      }
    },
    {
      id: 3,
      symbol: 'ETH',
      name: 'Ethereum',
      signal: 'buy',
      confidence: 85,
      currentPrice: 3542.85,
      entryMin: 3540,
      entryMax: 3580,
      takeProfit: 3850,
      stopLoss: 3420,
      riskReward: 2.51,
      profitPercent: 8.7,
      riskPercent: 3.5,
      timeframe: '4H',
      timestamp: '8 phút trước',
      indicators: {
        macd: { status: 'bullish', signal: 'Golden Cross' },
        rsi: { value: 52.8, status: 'neutral', signal: 'Neutral' },
        ema12: { status: 'bullish', signal: 'EMA12 > EMA26' },
        volume: { status: 'bullish', signal: 'High Volume' }
      }
    },
    {
      id: 4,
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      signal: 'hold',
      confidence: 65,
      currentPrice: 248.50,
      entryMin: 245,
      entryMax: 252,
      takeProfit: 265,
      stopLoss: 235,
      riskReward: 1.23,
      profitPercent: 6.6,
      riskPercent: 5.4,
      timeframe: '1D',
      timestamp: '12 phút trước',
      indicators: {
        rsi: { value: 55.3, status: 'neutral', signal: 'Neutral' },
        macd: { status: 'neutral', signal: 'Consolidation' },
        sma20: { status: 'neutral', signal: 'Price ≈ SMA20' },
        volume: { status: 'neutral', signal: 'Average Volume' }
      }
    },
    {
      id: 5,
      symbol: 'NVDA',
      name: 'NVIDIA Corporation',
      signal: 'buy',
      confidence: 88,
      currentPrice: 875.42,
      entryMin: 870,
      entryMax: 880,
      takeProfit: 950,
      stopLoss: 840,
      riskReward: 2.14,
      profitPercent: 8.5,
      riskPercent: 4.0,
      timeframe: '4H',
      timestamp: '15 phút trước',
      indicators: {
        macd: { status: 'bullish', signal: 'Momentum Building' },
        rsi: { value: 48.7, status: 'neutral', signal: 'Room to Grow' },
        ema12: { status: 'bullish', signal: 'Strong Uptrend' },
        volume: { status: 'bullish', signal: 'Institutional Buying' }
      }
    },
    {
      id: 6,
      symbol: 'MSFT',
      name: 'Microsoft Corporation',
      signal: 'sell',
      confidence: 72,
      currentPrice: 420.15,
      entryMin: 418,
      entryMax: 422,
      takeProfit: 395,
      stopLoss: 435,
      riskReward: 1.67,
      profitPercent: 6.0,
      riskPercent: 3.6,
      timeframe: '1D',
      timestamp: '20 phút trước',
      indicators: {
        rsi: { value: 71.2, status: 'bearish', signal: 'Overbought Territory' },
        macd: { status: 'bearish', signal: 'Weakening Momentum' },
        sma20: { status: 'bearish', signal: 'Resistance at SMA20' },
        volume: { status: 'neutral', signal: 'Declining Volume' }
      }
    }
  ];

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setRecommendations(mockRecommendations);
      setLoading(false);
    }, 800);
  }, []);

  // Real-time clock update
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const getFilteredRecommendations = () => {
    let filtered = recommendations;
    
    if (filter !== 'all') {
      filtered = filtered.filter(rec => rec.signal === filter);
    }
    
    if (confidenceFilter !== 'all') {
      if (confidenceFilter === 'high') {
        filtered = filtered.filter(rec => rec.confidence >= 80);
      } else if (confidenceFilter === 'medium') {
        filtered = filtered.filter(rec => rec.confidence >= 60 && rec.confidence < 80);
      } else if (confidenceFilter === 'low') {
        filtered = filtered.filter(rec => rec.confidence < 60);
      }
    }
    
    return filtered;
  };

  const getSummaryStats = () => {
    const buySignals = recommendations.filter(r => r.signal === 'buy');
    const sellSignals = recommendations.filter(r => r.signal === 'sell');
    const holdSignals = recommendations.filter(r => r.signal === 'hold');
    const highConfidence = recommendations.filter(r => r.confidence >= 80);
    
    return {
      buy: {
        count: buySignals.length,
        avgReturn: buySignals.reduce((acc, r) => acc + r.profitPercent, 0) / buySignals.length || 0
      },
      sell: {
        count: sellSignals.length,
        avgReturn: sellSignals.reduce((acc, r) => acc + r.profitPercent, 0) / sellSignals.length || 0
      },
      hold: {
        count: holdSignals.length,
        avgReturn: holdSignals.reduce((acc, r) => acc + r.profitPercent, 0) / holdSignals.length || 0
      },
      highConfidence: {
        count: highConfidence.length,
        avgConfidence: highConfidence.reduce((acc, r) => acc + r.confidence, 0) / highConfidence.length || 0
      }
    };
  };

  const getSignalIcon = (signal) => {
    switch (signal) {
      case 'buy':
        return '🟢';
      case 'sell':
        return '🔴';
      case 'hold':
        return '🟡';
      default:
        return '⚪';
    }
  };

  const getSignalText = (signal) => {
    switch (signal) {
      case 'buy':
        return 'MUA NGAY';
      case 'sell':
        return 'BÁN NGAY';
      case 'hold':
        return 'GIỮ';
      default:
        return 'CHỜ';
    }
  };

  const getConfidenceStars = (confidence) => {
    const stars = Math.floor(confidence / 20);
    return '⭐'.repeat(stars);
  };

  const getIndicatorIcon = (status) => {
    switch (status) {
      case 'bullish':
        return '✅';
      case 'bearish':
        return '⚠️';
      case 'neutral':
        return '➖';
      default:
        return '❓';
    }
  };

  const handleCardClick = (recommendation) => {
    setSelectedRecommendation(recommendation);
    setShowPopup(true);
  };

  const closePopup = () => {
    setShowPopup(false);
    setSelectedRecommendation(null);
  };

  const handleViewChart = (symbol) => {
    navigate(`/stock/${symbol.toLowerCase()}`);
    closePopup();
  };

  const filteredRecommendations = getFilteredRecommendations();
  const stats = getSummaryStats();

  return (
    <div className="news-page">
      <div className="news-header">
        <div className="news-header-content">
          <h1 className="impact-title">
            Khuyến nghị đầu tư
            <span className="title-glow"></span>
          </h1>
          <p className="news-subtitle">
            Tín hiệu mua/bán thông minh dựa trên phân tích đa chỉ báo kỹ thuật
          </p>
          <div className="last-updated">
            📅 Cập nhật: {currentTime.toLocaleTimeString('vi-VN')} - {currentTime.toLocaleDateString('vi-VN')}
          </div>
        </div>
        <div className="header-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      {/* Summary Dashboard */}
      <div className="summary-dashboard">
        <div className="summary-card buy-summary">
          <div className="summary-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 17L9 11L13 15L21 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M14 7H21V14" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="summary-content">
            <h3>MUA</h3>
            <div className="summary-count">{stats.buy.count} tín hiệu</div>
            <div className="summary-return">+{stats.buy.avgReturn.toFixed(1)}% trung bình</div>
          </div>
        </div>
        
        <div className="summary-card sell-summary">
          <div className="summary-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 7L9 13L13 9L21 17" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M14 17H21V10" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="summary-content">
            <h3>BÁN</h3>
            <div className="summary-count">{stats.sell.count} tín hiệu</div>
            <div className="summary-return">+{stats.sell.avgReturn.toFixed(1)}% trung bình</div>
          </div>
        </div>
        
        <div className="summary-card hold-summary">
          <div className="summary-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12H15" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
              <path d="M12 7V17" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
              <path d="M7 10L12 7L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M7 14L12 17L17 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div className="summary-content">
            <h3>GIỮ</h3>
            <div className="summary-count">{stats.hold.count} tín hiệu</div>
            <div className="summary-return">+{stats.hold.avgReturn.toFixed(1)}% trung bình</div>
          </div>
        </div>
        
        <div className="summary-card confidence-summary">
          <div className="summary-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <div className="summary-content">
            <h3>TIN CẬY CAO</h3>
            <div className="summary-count">{stats.highConfidence.count} tín hiệu</div>
            <div className="summary-return">{stats.highConfidence.avgConfidence.toFixed(0)}% tin cậy</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Loại tín hiệu:</label>
          <div className="filter-buttons">
            <button 
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >
              Tất cả
            </button>
            <button 
              className={filter === 'buy' ? 'active' : ''}
              onClick={() => setFilter('buy')}
            >
              🟢 MUA
            </button>
            <button 
              className={filter === 'sell' ? 'active' : ''}
              onClick={() => setFilter('sell')}
            >
              🔴 BÁN
            </button>
            <button 
              className={filter === 'hold' ? 'active' : ''}
              onClick={() => setFilter('hold')}
            >
              🟡 GIỮ
            </button>
          </div>
        </div>
        
        <div className="filter-group">
          <label>Độ tin cậy:</label>
          <div className="filter-buttons">
            <button 
              className={confidenceFilter === 'all' ? 'active' : ''}
              onClick={() => setConfidenceFilter('all')}
            >
              Tất cả
            </button>
            <button 
              className={confidenceFilter === 'high' ? 'active' : ''}
              onClick={() => setConfidenceFilter('high')}
            >
              ≥80%
            </button>
            <button 
              className={confidenceFilter === 'medium' ? 'active' : ''}
              onClick={() => setConfidenceFilter('medium')}
            >
              60-79%
            </button>
            <button 
              className={confidenceFilter === 'low' ? 'active' : ''}
              onClick={() => setConfidenceFilter('low')}
            >
              &lt;60%
            </button>
          </div>
        </div>
      </div>

      {/* Recommendations Grid */}
      <div className="news-container">
        {loading ? (
          <div className="loading-container">
            <div className="loader"></div>
            <p>Đang phân tích thị trường...</p>
          </div>
        ) : (
          <div className="recommendations-grid-compact">
            {filteredRecommendations.map(rec => (
              <div 
                key={rec.id}
                className={`recommendation-card-compact ${rec.signal}`}
                onClick={() => handleCardClick(rec)}
              >
                <div className="compact-header">
                  <div className="symbol-section">
                    <span className="symbol-large">{rec.symbol}</span>
                    <span className="asset-name-small">{rec.name}</span>
                  </div>
                  <div className="signal-section">
                    <div className={`signal-indicator ${rec.signal}`}>
                      {rec.signal === 'buy' ? (
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M3 17L9 11L13 15L21 7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M14 7H21V14" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      ) : rec.signal === 'sell' ? (
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M3 7L9 13L13 9L21 17" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M14 17H21V10" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      ) : (
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M9 12H15" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
                          <path d="M12 7V17" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
                          <path d="M7 10L12 7L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M7 14L12 17L17 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      )}
                    </div>
                    <span className="signal-text">{getSignalText(rec.signal)}</span>
                  </div>
                </div>

                <div className="compact-body">
                  <div className="price-display">
                    <span className="current-price">${rec.currentPrice.toLocaleString()}</span>
                    <span className={`profit-display ${rec.signal === 'sell' ? 'negative' : 'positive'}`}>
                      {rec.signal === 'sell' ? '-' : '+'}{rec.profitPercent}%
                    </span>
                  </div>
                  
                  <div className="confidence-display">
                    <span className="confidence-number">Tin cậy: {rec.confidence}%</span>
                  </div>
                </div>

                <div className="compact-footer">
                  <span className="timeframe-badge">{rec.timeframe}</span>
                  <span className="timestamp-small">{rec.timestamp}</span>
                </div>

                <div className="hover-overlay">
                  <span>👆 Click để xem chi tiết</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Popup chi tiết */}
      {showPopup && selectedRecommendation && (
        <div className="popup-overlay" onClick={closePopup}>
          <div className="popup-content" onClick={(e) => e.stopPropagation()}>
            <div className="popup-header">
              <div className="popup-title">
                <span className="popup-symbol">{selectedRecommendation.symbol}</span>
                <span className="popup-name">{selectedRecommendation.name}</span>
              </div>
              <button className="close-btn" onClick={closePopup}>✕</button>
            </div>

            <div className="popup-body">
              <div className="popup-signal-section">
                <div className={`popup-signal-badge ${selectedRecommendation.signal}`}>
                  {getSignalIcon(selectedRecommendation.signal)} {getSignalText(selectedRecommendation.signal)}
                </div>
                <div className="popup-confidence">
                  <span>Độ tin cậy: {selectedRecommendation.confidence}%</span>
                  <div className="confidence-stars">{getConfidenceStars(selectedRecommendation.confidence)}</div>
                </div>
              </div>

              <div className="popup-price-section">
                <h3>💰 Thông tin giá</h3>
                <div className="popup-price-grid">
                  <div className="price-item">
                    <span className="label">Giá hiện tại:</span>
                    <span className="value">${selectedRecommendation.currentPrice.toLocaleString()}</span>
                  </div>
                  <div className="price-item">
                    <span className="label">Vùng Entry:</span>
                    <span className="value">${selectedRecommendation.entryMin.toLocaleString()} - ${selectedRecommendation.entryMax.toLocaleString()}</span>
                  </div>
                  <div className="price-item">
                    <span className="label">🎯 Take Profit:</span>
                    <span className="value profit">${selectedRecommendation.takeProfit.toLocaleString()} (+{selectedRecommendation.profitPercent}%)</span>
                  </div>
                  <div className="price-item">
                    <span className="label">🛡️ Stop Loss:</span>
                    <span className="value loss">${selectedRecommendation.stopLoss.toLocaleString()} (-{selectedRecommendation.riskPercent}%)</span>
                  </div>
                  <div className="price-item">
                    <span className="label">⚖️ Risk/Reward:</span>
                    <span className="value">1:{selectedRecommendation.riskReward}</span>
                  </div>
                </div>
              </div>

              <div className="popup-indicators-section">
                <h3>📊 Chỉ báo kỹ thuật</h3>
                <div className="popup-indicators-grid">
                  {Object.entries(selectedRecommendation.indicators).map(([key, indicator]) => (
                    <div key={key} className={`indicator-card ${indicator.status}`}>
                      <div className="indicator-header">
                        {getIndicatorIcon(indicator.status)}
                        <span className="indicator-name">{key.toUpperCase()}</span>
                      </div>
                      <span className="indicator-signal">{indicator.signal}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="popup-meta">
                <span className="popup-timeframe">Khung thời gian: {selectedRecommendation.timeframe}</span>
                <span className="popup-timestamp">Cập nhật: {selectedRecommendation.timestamp}</span>
              </div>
            </div>

            <div className="popup-footer">
              <button 
                className="popup-btn primary"
                onClick={() => handleViewChart(selectedRecommendation.symbol)}
              >
                📈 Xem Chart
              </button>
              <button className="popup-btn secondary">
                🔔 Đặt Alert
              </button>
              <button className="popup-btn secondary" onClick={closePopup}>
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Recommendations; 