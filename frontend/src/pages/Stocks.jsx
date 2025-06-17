import React, { useMemo, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Chart from '../components/Chart';
import OrderTable from '../components/OrderTable';
import CompanyInfoBlock from '../components/CompanyInfoBlock';
import useChartData from '../hooks/useChartData';
import './StockDetail.css';

const StockDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [stockInfo, setStockInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const { initialData, realtimeUpdates, currentPrice, lastPrice, dataGenerationComplete } = useChartData();

  const chartData = useMemo(() => ({
    initialData,
    realtimeUpdates
  }), [initialData, realtimeUpdates]);

  const priceData = useMemo(() => ({
    currentPrice,
    lastPrice
  }), [currentPrice, lastPrice]);

  // Mock data các công ty
  useEffect(() => {
    const mockStocks = [
      {
        id: 1, 
        symbol: 'FPT', 
        name: 'Công ty Cổ phần FPT',
        founded: '1988',
        headquarters: 'Hà Nội, Việt Nam',
        industry: 'Công nghệ, Phần mềm và dịch vụ CNTT'
      },
      {
        id: 2, 
        symbol: 'VNM', 
        name: 'Công ty Cổ phần Sữa Việt Nam',
        founded: '1976',
        headquarters: 'TP. Hồ Chí Minh, Việt Nam',
        industry: 'Hàng tiêu dùng, Thực phẩm & Đồ uống'
      },
      {
        id: 3, 
        symbol: 'VCB', 
        name: 'Ngân hàng TMCP Ngoại thương Việt Nam',
        founded: '1963',
        headquarters: 'Hà Nội, Việt Nam',
        industry: 'Tài chính, Ngân hàng'
      },
      {
        id: 4, 
        symbol: 'VIC', 
        name: 'Tập đoàn Vingroup',
        founded: '1993',
        headquarters: 'Hà Nội, Việt Nam',
        industry: 'Đa ngành, Bất động sản, Bán lẻ'
      },
      {
        id: 5, 
        symbol: 'HPG', 
        name: 'Công ty Cổ phần Tập đoàn Hoà Phát',
        founded: '1992',
        headquarters: 'Hà Nội, Việt Nam',
        industry: 'Thép, Vật liệu xây dựng'
      },
      {
        id: 6, 
        symbol: 'MWG', 
        name: 'Công ty Cổ phần Đầu tư Thế Giới Di Động',
        founded: '2004',
        headquarters: 'TP. Hồ Chí Minh, Việt Nam',
        industry: 'Bán lẻ, Công nghệ'
      },
      {
        id: 7, 
        symbol: 'VHM', 
        name: 'Công ty Cổ phần Vinhomes',
        founded: '2008',
        headquarters: 'Hà Nội, Việt Nam',
        industry: 'Bất động sản'
      },
      {
        id: 8, 
        symbol: 'ACB', 
        name: 'Ngân hàng TMCP Á Châu',
        founded: '1993',
        headquarters: 'TP. Hồ Chí Minh, Việt Nam',
        industry: 'Tài chính, Ngân hàng'
      }
    ];

    // Tìm thông tin công ty dựa vào id
    const foundStock = mockStocks.find(stock => stock.id === parseInt(id));
    
    if (foundStock) {
      setStockInfo(foundStock);
      setLoading(false);
    } else {
      // Nếu không tìm thấy, mặc định hiển thị FPT
      setStockInfo(mockStocks[0]);
      setLoading(false);
    }
  }, [id]);

  const handleBackClick = () => {
    navigate('/stocks');
  };

  if (loading) {
    return (
      <div className="main-container">
        <div className="loading-container">
          <div className="loader"></div>
          <p>Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="main-container">
      <div className="stock-detail-header">
        <button className="back-button" onClick={handleBackClick}>
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Quay lại danh sách
        </button>
        <h1>{stockInfo.symbol} - {stockInfo.name}</h1>
      </div>

      <CompanyInfoBlock 
        currentPrice={priceData.currentPrice}
        lastPrice={priceData.lastPrice}
      />
      <div className="content-container">
        <div className="chart-container">
          {dataGenerationComplete && (
            <Chart 
              initialData={chartData.initialData} 
              realtimeUpdates={chartData.realtimeUpdates}
            />
          )}
        </div>
        {dataGenerationComplete && (
          <OrderTable 
            currentPrice={priceData.currentPrice}
            lastPrice={priceData.lastPrice}
          />
        )}
      </div>
    </div>
  );
};

export default StockDetail; 