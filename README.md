# Muse Terminal Connector — cho Muse một terminal thật trên Mac của bạn, theo cách an toàn

Skill này đóng gói quy trình đã chạy thật thành công ngày 2026-10-29 (Mac macOS 26.6.2) để một Muse agent có thể tự chạy lệnh trên Mac của người dùng, thay vì nhờ người dùng chạy hộ từng file `.command`.

## Vấn đề nó giải quyết

Kênh điều khiển Mac đi kèm Muse chỉ có file và màn hình: không có shell, Terminal bị chặn cố ý. Nhưng Muse và Mac thường đã cùng ở trong một mạng Tailscale, và đường hầm Tailscale chở được TCP thuần, bao gồm SSH. Thiếu mỗi một mắt xích: Mac chưa bật Remote Login, và không ai muốn bật nó theo cấu hình mặc định.

## Mô hình an toàn

- Chỉ đăng nhập bằng SSH key. Mật khẩu bị tắt hẳn ở phía server, và bài test cuối quy trình cố tình thử đăng nhập bằng mật khẩu để nhìn nó bị từ chối.
- Chỉ một tài khoản Mac, và chỉ từ đúng một địa chỉ nguồn là IP Tailscale của máy ảo Muse (`AllowUsers user@ip`). Máy khác cùng Wi-Fi hay cùng tailnet cũng không thử key được.
- Không root login, không port forwarding, không X11, tối đa 3 lần thử xác thực.
- Thu hồi bất cứ lúc nào theo 3 cách từ nhẹ tới mạnh: xoá dòng key trong `~/.ssh/authorized_keys`, xoá file cấu hình sshd, hoặc tắt Remote Login.
- Người dùng chỉ phải tự tay làm 2 việc macOS bắt chính chủ làm: gõ mật khẩu admin khi chạy installer, và bấm cấp Full Disk Access trong Settings.

## Quy trình tóm tắt

1. Agent thu thập: tên user Mac, IP Tailscale của VM, địa chỉ Mac trên tailnet, public key của VM.
2. Agent render installer từ template bằng `scripts/render_installer.py` (không sửa tay, có kiểm tra định dạng và chặn IP ngoài dải tailnet).
3. Người dùng chạy installer một lần trong Terminal bằng `zsh ~/Downloads/<tên file>` vì file chép qua kênh device không có quyền thực thi. Installer thêm key, tạo host key trước khi kiểm tra cấu hình, ghi cấu hình siết chặt, tự gỡ nếu cấu hình sai, bật Remote Login, và ghi log có mốc hoàn tất.
4. Agent SSH vào qua `scripts/proxy_connect.py` (HTTP CONNECT qua proxy của đường hầm Tailscale ở cổng 3130 — cổng 3128 là egress web thông thường và sẽ giết kết nối SSH).
5. Agent kiểm chứng: lệnh định danh, ghi/xoá file thử, thử đăng nhập mật khẩu để xem bị từ chối, đối chiếu `sshd -T`.
6. Nếu cần đọc Downloads/Documents/Desktop qua SSH, người dùng cấp Full Disk Access cho `/usr/libexec/sshd-keygen-wrapper`. Agent mở sẵn đúng trang Settings và copy sẵn đường dẫn vào clipboard để người dùng chỉ còn vài click.

## Bài học đắt giá đã gói vào skill

- Cổng proxy 3128 giết SSH trước cả bước xác thực. Mọi kết luận "không SSH được" rút ra từ cổng đó đều sai, phải dùng 3130.
- Mac chưa từng làm SSH server thì chưa có host key, và `sshd -t` sẽ báo lỗi như thể cấu hình sai. Tạo host key trước, kiểm tra sau.
- File `.command` chép từ xa không có execute bit. Chạy bằng `zsh <đường dẫn>` trong Terminal, đừng double-click.
- Ba thư mục Downloads, Documents, Desktop là vùng TCC riêng. SSH bị "Operation not permitted" ở đó là chuyện Full Disk Access, không phải chuyện SSH.

## Cấu trúc thư mục

- `SKILL.md` — playbook cho agent, từng bước một.
- `skill.yaml` — mô tả để hệ thống tìm thấy skill.
- `scripts/proxy_connect.py` — trợ thủ ProxyCommand cho ssh, đã test sống.
- `scripts/installer_template.command` — installer mẫu với placeholder, chính là bản đã cài thành công, đã xoá mọi giá trị cá nhân.
- `scripts/render_installer.py` — điền placeholder có kiểm tra, dùng cho cả installer và wrapper.
- `scripts/mac_wrapper_template.sh` — mẫu lệnh gọi tắt `mac '<lệnh>'` cho các lần dùng sau.
