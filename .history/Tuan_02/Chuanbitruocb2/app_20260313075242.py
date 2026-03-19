from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# --- DỮ LIỆU GIẢ LẬP (RESOURCES) ---
# Tài nguyên ở đây là danh sách sách trong thư viện (bám sát file PDF của thầy)
books = [
    {"id": 1, "title": "Lap trinh Python", "author": "Nguyen Van A", "status": "available"},
    {"id": 2, "title": "Thiet ke RESTful API", "author": "Tran Van B", "status": "borrowed"}
]

# =================================================================
# 1. CLIENT-SERVER SEPARATION (Tách biệt Giao diện và Logic)
# -----------------------------------------------------------------
# GIẢI THÍCH: Server (Flask) chỉ quản lý dữ liệu và trả về JSON. 
# Nó không quan tâm Client là ai (Web, Mobile, hay Postman). 
# Sự tách biệt này giúp ta có thể nâng cấp giao diện mà không cần sửa code Server.
# =================================================================
@app.route('/api/v1/status', methods=['GET'])
def get_server_status():
    return jsonify({
        "principle": "Client-Server Separation",
        "message": "Server san sang cung cap du lieu, khong phu thuoc vao giao dien Client."
    })

# =================================================================
# 2. STATELESS (Không lưu trạng thái)
# -----------------------------------------------------------------
# GIẢI THÍCH: Server không lưu giữ bất kỳ "ngữ cảnh" nào của Client. 
# Mỗi request gửi lên phải chứa ĐẦY ĐỦ thông tin để Server hiểu (ví dụ: filter).
# Server không dùng Session hay Cookie để nhớ Client vừa làm gì ở bước trước.
# =================================================================
@app.route('/api/v1/books', methods=['GET'])
def get_books():
    # Lấy tham số lọc trực tiếp từ Request gửi lên (Ví dụ: ?author=Nguyen Van A)
    author_query = request.args.get('author')
    
    if author_query:
        filtered_books = [b for b in books if b['author'] == author_query]
        return jsonify({"principle": "Stateless", "data": filtered_books})
    
    return jsonify({"principle": "Stateless", "data": books})

# =================================================================
# 3. UNIFORM INTERFACE (Giao diện nhất quán)
# -----------------------------------------------------------------
# GIẢI THÍCH: Sử dụng định danh tài nguyên qua URI (/books/<id>) 
# và thao tác qua các phương thức HTTP chuẩn (GET, POST, DELETE...).
# Ở đây em bổ sung thêm HATEOAS (các đường dẫn liên kết) để đúng chuẩn nhất quán.
# =================================================================
@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if book:
        # Bổ sung _links để dẫn dắt Client (HATEOAS)
        book_response = book.copy()
        book_response["_links"] = {
            "self": f"/api/v1/books/{book_id}",
            "collection": "/api/v1/books",
            "borrow": f"/api/v1/books/{book_id}/borrow"
        }
        return jsonify({"principle": "Uniform Interface", "book": book_response}), 200
    
    return jsonify({"error": "Resource not found"}), 404

# =================================================================
# 4. CACHEABLE (Khả năng lưu đệm)
# -----------------------------------------------------------------
# GIẢI THÍCH: Server phản hồi kèm chỉ dẫn Cache để Client biết dữ liệu 
# này có thể dùng lại mà không cần hỏi lại Server, giúp giảm tải hệ thống.
# =================================================================
@app.route('/api/v1/public-info', methods=['GET'])
def get_public_info():
    data = {"info": "Thư viện mở cửa từ 8h - 17h hàng ngày."}
    
    # Gửi kèm Header Cache-Control (Lưu đệm trong 60 giây)
    resp = make_response(jsonify({"principle": "Cacheable", "data": data}))
    resp.headers['Cache-Control'] = 'public, max-age=60'
    return resp

# =================================================================
# 5. LAYERED SYSTEM (Hệ thống phân lớp)
# -----------------------------------------------------------------
# GIẢI THÍCH: Client không cần biết mình đang nói chuyện trực tiếp với 
# Server hay qua một lớp trung gian (Proxy/Gateway/Security Layer).
# Ở đây em giả lập một lớp bảo mật "chặn" ở giữa để kiểm tra Key.
# =================================================================
@app.route('/api/v1/admin/add-book', methods=['POST'])
def add_book():
    # Giả lập lớp trung gian Security kiểm tra API Key trước khi vào logic chính
    api_key = request.headers.get('X-Library-Key')
    if api_key != "lab-tuần-3-secret":
        return jsonify({"error": "Layered System: Bạn bị chặn bởi lớp bảo mật trung gian!"}), 401
    
    return jsonify({"message": "Đã đi qua các lớp trung gian và thêm sách thành công!"}), 201

# =================================================================
# 6. CODE ON DEMAND (Mã nguồn theo yêu cầu - Tùy chọn)
# -----------------------------------------------------------------
# GIẢI THÍCH: Server có thể mở rộng chức năng của Client bằng cách gửi 
# một đoạn mã thực thi (Script). Đây là nguyên tắc không bắt buộc.
# =================================================================
@app.route('/api/v1/scripts/check-input', methods=['GET'])
def get_script():
    # Trả về mã Javascript để Client tự chạy logic kiểm tra dữ liệu
    js_code = "alert('Server đang gửi Code on Demand: Vui lòng nhập đúng định dạng sách!');"
    return js_code, 200, {'Content-Type': 'application/javascript'}

if __name__ == '__main__':
    # Chạy ở cổng 5000, bật debug để tự cập nhật code khi lưu
    app.run(debug=True, port=5000)