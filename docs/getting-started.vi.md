# Bắt đầu một review hữu ích

Cài **security-harness** từ marketplace `JimmyNguyen09-AI/claude-security-harness`
theo hướng dẫn giao diện trong README. Mở dự án cần kiểm tra trong Claude Code,
rồi nhập vào **ô chat**:

```text
/security-harness:start review dự án này, ưu tiên phân quyền và rò rỉ dữ liệu
```

Harness sẽ đọc cấu trúc, xác định phạm vi và bắt đầu kiểm tra luồng quan trọng.
Không cần học tất cả lệnh hoặc cài scanner trước. Dùng tài khoản Claude Code đang
đăng nhập; không cần API key riêng, Python hay Docker cho workflow native.

## Các tình huống thường gặp

| Mục tiêu | Nhập trong ô chat |
|---|---|
| Review thay đổi | `/security-harness:review so sánh với main, kiểm tra cả callers và lớp phân quyền liên quan` |
| Dự án nhiều service | `/security-harness:campaign audit API, workers và shared auth, lưu checkpoint ngoài repo` |
| SaaS nhiều tenant | `/security-harness:authz kiểm tra DB, cache, jobs và export giữa hai tenant` |
| Viết và chạy test | `/security-harness:test kiểm tra các lỗi đã xác nhận trong môi trường local, có cả ca hợp lệ` |
| Ứng dụng AI Agent | `/security-harness:agent-security kiểm tra quyền tool, approval và cách ly dữ liệu RAG` |
| Kiểm chứng báo cáo | `/security-harness:verify tìm phản chứng cho từng finding vừa báo cáo` |
| Sửa lỗi | `/security-harness:fix sửa AUTHZ-001, giữ quyền truy cập hợp lệ và thay đổi đang có` |
| Lỗi cài đặt | `/security-harness:doctor kiểm tra plugin mà không đổi cấu hình` |

Muốn review kèm sửa, hãy nói rõ "review và sửa". Muốn thu hẹp phạm vi, chỉ định
service, nhánh so sánh hoặc loại rủi ro. Bạn không cần chuyển sang tiếng Anh.

## Đọc kết quả đúng cách

Một finding cần có đường đi thực tế, bằng chứng mã nguồn, điều kiện khai thác,
lớp bảo vệ đã kiểm tra và hướng sửa. Báo cáo cần nêu phiên bản nguồn, phạm vi đã
đọc và phần chưa kiểm tra. Không tìm thấy lỗi trong phạm vi này không đồng nghĩa
toàn hệ thống an toàn.

Một bản sửa chỉ được gọi là đã kiểm chứng khi có kết quả thực thi phù hợp: ca bị
chặn, ca người dùng hợp lệ và kiểm tra side effect. Thiếu database hoặc test lỗi
setup phải được báo là bị chặn, không được tính là test bảo mật thành công.

Với dự án lớn, dùng `campaign` và `resume`; đừng dựa vào trí nhớ hội thoại để tiếp
tục. Giữ báo cáo ngoài repo ứng dụng và loại bỏ dữ liệu khách hàng/token trước
khi chia sẻ. Ghi lại phiên bản plugin, nguồn và môi trường/model của lần review.

Thử [bộ bài đánh giá](../evals/README.md) trước khi dùng kết quả làm điều kiện
release cho cả nhóm. Người phụ trách vẫn cần quyết định chấp nhận rủi ro nào.
Nếu cài đặt có vấn đề, xem [troubleshooting](troubleshooting.md).
