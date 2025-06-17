import { useState, useEffect, useRef } from 'react';

const useChartData = () => {
  const [initialData, setInitialData] = useState([]);
  const [realtimeUpdates, setRealtimeUpdates] = useState([]);
  const [currentPrice, setCurrentPrice] = useState(0);
  const [lastPrice, setLastPrice] = useState(0);
  const [dataGenerationComplete, setDataGenerationComplete] = useState(false);
  const dataIndexRef = useRef(0);

  const samplePoint = (i, randomFactor) => 
    i * (0.5 + 
      Math.sin(i / 1) * 0.2 + 
      Math.sin(i / 2) * 0.4 + 
      Math.sin(i / randomFactor) * 0.8 + 
      Math.sin(i / 50) * 0.5) + 
    200 + 
    i * 2;

  useEffect(() => {
    const generateData = (numberOfCandles = 500, updatesPerCandle = 5, startAt = 100) => {
      const createCandle = (val, time) => ({
        time,
        open: val,
        high: val,
        low: val,
        close: val,
      });
    
      const updateCandle = (candle, val) => ({
        time: candle.time,
        close: val,
        open: candle.open,
        low: Math.min(candle.low, val),
        high: Math.max(candle.high, val),
      });
    
      const randomFactor = 25 + Math.random() * 25;
      const date = new Date(Date.UTC(2023, 3, 1, 12, 0, 0, 0));
      const numberOfPoints = numberOfCandles * updatesPerCandle;
      let initialDataTemp = [];
      let realtimeUpdatesTemp = [];
      let lastCandle;
      let previousValue = samplePoint(-1, randomFactor);
      
      for (let i = 0; i < numberOfPoints; ++i) {
        if (i % updatesPerCandle === 0) {
          date.setUTCDate(date.getUTCDate() + 1);
          
          if (date.getUTCDate() === 1 && date.getUTCMonth() === 3) {
            date.setUTCMonth(4);
          }
        }
        const time = date.getTime() / 1000;
        let value = samplePoint(i, randomFactor);
        const diff = (value - previousValue) * Math.random();
        value = previousValue + diff;
        previousValue = value;
        
        if (i % updatesPerCandle === 0) {
          const candle = createCandle(value, time);
          lastCandle = candle;
          if (i >= startAt) {
            realtimeUpdatesTemp.push(candle);
          }
        } else {
          const newCandle = updateCandle(lastCandle, value);
          lastCandle = newCandle;
          if (i >= startAt) {
            realtimeUpdatesTemp.push(newCandle);
          } else if ((i + 1) % updatesPerCandle === 0) {
            initialDataTemp.push(newCandle);
          }
        }
      }
      
      setInitialData(initialDataTemp);
      setRealtimeUpdates(realtimeUpdatesTemp);
      
      if (initialDataTemp.length > 0) {
        const latestPrice = initialDataTemp[initialDataTemp.length - 1].close;
        setCurrentPrice(latestPrice);
        setLastPrice(latestPrice);
      } else {
        setCurrentPrice(25600);
        setLastPrice(25600);
      }
      
      setDataGenerationComplete(true);
    };
    
    generateData(2500, 20, 1000);
  }, []);

  useEffect(() => {
    if (!dataGenerationComplete || !realtimeUpdates || realtimeUpdates.length === 0) return;

    const intervalId = setInterval(() => {
      if (dataIndexRef.current < realtimeUpdates.length) {
        const update = realtimeUpdates[dataIndexRef.current];
        setLastPrice(currentPrice);
        setCurrentPrice(update.close);
        dataIndexRef.current += 1;
      } else {
        clearInterval(intervalId);
      }
    }, 2000);

    return () => clearInterval(intervalId);
  }, [dataGenerationComplete, realtimeUpdates, currentPrice]);

  return {
    initialData,
    realtimeUpdates,
    currentPrice,
    lastPrice,
    dataGenerationComplete,
  };
};

export default useChartData;