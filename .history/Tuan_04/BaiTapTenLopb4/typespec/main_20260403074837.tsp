import "@typespec/http";
import "@typespec/rest";
import "@typespec/openapi3";

using TypeSpec.Http;
using TypeSpec.Rest;

@service({ title: "Library Management" })
namespace Library;

model Book {
  @key id: int32;
  title: string;
  author: string;
}

@route("/books")
interface Books {
  @get list(): Book[];
}