# Security Harness cho Claude Code

[English](README.md) · [Giấy phép MIT](LICENSE) · [Báo lỗi bảo mật](SECURITY.md)

**Experimental:** plugin cộng đồng độc lập, không phải sản phẩm chính thức của
Anthropic. Chưa có benchmark hành vi Claude Code hoặc bảo đảm phát hiện đầy đủ lỗi.

Bộ skills để **Claude Code đọc repo, review bảo mật, kiểm chứng và sửa lỗi ngay
trong phiên làm việc của bạn**. Dùng tài khoản/model đang đăng nhập trong Claude
Code; không yêu cầu Anthropic API key, Agent SDK hay một dịch vụ gọi model riêng.
Không cần Python hoặc Docker để dùng các lệnh review/fix.

## Dùng ngay

Sau khi cài, mở dự án cần review và nhập vào **ô chat Claude Code**:

```text
/security-harness:start review dự án này, ưu tiên phân quyền và rò rỉ dữ liệu
```

Harness sẽ chọn workflow, nêu phạm vi rồi bắt đầu phân tích. Xem
[hướng dẫn dùng lần đầu](docs/getting-started.vi.md). Nếu lệnh không xuất hiện,
dùng `/security-harness:doctor` hoặc xem [troubleshooting](docs/troubleshooting.md).
Bản 0.4 có 11 skills và 5 vai trò chuyên môn. Có
[bộ bài đánh giá](evals/README.md) gồm mã lỗi, mã an toàn và tình huống đánh lạc
hướng reviewer; kết quả unit test không được coi là kết quả benchmark Claude.

### Cài bằng giao diện

Repo này đồng thời là một marketplace cộng đồng. Trong tab **Marketplaces** của
trình quản lý plugin, thêm nguồn GitHub:

```text
JimmyNguyen09-AI/claude-security-harness
```

- **Claude Desktop, tab Code:** mở phiên Local, bấm **+** cạnh ô chat, chọn
  **Add plugins** hoặc **Plugins → Browse plugins**.
- **VS Code:** gõ `/plugins` ngay trong ô chat Claude Code để mở giao diện quản lý.

Sau khi thêm marketplace, tìm **security-harness** trong tab **Plugins**, bấm
**Install** và chọn phạm vi cài đặt. Mở phiên mới nếu giao diện yêu cầu. Nhập
`/security-harness:review` trong ô chat để bắt đầu.

Tên marketplace là `claude-security-harness`; tên plugin là `security-harness`.
Đây là catalog cộng đồng do repo cung cấp, chưa phải danh sách chính thức của
Anthropic. Trình duyệt plugin Desktop dùng cho phiên Local/SSH; không có trong
phiên Cloud hoặc WSL.

Tham khảo hướng dẫn chính thức cho
[Desktop](https://code.claude.com/docs/en/desktop#install-plugins) và
[VS Code](https://code.claude.com/docs/en/vs-code#manage-plugins).

### Nạp từ thư mục local

Từ thư mục dự án muốn review, mở Claude Code và nạp plugin local:

```powershell
cd C:\path\to\your-project
claude --plugin-dir C:\tools\claude-security-harness
```

Đăng nhập Claude Code như bình thường nếu chưa đăng nhập. Trong phiên đó:

```text
/security-harness:review
/security-harness:authz kiểm tra API, phân quyền và truy cập chéo tenant
/security-harness:verify kiểm chứng các findings vừa tìm được
/security-harness:fix sửa các lỗi đã xác nhận và thêm regression tests
```

Với repo lớn, monorepo hoặc nhiều service, dùng luồng v0.3:

```text
/security-harness:campaign audit toàn bộ monorepo, ưu tiên auth, tenant isolation và billing; chia work packages và lưu checkpoint ngoài repo
/security-harness:threat-model lập bản đồ trust boundary và các abuse case giữa API, worker, database và dịch vụ ngoài
/security-harness:test viết và chạy security tests trong môi trường local, gồm cả ca bị từ chối và ca hợp lệ
/security-harness:agent-security kiểm tra prompt injection, quyền tool, memory/RAG isolation và approval replay
/security-harness:resume tiếp tục campaign tại C:\audits\my-project\run-001
```

`campaign` điều phối năm vai trò architect, reviewer, tester, verifier và fixer.
Các định nghĩa native agents nằm trong `agents/`; Claude Code có thể dùng chúng khi
task/phiên cho phép delegation. Nếu không, các vai trò chạy tuần tự và ghi rõ điều
đó. Tester/fixer dùng quyền bình thường của phiên; ba vai trò còn lại chỉ có tools
đọc/tìm kiếm. Không ghi đè model hoặc cấp bypass permissions.

Coverage được theo dõi theo **bề mặt hệ thống × 18 nhóm rủi ro**, tách static/dynamic.
Mỗi ô cần bằng chứng hoặc lý do N/A; test chưa chạy, môi trường lỗi, phạm vi chưa
đọc và dữ liệu cũ sau thay đổi đều không được biến thành kết quả đạt. Đọc
[thiết kế scale và tester](docs/scalable-campaigns.md) để xem quy trình chi tiết.

Có thể chỉ định phạm vi và yêu cầu kết hợp:

```text
/security-harness:review so sánh với main, tập trung auth, billing và error handling
/security-harness:review review và sửa lỗi bảo mật trong src/api, giữ nguyên các sửa đổi đang có
/security-harness:fix AUTHZ-001, đảm bảo owner vẫn truy cập được và tenant khác bị chặn
```

`review` chỉ phân tích nếu chưa được yêu cầu sửa. Khi đã yêu cầu review-và-sửa hoặc
gọi `fix`, Claude được hướng dẫn tiếp tục sửa và kiểm tra trong phạm vi đó.
Mặc định báo cáo trong chat; thêm đường dẫn output nếu muốn lưu file. Review có
thể đọc cả thay đổi chưa commit, staged/unstaged và untracked trong phạm vi đã chọn.

Nếu dùng Claude Code trong IDE, có thể cài bằng giao diện theo hướng dẫn ở trên.
Bản ZIP local nằm trong `dist/`; giải nén và
trỏ `--plugin-dir` vào thư mục chứa `.claude-plugin/plugin.json` để dùng ở máy khác.
Plugin không được tự cài vào cấu hình global hoặc ghi đè CLAUDE.md của dự án.
ZIP chứa plugin native và script stdlib tùy chọn để kiểm tra campaign. Bộ Python
scanner/helper riêng nằm trong source repository. Các skills vẫn dùng được khi
không có Python.

## Các lệnh làm gì?

| Lệnh | Kết quả |
|---|---|
| `start` | Tự chọn workflow, xác định phạm vi và bắt đầu review |
| `doctor` | Chẩn đoán cấu trúc/cài đặt plugin mà không sửa cấu hình |
| `review` | Bản đồ luồng quan trọng, finding có bằng chứng, counterevidence và coverage |
| `authz` | Ma trận subject/action/resource/tenant/context; kiểm tra quyền object, field, function |
| `verify` | Verdict cho từng finding; tìm lớp bảo vệ bị bỏ sót, phân biệt giả thuyết với tái hiện thật |
| `fix` | Bản sửa tập trung, negative/positive tests và kiểm tra diff cuối |
| `campaign` | Chia phạm vi, điều phối vai trò, theo dõi coverage và checkpoint |
| `threat-model` | Trust boundaries, threat register và kế hoạch kiểm chứng |
| `test` | Thiết kế/triển khai/chạy test bảo mật với oracle và execution scope |
| `agent-security` | Kiểm thử bề mặt tấn công đặc thù AI Agent |
| `resume` | Tiếp tục campaign và phát hiện source/config/fixture đã thay đổi |

Các kỹ năng ưu tiên auth/authz, tenant isolation, injection, secrets/configuration,
transaction, retry, idempotency, race condition và fail-open. Khi scanner không có,
Claude vẫn tiếp tục đọc code và ghi rõ giới hạn kiểm tra.

Harness không thay model, cấp quyền shell tự động, bỏ qua permission hay tự thêm
MCP/hook. Claude dùng tools và quyền của phiên hiện tại. Skills hướng dẫn quy trình;
chúng **không phải sandbox**. Kiểm chứng trong cùng phiên được ghi là self-verification,
không giả định một lượt prompt mới là reviewer độc lập. Test chỉ được ghi là đã
chạy khi có kết quả thực tế. Không tự commit/push/deploy ngoài yêu cầu của người dùng.

## Cấu trúc chính

```text
.claude-plugin/plugin.json
skills/
  review/SKILL.md
    references/audit-procedure.md
    references/report-contract.md
    references/failure-paths.md
  authz/SKILL.md
    references/authorization.md
  verify/SKILL.md
  fix/SKILL.md
  campaign/SKILL.md
    scripts/campaign_state.py
  threat-model/SKILL.md
  test/SKILL.md
  agent-security/SKILL.md
  resume/SKILL.md
agents/
  security-architect.md
  security-reviewer.md
  security-tester.md
  security-verifier.md
  security-fixer.md
```

## Công cụ Python tùy chọn

Phần Python từ bản đầu được giữ làm **local helper**, đã bỏ code gọi Claude SDK,
dependency SDK và các flag `--claude`/`--model`. Không cần cài phần này để dùng plugin.
Nó hỗ trợ snapshot Git, scanner/test Docker và kiểm tra JSON do Claude Code viết:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\csh.exe audit C:\path\to\repo `
  --ref HEAD `
  --review-json C:\audits\review.json `
  --verification-json C:\audits\verification.json `
  --auth-matrix C:\audits\auth-matrix.json `
  --policy C:\audits\policy.json `
  --out C:\audits\checked-run
```

Helper đối chiếu quote/path/line với **commit đã chọn**, không với dirty worktree.
Không được commit thay đổi của người dùng chỉ để chạy helper. Thiếu artifact hoặc
scanner bắt buộc thì helper trả INCOMPLETE; điều đó không ngăn review native trong
Claude Code. Xem [local helpers](docs/local-helpers.md) để cấu hình Docker/scanner.

## Kiểm tra và tài liệu

```powershell
claude plugin validate .
.\.venv\Scripts\python.exe -m pytest -q
python scripts/package_plugin.py
```

[Thiết kế](docs/architecture.md) · [Nguồn tham khảo](docs/sources.md) ·
[Kết quả kiểm tra](docs/validation.md).

Đây là harness hỗ trợ review; chưa có benchmark xác nhận recall/precision hoặc
khả năng phát hiện đầy đủ lỗ hổng trên codebase thực tế.
