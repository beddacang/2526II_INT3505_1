from locust import HttpUser, task, between

class APIUser(HttpUser):
    # Mỗi user giả lập sẽ đợi từ 1-2 giây giữa các request
    wait_time = between(1, 2)

    @task
    def get_user_info(self):
        """Giả lập request lấy thông tin user"""
        with self.client.get("/users/1", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

    @task(2) # Task này chạy thường xuyên gấp đôi task trên
    def get_all_users(self):
        """Giả lập request lấy danh sách toàn bộ user"""
        self.client.get("/users")