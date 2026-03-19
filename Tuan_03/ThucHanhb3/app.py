from fastapi import FastAPI, HTTPException

app = FastAPI()

# --------------------------------------------------------------------------
# PHẦN 1: NGHIÊN CỨU ĐIỂN HÌNH (CASE STUDY) - PHÁT HIỆN LỖI
# --------------------------------------------------------------------------

# LỖI 1: Tên endpoint chứa động từ "get" và không có phiên bản (Versioning)
# SAI: @app.get("/get-active-products") 
# GIẢI THÍCH: RESTful dùng HTTP Method (GET) để thể hiện hành động, URL chỉ chứa danh từ.
@app.get("/v1/products") 
def get_products(status: str = "active"):
    # COMMENT: Nên dùng Query Parameter (?status=active) để lọc thay vì tạo URL riêng.
    return {"data": "Danh sách sản phẩm"}


# LỖI 2: Dùng POST để xóa và đặt hành động "delete" vào URL
# SAI: @app.post("/api/book/delete/{id}")
# GIẢI THÍCH: Vi phạm nguyên tắc sử dụng phương thức truyền thống. Dùng danh từ số ít (book).
@app.delete("/v1/books/{book_id}")
def delete_book(book_id: int):
    # COMMENT: Dùng DELETE method + Path Parameter ({book_id}) là chuẩn nhất.
    return {"message": f"Đã xóa sách {book_id}"}


# LỖI 3: Cấu trúc lồng ghép quá sâu và không nhất quán (Snake_case vs CamelCase)
# SAI: @app.get("/v1/UserOrders/get_all_items_by_orderID/{orderID}")
# GIẢI THÍCH: URL nên dùng chữ thường, phân tách bằng dấu gạch ngang (kebab-case).
@app.get("/v1/users/{user_id}/orders/{order_id}/items")
def get_order_items(user_id: int, order_id: int):
    # COMMENT: Cấu trúc Tài nguyên cha -> ID -> Tài nguyên con giúp API dễ hiểu và có tính phân cấp.
    return {"items": ["item1", "item2"]}

# --------------------------------------------------------------------------
# PHẦN 2: THỰC HÀNH THIẾT KẾ CHUẨN (BEST PRACTICES)
# --------------------------------------------------------------------------

@app.post("/v1/orders", status_code=201)
def create_order(order_data: dict):
    """
    NGUYÊN TẮC:
    1. Danh từ số nhiều (orders).
    2. Chữ thường toàn bộ.
    3. Trả về Status Code 201 (Created) thay vì 200 mặc định.
    """
    return {"status": "success", "order": order_data}

@app.patch("/v1/users/{user_id}")
def update_user_partially(user_id: int, update_data: dict):
    """
    NGUYÊN TẮC:
    - Dùng PATCH cho cập nhật một phần, PUT cho cập nhật toàn bộ.
    - ID nằm ở Path để xác định tài nguyên cụ thể.
    """
    return {"message": f"Cập nhật user {user_id} thành công"}