from fastapi import FastAPI, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
import hmac
import hashlib
import json
import math

app = FastAPI(title="Hybrid API Design Patterns Demo")

WEBHOOK_SECRET = "my_shared_secret_key"

# -------------------------------------------------------------
# MÔ PHỎNG DATABASE TRONG BỘ NHỚ (IN-MEMORY DB)
# -------------------------------------------------------------
products = [
    {"id": 1, "name": "iPhone 15 Pro", "category": "electronics", "price": 1000},
    {"id": 2, "name": "MacBook Pro M3", "category": "electronics", "price": 2000},
    {"id": 3, "name": "Sony WH-1000XM5", "category": "audio", "price": 350},
    {"id": 4, "name": "Mechanical Keyboard", "category": "accessories", "price": 100},
]

orders = []

# -------------------------------------------------------------
# 1. EVENT-DRIVEN PATTERN (Mô phỏng Pub/Sub bằng Python)
# -------------------------------------------------------------
class SimpleEventEmitter:
    def __init__(self):
        self._listeners = {}

    def on(self, event_name: str, callback):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def emit(self, event_name: str, *args, **kwargs):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                callback(*args, **kwargs)

order_emitter = SimpleEventEmitter()

# Subscriber 1: Hệ thống kho (Inventory Service)
def inventory_service(order):
    print(f"[Event-Driven] 📦 Inventory Service: Đã trừ kho cho đơn hàng #{order['id']}")

# Subscriber 2: Hệ thống thông báo (Notification Service)
def notification_service(order):
    print(f"[Event-Driven] ✉️ Notification Service: Đã gửi email xác nhận cho đơn hàng #{order['id']}")

# Đăng ký các dịch vụ lắng nghe sự kiện Đơn hàng đã thanh toán (OrderPaid)
order_emitter.on("OrderPaid", inventory_service)
order_emitter.on("OrderPaid", notification_service)


# -------------------------------------------------------------
# 2. QUERY PATTERN (Phân trang, Lọc, Sắp xếp)
# -------------------------------------------------------------
# GET /api/products?category=electronics&sort=-price&page=1&limit=2
@app.get("/api/products")
def get_products(
    category: Optional[str] = None, 
    sort: Optional[str] = None, 
    page: int = 1, 
    limit: int = 10
):
    result = list(products)

    # Lọc (Filtering)
    if category:
        result = [p for p in result if p["category"] == category]

    # Sắp xếp (Sorting) - Ví dụ: sort=-price (giảm dần), sort=price (tăng dần)
    if sort:
        is_descending = sort.startswith('-')
        field = sort[1:] if is_descending else sort
        # Sắp xếp động dựa theo key
        result.sort(key=lambda x: x.get(field, 0), reverse=is_descending)

    # Phân trang (Pagination)
    start_index = (page - 1) * limit
    end_index = page * limit
    paginated_result = result[start_index:end_index]

    return {
        "metadata": {
            "total_items": len(result),
            "page": page,
            "limit": limit,
            "total_pages": math.ceil(len(result) / limit)
        },
        "data": paginated_result
    }


# -------------------------------------------------------------
# 3. CRUD PATTERN & HATEOAS PATTERN
# -------------------------------------------------------------
class OrderCreateDTO(BaseModel):
    product_id: int
    quantity: int

# Hàm bổ sung trạng thái HATEOAS động dựa trên trạng thái đơn hàng
def enrich_order_with_links(order: dict) -> dict:
    enriched = dict(order)
    enriched["_links"] = {
        "self": {"href": f"/api/orders/{order['id']}", "method": "GET"}
    }
    
    # State Machine: Sinh liên kết khả dụng dựa trên trạng thái hiện tại
    if order["status"] == "pending_payment":
        enriched["_links"]["cancel"] = {"href": f"/api/orders/{order['id']}/cancel", "method": "POST"}
        enriched["_links"]["simulate_payment"] = {
            "href": "/api/webhooks/payment-gateway-callback",
            "method": "POST",
            "note": "Dùng endpoint này để giả lập cổng thanh toán gọi Webhook về"
        }
    elif order["status"] == "paid":
        enriched["_links"]["track_shipping"] = {"href": f"/api/orders/{order['id']}/shipping", "method": "GET"}
        
    return enriched

# CRUD: Create - Tạo đơn hàng mới
@app.post("/api/orders", status_code=201)
def create_order(order_data: OrderCreateDTO):
    product = next((p for p in products if p["id"] == order_data.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
        
    new_order = {
        "id": len(orders) + 1,
        "product_id": order_data.product_id,
        "quantity": order_data.quantity,
        "total_amount": product["price"] * order_data.quantity,
        "status": "pending_payment"
    }
    orders.append(new_order)
    return enrich_order_with_links(new_order)

# CRUD: Read - Lấy chi tiết đơn hàng (Kết hợp HATEOAS)
@app.get("/api/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    return enrich_order_with_links(order)


# -------------------------------------------------------------
# 4. WEBHOOK PATTERN (Nhận dữ liệu callback từ bên thứ 3 bảo mật)
# -------------------------------------------------------------
@app.post("/api/webhooks/payment-gateway-callback")
async def payment_webhook(request: Request, x_signature: Optional[str] = Header(None)):
    if not x_signature:
        raise HTTPException(status_code=400, detail="Thiếu chữ ký bảo mật x-signature")
        
    # Lấy dữ liệu thô (raw bytes) để băm hash chính xác tuyệt đối
    payload_bytes = await request.body()
    
    # Tính toán chữ ký dựa trên Payload nhận được và Secret Key
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    print("\n========= DEBUG WEBHOOK =========")
    print(f"Raw Payload Server nhận được: {payload_bytes}")
    print(f"Chữ ký Server mong muốn (Expected): {expected_signature}")
    print(f"Chữ ký bạn đang gửi lên (Received): {x_signature}")
    print("=================================\n")

    # Kiểm tra bảo mật tính toàn vẹn và xác thực nguồn gốc
    if not hmac.compare_digest(x_signature, expected_signature):
        raise HTTPException(status_code=401, detail="Chữ ký không hợp lệ! Dữ liệu đã bị can thiệp.")
        
    # Parse dữ liệu sau khi đã an toàn
    data = json.loads(payload_bytes.decode('utf-8'))
    order_id = data.get("order_id")
    payment_status = data.get("payment_status")
    
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng không tồn tại")
        
    if payment_status == "completed" and order["status"] == "pending_payment":
        order["status"] = "paid"
        print(f"[Webhook] ✅ Đã xác thực thanh toán thành công cho đơn hàng #{order['id']}")
        
        # KÍCH HOẠT EVENT-DRIVEN: Bắn sự kiện ra hệ thống nội bộ
        order_emitter.emit("OrderPaid", order)
        
    # Phản hồi ngay lập tức cho cổng thanh toán (dưới 2 giây)
    return {"received": True}