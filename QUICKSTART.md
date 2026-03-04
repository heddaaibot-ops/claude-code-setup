# Claude Code CLI 代理 - 快速上手

## ⚡ 3 分鐘完成配置

### 前置需求

- ✅ Claude Max 或 Claude Team 訂閱
- ✅ macOS 系統
- ✅ OpenClaw 已安裝

### 步驟 1：安裝 Claude CLI

```bash
brew install claude
claude login
```

按提示在瀏覽器中用 Google 帳號登入。

### 步驟 2：運行配置

```bash
cd ~/.openclaw/skills/claude-code-setup
python3 setup.py
```

### 步驟 3：輸入 Agent 名稱

```
請輸入要配置的 agent 名稱：
> myagent
```

### 步驟 4：（可選）開機自動啟動

```
是否配置開機自動啟動? (y/N): y
```

### 步驟 5：完成！

```
✅ 配置完成！
代理端口: 8765
```

### 步驟 6：開始使用

1. 打開 OpenClaw
2. 選擇你的 agent
3. 選擇模型：**Claude Opus 4 (Local)**
4. 開始對話！

---

## 🎯 驗證安裝

```bash
# 檢查代理是否運行
curl http://localhost:8765/health

# 查看日誌
tail -f ~/claude-proxy-workspace/proxy.log
```

---

## 💡 快速命令

```bash
# 啟動代理
node ~/claude-proxy-workspace/claude-proxy.js

# 停止代理
pkill -f claude-proxy.js

# 查看狀態
ps aux | grep claude-proxy.js
```

---

## ❓ 遇到問題？

查看 [README.md](README.md) 的故障排除章節，或運行診斷腳本。

---

**享受免費的 Claude Opus 4-6！** 🚀
