import React, { useState, useRef, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import './Header.css';

const Header = () => {
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isNotificationOpen, setIsNotificationOpen] = useState(false);
  const searchRef = useRef(null);
  const notificationRef = useRef(null);

  // Mock notifications data
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: 'urgent',
      icon: '🔴',
      title: 'MACD Bullish Crossover - BTC',
      message: 'BTC báo hiệu thay đổi xu hướng tăng. Cơ hội mua vào!',
      time: '2 phút trước',
      isRead: false,
      symbol: 'BTC',
      price: '$67,420.50',
      change: '+2.3%'
    },
    {
      id: 2,
      type: 'warning',
      icon: '🟡',
      title: 'RSI Overbought - AAPL',
      message: 'Apple đang trong vùng mua quá mức (RSI > 70)',
      time: '15 phút trước',
      isRead: false,
      symbol: 'AAPL',
      price: '$193.85',
      change: '+0.81%'
    },
    {
      id: 3,
      type: 'info',
      icon: '🔵',
      title: 'Tin tức quan trọng',
      message: 'Fed công bố quyết định lãi suất mới',
      time: '1 giờ trước',
      isRead: true,
      symbol: 'NEWS',
      price: '',
      change: ''
    }
  ]);

  const unreadCount = notifications.filter(notif => !notif.isRead).length;
  
  // Xử lý click bên ngoài để đóng dropdowns
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsSearchFocused(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setIsNotificationOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === id ? { ...notif, isRead: true } : notif
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notif => ({ ...notif, isRead: true }))
    );
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <svg viewBox="0 0 36 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 22L10 18L6 22L2 18M34 26L30 22L26 26M34 6L30 10L26 6M14 10V18M6 2V14M34 14V22M22 2V26" 
                 stroke="#2962FF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>TradeView</span>
        </div>
        
        <div className="navigation-container">
          <nav className="navigation">
            <NavLink to="/stocks" className={({isActive}) => `nav-button ${isActive ? 'active' : ''}`}>
              <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 2V19C2 20.1046 2.89543 21 4 21H22" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M5 16L10 11L14 15L21 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Danh mục cổ phiếu
            </NavLink>
            <NavLink to="/news" className={({isActive}) => `nav-button ${isActive ? 'active' : ''}`}>
              <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" strokeWidth="2"/>
                <path d="M10 8H7V13H10V8Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                <path d="M17 8H12V10H17V8Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                <path d="M17 12H12V13H17V12Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                <path d="M7 15H17V16H7V15Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
              </svg>
              Tin tức
            </NavLink>
            <NavLink to="/recommendations" className={({isActive}) => `nav-button ${isActive ? 'active' : ''}`}>
              <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Khuyến nghị đầu tư
            </NavLink>
            <NavLink to="/contact" className={({isActive}) => `nav-button ${isActive ? 'active' : ''}`}>
              <svg className="nav-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 5C3 3.89543 3.89543 3 5 3H8.27924C8.70967 3 9.09181 3.27543 9.22792 3.68377L10.7279 8.68377C10.8826 9.14448 10.6352 9.64149 10.1945 9.82982L7.33447 11.0213C8.4536 13.2025 10.2746 14.9328 12.5059 15.9662L13.6163 13.1719C13.8138 12.7448 14.3061 12.5139 14.7554 12.6515L19.8373 14.1202C20.2695 14.2658 20.5532 14.6626 20.5532 15.1017V19C20.5532 20.1046 19.6577 21 18.5532 21H17C9.26801 21 3 14.732 3 7V5Z" stroke="currentColor" strokeWidth="2"/>
              </svg>
              Liên hệ
            </NavLink>
          </nav>
          
          <div 
            ref={searchRef} 
            className={`search-container ${isSearchFocused ? 'expanded' : ''}`}
          >
            <div className="search-input-wrapper">
              <svg className="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" 
                     stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <input
                type="text"
                placeholder="Tìm kiếm cổ phiếu, tin tức..."
                onFocus={() => setIsSearchFocused(true)}
                className="search-input"
              />
              {isSearchFocused && (
                <button className="clear-button" onClick={() => {
                  const input = searchRef.current.querySelector('input');
                  if (input) {
                    input.value = '';
                    input.focus();
                  }
                }}>
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </button>
              )}
            </div>
            
            {isSearchFocused && (
              <div className="search-dropdown">
                <div className="search-dropdown-header">
                  <span>Kết quả tìm kiếm gần đây</span>
                  <button className="clear-all">Xóa tất cả</button>
                </div>
                <div className="search-results">
                  <div className="search-result-item">
                    <div className="result-icon stock">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2"/>
                        <path d="M16 12H12V8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <div className="result-content">
                      <div className="result-title">VNM</div>
                      <div className="result-subtitle">Vinamilk</div>
                    </div>
                  </div>
                  <div className="search-result-item">
                    <div className="result-icon news">
                      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V5C21 3.89543 20.1046 3 19 3Z" stroke="currentColor" strokeWidth="2"/>
                        <path d="M10 8H7V13H10V8Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                        <path d="M17 8H12V10H17V8Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                        <path d="M17 12H12V13H17V12Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                        <path d="M7 15H17V16H7V15Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <div className="result-content">
                      <div className="result-title">Tin tức thị trường</div>
                      <div className="result-subtitle">Cập nhật thị trường ngày 12/06</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        <div className="user-actions">
          {/* Notification Bell */}
          <div 
            ref={notificationRef}
            className={`notification-container ${isNotificationOpen ? 'active' : ''}`}
          >
            <button 
              className="notification-button"
              onClick={() => setIsNotificationOpen(!isNotificationOpen)}
            >
              <svg className="bell-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 8A6 6 0 0 0 6 8C6 15 3 17 3 17H21S18 15 18 8Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M13.73 21C13.5542 21.3031 13.3019 21.5547 12.9982 21.7295C12.6946 21.9044 12.3504 21.9965 12 21.9965C11.6496 21.9965 11.3054 21.9044 11.0018 21.7295C10.6982 21.5547 10.4458 21.3031 10.27 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              {unreadCount > 0 && (
                <span className="notification-badge">{unreadCount}</span>
              )}
            </button>

            {isNotificationOpen && (
              <div className="notification-dropdown">
                <div className="notification-header">
                  <h3>Thông báo</h3>
                  {unreadCount > 0 && (
                    <button className="mark-all-read" onClick={markAllAsRead}>
                      Đánh dấu tất cả đã đọc
                    </button>
                  )}
                </div>
                
                <div className="notification-list">
                  {notifications.map(notification => (
                    <div 
                      key={notification.id}
                      className={`notification-item ${notification.type} ${notification.isRead ? 'read' : 'unread'}`}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div className="notification-icon">
                        {notification.icon}
                      </div>
                      
                      <div className="notification-content">
                        <div className="notification-title">
                          {notification.title}
                        </div>
                        <div className="notification-message">
                          {notification.message}
                        </div>
                        <div className="notification-meta">
                          <span className="notification-time">{notification.time}</span>
                          {notification.symbol && notification.symbol !== 'NEWS' && (
                            <div className="notification-price">
                              <span className="symbol">{notification.symbol}</span>
                              <span className="price">{notification.price}</span>
                              <span className={`change ${notification.change.startsWith('+') ? 'positive' : 'negative'}`}>
                                {notification.change}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {!notification.isRead && (
                        <div className="unread-indicator"></div>
                      )}
                    </div>
                  ))}
                </div>
                
                <div className="notification-footer">
                  <button className="view-all-button">
                    Xem tất cả thông báo
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User Avatar */}
          <button className="user-button">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 15C15.3137 15 18 12.3137 18 9C18 5.68629 15.3137 3 12 3C8.68629 3 6 5.68629 6 9C6 12.3137 8.68629 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M2.90625 20.2491C3.82834 18.6531 5.1542 17.3278 6.75064 16.4064C8.34708 15.485 10.1579 15 12.0004 15C13.8429 15 15.6536 15.4851 17.2501 16.4065C18.8466 17.3279 20.1724 18.6533 21.0944 20.2493" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 