import React, { useState, useEffect, memo } from 'react';
import './OrderTable.css';

const OrderTable = memo(({ currentPrice, lastPrice }) => {
  const [orders, setOrders] = useState([]);

  const generateRandomTime = () => {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
  };

  const generateRandomVolume = () => {
    const baseVolume = Math.floor(Math.random() * 5000000) + 100;
    if (Math.random() < 0.2) {
      return Math.floor(baseVolume / 1000) * 1000;
    }
    if (Math.random() < 0.1) {
      return baseVolume + 1000000;
    }
    return baseVolume;
  };

  const generateOrderData = (lastPriceValue, currentPriceValue) => {
    const percentChange = ((currentPriceValue / lastPriceValue - 1) * 100).toFixed(2);
    const isBuy = currentPriceValue >= lastPriceValue;
    return {
      time: generateRandomTime(),
      volume: generateRandomVolume(),
      price: currentPriceValue,
      percent: percentChange,
      type: isBuy ? 'Mua' : 'Bán'
    };
  };

  useEffect(() => {
    if (!currentPrice) return;

    const initializeOrderTable = () => {
      let initialPrice = currentPrice;
      const newOrders = [];
      for (let i = 0; i < 15; i++) {
        const randomChange = Math.floor(Math.random() * 100) - 50;
        const newPrice = Math.round((initialPrice + randomChange) * 100) / 100;
        newOrders.unshift(generateOrderData(initialPrice, newPrice));
        initialPrice = newPrice;
      }
      setOrders(newOrders);
    };

    initializeOrderTable();
  }, []);

  useEffect(() => {
    if (!currentPrice || !lastPrice || currentPrice === lastPrice) return;

    const addNewOrder = () => {
      const newOrder = generateOrderData(lastPrice, currentPrice);
      setOrders(prevOrders => {
        const updatedOrders = [newOrder, ...prevOrders].slice(0, 15);
        return updatedOrders;
      });
    };

    addNewOrder();
    const intervalId = setInterval(addNewOrder, 2000);
    return () => clearInterval(intervalId);
  }, [currentPrice, lastPrice]);

  return (
    <div className="order-container">
      <div className="order-header">
        <div className="title-badge">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '6px', verticalAlign: 'text-bottom' }}>
            <path d="M21 14H3M18 9H6M15 19H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Chi tiết khớp lệnh
        </div>
        <span>{orders.length}</span>
      </div>
      <div className="order-details">
        <table className="order-table">
          <thead>
            <tr>
              <th>Thời gian</th>
              <th>Khối lượng</th>
              <th>Giá</th>
              <th>%</th>
              <th>M/B</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order, index) => (
              <tr key={index}>
                <td>{order.time}</td>
                <td>{order.volume.toLocaleString()}</td>
                <td className={parseFloat(order.percent) > 0 ? 'price-up' : parseFloat(order.percent) < 0 ? 'price-down' : 'price-neutral'}>
                  {order.price.toLocaleString()}
                </td>
                <td className={parseFloat(order.percent) > 0 ? 'price-up' : parseFloat(order.percent) < 0 ? 'price-down' : 'price-neutral'}>
                  {parseFloat(order.percent) > 0 ? '+' + order.percent : order.percent}
                </td>
                <td className={`order-type ${order.type === 'Mua' ? 'price-up' : 'price-down'}`}>
                  {order.type}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
});

export default OrderTable;