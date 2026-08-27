# 数据说明

实验数据来自 SkullSecurity 的公开口令研究数据目录：

https://downloads.skullsecurity.org/passwords/

仓库中的两个文件均为带出现频数的压缩文本：

| 文件 | SHA-256 |
|---|---|
| `rockyou-withcount.txt.bz2` | `b4df8896db90521202ab56527993065ed57006631582cc1d685271eda3e884e7` |
| `phpbb-withcount.txt.bz2` | `67728b9b9fae57cf19e4139f5531bd7e46fd4c10d6f66a88c01e92901754c430` |

每行格式为“出现频数 + 空格 + 口令”。`数据处理.py` 按 Latin-1 读取原始字节，保留长度 4 到 40 且完全由 95 个可打印 ASCII 字符组成的口令。

这些文件源自历史泄露事件，只能用于授权的教学、安全研究和防御性离线统计。禁止利用数据识别个人、关联身份或尝试访问任何账户。
