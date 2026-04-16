## 2. Demo sinh tài liệu API từ TypeSpec

Thay vì viết tài liệu OpenAPI (YAML) thủ công, em sử dụng **TypeSpec** (ngôn ngữ đặc tả hiện đại của Microsoft) để sinh ra tài liệu chuẩn một cách tự động.

### Các bước thực hiện:
1. **Khởi tạo:** Cài đặt TypeSpec CLI và khởi tạo project bằng lệnh `npm init -y` tại thư mục `typespec`.
2. **Cài đặt Emitter:** Cài đặt bộ phát dữ liệu OpenAPI 3.0: 
   `npm install @typespec/openapi3`
3. **Định nghĩa API:** Viết cấu trúc API thư viện trong file `main.tsp` bằng cú pháp ngắn gọn, dễ quản lý.
4. **Biên dịch (Generate):** Sử dụng lệnh biên dịch trực tiếp trong Terminal của VS Code:
   ```powershell
   npx tsp compile main.tsp --emit @typespec/openapi3