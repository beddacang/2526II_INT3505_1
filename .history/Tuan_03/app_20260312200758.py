from flask import Flask, request, jsonify

app = Flask(__name__)

# --- DỮ LIỆU GIẢ LẬP (Mô phỏng Database) ---
# Trong thực tế, dữ liệu này sẽ nằm trong SQL/NoSQL. 
# Ở đây ta dùng List để demo nhanh các nguyên tắc thiết kế.
orders = [
    {"id": 1, "product": "Iphone 15", "status": "shipped", "created_at": "2026-03-10T08:00:00Z"},
    {"id": 2, "product": "Macbook M3", "status": "pending", "created_at": "2026-03-11T09:00:00Z"},
    {"id": 3, "product": "iPad Pro", "status": "shipped", "created_at": "2026-03-12T10:00:00Z"}
]

# =================================================================
# 1. NGUYÊN TẮC: NHẤT QUÁN (Consistency) & LỌC DỮ LIỆU
# =================================================================
@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    """
    TẠI SAO THIẾT KẾ NHƯ THẾ NÀY?
    - '/api/v1/': Versioning giúp bảo trì. Nếu sau này có v2, v1 vẫn chạy bình thường.
    - '/orders': Dùng danh từ số nhiều vì đây là một "Tập hợp" (Collection) các đơn hàng.
    - 'GET': Phương thức chuẩn để ĐỌC dữ liệu, không làm thay đổi dữ liệu hệ thống.
    """
    
    # LẤY THAM SỐ LỌC (Query Parameters):
    # Thay vì tạo nhiều Endpoint như /get-shipped-orders, ta dùng tham số ?status=
    # Điều này giúp API gọn gàng và dễ mở rộng các tiêu chí lọc sau này.
    status_filter = request.args.get('status')
    
    result = orders
    if status_filter:
        # Thực hiện lọc dữ liệu dựa trên giá trị người dùng gửi lên URL
        result = [o for o in orders if o['status'] == status_filter]
    
    # CẤU TRÚC PHẢN HỒI NHẤT QUÁN:
    # Luôn bọc dữ liệu trong một Object JSON có các trường cố định (status, count, data).
    # Việc này giúp phía Frontend (React/Angular) luôn biết cách đọc dữ liệu mà không bị bỡ ngỡ.
    return jsonify({
        "status": "success",
        "count": len(result),
        "data": result
    }), 200 # Mã 200 OK: Truy vấn thành công


# =================================================================
# 2. NGUYÊN TẮC: DỄ HIỂU (Clarity) & HTTP METHODS
# =================================================================
@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
def get_order_detail(order_id):
    """
    TẠI SAO THIẾT KẾ NHƯ THẾ NÀY?
    - '<int:order_id>': Path Parameter giúp xác định chính xác tài nguyên cần tìm.
    - Nó thể hiện tính phân cấp: Trong tất cả 'orders', tôi muốn lấy 'đơn hàng X'.
    """
    
    # Tìm kiếm đơn hàng trong danh sách dựa trên ID
    order = next((o for o in orders if o['id'] == order_id), None)
    
    # XỬ LÝ LỖI CHUẨN (Error Handling):
    # Một API tốt phải trả về đúng trạng thái của tài nguyên.
    if order:
        return jsonify(order), 200 # Tìm thấy thì trả về dữ liệu + mã 200
    
    # Nếu không thấy, KHÔNG được trả về mã 200 kèm tin nhắn lỗi.
    # PHẢI trả về mã 404 Not Found để các công cụ tự động (như Browser/Postman) hiểu ngay lập tức.
    return jsonify({
        "error": "NOT_FOUND",
        "message": f"Hệ thống không tìm thấy đơn hàng có mã ID: {order_id}"
    }), 404


# =================================================================
# 3. NGUYÊN TẮC: DỄ MỞ RỘNG (Extensibility) & POST METHOD
# =================================================================
@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    """
    TẠI SAO THIẾT KẾ NHƯ THẾ NÀY?
    - 'POST': Dùng để tạo mới tài nguyên. Dữ liệu nằm trong "Body", không nằm trên URL (bảo mật hơn).
    - Tính mở rộng: JSON cho phép ta thêm các trường mới (ví dụ: 'address', 'phone') 
      vào yêu cầu mà không làm hỏng logic của các phiên bản cũ.
    """
    
    # Đọc dữ liệu JSON từ yêu cầu của Client gửi lên
    data = request.get_json()
    
    # KIỂM TRA DỮ LIỆU (Validation):
    # API phải đóng vai trò là "người gác cổng", từ chối các yêu cầu thiếu thông tin quan trọng.
    if not data or 'product' not in data:
        # Trả về mã 400 Bad Request: Lỗi do phía người dùng gửi dữ liệu sai định dạng.
        return jsonify({"error": "Dữ liệu không hợp lệ. Bạn phải cung cấp tên 'product'."}), 400
    
    # Tạo đối tượng mới với định dạng thời gian chuẩn ISO 8601
    # ISO 8601 (YYYY-MM-DDTHH:MM:SSZ) là tiêu chuẩn vàng để giao tiếp giữa các múi giờ khác nhau.
    new_order = {
        "id": len(orders) + 1,
        "product": data['product'],
        "status": "pending",
        "created_at": "2026-03-12T12:00:00Z" 
    }
    
    orders.append(new_order)
    
    # TRẢ VỀ MÃ 201 CREATED:
    # Đây là mã chuẩn để thông báo rằng: "Tôi đã nhận yêu cầu và đã TẠO THÀNH CÔNG tài nguyên mới".
    return jsonify(new_order), 201


if __name__ == '__main__':
    # Chạy server ở chế độ debug để tự động tải lại code khi có thay đổi.
    print("--- API ĐANG CHẠY. THỬ TRUY CẬP: http://127.0.0.1:5000/api/v1/orders ---")
    app.run(debug=True)