# Optional local helpers

These scanners and evidence checks are optional. They do not call Claude or require model credentials. The native plugin works without Python or Docker.

## Scanner configuration

Copy `profiles/default.json` thành `profiles/local.json`. Mặc định yêu cầu Semgrep,
Gitleaks và OSV nhưng **không có image giả hoặc digest bịa sẵn**. Chọn và pull image
đã duyệt, kiểm tra RepoDigests rồi khai báo:

```json
{
  "required_scanners": ["semgrep", "gitleaks", "osv"],
  "scanners": [
    {"name": "semgrep", "image": "YOUR_SEMGREP_IMAGE@sha256:YOUR_64_HEX_DIGEST"},
    {"name": "gitleaks", "image": "YOUR_GITLEAKS_IMAGE@sha256:YOUR_64_HEX_DIGEST"},
    {"name": "osv", "image": "YOUR_OFFLINE_OSV_IMAGE@sha256:YOUR_64_HEX_DIGEST", "database_date": "YYYY-MM-DD"}
  ]
}
```

Đây là template: phải thay digest/date hợp lệ trước khi dùng. Harness không tự
pull image khi audit (`--pull=never`). Semgrep image cần nhận lệnh `semgrep scan`;
Gitleaks image cần entrypoint `gitleaks`; OSV image cần entrypoint `osv-scanner` v2.
Nếu image đã có entrypoint Semgrep, dùng image wrapper đã duyệt để khớp contract.

OSV chạy `scan source --offline`; image phải chứa database local cho các ecosystem
cần quét và đặt `OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY` tới cache đó. Tuổi database
được khai báo trong trusted policy, không quá 7 ngày. Harness không tự kiểm chứng
nguồn gốc ngày này: pipeline build image phải làm việc đó. Không có network để
download trong lúc audit. Xem [offline database docs](https://github.com/google/osv-scanner/blob/main/docs/offline-mode.md).

Scanner chạy network none, source read-only, non-root, drop capabilities, giới hạn
CPU/RAM/PIDs/output/time. Không mount Docker socket hoặc truyền credentials vào
container. Đây là hardening container, **không phải microVM hay bảo đảm chống
kernel escape**. Dùng runner host riêng cho repository không tin cậy.

Semgrep dùng 4 rule khởi đầu nằm trong package; chưa phải rule pack bao phủ OWASP.
Gitleaks dùng default rules của image thông qua trusted config. Repository-owned
ignore files của Semgrep/Gitleaks bị bỏ trong bản sao scanner; inline suppressions
bị vô hiệu hóa. OSV dùng trusted global config không có vulnerability ignores.
Kết quả scanner chưa được tự động dismiss: có signal thì yêu cầu triage và gate
không xanh, kể cả khi Claude không nhắc tới signal đó.

## Test cô lập

Tạo trusted spec bên ngoài target:

```json
{
  "id": "authorization-regression",
  "image": "YOUR_PREBUILT_TEST_IMAGE@sha256:YOUR_64_HEX_DIGEST",
  "argv": ["python", "-B", "-m", "unittest", "discover", "-s", "tests"],
  "expected_exit": 0
}
```

Image cần có dependencies sẵn. Source read-only; test phải ghi scratch vào `/tmp`.
Harness không chạy install/build script của target trên host.

```powershell
.\.venv\Scripts\csh.exe test C:\path\to\target-repo `
  --ref HEAD --spec C:\path\to\trusted\test.json `
  --out C:\path\to\audit-results\test-001
```

Xuất `test.json` với commit, manifest, command và exit status. Một command pass
**không tự biến finding thành reproduced**; cần review nội dung assertions, chạy
negative/positive controls và đối chiếu baseline với bản vá.

## Gate và CI

| Exit | Kết quả | Ý nghĩa |
|---|---|---|
| 0 | PASS | Không có blocker trong phạm vi được cấu hình; có thể còn finding thấp/trung bình |
| 2 | BLOCK | High/Critical được verifier hỗ trợ bằng source evidence hợp lệ |
| 3 | INCOMPLETE | Thiếu bước, context, tool, cấu hình hoặc bằng chứng |
| 4 | REVIEW | Có nghi vấn chưa thể kết luận |

BLOCK được giữ ngay cả khi còn coverage gaps. Báo cáo có `complete` riêng.
CI chỉ coi exit 0 là đạt; kiểm tra cả artifact và commit SHA tương ứng. Không chạy
workflow PR với write token hoặc production secrets. Harness không có publisher,
không tự merge, không tự cấp waiver và không tự sửa baseline.

`csh schema review`, `csh schema verification`, `csh schema policy`, `csh schema test`
và `csh schema auth-matrix` xuất schema JSON. Các schema trong `schemas/` được sinh
từ model dùng thật; không phải bản viết tay khác implementation.
