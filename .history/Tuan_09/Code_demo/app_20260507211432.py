from fastapi import FastAPI, Header, Response, APIRouter, Request
from typing import Optional, List
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Master API Versioning Demo")

# ---------------------------------------------------------
# 1. MODELS (Cấu trúc dữ liệu)
# ---------------------------------------------------------

# Schema cũ cho V1
class UserV1(BaseModel):
    id: int
    name: str

# Schema mới cho V2 (Breaking Change: tách firstName và lastName)
class UserV2(BaseModel):
    id: int
    first_name: str
    last_name: str
    is_active: bool = True

# ---------------------------------------------------------
# 2. VERSION 1: ROUTER & LIFECYCLE
# ---------------------------------------------------------
v1 = APIRouter()

@v1.get("/users", response_model=List[UserV1])
async def get_users_v1(response: Response):
    # Thêm Header cảnh báo vòng đời (Lifecycle)
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Wed, 31 Dec 2026 23:59:59 GMT"
    response.headers["Link"] = '<https://api.example.com/v2/docs>; rel="successor-version"'
    
    return [
        {"id": 1, "name": "Nguyen Van A"},
        {"id": 2, "name": "Tran Thi B"}
    ]

# ---------------------------------------------------------
# 3. VERSION 2: ROUTER (THE NEW ERA)
# ---------------------------------------------------------
v2 = APIRouter()

@v2.get("/users", response_model=List[UserV2])
async def get_users_v2():
    return [
        {"id": 1, "first_name": "A", "last_name": "Nguyen Van", "is_active": True},
        {"id": 2, "first_name": "B", "last_name": "Tran Thi", "is_active": False}
    ]

# ---------------------------------------------------------
# 4. CHIẾN LƯỢC ĐIỀU HƯỚNG (ROUTING STRATEGIES)
# ---------------------------------------------------------

# Cách 1: URL Path Versioning (Khuyên dùng vì tường minh)
app.include_router(v1, prefix="/api/v1", tags=["v1"])
app.include_router(v2, prefix="/api/v2", tags=["v2"])

# Cách 2: Header-based Versioning (Logic tùy biến)
@app.get("/api/users")
async def dynamic_versioning(
    request: Request,
    response: Response,
    x_api_version: Optional[str] = Header(None)
):
    if x_api_version == "2":
        return await get_users_v2()
    
    # Mặc định trả về V1 kèm cảnh báo
    return await get_users_v1(response)

# ---------------------------------------------------------
# 5. XỬ LÝ API ĐÃ BỊ KHAI TỬ (GONE)
# ---------------------------------------------------------
@app.api_route("/api/v0/{path:path}", methods=["GET", "POST"])
async def retired_version():
    return Response(
        status_code=410, 
        content='{"error": "Gone", "message": "Phien ban v0 da ngung hoat dong. Hay dung v2."}',
        media_type="application/json"
    )

if __name__ == "__main__":
    print("🚀 Server đang khởi động tại http://127.0.0.1:8000")
    print("Mở http://127.0.0.1:8000/docs để xem Swagger UI cực đẹp!")
    uvicorn.run(app, host="127.0.0.1", port=8000)