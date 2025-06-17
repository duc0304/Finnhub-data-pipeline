import React, { useRef, useEffect, useState, useCallback, memo } from 'react';
import { createChart } from 'lightweight-charts';
import './Chart.css';

const Chart = memo(({ initialData, realtimeUpdates }) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const resizeObserverRef = useRef(null);
  const dataIndexRef = useRef(0);
  const transactionCountRef = useRef(0);
  const currentCandleRef = useRef(null);
  const [chartReady, setChartReady] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');

  const handleTimeframeChange = (timeframe) => {
    setSelectedTimeframe(timeframe);
    // Logic chuyển đổi khung thời gian sẽ được thêm sau
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chartOptions = {
      layout: {
        textColor: "black",
        background: { type: "solid", color: "white" },
      },
      height: chartContainerRef.current.clientHeight || 500,
      width: chartContainerRef.current.clientWidth || 800,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
        borderColor: '#D6DCDE',
      },
      grid: {
        vertLines: {
          color: 'rgba(0, 0, 0, 0.2)',
        },
        horzLines: {
          color: 'rgba(0, 0, 0, 0.2)',
        },
      },
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
      autoSize: true,
    };

    chartRef.current = createChart(chartContainerRef.current, chartOptions);
    seriesRef.current = chartRef.current.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });

    if (initialData && initialData.length > 0) {
      seriesRef.current.setData(initialData);
      // Lưu trữ cây nến cuối cùng từ dữ liệu ban đầu
      currentCandleRef.current = {...initialData[initialData.length - 1]};
      chartRef.current.timeScale().fitContent();
      chartRef.current.timeScale().scrollToPosition(5);
      setChartReady(true);
    }

    chartRef.current.subscribeCrosshairMove(param => {
      if (param && param.time && param.seriesPrices) {
        const price = param.seriesPrices.get(seriesRef.current);
        if (price) {
          handleCandleHover(price, param.point);
        }
      } else {
        const existingInfo = document.querySelector('.candle-info');
        if (existingInfo) {
          existingInfo.remove();
        }
      }
    });

    let resizeTimeout;
    resizeObserverRef.current = new ResizeObserver(entries => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        if (entries[0] && chartRef.current) {
          const { width, height } = entries[0].contentRect;
          chartRef.current.applyOptions({ 
            width, 
            height: height || 500
          });
        }
      }, 100);
    });

    if (chartContainerRef.current) {
      resizeObserverRef.current.observe(chartContainerRef.current);
    }

    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
      if (resizeObserverRef.current && chartContainerRef.current) {
        resizeObserverRef.current.unobserve(chartContainerRef.current);
        resizeObserverRef.current = null;
      }
      const existingInfo = document.querySelector('.candle-info');
      if (existingInfo) {
        existingInfo.remove();
      }
    };
  }, []);

  const handleCandleHover = useCallback((price, point) => {
    const candleInfo = document.createElement('div');
    candleInfo.className = 'candle-info';
    candleInfo.innerHTML = `
      <div style="padding: 5px; font-size: 14px;">
        <div><strong>Mở:</strong> ${price.open.toLocaleString()}</div>
        <div><strong>Cao:</strong> ${price.high.toLocaleString()}</div>
        <div><strong>Thấp:</strong> ${price.low.toLocaleString()}</div>
        <div><strong>Đóng:</strong> ${price.close.toLocaleString()}</div>
      </div>
    `;
    
    const existingInfo = document.querySelector('.candle-info');
    if (existingInfo) {
      existingInfo.remove();
    }
    
    document.body.appendChild(candleInfo);
    
    if (chartContainerRef.current) {
      const containerRect = chartContainerRef.current.getBoundingClientRect();
      candleInfo.style.position = 'absolute';
      candleInfo.style.left = `${point.x + containerRect.left + 15}px`;
      candleInfo.style.top = `${point.y + containerRect.top - 100}px`;
      candleInfo.style.zIndex = '1000';
    }
  }, []);

  useEffect(() => {
    if (!chartReady || !seriesRef.current || !realtimeUpdates || realtimeUpdates.length === 0) return;

    const intervalId = setInterval(() => {
      if (dataIndexRef.current < realtimeUpdates.length) {
        const update = realtimeUpdates[dataIndexRef.current];
        
        // Cập nhật đếm số giao dịch
        transactionCountRef.current += 1;
        
        // Cập nhật cây nến hiện tại
        if (currentCandleRef.current) {
          const updatedCandle = {
            time: currentCandleRef.current.time,
            open: currentCandleRef.current.open,
            high: Math.max(currentCandleRef.current.high, update.close),
            low: Math.min(currentCandleRef.current.low, update.close),
            close: update.close
          };
          
          // Nếu đã đạt 50 giao dịch, tạo cây nến mới
          if (transactionCountRef.current >= 50) {
            // Tạo cây nến mới với giá đóng của cây nến hiện tại làm giá mở
            const newCandleTime = update.time;
            const newCandle = {
              time: newCandleTime,
              open: updatedCandle.close,
              high: updatedCandle.close,
              low: updatedCandle.close,
              close: updatedCandle.close
            };
            
            // Cập nhật cây nến trước khi reset
            seriesRef.current.update(updatedCandle);
            
            // Sau đó tạo cây nến mới
            setTimeout(() => {
              seriesRef.current.update(newCandle);
              currentCandleRef.current = newCandle;
            }, 50);
            
            // Reset bộ đếm giao dịch
            transactionCountRef.current = 0;
          } else {
            // Cập nhật cây nến hiện tại
            seriesRef.current.update(updatedCandle);
            currentCandleRef.current = updatedCandle;
          }
        } else {
          // Nếu chưa có cây nến hiện tại, tạo một cái mới
          currentCandleRef.current = update;
          seriesRef.current.update(update);
        }
        
        dataIndexRef.current += 1;
      } else {
        clearInterval(intervalId);
      }
    }, 2000);

    return () => clearInterval(intervalId);
  }, [chartReady, realtimeUpdates]);

  const showGoToRealtimeButton = dataIndexRef.current > 5;
  const handleGoToRealtime = useCallback(() => {
    if (chartRef.current) {
      chartRef.current.timeScale().scrollToRealTime();
    }
  }, []);

  return (
    <div className="chart-wrapper">
      <div className="chart-header">
        <div className="title-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '6px', verticalAlign: 'text-bottom' }}>
            <path d="M3 9L7 5M7 5L11 9M7 5V16M21 15L17 19M17 19L13 15M17 19V8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Biểu đồ giá
        </div>
        <div className="timeframe-selector">
          <button 
            className={`timeframe-button ${selectedTimeframe === '1D' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('1D')}
          >
            1D
          </button>
          <button 
            className={`timeframe-button ${selectedTimeframe === '1M' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('1M')}
          >
            1M
          </button>
          <button 
            className={`timeframe-button ${selectedTimeframe === '1Y' ? 'active' : ''}`}
            onClick={() => handleTimeframeChange('1Y')}
          >
            1Y
          </button>
        </div>
      </div>
      <div ref={chartContainerRef} className="chart-content" />
      {showGoToRealtimeButton && (
        <div className="buttons-container">
          <button onClick={handleGoToRealtime}>Go to realtime</button>
        </div>
      )}
    </div>
  );
});

export default Chart;