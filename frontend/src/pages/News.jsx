import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './News.css';

const News = () => {
  const [showAllNews, setShowAllNews] = useState(false);
  const navigate = useNavigate();

  // Dữ liệu tin tức mẫu
  const newsData = [
    {
      id: 1,
      hours: 7,
      source: 'Dow Jones Newswires',
      title: 'Naver 1Q Net Slumps on Higher Costs',
      trending: true,
      country: 'kr',
      symbol: 'N'
    },
    {
      id: 2,
      hours: 18,
      source: 'Dow Jones Newswires',
      title: 'Toyota Expects U.S. Tariffs, Material Costs to Dent Profit',
      country: 'jp',
      symbol: 'T'
    },
    {
      id: 3,
      hours: 18,
      source: 'Dow Jones Newswires',
      title: 'Jobless Claims Fell Last Week',
      trending: true,
      country: 'us',
      symbol: 'US'
    },
    {
      id: 4,
      hours: 19, 
      source: 'TradingView',
      title: 'EUR/USD: Dollar Powers Up as Fed\'s Powell Says Rates Stay Unchanged. Trump Calls Him a "FOOL"',
      country: 'eu-us',
      symbol: 'EU-US'
    },
    {
      id: 5,
      hours: 19,
      source: 'Dow Jones Newswires',
      title: 'Bank of England Cuts Key Rate After Fed Stands Pat',
      trending: true,
      country: 'gb',
      symbol: 'UK'
    },
    {
      id: 6,
      hours: 0,
      isYesterday: true,
      source: 'TradingView',
      title: 'BTC/USD: Bitcoin Eyes $100,000 as Powell\'s Presser Sparks Fresh Crypto Enthusiasm',
      country: 'btc',
      symbol: 'BTC'
    },
    {
      id: 7,
      hours: 0,
      isYesterday: true,
      source: 'Dow Jones Newswires',
      title: 'Bud Brewer AB InBev Profit Jumps as Volumes Beat Expectations',
      trending: true,
      country: 'be',
      symbol: 'BUD'
    },
    {
      id: 8,
      days: 2,
      source: 'TradingView',
      title: 'Fed Holds Rates Steady Ignoring Trump\'s Calls to Lower Them. S&P 500 Erases Daily Gains',
      country: 'us',
      symbol: 'US'
    },
    {
      id: 9,
      days: 2,
      source: 'TradingView',
      title: 'DIS: Disney Stock Rallies 6% as Earnings Deliver Surprise Beat. Revenue Flies, Too',
      country: 'us',
      symbol: 'DIS'
    },
    {
      id: 10,
      days: 2,
      source: 'Dow Jones Newswires',
      title: 'Novo Nordisk Investors Breathe Sigh of Relief Despite Guidance Hit From Copycat Drugs',
      country: 'dk',
      symbol: 'N'
    },
    {
      id: 11,
      days: 2,
      source: 'TradingView',
      title: 'USD/JPY: Dollar to Snap 3-Day Losing Streak as Fed Rate Decision Looms. Here\'s What to Expect.',
      country: 'jp-us',
      symbol: 'JP-US'
    }
  ];

  // Hiển thị cờ quốc gia
  const renderFlag = (country) => {
    if (country === 'kr') {
      return <div className="flag flag-kr"></div>;
    } else if (country === 'jp') {
      return <div className="flag flag-jp"></div>;
    } else if (country === 'us') {
      return <div className="flag flag-us"></div>;
    } else if (country === 'eu-us') {
      return <div className="flag flag-euus"></div>;
    } else if (country === 'jp-us') {
      return <div className="flag flag-jpus"></div>;
    } else if (country === 'gb') {
      return <div className="flag flag-gb"></div>;
    } else if (country === 'btc') {
      return <div className="flag flag-btc"></div>;
    } else if (country === 'be') {
      return <div className="flag flag-be"></div>;
    } else if (country === 'dk') {
      return <div className="flag flag-dk"></div>;
    }
    return null;
  };

  // Hiển thị thời gian
  const getTimeString = (hours, days, isYesterday) => {
    if (isYesterday) {
      return 'hôm qua';
    } else if (days) {
      return `${days} ngày trước`;
    }
    return `${hours} giờ trước`;
  };

  const handleNewsClick = (newsId) => {
    navigate(`/news/${newsId}`);
  };

  // Lấy 6 tin đầu tiên cho phần tin nổi bật
  const featuredNews = newsData.slice(0, 6);
  
  // Lấy tin cho bảng dựa vào trạng thái showAllNews
  const tableNews = showAllNews ? newsData : newsData.slice(0, 10);
  
  // Hiển thị biểu tượng trending
  const renderTrendingIcon = () => (
    <svg className="trending-fire-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C9.39 2.11 6.22 3.25 5 6.92C5.02 6.92 6.57 4.92 8.5 4.92C11.55 4.92 10.5 8.92 11.5 10.92C12.5 12.92 15 11.92 15 14.92C15 17.92 12 18.98 12 18.98C12 18.98 15.98 18.92 17.5 14.92C19.02 10.92 16.04 8.92 16.04 8.92C16.04 8.92 18.04 4.92 12 2Z" fill="#ff4136" stroke="#ff4136" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );

  return (
    <div className="news-page">
      <div className="news-header">
        <div className="news-header-content">
          <h1 className="impact-title">
            Tin tức thị trường
            <span className="title-glow"></span>
          </h1>
          <p className="news-subtitle">Đừng bỏ lỡ bất kỳ thông tin quan trọng nào với các cập nhật thời gian thực.</p>
        </div>
        <div className="header-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      {/* Phần tin nổi bật */}
      <div className="news-container">
        <h2 className="section-title">
          <svg className="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 15L8.5 12L5 15L2 12M22 15L18.5 12L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M19 6L17.5 8L16 6M12 3V12M5 3V9M19 9V15M12 18V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <div className="title-text-group">
            <span className="title-main">Tin nổi bật</span>
            <span className="title-sub">Tin quan trọng nhất hôm nay</span>
          </div>
          <span className="section-arrow">›</span>
          <span className="section-highlight">Top 6</span>
        </h2>

        <div className="news-list">
          {featuredNews.map((news) => (
            <div 
              key={news.id} 
              className={`news-item ${news.trending ? 'trending' : ''}`}
              onClick={() => handleNewsClick(news.id)}
            >
              <div className="news-meta">
                {renderFlag(news.country)}
                <span className="news-time">{getTimeString(news.hours, news.days, news.isYesterday)}</span>
                <span className="news-dot">•</span>
                <span className="news-source">{news.source}</span>
              </div>
              <h3 className="news-title">{news.title}</h3>
              {news.trending && (
                <div className="trending-indicator">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12.9 7.5H10.7V5.3C10.7 5.1 10.5 5 10.4 5H8.6C8.5 5 8.3 5.1 8.3 5.3V7.5H6.1C5.9 7.5 5.8 7.7 5.8 7.8V9.6C5.8 9.7 5.9 9.9 6.1 9.9H8.3V12.1C8.3 12.3 8.5 12.4 8.6 12.4H10.4C10.5 12.4 10.7 12.3 10.7 12.1V9.9H12.9C13.1 9.9 13.2 9.7 13.2 9.6V7.8C13.2 7.7 13.1 7.5 12.9 7.5Z" fill="currentColor"/>
                    <path d="M19 2H5C3.3 2 2 3.3 2 5V19C2 20.7 3.3 22 5 22H19C20.7 22 22 20.7 22 19V5C22 3.3 20.7 2 19 2ZM19 19H5V5H19V19Z" fill="currentColor"/>
                  </svg>
                  <span>Thịnh hành</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Bảng tin tức */}
      <div className="news-container">
        <h2 className="section-title">
          <svg className="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 5H7C5.89543 5 5 5.89543 5 7V19C5 20.1046 5.89543 21 7 21H17C18.1046 21 19 20.1046 19 19V7C19 5.89543 18.1046 5 17 5H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            <path d="M9 5C9 3.89543 9.89543 3 11 3H13C14.1046 3 15 3.89543 15 5C15 6.10457 14.1046 7 13 7H11C9.89543 7 9 6.10457 9 5Z" stroke="currentColor" strokeWidth="2"/>
            <path d="M9 12H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            <path d="M9 16H15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <div className="title-text-group">
            <span className="title-main">Tất cả tin tức</span>
            <span className="title-sub">Theo thứ tự thời gian</span>
          </div>
          <span className="section-arrow">›</span>
          <div className="news-filter">
            <span className="active">Tất cả</span>
            <span>Thịnh hành</span>
          </div>
        </h2>

        <div className="news-table-container">
          <table className="news-table">
            <thead>
              <tr>
                <th className="time-column">Thời gian</th>
                <th className="symbol-column">Ký hiệu</th>
                <th className="headline-column">Tiêu đề</th>
                <th className="provider-column">Nguồn</th>
              </tr>
            </thead>
            <tbody>
              {tableNews.map((news) => (
                <tr 
                  key={news.id} 
                  className={news.trending ? 'trending-row' : ''}
                  onClick={() => handleNewsClick(news.id)}
                >
                  <td className="time-column">{getTimeString(news.hours, news.days, news.isYesterday)}</td>
                  <td className="symbol-column">
                    <div className="symbol-container">
                      {renderFlag(news.country)}
                      <span className="symbol-text">{news.symbol}</span>
                    </div>
                  </td>
                  <td className="headline-column">
                    <div className="headline-container">
                      {news.trending && renderTrendingIcon()} 
                      <span>{news.title}</span>
                    </div>
                  </td>
                  <td className="provider-column">{news.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {newsData.length > 10 && (
            <div className="load-more-container">
              <button 
                className="load-more-button"
                onClick={() => setShowAllNews(!showAllNews)}
              >
                {showAllNews ? 'Thu gọn' : 'Xem thêm'} 
                <svg className={`arrow-icon ${showAllNews ? 'up' : 'down'}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M19 9L12 16L5 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default News;