# Muse Terminal Connector

## Cái này để làm gì?

Bình thường Muse **không tự chạy được lệnh trên Mac của bạn**. Mỗi lần cần cài đặt hay render gì trên Mac, Muse phải nhờ bạn chạy hộ một file, khá phiền.

Cài xong bộ này, **Muse tự làm được các việc đó luôn**, qua một kết nối đã khoá chặt: chỉ đúng Muse của bạn mới vào được, người lạ không vào được, và bạn gỡ bỏ lúc nào cũng được.

Bạn **không cần biết gì về IT**. Bạn chỉ cần làm 2 việc: cài 2 phần mềm đơn giản ở mục dưới, rồi copy các câu lệnh (prompt) có sẵn dán vào khung chat với Muse. Phần khó Muse tự lo.

## Cần cài những phần mềm gì?

Chỉ 2 phần mềm, đều miễn phí:

### 1. Muse cho Mac

- Tải tại: https://ai.meta.com/muse/download/
- Mở file vừa tải, cài như mọi app Mac bình thường, mở app lên và **đăng nhập tài khoản Muse của bạn**.
- Nếu app hỏi ghép nối Mac này với Muse thì bấm đồng ý.

### 2. Tailscale

Đây là phần mềm tạo một "mạng riêng" nối Mac của bạn với Muse, để hai bên nói chuyện với nhau an toàn.

- Tải tại: https://tailscale.com/download/mac (hoặc mở App Store trên Mac, tìm "Tailscale").
- Cài xong mở app, bấm **Log in** và đăng nhập (bằng Google, Apple... tuỳ bạn).
- Máy hỏi cho phép thêm VPN thì bấm **Allow**.

Ngoài 2 phần mềm trên thì **không cần cài thêm gì nữa**. Mac của bạn chỉ cần là macOS bản tương đối mới (đã kiểm chứng trên macOS 26) và bạn nhớ mật khẩu mở khoá/quản trị của máy mình.

## Cách dùng: copy prompt dán vào chat với Muse

Làm lần lượt từng prompt. Copy nguyên văn, dán vào khung chat với Muse của bạn, gửi đi, rồi làm theo hướng dẫn Muse trả lời.

### Prompt 1 — Cài đặt (chỉ làm 1 lần)

```text
Hãy tải skill Muse Terminal Connector từ https://github.com/kieentrong/muse-terminal-connector, cài vào thư mục custom-skills của bạn, đọc kỹ SKILL.md trong đó rồi cấu hình cho tôi theo đúng quy trình trong skill: cho bạn quyền chạy Terminal trên Mac của tôi qua SSH đã siết chặt (chỉ dùng key, tắt đăng nhập bằng mật khẩu, chỉ cho phép kết nối từ đúng máy của bạn). Trước khi thay đổi bất cứ thứ gì trên Mac của tôi, hãy giải thích ngắn gọn bằng tiếng Việt dễ hiểu là bạn sắp làm gì và có rủi ro gì, đợi tôi đồng ý rồi mới làm. Phần nào macOS bắt chính tôi thao tác, hãy hướng dẫn tôi từng bước thật đơn giản, mỗi lần một bước.
```

Trong lúc Muse làm, bạn sẽ được nhờ làm **2 việc nhỏ**, Muse sẽ chỉ tận nơi:

- **Chạy một lệnh trong Terminal:** mở Terminal bằng cách nhấn `Cmd + Space`, gõ `Terminal`, Enter — rồi dán đúng dòng Muse đưa, gõ **mật khẩu của Mac** khi máy hỏi (gõ mà không thấy chữ hiện là bình thường).
- **Duyệt kết nối:** nếu Muse đưa một link hoặc hỏi duyệt, bấm duyệt là xong.

### Prompt 2 — Mở quyền đọc mọi thư mục (nên làm, sau Prompt 1)

```text
Làm tiếp bước Full Disk Access trong skill Muse Terminal Connector, để bạn đọc được cả các thư mục Downloads, Documents, Desktop trên Mac của tôi qua SSH. Mở sẵn trang cài đặt và copy sẵn đường dẫn như skill hướng dẫn, rồi chỉ cho tôi từng click cần bấm, mỗi lần một bước.
```

### Prompt 3 — Kiểm tra khi nào thấy lạ

```text
Kiểm tra giúp tôi kết nối Terminal vào Mac còn hoạt động không. Chạy thử một lệnh vô hại trên Mac và báo kết quả thật cho tôi.
```

### Prompt gỡ bỏ — Khi không muốn dùng nữa

```text
Thu hồi quyền chạy Terminal trên Mac mà tôi đã cấp cho bạn theo skill Muse Terminal Connector: hướng dẫn tôi tắt Remote Login và xoá key của bạn khỏi Mac, từng bước đơn giản, rồi kiểm tra lại và xác nhận là bạn không còn vào được nữa.
```

## Câu hỏi thường gặp

**Có an toàn không?**
Có, nếu làm đúng quy trình Muse sẽ tự áp dụng: chỉ Muse của bạn vào được bằng một "chìa khoá" riêng, đăng nhập bằng mật khẩu bị tắt hẳn, người lạ dù biết địa chỉ cũng không vào được. Bạn vẫn là người quyết định cuối cùng: mỗi thay đổi lớn trên máy đều phải qua tay bạn duyệt hoặc gõ mật khẩu.

**Có mất phí không?**
Không. Hai phần mềm ở trên miễn phí. Muse thì theo gói bạn đang dùng sẵn.

**Tôi không rành máy tính, lỡ làm sai thì sao?**
Cứ dừng lại và nhắn cho Muse: "tôi đang kẹt ở bước này" kèm ảnh chụp màn hình. Hầu hết các bước đều làm lại được từ đầu một cách an toàn.

**Muốn xem chi tiết kỹ thuật thì xem ở đâu?**
Toàn bộ quy trình kỹ thuật nằm trong file `SKILL.md` — đó là tài liệu cho Muse đọc, bạn không cần đọc cũng được.

## Giấy phép

Repo này dùng giấy phép **MIT** (toàn văn trong file `LICENSE`): ai cũng được dùng, sao chép, sửa đổi và chia sẻ lại, kể cả dùng cho thương mại, chỉ cần giữ lại dòng ghi công tác giả kèm theo. Phần mềm được cung cấp "nguyên trạng", không kèm bảo hành.
