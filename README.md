# Muse Terminal Connector — cho Muse một terminal thật trên Mac của bạn, theo cách an toàn

Skill này đóng gói quy trình đã chạy thật thành công ngày 2026-10-29 để một Muse agent có thể tự chạy lệnh trên Mac của người dùng qua SSH, thay vì nhờ người dùng chạy hộ từng file `.command`. Kết nối đi qua mạng Tailscale riêng của chính người dùng, SSH bị khoá chỉ còn một key, một tài khoản, một địa chỉ nguồn, và thu hồi được bất cứ lúc nào.

## Vấn đề nó giải quyết

Kênh điều khiển Mac đi kèm Muse chỉ có file và màn hình: không có shell, Terminal bị chặn cố ý. Nhưng Muse và Mac thường đã cùng ở trong một mạng Tailscale, và đường hầm Tailscale chở được TCP thuần, bao gồm SSH. Thiếu mỗi một mắt xích: Mac chưa bật Remote Login, và không ai muốn bật nó theo cấu hình mặc định.

## Hệ điều hành hỗ trợ

- **Máy đích (máy được điều khiển): chỉ macOS.** Toàn bộ quy trình dựa trên các thành phần riêng của macOS là OpenSSH server tích hợp, `systemsetup`, thư mục cấu hình `/etc/ssh/sshd_config.d/` và cơ chế TCC Full Disk Access.
- **Đã kiểm chứng đầu cuối trên macOS 26.6.2 (Tahoe), Mac Apple Silicon.** Các bản macOS gần đây (Ventura 13 trở lên) có cùng cơ chế nên dự kiến dùng được, nhưng ngoài bản 26.6.2 thì chưa kiểm chứng — ai chạy bản khác nên đi đủ bước kiểm chứng ở dưới thay vì tin ngay.
- **Phía agent: máy ảo Linux của Muse**, nơi có sẵn `ssh`, Python 3 và công cụ Tailscale của Muse. Quy trình này viết cho cặp Muse + Mac, không áp dụng cho máy đích Windows hay Linux.

## Cần cài thêm những gì

Chỉ hai thứ, cả hai đều miễn phí cho nhu cầu cá nhân:

1. **Tailscale, cài ở cả hai phía và đăng nhập cùng một mạng (tailnet):**
   - Trên Mac: cài app Tailscale từ Mac App Store hoặc từ [tailscale.com/download](https://tailscale.com/download), mở app và đăng nhập.
   - Phía Muse: máy ảo Muse tham gia tailnet bằng `tailscale up`, người dùng mở link duyệt một lần là xong. Kiểm tra bằng `tailscale status` ở phía agent: phải thấy cả máy ảo Muse và Mac trong cùng danh sách.
2. **Muse app trên Mac, đã ghép nối với tài khoản Muse của bạn** (tải tại [ai.meta.com/muse/download](https://ai.meta.com/muse/download/)). Kênh này dùng để agent gửi file installer vào `~/Downloads` và đọc log kết quả. Đây là kênh sẵn có của Muse, không phải phần mềm lạ.

Ngoài ra **không cần cài thêm gì**: OpenSSH server và client, `zsh`, `systemsetup`, `lsof` đều có sẵn trong macOS; phía máy ảo Muse có sẵn `ssh` và Python 3. Không cần Homebrew, không cần Xcode, không cần mở port trên router.

Điều kiện đi kèm: bạn có **mật khẩu admin của Mac** (installer sẽ hỏi một lần qua `sudo`) và có quyền duyệt thiết bị mới vào tailnet của mình.

## Giấy phép

Repo này dùng **giấy phép MIT** (toàn văn trong file `LICENSE` ở thư mục gốc). Hiểu đơn giản:

- **Được** dùng, sao chép, sửa đổi, gộp, xuất bản, phân phối và bán lại, kể cả cho mục đích thương mại.
- **Điều kiện duy nhất:** giữ nguyên dòng ghi công tác giả và toàn văn giấy phép MIT trong mọi bản sao hoặc phần đáng kể của repo.
- **Không có bảo hành:** phần mềm được cung cấp "nguyên trạng", tác giả không chịu trách nhiệm cho bất kỳ thiệt hại nào phát sinh từ việc sử dụng.
- Giấy phép MIT chỉ áp dụng cho nội dung trong repo này. Muse, Tailscale và macOS là sản phẩm của các hãng tương ứng với điều khoản riêng của họ.

## Hướng dẫn đầy đủ

### Bước 0 — Thỏa thuận an toàn trước khi đụng vào máy

Agent phải nói rõ với người dùng trước: bật Remote Login là mở một cổng SSH trên Mac, và key đưa cho máy ảo Muse tương đương quyền chạy lệnh như chính tài khoản của người dùng nếu máy ảo đó bị xâm nhập. Chỉ tiến hành khi người dùng đồng ý rõ ràng với bản cấu hình siết chặt ở các bước sau.

### Bước 1 — Thu thập các giá trị cần thiết

Phía máy ảo Muse, chạy:

```bash
/opt/hatch/bin/tailscale status     # ghi lại IPv4 của máy ảo Muse và tên + IPv4 của Mac
cat ~/.ssh/id_ed25519.pub           # public key của máy ảo
```

Nếu chưa có key, tạo một cặp key riêng cho việc này:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""
```

Phía Mac, cần **tên tài khoản macOS** (ví dụ dạng `nguyen.van.a` — hãy dùng tên thật của bạn). Agent lấy qua lệnh môi trường của thiết bị đã ghép nối, hoặc người dùng tự xem bằng `whoami` trong Terminal.

Ba giá trị sẽ dùng: public key của máy ảo, tên tài khoản Mac, IPv4 tailnet của máy ảo. Tên MagicDNS của Mac (dạng `ten-mac.tailXXXX.ts.net`) dùng làm địa chỉ SSH ở bước 4.

### Bước 2 — Render installer từ template

Đừng sửa template bằng tay. Dùng script render, nó kiểm tra định dạng key, tên user và bắt buộc IP phải thuộc dải tailnet `100.64.0.0/10`:

```bash
python3 scripts/render_installer.py scripts/installer_template.command ~/Cai-SSH-cho-Muse.command \
  --pubkey-file ~/.ssh/id_ed25519.pub \
  --mac-user <ten-tai-khoan-mac> \
  --vm-ip <ipv4-tailnet-cua-may-ao>
```

Agent chép file vừa render vào `~/Downloads` trên Mac qua kênh file của Muse và **đối chiếu số byte** hai phía để chắc chắn file sang nguyên vẹn.

### Bước 3 — Người dùng chạy installer đúng một lần

Trên Mac, mở Terminal (Cmd + Space, gõ `Terminal`) và chạy:

```bash
zsh ~/Downloads/Cai-SSH-cho-Muse.command
```

Đừng double-click file: file chép qua kênh từ xa không có quyền thực thi nên double-click sẽ báo lỗi privileges. Installer sẽ:

1. Thêm public key của máy ảo vào `~/.ssh/authorized_keys` (đã có thì bỏ qua, chạy lại an toàn).
2. Ghi cấu hình sshd siết chặt vào `/etc/ssh/sshd_config.d/100-muse-hardened.conf` (có sao lưu nếu đã tồn tại bản cũ), gồm: tắt đăng nhập mật khẩu, tắt root login, `AllowUsers <user>@<ipv4 máy ảo>`, tắt forwarding và X11, tối đa 3 lần thử.
3. Tạo SSH host key bằng `ssh-keygen -A` **trước** khi kiểm tra cấu hình bằng `sshd -t`. Cấu hình sai thì installer tự gỡ file vừa ghi và dừng, không bật gì cả.
4. Bật Remote Login và tự kiểm chứng: trạng thái Remote Login, cấu hình hiệu lực qua `sshd -T`, cổng 22.
5. Ghi toàn bộ vào log `~/Downloads/cai-ssh-muse.log` và kết thúc bằng dòng mốc `MUSE_SSH_SETUP_DONE`.

Trong lúc chạy, Terminal hỏi mật khẩu admin một lần — người dùng gõ trực tiếp trên Mac, không bao giờ gửi qua chat.

### Bước 4 — Kết nối thử từ phía Muse

SSH thường không tới được địa chỉ tailnet. Phải đi qua proxy của đường hầm Tailscale ở **cổng 3130** bằng trợ thủ `proxy_connect.py` trong vai `ProxyCommand`:

```bash
ssh -o ProxyCommand="python3 scripts/proxy_connect.py %h %p" \
  -i ~/.ssh/id_ed25519 \
  <user>@<ten-mac>.tailXXXX.ts.net 'hostname; whoami; sw_vers -productVersion'
```

Lưu ý sống còn: cổng **3128** là proxy egress web thông thường và nó **giết kết nối SSH trước cả bước xác thực**. Mọi kết luận "không SSH được" rút ra từ cổng 3128 đều sai.

Lần đầu kết nối tới một địa chỉ tailnet, hệ thống có thể hiện thẻ xin quyền — người dùng duyệt một lần, và quyền đó bao phủ các dịch vụ TCP khác, gồm SSH, trên đúng địa chỉ đó. Hãy dùng nhất quán một địa chỉ (ưu tiên tên MagicDNS) để không phải duyệt lại.

Để dùng hằng ngày, render sẵn lệnh gọi tắt từ `scripts/mac_wrapper_template.sh`:

```bash
python3 scripts/render_installer.py scripts/mac_wrapper_template.sh ~/mac \
  --mac-user <ten-tai-khoan-mac> \
  --mac-host <ten-mac>.tailXXXX.ts.net \
  --proxy-path <duong-dan-tuyet-doi-toi-proxy_connect.py>
chmod +x ~/mac
~/mac 'ls ~/Downloads | head'
```

### Bước 5 — Kiểm chứng đầu cuối, không tin lời nói suông

Cả bốn bài test đều phải qua trước khi tuyên bố xong:

1. **Định danh:** lệnh ở bước 4 trả về đúng hostname của Mac, đúng tên user và đúng phiên bản macOS.
2. **Ghi thử:** qua SSH, tạo rồi xoá một file rỗng trong thư mục home của Mac. Đăng nhập mà không ghi được là chưa đạt.
3. **Cấu hình hiệu lực:** trong log installer, phần `sshd -T` phải cho thấy `passwordauthentication no`, `kbdinteractiveauthentication no`, `pubkeyauthentication yes`, `permitrootlogin no` và đúng dòng `allowusers <user>@<ipv4 máy ảo>`.
4. **Thử đường yếu:** cố tình đăng nhập bằng mật khẩu và phải bị từ chối:

```bash
ssh -o PubkeyAuthentication=no -o PreferredAuthentications=password \
  -o ProxyCommand="python3 scripts/proxy_connect.py %h %p" \
  <user>@<ten-mac>.tailXXXX.ts.net 'echo khong-bao-gio-thay-dong-nay'
# Kết quả mong đợi: Permission denied (publickey).
```

### Bước 6 — Cấp Full Disk Access (tuỳ chọn, nên làm)

Trước bước này, SSH đọc `~/Downloads`, `~/Documents`, `~/Desktop` sẽ gặp lỗi `Operation not permitted` vì macOS TCC coi phiên SSH là một client riêng. Cách cấp đúng:

1. Từ phiên SSH, agent mở sẵn đúng trang cài đặt và copy sẵn đường dẫn vào clipboard của Mac:

```bash
open "x-apple.systempreferences:com.apple.settings.PrivacySecurity.extension?Privacy_AllFiles"
printf "/usr/libexec/sshd-keygen-wrapper" | pbcopy
```

2. Người dùng, trên Mac: vào **System Settings → Privacy & Security → Full Disk Access**, bấm nút **+**, xác thực bằng Touch ID hoặc mật khẩu, nhấn **Cmd + Shift + G**, dán đường dẫn, chọn **Open**, và bật công tắc cho `sshd-keygen-wrapper`.
3. Agent SSH kiểm tra lại cả ba thư mục ngay sau đó. Việc cấp này bắt buộc chính chủ bấm — không kênh agent nào làm thay được, và đó là chủ đích của Apple.

### Bước 7 — Dùng hằng ngày

Từ đây agent tự chạy mọi lệnh Mac qua wrapper `mac '<lệnh>'`: render video, chạy script, kiểm tra file, cài đặt. Người dùng không còn phải chạy hộ file `.command` nữa. Việc nào chạy lâu, agent nên ghi log ra file trên Mac để cả hai phía cùng đọc được tiến độ.

## Thu hồi quyền truy cập

Từ nhẹ tới mạnh, hiệu lực ngay:

1. **Nhẹ:** xoá dòng key có ghi chú `muse-vm` trong `~/.ssh/authorized_keys` trên Mac — chỉ Muse mất quyền, Remote Login vẫn còn cho người khác.
2. **Vừa:** xoá file `/etc/ssh/sshd_config.d/100-muse-hardened.conf` — gỡ cấu hình siết chặt của bộ này.
3. **Mạnh nhất:** tắt **Remote Login** trong System Settings → General → Sharing — đóng hẳn cổng SSH. Muốn chắc chắn nữa thì tắt thêm công tắc của `sshd-keygen-wrapper` trong Full Disk Access.

## Xử lý sự cố

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Kết nối chết trước khi hỏi xác thực, lỗi nhắc tới cổng 3128 | Đang đi qua proxy egress web thay vì đường hầm Tailscale | Luôn dùng `proxy_connect.py` (cổng 3130) làm `ProxyCommand` |
| Installer dừng ở `sshd: no hostkeys available` | Mac chưa từng làm SSH server nên chưa có host key | Chạy `ssh-keygen -A` trước `sshd -t` (template trong repo đã đúng thứ tự này) |
| Double-click file `.command` báo lỗi privileges | File chép từ xa không có execute bit | Chạy bằng `zsh <đường dẫn file>` trong Terminal |
| Key đúng mà vẫn `Permission denied (publickey)` | IPv4 tailnet của máy ảo đã đổi so với dòng `AllowUsers`, hoặc key chưa vào `authorized_keys` | Đối chiếu `tailscale status` với nội dung drop-in, cập nhật lại đúng IP rồi chạy lại installer |
| `Operation not permitted` ở Downloads, Documents, Desktop | Thiếu Full Disk Access cho phiên SSH | Làm bước 6, cấp cho `/usr/libexec/sshd-keygen-wrapper` |
| Kết nối treo lâu bất thường ở lần đầu | Đang chờ người dùng duyệt địa chỉ tailnet mới | Người dùng duyệt thẻ quyền, các lần sau dùng lại đúng tên hoặc IP đã duyệt |
| Installer in cảnh báo Full Disk Access ở lệnh `systemsetup` nhưng vẫn xong | Cảnh báo đó không chặn việc bật khi đường launch daemon thành công | Tin vào kiểm chứng cuối: Remote Login báo On và bài test SSH ở bước 5 qua là đạt |

## Mô hình an toàn

- Chỉ đăng nhập bằng SSH key. Mật khẩu bị tắt hẳn ở phía server, và bước 5 cố tình thử đăng nhập bằng mật khẩu để nhìn nó bị từ chối.
- Chỉ một tài khoản Mac, và chỉ từ đúng một địa chỉ nguồn là IPv4 Tailscale của máy ảo Muse (`AllowUsers user@ip`). Máy khác cùng Wi-Fi hay cùng tailnet cũng không thử key được.
- Không root login, không port forwarding, không X11, không agent forwarding, tối đa 3 lần thử xác thực.
- Không mở port nào trên router. Toàn bộ đường đi nằm trong tailnet riêng của người dùng.
- Người dùng chỉ phải tự tay làm 2 việc macOS bắt chính chủ làm: gõ mật khẩu admin khi chạy installer, và bấm cấp Full Disk Access trong Settings.

## Bài học đắt giá đã gói vào skill

- Cổng proxy 3128 giết SSH trước cả bước xác thực. Mọi kết luận "không SSH được" rút ra từ cổng đó đều sai, phải dùng 3130.
- Mac chưa từng làm SSH server thì chưa có host key, và `sshd -t` sẽ báo lỗi như thể cấu hình sai. Tạo host key trước, kiểm tra sau.
- File `.command` chép từ xa không có execute bit. Chạy bằng `zsh <đường dẫn>` trong Terminal, đừng double-click.
- Ba thư mục Downloads, Documents, Desktop là vùng TCC riêng. SSH bị "Operation not permitted" ở đó là chuyện Full Disk Access, không phải chuyện SSH.

## Cấu trúc thư mục

- `SKILL.md` — playbook cho agent, từng bước một.
- `skill.yaml` — mô tả để hệ thống tìm thấy skill.
- `LICENSE` — giấy phép MIT.
- `scripts/proxy_connect.py` — trợ thủ ProxyCommand cho ssh, đã test sống.
- `scripts/installer_template.command` — installer mẫu với placeholder, chính là bản đã cài thành công, đã xoá mọi giá trị cá nhân.
- `scripts/render_installer.py` — điền placeholder có kiểm tra, dùng cho cả installer và wrapper.
- `scripts/mac_wrapper_template.sh` — mẫu lệnh gọi tắt `mac '<lệnh>'` cho các lần dùng sau.

## Trạng thái kiểm chứng

Quy trình trong repo này không phải lý thuyết. Nó đã được chạy thật ngày 2026-10-29 trên một Mac chạy macOS 26.6.2: installer chạy thành công ở lần thứ hai (lần đầu vấp đúng lỗi host key đã ghi ở mục sự cố), SSH vào được từ máy ảo Muse, bài test mật khẩu bị từ chối đúng như thiết kế, và Full Disk Access phát huy tác dụng ngay sau khi cấp. Các phiên bản macOS khác chưa được kiểm chứng — hãy đi đủ bước 5 trước khi tin.
