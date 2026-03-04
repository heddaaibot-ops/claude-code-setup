#!/bin/bash

# Claude Code Proxy 診斷工具

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${BOLD}${BLUE}==========================================${NC}"
echo -e "${BOLD}${BLUE}   Claude Code Proxy 診斷工具${NC}"
echo -e "${BOLD}${BLUE}==========================================${NC}"
echo

PASS=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. 檢查 Claude CLI
echo -e "${BOLD}[1] 檢查 Claude CLI${NC}"
if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>&1 | head -1)
    check_pass "Claude CLI: $CLAUDE_VERSION"
    CLAUDE_PATH=$(which claude)
    echo -e "   ${BLUE}路徑: $CLAUDE_PATH${NC}"
else
    check_fail "Claude CLI 未安裝 (運行: brew install claude)"
fi
echo

# 2. 檢查 Claude 登入狀態
echo -e "${BOLD}[2] 檢查 Claude 登入狀態${NC}"
AUTH_STATUS=$(claude auth whoami 2>&1)
if echo "$AUTH_STATUS" | grep -q "You are"; then
    check_pass "已登入 Claude"
    echo -e "   ${BLUE}$(echo "$AUTH_STATUS" | head -1)${NC}"
else
    check_fail "未登入 Claude (運行: claude login)"
fi
echo

# 3. 檢查 Node.js
echo -e "${BOLD}[3] 檢查 Node.js${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    check_pass "Node.js: $NODE_VERSION"
else
    check_fail "Node.js 未安裝 (運行: brew install node)"
fi
echo

# 4. 檢查工作目錄
echo -e "${BOLD}[4] 檢查工作目錄${NC}"
WORKSPACE="$HOME/claude-proxy-workspace"
if [ -d "$WORKSPACE" ]; then
    check_pass "工作目錄存在: $WORKSPACE"

    if [ -f "$WORKSPACE/claude-proxy.js" ]; then
        check_pass "代理文件存在"
    else
        check_fail "代理文件不存在"
    fi

    if [ -d "$WORKSPACE/history" ]; then
        check_pass "歷史目錄存在"
    else
        check_warn "歷史目錄不存在"
    fi
else
    check_fail "工作目錄不存在 (運行: python3 setup.py)"
fi
echo

# 5. 檢查代理運行狀態
echo -e "${BOLD}[5] 檢查代理運行狀態${NC}"
PROXY_PID=$(pgrep -f "claude-proxy.js")
if [ -n "$PROXY_PID" ]; then
    check_pass "代理正在運行 (PID: $PROXY_PID)"
else
    check_fail "代理未運行 (運行: node ~/claude-proxy-workspace/claude-proxy.js &)"
fi
echo

# 6. 檢查代理日誌
echo -e "${BOLD}[6] 檢查代理日誌${NC}"
LOG_FILE="$WORKSPACE/proxy.log"
if [ -f "$LOG_FILE" ]; then
    check_pass "日誌文件存在: $LOG_FILE"
    LOG_SIZE=$(wc -c < "$LOG_FILE")
    echo -e "   ${BLUE}大小: $LOG_SIZE bytes${NC}"

    ERROR_COUNT=$(grep -i "error" "$LOG_FILE" 2>/dev/null | wc -l)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        check_warn "發現 $ERROR_COUNT 個錯誤"
        echo -e "   ${YELLOW}最近的錯誤:${NC}"
        grep -i "error" "$LOG_FILE" | tail -3 | sed 's/^/   /'
    else
        check_pass "無錯誤記錄"
    fi
else
    check_warn "日誌文件不存在"
fi
echo

# 7. 測試代理連接
echo -e "${BOLD}[7] 測試代理連接${NC}"
HEALTH_CHECK=$(curl -s http://localhost:8765/health 2>/dev/null)
if [ -n "$HEALTH_CHECK" ]; then
    if echo "$HEALTH_CHECK" | grep -q '"status":"ok"'; then
        check_pass "代理響應正常"
        echo -e "   ${BLUE}回應: $HEALTH_CHECK${NC}"
    else
        check_fail "代理響應異常"
    fi
else
    check_fail "無法連接到代理 (端口 8765)"
fi
echo

# 8. 檢查 OpenClaw 配置
echo -e "${BOLD}[8] 檢查 OpenClaw 配置${NC}"
if command -v openclaw &> /dev/null; then
    check_pass "OpenClaw 已安裝"

    AGENTS_DIR="$HOME/.openclaw/agents"
    if [ -d "$AGENTS_DIR" ]; then
        AGENT_COUNT=$(ls -1 "$AGENTS_DIR" 2>/dev/null | wc -l)
        echo -e "   ${BLUE}發現 $AGENT_COUNT 個 agents${NC}"

        # 檢查是否有 agent 配置了 claude-local
        CONFIGURED=0
        for agent_dir in "$AGENTS_DIR"/*; do
            if [ -d "$agent_dir" ]; then
                MODELS_JSON="$agent_dir/agent/models.json"
                if [ -f "$MODELS_JSON" ]; then
                    if grep -q '"claude-local"' "$MODELS_JSON"; then
                        AGENT_NAME=$(basename "$agent_dir")
                        echo -e "   ${GREEN}✓ $AGENT_NAME 已配置 claude-local${NC}"
                        ((CONFIGURED++))
                    fi
                fi
            fi
        done

        if [ $CONFIGURED -gt 0 ]; then
            check_pass "找到 $CONFIGURED 個已配置的 agents"
        else
            check_warn "沒有 agent 配置 claude-local"
        fi
    fi
else
    check_fail "OpenClaw 未安裝"
fi
echo

# 9. 檢查 LaunchAgent
echo -e "${BOLD}[9] 檢查自動啟動${NC}"
PLIST_PATH="$HOME/Library/LaunchAgents/com.claude.proxy.plist"
if [ -f "$PLIST_PATH" ]; then
    check_pass "LaunchAgent 已配置"

    if launchctl list | grep -q "com.claude.proxy"; then
        check_pass "LaunchAgent 已載入"
    else
        check_warn "LaunchAgent 未載入"
    fi
else
    check_warn "未配置自動啟動"
fi
echo

# 10. 完整流程測試
echo -e "${BOLD}[10] 完整流程測試${NC}"
if [ -n "$PROXY_PID" ] && [ -n "$HEALTH_CHECK" ]; then
    check_pass "所有核心組件就緒"
    echo -e "   ${GREEN}✨ 系統配置正常，可以開始使用 Claude Opus 4${NC}"
else
    check_fail "存在配置問題，請查看上方錯誤"
fi
echo

# 總結
echo -e "${BOLD}${BLUE}==========================================${NC}"
echo -e "${BOLD}   診斷結果總結${NC}"
echo -e "${BOLD}${BLUE}==========================================${NC}"
echo -e "${GREEN}通過: $PASS${NC}"
echo -e "${RED}失敗: $FAIL${NC}"
echo

if [ $FAIL -eq 0 ]; then
    echo -e "${BOLD}${GREEN}🎉 所有檢查通過！系統配置正確。${NC}"
    echo -e "${GREEN}您可以在 OpenClaw 中使用 Claude Opus 4 (Local) 了。${NC}"
else
    echo -e "${BOLD}${RED}❌ 發現 $FAIL 個問題${NC}"
    echo -e "${YELLOW}建議操作：${NC}"
    echo -e "1. 查看上方失敗的項目"
    echo -e "2. 或重新運行配置: ${BOLD}python3 setup.py${NC}"
fi
echo

# 快速修復建議
if [ $FAIL -gt 0 ]; then
    echo -e "${BOLD}${BLUE}快速修復命令：${NC}"

    if [ -z "$PROXY_PID" ] && [ -f "$WORKSPACE/claude-proxy.js" ]; then
        echo -e "${YELLOW}# 啟動代理${NC}"
        echo -e "node ~/claude-proxy-workspace/claude-proxy.js &"
        echo
    fi

    if [ ! -d "$WORKSPACE" ]; then
        echo -e "${YELLOW}# 運行配置${NC}"
        echo -e "cd ~/.openclaw/skills/claude-code-setup"
        echo -e "python3 setup.py"
        echo
    fi
fi

exit $FAIL
