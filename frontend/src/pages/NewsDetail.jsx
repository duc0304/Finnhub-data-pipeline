import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './NewsDetail.css';

const NewsDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [newsDetail, setNewsDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [relatedNews, setRelatedNews] = useState([]);

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

  useEffect(() => {
    // Dữ liệu tin tức mẫu
    const newsData = [
      {
        id: 1,
        hours: 7,
        source: 'Dow Jones Newswires',
        title: 'Naver 1Q Net Slumps on Higher Costs',
        content: `<p>Naver Corp. (035420.SE) reported a 76% drop in first-quarter net profit due to higher costs.</p>
        <p>The South Korean internet company said Wednesday that net profit fell to 33.03 billion Korean won ($24.0 million) from KRW137.31 billion a year earlier. The result was below a FactSet consensus of KRW204.41 billion, based on a poll of eight analysts.</p>
        <p>Revenue rose 9.9% on year to KRW2.391 trillion, led by the search platform's 10% growth to KRW1.126 trillion. First-quarter revenue matched a FactSet consensus.</p>
        <p>Operating profit more than halved to KRW100.48 billion. Costs increased 20% from a year ago to KRW2.290 trillion.</p>
        <p>Shares were recently 2.7% lower at KRW149,400 after the results.</p>`,
        trending: true,
        country: 'kr',
        symbol: 'N',
        author: 'Kwanwoo Jun',
        publishTime: '15:43 GMT+7',
        category: 'Earnings',
        image: 'https://example.com/images/naver.jpg'
      },
      {
        id: 2,
        hours: 18,
        source: 'Dow Jones Newswires',
        title: 'Toyota Expects U.S. Tariffs, Material Costs to Dent Profit',
        content: `<p>TOKYO--Toyota Motor Corp. (7203.TO) expects a drop in profit this fiscal year, anticipating a hit from tariffs and trade policies, particularly in the large U.S. market, and from higher material prices.</p>
        <p>The world's biggest car maker by sales volume also plans fewer vehicle sales world-wide in the year through March 2025, as consumer spending remains under pressure amid persistent inflation.</p>
        <p>Toyota on Wednesday forecast a fiscal year operating profit of Y4.0 trillion ($25.78 billion), compared with a record Y4.90 trillion in the year ended March 31. It expects to sell 10.98 million vehicles globally this year, down from 11.09 million last year.</p>
        <p>A drop in annual profit would mark a break from the string of strong results by Toyota compared with rivals, as it has overcome a series of challenges in recent years including vehicle recalls, the COVID-19 pandemic, a shortage of chips and other parts, inflation and supply-chain disruptions.</p>
        <p>Toyota said the bleaker profit outlook doesn't reflect the continued impact of production irregularities related to manipulated certification testing by two subsidiaries, which have led to a sales halt of affected vehicles and production suspensions.</p>`,
        country: 'jp',
        symbol: 'T',
        author: 'Chukyo Keiichi',
        publishTime: '08:15 GMT+7',
        category: 'Corporate News',
        image: 'https://example.com/images/toyota.jpg'
      },
      {
        id: 3,
        hours: 18,
        source: 'Dow Jones Newswires',
        title: 'Jobless Claims Fell Last Week',
        content: `<p>Initial unemployment-insurance claims fell by 8,000 to 212,000 in the week ended May 4, the Labor Department said Thursday. The figure is slightly below economist forecasts of 214,000.</p>
        <p>Continuing claims, which reflect the number of people seeking ongoing unemployment benefits, fell to 1.781 million in the week ended April 27. The four-week moving average, which helps smooth out volatility, decreased to 1.793 million.</p>
        <p>The data suggests the jobs market remains tight, with employers reluctant to lay off workers despite recent signs of some cooling in hiring and wage growth. The employment report released last week showed a slowing pace of hiring in April, with the unemployment rate ticking up to 3.9%.</p>
        <p>Economists are closely monitoring unemployment claims for early signs that the labor market may be cracking under the weight of high interest rates and slowing economic growth. So far, the data suggests labor-market conditions remain relatively strong, with layoffs remaining at low levels compared with historical standards.</p>
        <p>Fed officials have been watching for a gentle cooling of the labor market that would help ease wage and price pressures without triggering a sharp rise in unemployment. Recent data suggest they might be getting their wish, with job growth continuing but at a more moderate pace.</p>`,
        trending: true,
        country: 'us',
        symbol: 'US',
        author: 'David Harrison',
        publishTime: '13:10 GMT+7',
        category: 'Economic News',
        image: 'https://example.com/images/jobless.jpg'
      },
      {
        id: 4,
        hours: 19, 
        source: 'TradingView',
        title: 'EUR/USD: Dollar Powers Up as Fed\'s Powell Says Rates Stay Unchanged. Trump Calls Him a "FOOL"',
        content: `<p>The EUR/USD pair dipped below 1.07 after Federal Reserve Chair Jerome Powell's press conference where he indicated that interest rates would remain unchanged for the foreseeable future.</p>
        <p>Powell emphasized that the Fed needs to see more evidence that inflation is moving sustainably toward its 2% target before considering rate cuts. "The committee is not thinking about rate hikes at this time," Powell said, "but is focused on determining how long to maintain the current restrictive policy stance."</p>
        <p>Markets had hoped for signals of potential rate cuts in the coming months, but Powell's cautious tone disappointed those expectations, sending the dollar higher across the board.</p>
        <p>Former President Donald Trump swiftly responded to the Fed's decision, calling Powell a "fool" on his social media platform. Trump accused the Fed chair of playing politics by keeping rates high during an election year.</p>
        <p>Technical analysts note that EUR/USD now faces key support at 1.0650, with a break below potentially opening the way to 1.0600. On the upside, resistance is seen at 1.0750 and then the 1.0800 level.</p>
        <p>Traders are now looking ahead to Friday's non-farm payrolls report for additional clues about the U.S. economy's health and the future path of monetary policy.</p>`,
        country: 'eu-us',
        symbol: 'EU-US',
        author: 'Maria Rodriguez',
        publishTime: '07:45 GMT+7',
        category: 'Forex',
        image: 'https://example.com/images/eurusd.jpg'
      },
      {
        id: 5,
        hours: 19,
        source: 'Dow Jones Newswires',
        title: 'Bank of England Cuts Key Rate After Fed Stands Pat',
        content: `<p>LONDON—The Bank of England cut its key interest rate for the first time in more than four years Thursday, a day after the Federal Reserve signaled it would keep borrowing costs steady as it waits for clearer signs that inflation is headed back to its 2% target.</p>
        <p>The BOE cut its key rate to 5% from 5.25%, having left it unchanged at 16-year high since August 2023. The Monetary Policy Committee voted 5-4 in favor of the move, which was in line with expectations from economists and investors.</p>
        <p>The cut was the first since March 2020, when the central bank slashed its key rate as the Covid-19 pandemic hit. But it comes later than reductions by other major central banks, with the European Central Bank having reduced its key rate in June and the Swiss National Bank acting in March.</p>
        <p>The Bank of England has been more cautious because of worries about longer-lasting inflation in the services sector, which is fueled by strong wage growth. But with the headline rate of inflation having fallen back to its 2% target in May and then below it in June, policy makers were persuaded that a move was warranted.</p>
        <p>"Inflation has returned to target more rapidly than expected, reflecting larger falls in goods and energy price inflation, and is likely to fall further below target in the near term," the Bank of England said in a statement.</p>`,
        trending: true,
        country: 'gb',
        symbol: 'UK',
        author: 'Paul Hannon',
        publishTime: '14:30 GMT+7',
        category: 'Monetary Policy',
        image: 'https://example.com/images/boe.jpg'
      }
    ];

    // Tìm tin tức dựa trên id
    const newsItem = newsData.find(item => item.id === parseInt(id));
    
    if (newsItem) {
      setNewsDetail(newsItem);
      
      // Tìm tin tức liên quan (cùng quốc gia hoặc category)
      const related = newsData
        .filter(item => item.id !== parseInt(id) && (item.country === newsItem.country || item.category === newsItem.category))
        .slice(0, 3);
      
      setRelatedNews(related);
      setLoading(false);
    } else {
      // Nếu không tìm thấy, chuyển về trang tin tức chính
      navigate('/news');
    }
  }, [id, navigate]);

  const handleBackClick = () => {
    navigate('/news');
  };

  if (loading) {
    return (
      <div className="news-detail-page">
        <div className="loading-container">
          <div className="loader"></div>
          <p>Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="news-detail-page">
      <div className="news-detail-header">
        <button className="back-button" onClick={handleBackClick}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Quay lại tin tức
        </button>
      </div>

      <div className="news-detail-container">
        <div className="news-detail-meta">
          {renderFlag(newsDetail.country)}
          <span className="news-detail-symbol">{newsDetail.symbol}</span>
          <span className="news-detail-dot">•</span>
          <span className="news-detail-time">{getTimeString(newsDetail.hours, newsDetail.days, newsDetail.isYesterday)}</span>
          <span className="news-detail-dot">•</span>
          <span className="news-detail-source">{newsDetail.source}</span>
          {newsDetail.trending && (
            <div className="news-trending-badge">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C9.39 2.11 6.22 3.25 5 6.92C5.02 6.92 6.57 4.92 8.5 4.92C11.55 4.92 10.5 8.92 11.5 10.92C12.5 12.92 15 11.92 15 14.92C15 17.92 12 18.98 12 18.98C12 18.98 15.98 18.92 17.5 14.92C19.02 10.92 16.04 8.92 16.04 8.92C16.04 8.92 18.04 4.92 12 2Z" fill="#ff4136" stroke="#ff4136" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Thịnh hành</span>
            </div>
          )}
        </div>

        <h1 className="news-detail-title">{newsDetail.title}</h1>
        
        <div className="news-detail-author-info">
          <span className="news-detail-author">Tác giả: {newsDetail.author}</span>
          <span className="news-detail-publish-time">Đăng lúc: {newsDetail.publishTime}</span>
          <span className="news-detail-category">Danh mục: {newsDetail.category}</span>
        </div>

        <div className="news-detail-content" dangerouslySetInnerHTML={{ __html: newsDetail.content }}></div>
        
        {relatedNews.length > 0 && (
          <div className="related-news-section">
            <h2 className="related-news-title">Tin tức liên quan</h2>
            <div className="related-news-list">
              {relatedNews.map(news => (
                <div 
                  key={news.id}
                  className="related-news-item"
                  onClick={() => navigate(`/news/${news.id}`)}
                >
                  <div className="related-news-meta">
                    {renderFlag(news.country)}
                    <span className="related-news-time">{getTimeString(news.hours, news.days, news.isYesterday)}</span>
                    <span className="news-detail-dot">•</span>
                    <span className="related-news-source">{news.source}</span>
                  </div>
                  <h3 className="related-news-headline">{news.title}</h3>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NewsDetail; 