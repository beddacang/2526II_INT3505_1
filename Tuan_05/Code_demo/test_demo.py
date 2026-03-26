import requests
import json
import base64

# Cấu hình URL cơ sở của API (Mặc định FastAPI chạy ở port 8000)
BASE_URL = "http://127.0.0.1:8000"

def test_offset_pagination():
    print("\n--- TEST 1: OFFSET-BASED PAGINATION (Phân trang truyền thống) ---")
    # Giả lập lấy trang số 2, mỗi trang 5 đơn hàng của User có ID = 1
    user_id = 1
    params = {
        "page": 2,
        "limit": 5
    }
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/orders", params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Trạng thái: Thành công!")
        print(f"Tổng số đơn hàng trong DB: {data['total']}")
        print(f"Đang hiển thị trang: {data['page']}")
        print(f"Dữ liệu nhận được: {len(data['data'])} đơn hàng")
        # In ra 2 đơn hàng đầu tiên của trang này để kiểm tra
        for order in data['data'][:2]:
            print(f"  - ID: {order['order_id']} | Sản phẩm: {order['product_name']}")
    else:
        print(f"Lỗi: {response.status_code}")

def test_cursor_pagination():
    print("\n--- TEST 2: CURSOR-BASED PAGINATION (Phân trang con trỏ) ---")
    
    # Bước 1: Lấy trang đầu tiên (không gửi cursor)
    print("Đang lấy trang 1...")
    first_page = requests.get(f"{BASE_URL}/orders/cursor", params={"limit": 3})
    res_1 = first_page.json()
    
    for item in res_1['data']:
        print(f"  [Trang 1] ID: {item['order_id']}")
        
    # Lấy next_cursor từ kết quả trang 1
    cursor = res_1['paging']['next_cursor']
    print(f"==> Cursor nhận được (Base64): {cursor}")
    
    # Bước 2: Dùng cursor đó để lấy trang tiếp theo
    if cursor:
        print("\nĐang dùng Cursor để lấy trang 2...")
        second_page = requests.get(f"{BASE_URL}/orders/cursor", params={"cursor": cursor, "limit": 3})
        res_2 = second_page.json()
        
        for item in res_2['data']:
            print(f"  [Trang 2] ID: {item['order_id']}")
            
        print(f"Có còn dữ liệu không? {'Có' if res_2['paging']['has_more'] else 'Không'}")

def test_resource_modeling_structure():
    print("\n--- TEST 3: KIỂM TRA CẤU TRÚC CÂY TÀI NGUYÊN ---")
    # Kiểm tra xem đường dẫn /users/1/orders có đúng chuẩn REST không
    user_id = 99
    response = requests.get(f"{BASE_URL}/users/{user_id}/orders")
    
    # Kiểm tra xem logic đường dẫn có phản ánh đúng User ID không
    if response.status_code == 200:
        print(f"Đường dẫn /users/{user_id}/orders hoạt động đúng chuẩn Resource Modeling.")
    else:
        print("Đường dẫn không tồn tại hoặc sai cấu trúc.")

if __name__ == "__main__":
    # Lưu ý: Bạn cần chạy file app.py trước khi chạy script test này
    try:
        test_offset_pagination()
        test_cursor_pagination()
        test_resource_modeling_structure()
    except requests.exceptions.ConnectionError:
        print("LỖI: Hãy đảm bảo bạn đã chạy 'uvicorn app:app --reload' trước khi test!")