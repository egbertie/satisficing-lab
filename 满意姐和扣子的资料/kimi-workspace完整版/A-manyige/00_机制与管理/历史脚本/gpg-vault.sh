#!/bin/bash
# GPG加密环境变量文件
# 用于加密敏感配置文件

VAULT_DIR="$HOME/.openclaw/security/vault"
mkdir -p "$VAULT_DIR"

encrypt_file() {
    local file="$1"
    if [ -f "$file" ]; then
        # 使用GPG对称加密（AES-256）
        gpg --symmetric --cipher-algo AES256 --compress-algo 0 --batch --yes \
            --passphrase-file "$VAULT_DIR/.gpg-passphrase" \
            -o "$file.gpg" "$file" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            # 设置严格权限
            chmod 600 "$file.gpg"
            # 安全擦除原文件（可选）
            # shred -u "$file"
            echo "✓ 已加密: $file → $file.gpg"
        else
            echo "✗ 加密失败: $file"
        fi
    fi
}

decrypt_file() {
    local file="$1"
    if [ -f "$file.gpg" ]; then
        gpg --decrypt --batch --yes \
            --passphrase-file "$VAULT_DIR/.gpg-passphrase" \
            -o "$file" "$file.gpg" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            chmod 600 "$file"
            echo "✓ 已解密: $file.gpg → $file"
        else
            echo "✗ 解密失败: $file.gpg"
        fi
    fi
}

# 主命令
case "$1" in
    encrypt)
        shift
        for file in "$@"; do
            encrypt_file "$file"
        done
        ;;
    decrypt)
        shift
        for file in "$@"; do
            decrypt_file "$file"
        done
        ;;
    init)
        # 初始化GPG密码
        if [ ! -f "$VAULT_DIR/.gpg-passphrase" ]; then
            openssl rand -base64 32 > "$VAULT_DIR/.gpg-passphrase"
            chmod 600 "$VAULT_DIR/.gpg-passphrase"
            echo "✓ GPG密码已生成"
        fi
        ;;
    *)
        echo "用法: $0 {init|encrypt|decrypt} [文件...]"
        exit 1
        ;;
esac
