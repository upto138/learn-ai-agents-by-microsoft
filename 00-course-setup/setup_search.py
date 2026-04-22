import os
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import SearchIndex, SimpleField, edm
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType as edm,
)

# 1. Lấy thông tin từ biến môi trường
service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
api_key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = "sample-index"

credential = AzureKeyCredential(api_key)

# 2. Tạo client quản lý Index
index_client = SearchIndexClient(service_endpoint, credential)

# Định nghĩa Schema cho Index
fields = [
    SimpleField(name="id", type=edm.String, key=True),
    SimpleField(name="content", type=edm.String, searchable=True),
]

index = SearchIndex(name=index_name, fields=fields)

# Thực thi tạo Index trên server
print(f"Đang tạo index '{index_name}'...")
try:
    index_client.create_index(index)
    print("Tạo index thành công!")
except HttpResponseError as e:
    if e.error and e.error.code == "ResourceNameAlreadyInUse":
        print(f"Index '{index_name}' đã tồn tại, bỏ qua bước tạo mới.")
    else:
        raise

# 3. Tạo client thao tác với Data (Documents)
search_client = SearchClient(service_endpoint, index_name, credential)

# Chuẩn bị dữ liệu mẫu
documents = [
    {"id": "1", "content": "Hello world"},
    {"id": "2", "content": "Azure Cognitive Search"}
]

# Thực thi đẩy dữ liệu lên server
print("Đang upload dữ liệu...")
result = search_client.upload_documents(documents)
print(f"Đã upload xong {len(result)} documents!")