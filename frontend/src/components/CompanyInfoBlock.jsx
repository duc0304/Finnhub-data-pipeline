import React from 'react';
import './CompanyInfoBlock.css';

const CompanyInfoBlock = ({ currentPrice, lastPrice }) => {
  const calculatePriceChange = () => {
    if (!currentPrice || !lastPrice) return { percentage: 0 };
    const change = currentPrice - lastPrice;
    const percentage = (change / lastPrice) * 100;
    return {
      percentage: percentage.toFixed(2)
    };
  };

  const priceChange = calculatePriceChange();
  const isPositive = currentPrice > lastPrice;
  const isNegative = currentPrice < lastPrice;

  const formatPrice = (price) => {
    if (!price) return '171,800.0';
    return price.toLocaleString('vi-VN', { 
      minimumFractionDigits: 1, 
      maximumFractionDigits: 1 
    });
  };

  return (
    <div className="company-info-block">
      {/* Section 1: Thông tin công ty */}
      <div className="company-info-section">
        <div className="company-logo">DNT</div>
        <div className="company-details">
          <h2 className="company-name">Công ty Cổ phần FPT<span className="stock-code">(FPT)</span></h2>
          <p className="company-meta"><strong>Thành lập:</strong> 1988</p>
          <p className="company-meta"><strong>Trụ sở:</strong> Hà Nội, Việt Nam</p>
          <p className="company-meta"><strong>Ngành:</strong> Công nghệ, Phần mềm và dịch vụ CNTT</p>
          
          <div className="company-description">Công ty Cổ phần FPT (FPT) có tiền thân là Công ty Công nghệ Thực phẩm được thành lập năm 1988.  Công ty hoạt động chính trong lĩnh vực phần mềm, công nghệ thông tin, tích hợp hệ thống, viễn thông, và giáo dục đào tạo. FPT chính thức hoạt động theo mô hình công ty cổ phần từ năm 2002. FPT sở hữu hơn 100 giải pháp phần mềm được cấp bản quyền trong các lĩnh vực chuyên biệt, mạng lưới hạ tầng internet phủ rộng khắp tới 59/63 tỉnh thành của cả nước.  
          </div>
          
          <div className="company-links-grid">
            <div className="link-item-container">
              <div className="link-item">
                <div className="link-icon-wrapper">
                  <svg className="link-svg-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21Z" stroke="currentColor" strokeWidth="2"/>
                    <path d="M12 8V16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    <path d="M8 12H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>
                <a href="#" className="company-link">Website công ty - Company Website</a>
              </div>
            </div>
            <div className="link-item-container">
              <div className="link-item">
                <div className="link-icon-wrapper">
                  <svg className="link-svg-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2"/>
                  </svg>
                </div>
                <a href="#" className="company-link">Lịch sử trả cổ tức</a>
              </div>
            </div>
            <div className="link-item-container">
              <div className="link-item">
                <div className="link-icon-wrapper">
                  <svg className="link-svg-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 7L12 3L4 7M20 7V17L12 21M20 7L12 11M12 21L4 17V7M12 21V11M4 7L12 11" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <a href="#" className="company-link">Báo cáo tài chính</a>
              </div>
            </div>
            <div className="link-item-container">
              <div className="link-item">
                <div className="link-icon-wrapper">
                  <svg className="link-svg-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="8" r="5" stroke="currentColor" strokeWidth="2"/>
                    <path d="M20 21C20 16.5817 16.4183 13 12 13C7.58172 13 4 16.5817 4 21" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </div>
                <a href="#" className="company-link">Cơ cấu cổ đông</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Thông tin giá và khuyến nghị */}
      <div className="price-recommendation-section">
        {/* Phần trên hiển thị giá và range */}
        <div className="price-top-section">
          <div className="price-header">
            <span className="current-price">{formatPrice(currentPrice)}</span>
            <span className={`percentage-badge ${isPositive ? 'positive' : isNegative ? 'negative' : ''}`}>
              <i className={isPositive ? 'arrow-up' : 'arrow-down'}></i>
              {priceChange.percentage}%
            </span>
          </div>
          <div className="price-range">
            <div className="range-values">
              <span className="range-value">23,600</span>
              <span className="range-value">27,300</span>
            </div>
            <div className="range-bar">
              <div className="range-fill" style={{ width: '54%' }}></div>
              <div className="current-marker" style={{ left: '53%' }}></div>
            </div>
            <div className="range-labels">
              <span className="range-label">Giá thấp nhất</span>
              <span className="range-label">Giá cao nhất</span>
            </div>
          </div>
        </div>

        {/* Phần dưới chia đôi: metrics và khuyến nghị */}
        <div className="info-recommendation-container">
          {/* Phần thông tin tài chính */}
          <div className="financial-metrics">
            <div className="metrics-grid">
              <div className="metric-item">
                <p>
                  <span className="metric-label">Vốn hóa</span>
                  <strong>1,200 tỷ VND</strong>
                </p>
              </div>
              <div className="metric-item">
                <p>
                  <span className="metric-label">CP phát hành</span>
                  <strong>50,000,000</strong>
                </p>
              </div>
              <div className="metric-item">
                <p>
                  <span className="metric-label">Chỉ số P/E</span> 
                  <strong>
                    52.61
                    <span className="tooltip-icon" title="Tỷ lệ giữa giá cổ phiếu và thu nhập trên mỗi cổ phiếu">i</span>
                  </strong>
                </p>
              </div>
              <div className="metric-item">
                <p>
                  <span className="metric-label">Chỉ số P/B</span> 
                  <strong>
                    11.3
                    <span className="tooltip-icon" title="Tỷ lệ giữa giá cổ phiếu và giá trị sổ sách mỗi cổ phiếu">i</span>
                  </strong>
                </p>
              </div>
              <div className="metric-item">
                <p>
                  <span className="metric-label">ROE</span> 
                  <strong>
                    21.5%
                    <span className="tooltip-icon" title="Tỷ suất lợi nhuận trên vốn chủ sở hữu, đo lường hiệu quả sử dụng vốn của công ty">i</span>
                  </strong>
                </p>
              </div>
              <div className="metric-item">
                <p>
                  <span className="metric-label">EPS</span> 
                  <strong>
                    3,265 VND
                    <span className="tooltip-icon" title="Thu nhập trên mỗi cổ phiếu, phản ánh lợi nhuận công ty trên mỗi cổ phần">i</span>
                  </strong>
                </p>
              </div>
              <div className="metric-item wide">
                <p>
                  <span className="metric-label">Khối lượng giao dịch</span>
                  <strong>2,500,000</strong>
                </p>
              </div>
            </div>
          </div>

          {/* Phần khuyến nghị */}
          <div className="recommendation-section">
            <div className="recommendation-card">
              <h3 className="recommendation-title">Khuyến nghị đầu tư</h3>
              
              <div className="recommendation-rating-container">
                <div className="recommendation-rating-item">
                  <div className="rating-label">Định giá</div>
                  <div className="rating-value medium">Hợp lý</div>
                </div>
                
                <div className="recommendation-rating-item">
                  <div className="rating-label">Rủi ro</div>
                  <div className="rating-value medium">Trung bình</div>
                </div>
                
                <div className="recommendation-rating-item">
                  <div className="rating-label">Tiềm năng</div>
                  <div className="rating-value high">Cao</div>
                </div>
              </div>
              
              <div className="recommendation-decision">
                <span className="decision-badge positive">Nên đầu tư</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyInfoBlock;