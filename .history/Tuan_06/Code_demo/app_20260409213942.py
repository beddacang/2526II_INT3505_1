from flask import Flask, request, jsonify
import jwt
import datetime
# wraps giúp giữ nguyên tên hàm và metadata (docstring) của hàm gốc. 
# TẠI SAO CẦN? Vì Flask sử dụng tên hàm để map với URL (routing). 
# Nếu không có @wraps, tất cả các hàm dùng decorator đều bị đổi tên thành 'decorated', gây lỗi trùng lặp route.
from functools import wraps 

app = Flask(__name__)

# TẠI SAO CẦN SECRET_KEY? 
# Đây là chìa khóa đối xứng (Symmetric Key) dùng để KÝ (sign) và XÁC MINH (verify) chữ ký JWT. 
# Chỉ có server nắm giữ key này mới có thể tạo ra và xác minh được token hợp lệ, 
# giúp chống lại việc token bị giả mạo (tampering) từ phía client.
app.config['SECRET_KEY'] = 'chuoi_ky_mat_cua_he_thong_soa'

# ==========================================
# Middleware: Kiểm tra Bearer Token (Decorator)
# TẠI SAO DÙNG MIDDLEWARE/DECORATOR?
# Để đảm bảo nguyên tắc DRY (Don't Repeat Yourself). Thay vì API nào cũng phải viết lại 
# đoạn code kiểm tra token, ta viết 1 lần ở đây và "gắn" (decorate) vào bất kỳ API nào cần bảo vệ.
# Trong SOA, logic này thường được đẩy lên tầng API Gateway chứ không nằm ở từng Microservice.
# ==========================================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 1. TẠI SAO LẤY Ở HEADER AUTHORIZATION? 
        # Đây là tiêu chuẩn của giao thức HTTP và OAuth 2.0 (RFC 6750) để truyền tải thông tin xác thực.
        auth_header = request.headers.get('Authorization')
        
        # 2. TẠI SAO PHẢI KIỂM TRA TIỀN TỐ "Bearer "?
        # "Bearer" có nghĩa là "Người mang nó". Tiêu chuẩn quy định format là "Bearer <chuỗi_token>".
        # Việc này giúp hệ thống nhận diện chính xác loại token đang được sử dụng.
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        # 3. TẠI SAO TRẢ VỀ 401 (Unauthorized)?
        # 401 có nghĩa là "Bạn chưa đăng nhập hoặc thiếu thông tin danh tính". 
        # Đây là lỗi xác thực (Authentication).
        if not token:
            return jsonify({'message': 'Thiếu token xác thực. Vui lòng cung cấp Bearer Token.'}), 401
            
        try:
            # 4. HÀM DECODE NÀY LÀM GÌ NGẦM BÊN DƯỚI?
            # - Nó tách token làm 3 phần (Header, Payload, Signature).
            # - Nó dùng SECRET_KEY băm Header + Payload hiện tại xem có khớp với Signature không.
            # - Nó tự động đọc claim 'exp' để xem thời gian hiện tại đã vượt qua thời gian hết hạn chưa.
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # 5. TẠI SAO GÁN DECODED VÀO REQUEST.USER?
            # Đây là cốt lõi của STATELESS AUTHENTICATION. Server không cần truy vấn Database 
            # để biết user này là ai. Thông tin (id, role) đã nằm sẵn trong token và được truyền 
            # xuống cho các tầng logic nghiệp vụ phía sau sử dụng.
            request.user = decoded 
            
        except jwt.ExpiredSignatureError:
            # TẠI SAO TRẢ VỀ 403 (Forbidden) THAY VÌ 401?
            # Server biết bạn là ai, nhưng phiên làm việc (token) của bạn đã hết hạn. 
            # Bạn bị từ chối cấp quyền (Authorization).
            return jsonify({'message': 'Token đã hết hạn. Vui lòng dùng Refresh Token.'}), 403
            
        except jwt.InvalidTokenError:
            # Lỗi này xảy ra khi chữ ký không khớp hoặc token bị cắt ghép, chỉnh sửa sai lệch.
            return jsonify({'message': 'Token không hợp lệ hoặc đã bị sửa đổi'}), 403
            
        return f(*args, **kwargs)
    return decorated

# ==========================================
# API 1: Đăng nhập và cấp phát JWT (Tương đương Authentication Service)
# ==========================================
@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if data and data.get('username') == 'admin' and data.get('password') == '123456':
        # TẠI SAO ĐƯA ID VÀ ROLE VÀO PAYLOAD?
        # Vì token là phương tiện để Client "chứng minh" quyền hạn của mình khi gọi các Microservices.
        # Mang theo 'role' giúp các service sau biết user có phải là Admin không mà không cần gọi lên DB.
        payload = {
            'id': 101,
            'username': 'admin',
            'role': 'Administrator',
            
            # TẠI SAO PHẢI SET 'exp' (Expiration time)?
            # Để giảm thiểu rủi ro Token Leakage & Replay Attack. Access Token sinh ra thường có 
            # tuổi thọ rất ngắn (VD: 15 phút). Nếu kẻ gian trộm được token này, họ cũng chỉ 
            # xài được trong vài phút chứ không thể xài vĩnh viễn.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }
        
        # TẠI SAO DÙNG HS256?
        # HMAC-SHA256 là thuật toán mã hóa đối xứng (dùng chung 1 key để tạo và kiểm tra).
        # Hiệu năng nhanh, phù hợp cho hệ thống vừa và nhỏ. (Nếu là hệ thống lớn / OAuth2 chuẩn 
        # thì thường dùng RS256 - bất đối xứng với Private/Public Key).
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            'message': 'Đăng nhập thành công',
            'accessToken': token
        })
        
    return jsonify({'message': 'Sai tài khoản hoặc mật khẩu'}), 401

# ==========================================
# API 2: Tài nguyên cần bảo vệ (Tương đương Resource Server)
# ==========================================
@app.route('/api/v1/profile', methods=['GET'])
@token_required # Kích hoạt middleware chặn ở cửa API này
def profile():
    # MỤC ĐÍCH THỰC TẾ CỦA REQUEST.USER:
    # Ví dụ: Select * from Orders where user_id = request.user['id']
    # Code ở đây rất gọn gàng vì việc chứng thực đã được giải quyết hết ở Middleware
    return jsonify({
        'message': 'Truy cập tài nguyên thành công!',
        'userInfo': request.user
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)