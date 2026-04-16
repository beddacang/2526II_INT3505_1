import "@typespec/http";
import "@typespec/openapi3"; // Rất quan trọng: Thêm dòng này để hỗ trợ xuất file OpenAPI

using Http;

/**
 * API Quản lý thư viện đơn giản cho bài tập Tuần 4
 */
@service({
  title: "Library API",
})
namespace Library;

model Book {
  id: int32;
  title: string;
  author?: string; // Bạn có thể thêm các trường khác nếu muốn
}

@route("/books")
interface Books {
  @get list(): Book[];
}