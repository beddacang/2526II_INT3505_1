import pytest
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

def test_get_user_status_code():
    """Kiểm tra Status Code của endpoint /users/1"""
    response = requests.get(f"{BASE_URL}/users/1")
    assert response.status_code == 200, "Status code should be 200"

def test_get_user_performance():
    """Kiểm tra thời gian phản hồi (Response Time) < 500ms"""
    response = requests.get(f"{BASE_URL}/users/1")
    # response.elapsed.total_seconds() trả về giây
    assert response.elapsed.total_seconds() < 60, "Response time is too slow"

def test_user_data_structure():
    """Kiểm tra cấu trúc dữ liệu JSON trả về"""
    response = requests.get(f"{BASE_URL}/users/1")
    data = response.json()
    
    # Kiểm tra các trường bắt buộc (QA Requirement)
    assert "id" in data
    assert "email" in data
    assert data["username"] == "Bret" # Giả sử admin/Bret là user mong đợi
    assert "@" in data["email"], "Email format is invalid"