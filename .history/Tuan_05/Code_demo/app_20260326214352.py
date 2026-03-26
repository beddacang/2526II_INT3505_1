from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import base64

# =================================================================
# 1. KHỞI TẠO ỨNG DỤNG (Ngày 5: Resource Modeling & Pagination)
# =================================================================
app = FastAPI(
    title="Hệ thống Quản lý Đơn hàng SOA (Ngày 5)",
    description="Demo về thiết kế cây tài nguyên /users/{id}/orders và các chiến lược phân trang.",
    version="1.0.0"
)

# =================================================================
# 2. ĐỊNH NGHĨA SCHEMA (Model dữ liệu)
# =================================================================

class Order(BaseModel):
    """Mô hình tài nguyên Đơn hàng (Resource Model)"""
    order_id: int = Field(..., example=101)
    product_name: str = Field(..., example="Laptop Dell XPS")
    amount: float = Field(..., example=1500.0)

class OrderResponse(BaseModel):
    """Cấu trúc dữ liệu trả về kèm thông tin phân trang"""
    total: int
    page: int
    page_size: int
    data: List[Order]

# Giả lập Database cho 100 đơn hàng
fake_orders_db = [
    {"order_id": i, "product_name": f"Sản phẩm {i}", "amount": i * 10.5} 
    for i in range(1, 101)
]

# =================================================================
# 3. THIẾT KẾ CÂY TÀI NGUYÊN (Nested Resources)
# =================================================================

# Đường dẫn: /users/{user_id}/orders -> Thể hiện quan hệ sở hữu
@app.get(
    "/users/{user_id}/orders", 
    response_model=OrderResponse,
    tags=["Resource Modeling"]
)
async def get_user_orders(
    user_id: int,
    # Chiến lược 1: Offset-based Pagination (Phân trang dựa trên độ lệch)
    page: int = Query(1, ge=1, description="Số thứ tự trang muốn lấy"),
    limit: int = Query(10, le=50, description="Số lượng bản ghi trên mỗi trang")
):
    """
    Lấy danh sách đơn hàng của một User cụ thể kèm phân trang Offset.
    - Ưu điểm: Dễ nhảy trang (ví dụ nhảy từ trang 1 đến trang 5).
    - Nhược điểm: Chậm khi dữ liệu cực lớn (Database phải quét qua các bản ghi cũ).
    """
    
    # Tính toán vị trí bắt đầu (Offset)
    start_index = (page - 1) * limit
    end_index = start_index + limit
    
    # Cắt lát dữ liệu giả lập (Slicing)
    orders_slice = fake_orders_db[start_index:end_index]
    
    return {
        "total": len(fake_orders_db),
        "page": page,
        "page_size": limit,
        "data": orders_slice
    }

# =================================================================
# 4. CHIẾN LƯỢC PHÂN TRANG CON TRỎ (Cursor-based Pagination)
# =================================================================

@app.get("/orders/cursor", tags=["Pagination Strategy"])
async def get_orders_by_cursor(
    # cursor thường là một chuỗi mã hóa (Base64) chứa ID của bản ghi cuối cùng
    cursor: Optional[str] = Query(None, description="Con trỏ để lấy trang tiếp theo"),
    limit: int = Query(10, le=50)
):
    """
    Phân trang dựa trên Cursor (thường dùng cho Infinite Scroll như Facebook/TikTok).
    - Ưu điểm: Hiệu năng cực cao, không bị lặp dữ liệu khi có bản ghi mới chèn vào.
    - Nhược điểm: Không thể nhảy trang tự do.
    """
    
    # 1. Giải mã cursor để lấy ID bắt đầu (Nếu không có thì lấy từ ID 0)
    last_id = 0
    if cursor:
        try:
            last_id = int(base64.b64decode(cursor).decode())
        except:
            raise HTTPException(status_code=400, detail="Cursor không hợp lệ")

    # 2. Lọc dữ liệu: Lấy các bản ghi có ID lớn hơn last_id (Tối ưu bằng Index trong DB)
    results = [o for o in fake_orders_db if o["order_id"] > last_id][:limit]

    # 3. Tạo cursor mới cho trang tiếp theo (Mã hóa ID của bản ghi cuối cùng)
    next_cursor = None
    if results:
        new_last_id = results[-1]["order_id"]
        next_cursor = base64.b64encode(str(new_last_id).encode()).decode()

    return {
        "data": results,
        "paging": {
            "next_cursor": next_cursor,
            "has_more": len(results) == limit
        }
    }

# =================================================================
# 5. SO SÁNH NHANH (Phục vụ trả lời lý thuyết)
# =================================================================
# - Offset: Dễ code, phù hợp Web quản trị (Admin Dashboard) cần số trang 1, 2, 3.
# - Cursor: Hiệu năng cao, phù hợp Mobile App (Vuốt xuống tải thêm).