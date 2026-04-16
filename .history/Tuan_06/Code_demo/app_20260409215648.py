from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import datetime

app = FastAPI(
    title="SOA JWT Authentication",
    description="Demo API bảo mật bằng JWT có tích hợp sẵn Swagger UI"
)

# TẠI SAO CẦN SECRET_KEY? 
# Đây là chìa khóa đối xứng (Symmetric Key) dùng để KÝ (sign) và XÁC MINH (verify) chữ ký JWT. 
# Chỉ có server nắm giữ key này mới có thể tạo ra và xác minh được token hợp lệ, 
# giúp chống lại việc token bị giả mạo (tampering) từ phía client.
SECRET_KEY = 'chuoi_ky_mat_cua_he_thong_soa'

# Cấu hình Security Bearer cho hệ thống
# TẠI SAO CẦN HTTPBearer()?
# Khác với Flask bạn phải tự lấy Header, FastAPI cung cấp sẵn class này. 
# Nó có 2 tác dụng: 
# 1. Tự động kiểm tra xem request có Header "Authorization: Bearer ..." không.
# 2. Tự động sinh ra nút "Authorize" (hình ổ khóa) trên giao diện Web Swagger UI.
security = HTTPBearer()

# ==========================================
# Middleware: Kiểm tra Bearer Token (Dependency Injection)
# TẠI SAO DÙNG DEPENDS Ở ĐÂY?
# Trong FastAPI, thay vì dùng Decorator (@wraps) như Flask, ta dùng cơ chế Dependency Injection (Depends).
# Hàm verify_token này đóng vai trò như một "người gác cổng" (API Gateway / Middleware).
# Bất kỳ API nào gọi hàm này đều sẽ bị kiểm tra Token trước khi được phép chạy logic bên trong.
# ==========================================
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    # Biến credentials.credentials chứa sẵn chuỗi Token (FastAPI đã tự cắt bỏ chữ "Bearer " giúp mình).
    token = credentials.credentials
    
    try:
        # HÀM DECODE NÀY LÀM GÌ NGẦM BÊN DƯỚI?
        # - Nó tách token làm 3 phần (Header, Payload, Signature).
        # - Nó dùng SECRET_KEY băm Header + Payload hiện tại xem có khớp với Signature không.
        # - Nó tự động đọc claim 'exp' để xem thời gian hiện tại đã vượt qua thời gian hết hạn chưa.
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # TRẢ VỀ DECODED ĐỂ LÀM GÌ?
        # Đây là cốt lõi của STATELESS AUTHENTICATION. Server không cần truy xuất Database.
        # Thông tin user (id, role) đã nằm trong token, hàm này trả về để các hàm API bên dưới xài luôn.
        return decoded 
        
    except jwt.ExpiredSignatureError:
        # TẠI SAO TRẢ VỀ 403 (Forbidden)?
        # Server biết bạn là ai, nhưng phiên làm việc (token) của bạn đã hết hạn. Bạn bị từ chối cấp quyền.
        raise HTTPException(status_code=403, detail="Token đã hết hạn. Vui lòng đăng nhập lại.")
        
    except jwt.InvalidTokenError:
        # Lỗi này xảy ra khi chữ ký không khớp hoặc token bị cắt ghép, chỉnh sửa sai lệch.
        raise HTTPException(status_code=403, detail="Token không hợp lệ hoặc đã bị sửa đổi.")

# ==========================================
# API 1: Đăng nhập và cấp phát JWT (Tương đương Authentication Service)
# ==========================================
@app.post('/api/v1/login', tags=["Authentication"])
def login(user_data: dict):
    if user_data.get('username') == 'admin' and user_data.get('password') == '123456':
        
        # TẠI SAO ĐƯA ID VÀ ROLE VÀO PAYLOAD?
        # Vì token là phương tiện để Client "chứng minh" quyền hạn của mình.
        # Mang theo 'role' giúp các service sau biết user có phải là Admin không mà không cần gọi DB.
        payload = {
            'id': 101,
            'username': 'admin',
            'role': 'Administrator',
            
            # TẠI SAO PHẢI SET 'exp' (Expiration time)?
            # Để giảm thiểu rủi ro Token Leakage (Lộ token). Token chỉ sống được 15 phút.
            # Nếu kẻ gian trộm được, chúng cũng không thể xài vĩnh viễn được.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        
        # TẠI SAO DÙNG HS256?
        # HMAC-SHA256 là thuật toán mã hóa đối xứng (dùng chung 1 key để tạo và kiểm tra).
        # Tốc độ nhanh, cực kỳ phù hợp cho Microservices quy mô vừa và nhỏ.
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        
        return {
            'message': 'Đăng nhập thành công',
            'accessToken': token
        }
        
    # 401 Unauthorized: Lỗi xác thực (Không biết bạn là ai do sai pass)
    raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")

# ==========================================
# API 2: Tài nguyên cần bảo vệ (Tương đương Resource Server)
# ==========================================
@app.get('/api/v1/profile', tags=["Resources"])
def profile(current_user: dict = Depends(verify_token)):
    """
    Depends(verify_token): Kích hoạt Middleware chặn ở cửa API này.
    Nếu không có token hợp lệ, nó sẽ văng lỗi ngay.
    Nếu hợp lệ, current_user sẽ nhận toàn bộ thông tin giải mã từ Token.
    """
    
    # MỤC ĐÍCH THỰC TẾ CỦA CURRENT_USER:
    # Ví dụ: Select * from Orders where user_id = current_user['id']
    # Rất gọn gàng vì việc chứng thực đã được giải quyết ở hàm verify_token.
    return {
        'message': 'Truy cập tài nguyên thành công!',
        'userInfo': current_user
    }python -m uvicorn app:app --reload