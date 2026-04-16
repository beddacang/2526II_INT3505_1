import "@typespec/http";
import "@typespec/openapi3"; // Thêm dòng này để hỗ trợ xuất OpenAPI

using Http;

@service({ title: "Library API" })
namespace Library;

model Book {
  id: int32;
  title: string;
}

@route("/books")
interface Books {
  @get list(): Book[];
}