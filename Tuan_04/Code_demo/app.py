from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# =============================================================================
# 1. KHỞI TẠO ỨNG DỤNG (OpenAPI Object: Info & Servers)
# Phần này định nghĩa metadata của toàn bộ API hệ thống.
# Nó sẽ xuất hiện ở phần đầu tiên của tài liệu Swagger UI.
# =============================================================================
app = FastAPI(
    title="Hệ thống Quản lý Sách SOA (Tuần 4)",
    description="Đây là API demo cho Ngày 4 về Đặc tả OpenAPI. Hỗ trợ CRUD sách.",
    version="1.0.0",
    # OpenAPI có thể định nghĩa nhiều server (Dev, Staging, Production)
    servers=[{"url": "http://127.0.0.1:8000", "description": "Local server"}]
)

# =============================================================================
# 2. ĐỊNH NGHĨA SCHEMA (OpenAPI: Components -> Schemas)
# Pydantic Model giúp tự động tạo cấu trúc dữ liệu cho tệp JSON OpenAPI.
# Field() giúp cung cấp thông tin chi tiết cho từng thuộc tính dữ liệu.
# =============================================================================
class Book(BaseModel):
    # '...' (Ellipsis) nghĩa là trường này bắt buộc (Required)
    id: int = Field(..., example=1, description="Định danh duy nhất của cuốn sách")
    
    title: str = Field(..., example="Kiến trúc Microservices", description="Tiêu đề sách")
    
    author: str = Field(..., example="Tác giả A", description="Tên tác giả viết sách")
    
    # 'gt=0' (greater than) giúp OpenAPI hiểu quy tắc ràng buộc dữ liệu (Validation)
    price: float = Field(..., gt=0, example=250.0, description="Giá bán sản phẩm (phải lớn hơn 0)")
    
    # Optional giúp thuộc tính này có thể có hoặc không trong JSON (Nullable)
    description: Optional[str] = Field(None, description="Mô tả tóm tắt nội dung sách")

# Giả lập database trong bộ nhớ (In-memory database)
fake_db = [
    {"id": 1, "title": "SOA căn bản", "author": "Giảng viên B", "price": 100.0, "description": "Tài liệu học SOA"}
]

# =============================================================================
# 3. ĐỊNH NGHĨA CÁC PATHS & PARAMETERS (OpenAPI: Paths)
# Mỗi Decorator (@app.get, @app.post,...) định nghĩa một Endpoint.
# =============================================================================

# --- Endpoint 1: Lấy danh sách (Minh họa Query Parameter) ---
@app.get("/books", response_model=List[Book], summary="Danh sách toàn bộ sách")
async def read_books(
    # Query() định nghĩa tham số nằm sau dấu '?' trên URL (vd: /books?limit=5)
    # le=100 (less than or equal) là ràng buộc trong đặc tả OpenAPI
    limit: int = Query(10, le=100, description="Số lượng sách tối đa muốn lấy")
):
    """
    **Mô tả chi tiết (Docstring):**
    Lấy danh sách các cuốn sách đang có trong hệ thống. 
    Hỗ trợ phân trang qua tham số limit.
    """
    return fake_db[:limit]

# --- Endpoint 2: Thêm mới (Minh họa Request Body) ---
@app.post("/books", status_code=201, summary="Thêm một cuốn sách mới")
async def create_book(book: Book):
    """
    Tạo mới một cuốn sách. 
    Dữ liệu đầu vào phải khớp với cấu trúc **Book Schema**.
    """
    fake_db.append(book.dict())
    return {"message": "Thêm thành công", "data": book}

# --- Endpoint 3: Lấy chi tiết (Minh họa Path Parameter) ---
@app.get("/books/{book_id}", response_model=Book, summary="Truy vấn sách theo ID")
async def get_book(
    # Path() định nghĩa tham số nằm trực tiếp trên đường dẫn URL (vd: /books/1)
    book_id: int = Path(..., description="ID của cuốn sách bạn muốn xem thông tin")
):
    for b in fake_db:
        if b["id"] == book_id:
            return b
    # HTTPException tự động tạo ra 'Responses' lỗi 404 trong OpenAPI Spec
    raise HTTPException(status_code=404, detail="Sách không tồn tại trong hệ thống")

# --- Endpoint 4: Cập nhật (Minh họa Update) ---
@app.put("/books/{book_id}", summary="Cập nhật thông tin cuốn sách")
async def update_book(book_id: int, book: Book):
    """
    Yêu cầu cả **Path Parameter** (ID) và **Request Body** (Dữ liệu mới).
    """
    return {"message": f"Dữ liệu sách ID {book_id} đã được cập nhật thành công"}

# --- Endpoint 5: Xóa (Minh họa Delete) ---
@app.delete("/books/{book_id}", summary="Xóa sách khỏi cơ sở dữ liệu")
async def delete_book(book_id: int = Path(..., description="ID của sách cần xóa")):
    """
    Xóa vĩnh viễn cuốn sách khỏi hệ thống dựa trên ID.
    """
    return {"message": f"Đã xóa sách có ID {book_id}"}