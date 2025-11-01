# iMessage 发送方案文档

> 通过 AppleScript + osascript 直接在 macOS 上发送 iMessage，无需依赖 Ruby/Python 环境

## 概述

本文档介绍了几种简洁的 iMessage 发送方案，核心原理是通过 `osascript` 命令执行 AppleScript，与 macOS 的 Messages 应用进行自动化交互。

**前提条件**：
- macOS 系统
- 已登录 iMessage 的 Messages 应用
- 支持邮箱地址或手机号作为收件人

---

## 方案一：oneliner 单行命令

### 发送文本消息

```bash
osascript -e 'tell application "Messages" to send "你的消息内容" to buddy "收件人邮箱或手机号" of (service 1 whose service type is iMessage)'
```

**示例**：
```bash
# 发送到手机号
osascript -e 'tell application "Messages" to send "Hello World" to buddy "+8615510010000" of (service 1 whose service type is iMessage)'

# 发送到邮箱
osascript -e 'tell application "Messages" to send "Hello" to buddy "user@example.com" of (service 1 whose service type is iMessage)'
```

### 发送附件

```bash
osascript -e 'tell application "Messages" to send POSIX file "/path/to/file.jpg" to buddy "收件人" of (service 1 whose service type is iMessage)'
```

**示例**：
```bash
osascript -e 'tell application "Messages" to send POSIX file "/Users/username/Pictures/photo.png" to buddy "+8615510010000" of (service 1 whose service type is iMessage)'
```

**优点**：
- 最简洁，一行命令搞定
- 适合快速测试

**缺点**：
- 消息内容包含特殊字符时需要转义
- 不适合复杂场景

---

## 方案二：Shell 脚本函数（推荐 ⭐）

创建一个 `imessage.sh` 脚本文件：

``` bash
#!/bin/bash

# 发送文本消息
send_imessage() {
    local recipient="$1"
    local message="$2"

    if [[ -z "$recipient" || -z "$message" ]]; then
        echo "错误: 缺少参数"
        echo "用法: send_imessage <收件人> <消息内容>"
        return 1
    fi

    osascript -e "
        tell application \"Messages\"
            send \"$message\" to buddy \"$recipient\" of (service 1 whose service type is iMessage)
        end tell
    "

    if [[ $? -eq 0 ]]; then
        echo "✓ 消息已发送到: $recipient"
    else
        echo "✗ 发送失败"
    fi
}

# 发送附件
send_attachment() {
    local recipient="$1"
    local file_path="$2"

    if [[ -z "$recipient" || -z "$file_path" ]]; then
        echo "错误: 缺少参数"
        echo "用法: send_attachment <收件人> <文件路径>"
        return 1
    fi

    if [[ ! -f "$file_path" ]]; then
        echo "错误: 文件不存在: $file_path"
        return 1
    fi

    osascript -e "
        tell application \"Messages\"
            send POSIX file \"$file_path\" to buddy \"$recipient\" of (service 1 whose service type is iMessage)
        end tell
    "

    if [[ $? -eq 0 ]]; then
        echo "✓ 附件已发送到: $recipient"
    else
        echo "✗ 发送失败"
    fi
}

# 批量发送
send_bulk() {
    local recipients="$1"
    local message="$2"

    if [[ -z "$recipients" || -z "$message" ]]; then
        echo "错误: 缺少参数"
        echo "用法: send_bulk <收件人列表(逗号分隔)> <消息内容>"
        return 1
    fi

    IFS=',' read -ra ADDR <<< "$recipients"
    for recipient in "${ADDR[@]}"; do
        # 去除空格
        recipient=$(echo "$recipient" | xargs)
        echo "正在发送到: $recipient"
        send_imessage "$recipient" "$message"
        sleep 1  # 避免发送过快
    done
}

# 主函数 - 命令行参数解析
case "$1" in
    text)
        send_imessage "$2" "$3"
        ;;
    attach)
        send_attachment "$2" "$3"
        ;;
    bulk)
        send_bulk "$2" "$3"
        ;;
    *)
        echo "=== iMessage 发送工具 ==="
        echo ""
        echo "用法:"
        echo "  $0 text <收件人> <消息内容>    - 发送文本消息"
        echo "  $0 attach <收件人> <文件路径>  - 发送附件"
        echo "  $0 bulk <收件人列表> <消息>    - 批量发送"
        echo ""
        echo "示例:"
        echo "  $0 text \"+8615510010000\" \"Hello\""
        echo "  $0 attach \"user@example.com\" \"/path/to/image.png\""
        echo "  $0 bulk \"user1@example.com,user2@example.com\" \"通知消息\""
        exit 1
        ;;
esac
```

### 使用方法

**保存并设置权限**：
```bash
chmod +x imessage.sh
```

**发送文本**：
```bash
./imessage.sh text "+8615510010000" "Hello World"
```

**发送附件**：
```bash
./imessage.sh attach "+8615510010000" "/Users/username/Pictures/photo.png"
```

**批量发送**：
```bash
./imessage.sh bulk "user1@example.com,user2@example.com,user3@icloud.com" "会议通知"
```

### 功能特性

- ✅ 参数验证
- ✅ 文件存在性检查
- ✅ 发送状态反馈
- ✅ 批量发送支持
- ✅ 错误处理

---

## 方案三：Shell 别名

将别名添加到 `~/.zshrc` 或 `~/.bash_profile`：

```bash
# iMessage 快捷命令
alias imsg='osascript -e '\''tell application "Messages" to send "群发测试消息" to buddy "联系人" of (service 1 whose service type is iMessage)'\'''

# 带参数的函数别名
function im() {
    osascript -e "tell application \"Messages\" to send \"$2\" to buddy \"$1\" of (service 1 whose service type is iMessage)"
}
```

**重新加载配置**：
```bash
source ~/.zshrc  # 或 source ~/.bash_profile
```

**使用**：
```bash
# 使用别名（固定消息）
imsg

# 使用函数（自定义消息）
im "+8615510010000" "Hello from alias"
```

**优点**：
- 最便捷，无需执行脚本

**缺点**：
- 灵活性较低
- 特殊字符需要转义

---

## 方案四：交互式脚本

```bash
#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "================================"
echo "     iMessage 发送器 v1.0"
echo "================================"
echo ""

# 选择发送类型
echo "选择发送类型:"
echo "1) 发送文本消息"
echo "2) 发送附件"
read -p "请输入选择 (1-2): " choice

case $choice in
    1)
        read -p "收件人 (邮箱或手机号): " recipient
        read -p "消息内容: " message

        echo ""
        echo "正在发送..."
        result=$(osascript -e "
            tell application \"Messages\"
                send \"$message\" to buddy \"$recipient\" of (service 1 whose service type is iMessage)
                return \"success\"
            end tell
        " 2>&1)

        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✓ 消息发送成功!${NC}"
            echo "收件人: $recipient"
            echo "内容: $message"
        else
            echo -e "${RED}✗ 发送失败${NC}"
            echo "错误: $result"
        fi
        ;;

    2)
        read -p "收件人 (邮箱或手机号): " recipient
        read -p "文件路径: " file_path

        if [[ ! -f "$file_path" ]]; then
            echo -e "${RED}错误: 文件不存在${NC}"
            exit 1
        fi

        echo ""
        echo "正在发送..."
        result=$(osascript -e "
            tell application \"Messages\"
                send POSIX file \"$file_path\" to buddy \"$recipient\" of (service 1 whose service type is iMessage)
                return \"success\"
            end tell
        " 2>&1)

        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✓ 附件发送成功!${NC}"
            echo "收件人: $recipient"
            echo "文件: $file_path"
        else
            echo -e "${RED}✗ 发送失败${NC}"
            echo "错误: $result"
        fi
        ;;

    *)
        echo "无效选择"
        exit 1
        ;;
esac
```

**使用**：
```bash
chmod +x interactive_imessage.sh
./interactive_imessage.sh
```

---

## 方案五：Python 版本（简化）

如果需要更灵活的控制，可以使用 Python：

```python
#!/usr/bin/env python3
import subprocess
import sys

def send_imessage(recipient, message):
    """发送 iMessage"""
    script = f'''
    tell application "Messages"
        send "{message}" to buddy "{recipient}" of (service 1 whose service type is iMessage)
    end tell
    '''
    result = subprocess.run(['osascript', '-e', script],
                          capture_output=True,
                          text=True)
    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python3 imessage.py <收件人> <消息>")
        sys.exit(1)

    recipient = sys.argv[1]
    message = sys.argv[2]

    if send_imessage(recipient, message):
        print(f"✓ 消息已发送到: {recipient}")
    else:
        print(f"✗ 发送失败: {recipient}")
        sys.exit(1)
```

**使用**：
```bash
python3 imessage.py "+8615510010000" "Hello from Python"
```

---

## 注意事项

### 1. 特殊字符处理

消息内容包含特殊字符（如引号、换行等）时需要转义：

```bash
# 避免直接使用
osascript -e 'tell application "Messages" to send "Hello "World"" to buddy "user"'

# 安全的做法 - 使用变量
message='Hello "World"'
osascript -e "tell application \"Messages\" to send \"$message\" to buddy \"user\""
```

### 2. 权限问题

确保：
- Messages 应用已登录 iMessage
- 允许终端/脚本控制 Messages（首次运行时会在系统偏好设置中提示）

### 3. 发送限制

- 避免发送过快（可能触发垃圾邮件检测）
- 批量发送时建议添加间隔：`sleep 1`

### 4. 错误处理

检查返回值：
```bash
osascript -e '...' && echo "成功" || echo "失败"
```

---

## 最佳实践推荐

**日常使用**：方案二（Shell 脚本函数）
- 功能完整
- 参数验证
- 状态反馈
- 易于维护

**快速测试**：方案一（oneliner）
- 无需创建文件
- 一条命令搞定

**生产环境**：方案二 + 日志记录
- 记录发送日志
- 错误监控
- 重试机制

---

## 总结

所有方案的核心都是通过 `osascript` 调用 AppleScript 与 Messages 应用交互。选择哪种方案取决于你的具体需求：

| 方案 | 复杂度 | 灵活性 | 维护性 | 推荐场景 |
|------|--------|--------|--------|----------|
| oneliner | ⭐ | ⭐ | ⭐ | 快速测试 |
| Shell 函数 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 日常使用 |
| 别名 | ⭐⭐ | ⭐⭐ | ⭐⭐ | 简单重复任务 |
| 交互式 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 临时使用 |
| Python | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 复杂逻辑 |

选择最适合你的方案即可！
