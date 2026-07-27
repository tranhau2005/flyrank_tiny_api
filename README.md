# FlyRank Tiny Task API

Một REST API quản lý công việc (task) đơn giản, được xây dựng bằng FastAPI và Pydantic. API hỗ trợ đầy đủ các thao tác tạo, đọc, cập nhật và xóa (CRUD), kèm kiểm tra dữ liệu đầu vào và tài liệu tương tác tự động.

## Tính năng

- Lấy danh sách hoặc chi tiết một task.
- Tạo task mới với tiêu đề bắt buộc.
- Cập nhật tiêu đề hoặc trạng thái hoàn thành của task.
- Xóa task theo ID.
- Trả về lỗi `400` khi dữ liệu không hợp lệ và `404` khi không tìm thấy task.
- Cung cấp Swagger UI và ReDoc tự động.

> [!NOTE]
> Dữ liệu hiện được lưu trong bộ nhớ. Mọi thay đổi sẽ mất và danh sách task mẫu sẽ được khôi phục khi server khởi động lại.

## Yêu cầu

- Python 3.10 trở lên
- `pip`

## Cài đặt

Clone repository và di chuyển vào thư mục dự án:

```bash
git clone https://github.com/tranhau2005/flyrank_tiny_api.git
cd flyrank_tiny_api
```

Tạo và kích hoạt môi trường ảo:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Trên Windows, kích hoạt môi trường ảo bằng lệnh:

```powershell
.venv\Scripts\activate
```

Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
uvicorn main:app --reload --port 8000
```

Server mặc định chạy tại `http://127.0.0.1:8000`.

Tài liệu API tương tác:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Các endpoint

| Phương thức | Endpoint | Mô tả | Mã thành công |
| --- | --- | --- | --- |
| `GET` | `/` | Thông tin cơ bản của API | `200` |
| `GET` | `/health` | Kiểm tra trạng thái server | `200` |
| `GET` | `/tasks` | Lấy tất cả task | `200` |
| `GET` | `/tasks/{id}` | Lấy một task theo ID | `200` |
| `POST` | `/tasks` | Tạo task mới | `201` |
| `PUT` | `/tasks/{id}` | Cập nhật một hoặc nhiều trường của task | `200` |
| `DELETE` | `/tasks/{id}` | Xóa task theo ID | `204` |

Mỗi task có cấu trúc:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "done": false
}
```

## Ví dụ sử dụng

### Lấy danh sách task

```bash
curl http://127.0.0.1:8000/tasks
```

### Lấy task theo ID

```bash
curl http://127.0.0.1:8000/tasks/1
```

Nếu ID không tồn tại, API trả về `404`:

```json
{
  "detail": "Task 999 was not found"
}
```

### Tạo task mới

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Write project documentation"}'
```

Kết quả:

```json
{
  "id": 4,
  "title": "Write project documentation",
  "done": false
}
```

`title` không được để trống. Khoảng trắng ở đầu và cuối tiêu đề sẽ được loại bỏ.

### Cập nhật task

Có thể gửi `title`, `done` hoặc cả hai trường:

```bash
curl -X PUT http://127.0.0.1:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"title":"Finish project documentation","done":true}'
```

Request phải chứa ít nhất một trường. `title` không được rỗng và `done` không được là `null` hoặc chuỗi rỗng.

### Xóa task

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/4
```

Khi xóa thành công, API trả về `204 No Content` và không có response body.

### Kiểm tra server

```bash
curl http://127.0.0.1:8000/health
```

Kết quả:

```json
{
  "status": "oke"
}
```

## Cấu trúc dự án

```text
flyrank_tiny_api/
├── main.py           # Khai báo ứng dụng, schema và các endpoint
├── requirements.txt  # Danh sách thư viện Python
└── README.md          # Tài liệu dự án
```
