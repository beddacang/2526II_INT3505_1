# Hướng dẫn test API

Server sẽ chạy tại: `http://127.0.0.1:8000`

> FastAPI tự sinh tài liệu API Docs cực đẹp tại: `http://127.0.0.1:8000/docs`

## 1. Tiến hành Test chuỗi luồng thiết kế

### Bước 1: Test Query Pattern

- Method: `GET`
- URL: `http://127.0.0.1:8000/api/products?category=electronics&sort=-price&page=1&limit=2`

### Bước 2: Test CRUD & HATEOAS (Tạo đơn hàng)

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/orders`

Body (JSON):

```json
{
  "product_id": 1,
  "quantity": 2
}
```

> Hãy chú ý phần `_links` trả về từ kết quả, nó chứa endpoint giả lập webhook ở bước kế tiếp.

### Bước 3: Test Webhook & Event-driven

- Method: `POST`
- URL: `http://127.0.0.1:8000/api/webhooks/payment-gateway-callback`
- Headers:
  - `x-signature: 955745811776898d9ba88022a36b306b3e6c0c29f27c81dcb0673076ff7a18bb`

Body (JSON):

```json
{ "order_id": 1, "payment_status": "completed" }
```

> Viết liền không khoảng cách để khớp mã băm chữ ký.

## 2. Kết quả mong đợi

Ngay khi gửi thành công bước 3, hãy nhìn vào Terminal chạy Python của bạn. Các Subscriber sẽ log ra màn hình ngay lập tức nhờ cơ chế Event-driven:

```text
[Webhook] ✅ Đã xác thực thanh toán thành công cho đơn hàng #1
[Event-Driven] 📦 Inventory Service: Đã trừ kho cho đơn hàng #1
[Event-Driven] ✉️ Notification Service: Đã gửi email xác nhận cho đơn hàng #1
```
