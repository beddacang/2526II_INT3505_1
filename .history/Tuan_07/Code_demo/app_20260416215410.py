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
# Beanie giúp ánh xạ Class Python thành một Collection trong MongoDB.
# ==========================================
class Book(Document):
    title: str
    author: str
    price: float
    description: Optional[str] = None

    class Settings:
        # Tên của "bảng" (collection) sẽ hiển thị trong MongoDB Atlas
        name = "books"

# ==========================================
# 2. CẤU HÌNH KẾT NỐI DATABASE (Startup Event)
# SỬ DỤNG DUY NHẤT MỘT HÀM STARTUP ĐỂ TRÁNH LỖI 500
# ==========================================
@app.on_event("startup")
async def startup_db_client():
    # Chuỗi kết nối từ MongoDB Atlas của bạn
    uri = "mongodb+srv://23020039_db_user:RyRoE8QPT4jDvCfW@cluster0.qeahatc.mongodb.net/library_db?retryWrites=true&w=majority"
    
    try:
        # TẠI SAO DÙNG MOTOR? Vì hỗ trợ Async, tránh treo server khi chờ DB.
        client = AsyncIOMotorClient(uri)
        
        # Kiểm tra thực tế xem có ping được tới Atlas không
        await client.admin.command('ping')
        
        # Khởi tạo Beanie với database tên là "library_db"
        await init_beanie(database=client.library_db, document_models=[Book])
        print("--- [SUCCESS] KẾT NỐI MONGODB ATLAS THÀNH CÔNG ---")
    except Exception as e:
        print(f"--- [ERROR] KẾT NỐI THẤT BẠI: {e} ---")
        # Nếu DB không kết nối được, server sẽ báo lỗi ngay lúc khởi động thay vì đợi tới khi GET mới lỗi 500
        raise e

# ==========================================
# 3. TRIỂN KHAI CÁC API (Từ OpenAPI Spec)
# ==========================================

@app.get("/api/v1/books", response_model=List[Book], tags=["Books"])
async def get_all_books():
    """Truy vấn toàn bộ dữ liệu từ MongoDB Atlas."""
    return await Book.find_all().to_list()

@app.post("/api/v1/books", response_model=Book, tags=["Books"])
async def create_book(book: Book):
    """Lưu trữ dữ liệu vĩnh viễn (Persistent Storage) lên Cloud."""
    await book.insert() 
    return book

@app.get("/api/v1/books/{book_id}", response_model=Book, tags=["Books"])
async def get_book_by_id(book_id: str):
    """Tìm kiếm chính xác theo ID của NoSQL."""
    book = await Book.get(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Không tìm thấy cuốn sách này")
    return book

# ==========================================
# TẠI SAO BÀI NÀY LÀ CỐT LÕI CỦA BACKEND?
# 1. Stateless: Server không giữ dữ liệu, dữ liệu nằm ở Database.
# 2. Scalable: Có thể chạy nhiều server cùng trỏ vào 1 Database Atlas.
# 3. Spec-driven: Thiết kế chuẩn từ OpenAPI.
# ==========================================