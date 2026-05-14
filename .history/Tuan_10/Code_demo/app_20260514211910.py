import logging
import time
import random
from fastapi import FastAPI, Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

# 1. THIẾT LẬP LOGGING (Audit & Application Logs)
logging.basicConfig(level=logging.INFO, format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
logger = logging.getLogger("production_api")

# 2. THIẾT LẬP RATE LIMITING (Giới hạn tốc độ)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Production Ready API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. THIẾT LẬP METRICS (Giám sát cho Prometheus/Grafana)
Instrumentator().instrument(app).expose(app)

# --- GIẢ LẬP CIRCUIT BREAKER ---
class CircuitBreaker:
    def __init__(self):
        self.is_open = False
        self.failure_count = 0
        self.threshold = 3  # Quá 3 lỗi sẽ ngắt mạch

    def call_service(self):
        if self.is_open:
            logger.warning("Circuit is OPEN - Request rejected immediately")
            raise HTTPException(status_code=503, detail="Service Unavailable (Circuit Breaker Open)")
        
        # Giả lập gọi một service bên thứ 3 (ví dụ: API Thanh toán)
        success = random.choice([True, False])
        if not success:
            self.failure_count += 1
            logger.error(f"External Service Failed ({self.failure_count}/{self.threshold})")
            if self.failure_count >= self.threshold:
                self.is_open = True
            raise HTTPException(status_code=500, detail="External Service Error")
        
        self.failure_count = 0 # Reset nếu thành công
        return {"status": "success", "data": "Payment Processed"}

cb = CircuitBreaker()

# --- CÁC ENDPOINT ---

@app.get("/")
@limiter.limit("5/minute")  # Giới hạn 5 request mỗi phút
async def root(request: Request):
    logger.info(f"User {request.client.host} accessed root")
    return {"message": "Chào mừng đến với API Production!"}

@app.get("/checkout")
async def checkout():
    # Sử dụng Circuit Breaker để bảo vệ hệ thống
    return cb.call_service()

@app.get("/admin/reset-circuit")
async def reset_circuit():
    # Audit Log: Ghi lại hành động nhạy cảm
    logger.info("AUDIT: Admin manual reset circuit breaker")
    cb.is_open = False
    cb.failure_count = 0
    return {"message": "Circuit reset successfully"}