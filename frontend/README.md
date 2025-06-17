# DUCNT Stock Chart

Ứng dụng biểu đồ chứng khoán real-time sử dụng React và Lightweight Charts.

## Các tính năng

- Biểu đồ nến (candlestick) real-time
- Cập nhật dữ liệu theo thời gian thực
- Hiển thị thông tin chi tiết khi di chuột qua nến
- Tự động cập nhật kích thước khi thay đổi cửa sổ
- Nút "Go to realtime" để quay về dữ liệu mới nhất

## Cài đặt

1. Clone repository:

```
git clone <repository-url>
cd test-chart/frontend
```

2. Cài đặt dependencies:

```
npm install
```

3. Chạy ứng dụng:

```
npm start
```

Ứng dụng sẽ chạy ở [http://localhost:3000](http://localhost:3000).

## Cấu trúc dự án

- `src/App.jsx` - Component chính
- `src/components/Chart.jsx` - Component biểu đồ sử dụng lightweight-charts
- `src/hooks/useChartData.js` - Custom hook để xử lý và tạo dữ liệu cho biểu đồ

## Tối ưu hiệu suất

Các kỹ thuật được sử dụng để tối ưu hiệu suất:

1. `memo` - Tránh render lại không cần thiết cho Chart component
2. `useRef` - Lưu trữ giá trị mà không gây re-render
3. `useMemo` - Lưu trữ kết quả tính toán tránh tính toán lại khi re-render
4. `ResizeObserver` - Cập nhật kích thước chart mà không gây re-render toàn bộ component
5. `useCallback` - Đảm bảo tính nhất quán của hàm qua các lần render
