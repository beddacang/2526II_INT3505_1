from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

# 1. Khởi tạo ứng dụng (Tương ứng với phần 'info' và 'servers' trong OpenAPI)
app = FastAPI(
    title="Hệ thống Quản lý Sách SOA",
    description="API này tuân thủ chuẩn OpenAPI 3.0, dùng để quản lý kho sách.",
    version="1.0.0"
)

# 2. Định nghĩa Schema (Tương ứng với 'components/schemas' trong OpenAPI)
class Book(BaseModel):
    id: int = Field(..., example=1, description="ID duy nhất của cuốn sách")
    title: str = Field(..., example="Lập trình Python cơ bản", description="Tiêu đề sách")
    author: str = Field(..., example="Nguyễn Văn A", description="Tên tác giả")
    price: float = Field(..., gt=0, example=150000, description="Giá bán (phải > 0)")

# Giả lập cơ sở dữ liệu (In-memory Database)
fake_db = [
    {"id": 1, "title": "Kiến trúc SOA", "author": "Trần Văn B", "price": 200000}
]

# 3. Định nghĩa các Endpoints (Tương ứng với 'paths' và 'parameters' trong OpenAPI)

@app.get("/books", response_model=List[Book], summary="Lấy danh sách sách")
async def read_books(limit: int = Query(10, le=100, description="Số lượng bản ghi tối đa")):
    """
    Endpoint này tương ứng với phương thức GET.
    - **limit**: Tham số dạng 'query' để phân trang.
    """
    return fake_db[:limit]

@app.post("/books", status_code=201, summary="Thêm sách mới")
async def create_book(book: Book):
    """
    Endpoint này nhận một 'requestBody' có cấu trúc giống schema Book.
    """
    fake_db.append(book.dict())
    return {"message": "Thêm sách thành công", "data": book}

@app.get("/books/{book_id}", response_model=Book, summary="Xem chi tiết một cuốn sách")
async def get_book(book_id: int = Path(..., description="ID của sách cần tìm")):
    """
    - **book_id**: Tham số dạng 'path'.
    """
    for b in fake_db:
        if b["id"] == book_id:
            return b
    raise HTTPException(status_code=404, detail="Không tìm thấy sách")

@app.put("/books/{book_id}", summary="Cập nhật thông tin sách")
async def update_book(book_id: int, book: Book):
    return {"message": f"Đã cập nhật sách ID {book_id}"}

@app.delete("/books/{book_id}", summary="Xóa sách khỏi hệ thống")
async def delete_book(book_id: int):
    return {"message": f"Đã xóa sách ID {book_id}"}