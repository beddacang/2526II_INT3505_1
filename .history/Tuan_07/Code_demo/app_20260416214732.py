from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, init_beanie
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="SOA - Tuan 07: Backend Service with MongoDB",
    description="Demo kết nối Database thực tế và triển khai từ OpenAPI Spec"
)


# ==========================================
# 1. ĐỊNH NGHĨA MODEL (Tương đương Mongoose Schema bên Node.js)
# TẠI SAO DÙNG BEANIE DOCUMENT?
# Beanie giúp ánh xạ (map) trực tiếp Class Python thành một Collection trong MongoDB.
# Nó đóng vai trò là tầng ODM (Object Data Modeling) giúp quản lý cấu trúc dữ liệu chặt chẽ.
# ==========================================
class Book(Document):
    title: str
    author: str
    price: float
    description: Optional[str] = None

    class Settings:
        # TẠI SAO CẦN name? Đây là tên của "bảng" (collection) sẽ hiển thị trong MongoDB.
        name = "books"

# ==========================================
# 2. CẤU HÌNH KẾT NỐI DATABASE (Startup Event)
# TẠI SAO CẦN @app.on_event("startup")?
# Trong kiến trúc SOA, một service chỉ được coi là "sống" khi nó kết nối thành công với các tài nguyên.
# Việc khởi tạo này giúp đảm bảo khi có request tới, kết nối Database đã sẵn sàng.
# ==========================================
@app.on_event("startup")
async def startup_db_client():
    # Kết nối tới MongoDB (Mặc định localhost:27017)
    # TẠI SAO DÙNG MOTOR? Vì Motor hỗ trợ Async (bất đồng bộ), giúp server không bị treo khi chờ DB trả dữ liệu.
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    
    # Khởi tạo Beanie với database tên là "library_db"
    await init_beanie(database=client.library_db, document_models=[Book])
    print("--- KẾT NỐI MONGODB THÀNH CÔNG ---")

# ==========================================
# 3. TRIỂN KHAI CÁC API (Từ OpenAPI Spec)
# ==========================================

# API 1: Lấy danh sách toàn bộ sách
@app.get("/api/v1/books", response_model=List[Book], tags=["Books"])
async def get_all_books():
    """
    MỤC ĐÍCH: Truy vấn toàn bộ dữ liệu từ Database.
    Thay vì trả về biến list tạm thời, code này gọi trực tiếp xuống MongoDB.
    """
    books = await Book.find_all().to_list()
    return books

# API 2: Thêm một cuốn sách mới
@app.post("/api/v1/books", response_model=Book, tags=["Books"])
async def create_book(book: Book):
    """
    MỤC ĐÍCH: Lưu trữ dữ liệu vĩnh viễn (Persistent Storage).
    Dữ liệu gửi từ Client sẽ được kiểm tra kiểu (Validate) qua Pydantic trước khi lưu.
    """
    await book.insert() # Lưu trực tiếp vào MongoDB
    return book

# API 3: Tìm sách theo ID
@app.get("/api/v1/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book_by_id(book_id: str):
    """
    MỤC ĐÍCH: Demo khả năng tìm kiếm chính xác theo khóa chính của NoSQL.
    """
    book = await Book.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuốn sách này")
    return book

# ==========================================
# TẠI SAO BÀI NÀY LÀ CỐT LÕI CỦA BACKEND?
# 1. Stateless: Server không giữ dữ liệu, dữ liệu nằm ở Database.
# 2. Scalable: Bạn có thể bật 10 cái server này cùng chạy mà vẫn nhìn chung vào 1 Database MongoDB.
# 3. Spec-driven: Các đường dẫn /api/v1/books được thiết kế chuẩn từ OpenAPI.
# ==========================================