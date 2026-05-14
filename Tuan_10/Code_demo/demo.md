## 3. Giải thích các thành phần vận hành

### A. Giám sát & Quan sát (Observability)

**Structured Logging:** Log được xuất ra dưới dạng JSON. Điều này cực kỳ quan trọng trong Production vì các công cụ như ELK (Elasticsearch, Logstash, Kibana) hoặc Grafana Loki có thể bóc tách dữ liệu dễ dàng thay vì đọc text thuần.

**Metrics:** Endpoint `/metrics` được tự động tạo ra. Nó cung cấp các con số về: số lượng request, thời gian phản hồi, trạng thái HTTP, giúp Prometheus thu thập và Grafana vẽ biểu đồ.

### B. Khả năng chịu tải (Resilience)

**Rate Limiting:** Sử dụng decorator `@limiter.limit`. Nếu một IP gửi quá nhiều request trong thời gian ngắn, hệ thống trả về lỗi 429, ngăn chặn việc cạn kiệt tài nguyên server.

**Circuit Breaker:** Khi service thanh toán giả lập bị lỗi 3 lần liên tiếp, hệ thống sẽ "ngắt mạch". Mọi request sau đó bị từ chối ngay lập tức mà không cần thử lại, giúp giảm tải cho hệ thống đang lỗi và tránh treo luồng xử lý.

### C. Bảo mật (Security)

**Audit Logs:** Các hành động admin (như reset mạch) được đánh dấu nhãn AUDIT. Đây là bằng chứng pháp lý và bảo mật để truy vết "ai đã làm gì".

---

## 4. Hướng dẫn các bước Test Demo

### Bước 1: Khởi chạy Server

Mở terminal và chạy lệnh:

```bash
uvicorn main:app --reload

Bước 2: Kiểm tra Rate Limiting

Truy cập http://127.0.0.1:8000/
 bằng trình duyệt.

Nhấn F5 liên tục hơn 5 lần.

Kết quả: Ở lần thứ 6, bạn sẽ nhận được thông báo lỗi:

{"error": "Rate limit exceeded: 5 per 1 minute"}.
Bước 3: Kiểm tra Metrics

Truy cập http://127.0.0.1:8000/metrics
.

Kết quả: Bạn sẽ thấy một danh sách dài các con số kỹ thuật. Đây là dữ liệu mà các hệ thống giám sát sẽ đọc để hiển thị biểu đồ sức khỏe API.

Bước 4: Kiểm tra Circuit Breaker (Ngắt mạch)

Truy cập http://127.0.0.1:8000/checkout
.

Nhấn F5 nhiều lần. Vì tỷ lệ lỗi là 50/50, sau vài lần bạn sẽ thấy lỗi 500 External Service Error.

Khi lỗi xảy ra đủ 3 lần liên tiếp, thông báo sẽ đổi thành:

{"detail": "Service Unavailable (Circuit Breaker Open)"}.

Lưu ý: Lúc này mạch đã mở, dù service bên kia có sống lại thì bạn vẫn bị chặn để bảo vệ hệ thống.

Bước 5: Kiểm tra Audit Logs và Reset

Truy cập http://127.0.0.1:8000/admin/reset-circuit
 để đóng mạch thủ công.

Quay lại terminal đang chạy code.

Kết quả: Bạn sẽ thấy dòng log dạng JSON có chứa nội dung "AUDIT: Admin manual reset circuit breaker". Đây chính là nhật ký kiểm tra.