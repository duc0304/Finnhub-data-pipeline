import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import StockDetail from './pages/Stocks';
import StocksList from './pages/StocksList';
import News from './pages/News';
import NewsDetail from './pages/NewsDetail';
import Recommendations from './pages/Recommendations';

const App = () => {
  return (
    <Router>
      <div className="app-wrapper">
        <Header />
        <Routes>
          <Route path="/" element={<StocksList />} />
          <Route path="/stocks" element={<StocksList />} />
          <Route path="/stock/:id" element={<StockDetail />} />
          <Route path="/news" element={<News />} />
          <Route path="/news/:id" element={<NewsDetail />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/contact" element={
            <div className="main-container">
              <h1>Trang Liên hệ</h1>
              <p>Nội dung trang liên hệ sẽ được cập nhật sau.</p>
            </div>
          } />
        </Routes>
      </div>
    </Router>
  );
};

export default App;