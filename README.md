# Claude Code CLI 反向代理配置 Skill

> 🚀 利用 Claude Max/Team 訂閱免費運行 Claude Opus 4-6，完整工具支援，官方認可，無封號風險

---

## 🎯 項目概述

本 Skill 讓你通過 **Claude Code CLI + OpenClaw Gateway** 架構，使用 Claude Max/Team 訂閱來免費運行 Claude Opus 4-6，同時保持完整的工具支援。

**核心優勢：**
- ✅ **官方認可**（使用 Claude Code CLI，不會被封號）
- ✅ **完整工具支援**（Read, Write, Bash, Grep, Glob 等所有工具）
- ✅ **完整 Claude Opus 4-6 功能**
- ✅ **免費使用**（利用現有 Claude Max/Team 訂閱）
- ✅ **與 OpenClaw 完美集成**
- ✅ **對話歷史管理**（自動保存，支持長期對話）
- ✅ **一鍵安裝**（全自動配置）

---

## 📐 架構圖

```
OpenClaw Agent
     ↓
http://localhost:8765 (Node.js Proxy)
     ↓ [轉換 Anthropic Messages API → Claude CLI]
Claude Code CLI (官方工具)
     ↓ [完整工具支援]
Claude.ai (使用 Max/Team 訂閱)
```

**關鍵點：**
- 代理服務器接收標準的 Anthropic Messages API 請求
- 轉換為 Claude CLI 命令並執行
- 返回標準 API 格式的回應
- 支持 SSE streaming
- 自動管理對話歷史

---

## 💰 成本對比

| 方案 | 月費 | Opus 使用 | 工具支援 | 風險 |
|------|------|-----------|----------|------|
| **Anthropic API** | $100+ | Unlimited | ✅ | 無 |
| **Claude Max + CLI** | $200 | Unlimited | ✅ | 無 |
| **Claude Team + CLI** | $30/人 | 有限制 | ✅ | 無 |

**推薦：**
- 已有 Claude Max → 🌟 最佳選擇
- 已有 Claude Team → 適合低頻使用
- 無訂閱 → 建議購買 Claude Max 或使用 Anthropic API

---

## 🚀 快速開始

### 前置需求

1. **Claude Max 或 Claude Team** 訂閱帳戶
2. **macOS** 系統（未來支持 Linux）
3. **Homebrew** 已安裝
4. **OpenClaw** 已安裝

### 一鍵安裝

```bash
cd ~/.openclaw/skills/claude-code-setup
python3 setup.py
```

腳本會自動：
1. ✅ 檢查 Claude CLI 是否安裝和登入
2. ✅ 檢查 Node.js 是否安裝
3. ✅ 創建工作目錄和子目錄結構
4. ✅ 生成 Node.js 代理服務器
5. ✅ 啟動並測試代理
6. ✅ 配置 OpenClaw Agent
7. ✅ （可選）設置開機自動啟動

### 配置流程

**步驟 1：安裝 Claude CLI（如果未安裝）**

```bash
brew install claude
claude login
```

按照提示在瀏覽器中完成 Google OAuth 登入。

**步驟 2：運行配置腳本**

```bash
python3 setup.py
```

**步驟 3：輸入要配置的 Agent**

當提示輸入 agent 名稱時：
```
請輸入要配置的 agent 名稱（多個用逗號分隔）：
> myagent
```

**步驟 4：完成！**

看到 ✅ 配置完成後，即可開始使用。

---

## 📁 文件結構

配置完成後會在你的主目錄創建以下結構：

```
~/claude-proxy-workspace/
├── claude-proxy.js          # Node.js 代理服務器
├── proxy.log                # 服務器日誌
├── README.md                # 工作目錄說明
├── bootstrap.md             # Claude 啟動提示
├── memory/                  # 長期記憶存儲
│   └── 語義記憶/
└── history/                 # 對話歷史
    └── [chatId].json        # 各個對話的歷史
```

---

## 🔧 使用方法

### 在 OpenClaw 中使用

配置完成後：

1. 打開 OpenClaw
2. 選擇你配置的 agent
3. 在模型選擇中選擇 **"Claude Opus 4 (Local)"**
4. 開始對話！

### 管理代理服務器

**查看狀態：**
```bash
ps aux | grep claude-proxy.js
```

**啟動代理：**
```bash
node ~/claude-proxy-workspace/claude-proxy.js
```

**停止代理：**
```bash
pkill -f claude-proxy.js
```

**查看日誌：**
```bash
tail -f ~/claude-proxy-workspace/proxy.log
```

**健康檢查：**
```bash
curl http://localhost:8765/health
```

---

## 🛠 技術細節

### 代理服務器工作原理

1. **接收請求**：監聽 `http://localhost:8765/v1/messages`
2. **提取消息**：從 Anthropic Messages API 格式中提取用戶消息
3. **構建 Prompt**：結合對話歷史構建完整 prompt
4. **調用 CLI**：使用 `spawn` 執行 `claude --print --dangerously-skip-permissions`
5. **流式返回**：通過 SSE 實時返回 Claude 的輸出
6. **保存歷史**：將對話保存到歷史文件

### 對話歷史管理

- **短期記憶**：記憶體保留最近 10 條消息
- **長期記憶**：自動保存到 `history/[chatId].json`
- **自動清理**：24 小時無活動自動清理記憶體
- **持久化**：所有歷史永久保存在文件中

### Agent 配置

代理會在 agent 的 `models.json` 中添加：

```json
{
  "providers": {
    "claude-local": {
      "baseUrl": "http://127.0.0.1:8765",
      "api": "anthropic-messages",
      "apiKey": "sk-ant-dummy-key-for-local-proxy",
      "models": [
        {
          "id": "claude-opus-4",
          "name": "Claude Opus 4 (Local)",
          "contextWindow": 200000,
          "maxTokens": 8192,
          "input": ["text", "image"],
          "cost": {
            "input": 0,
            "output": 0
          }
        }
      ]
    }
  }
}
```

---

## 🎨 自定義配置

### 修改系統提示

編輯 `~/claude-proxy-workspace/bootstrap.md` 來自定義 Claude 的行為：

```markdown
# System Bootstrap

你是一個專門處理 XXX 的助手...

## 專業領域

- 領域 1
- 領域 2

## 工作風格

簡潔、專業、高效
```

### 調整歷史保留數量

編輯 `claude-proxy.js` 中的常量：

```javascript
const MAX_HISTORY_MESSAGES = 10;  // 改為你想要的數量
```

---

## 🔄 開機自動啟動

配置時選擇 "是否配置開機自動啟動"，腳本會自動創建 LaunchAgent。

**手動管理 LaunchAgent：**

```bash
# 載入
launchctl load ~/Library/LaunchAgents/com.claude.proxy.plist

# 卸載
launchctl unload ~/Library/LaunchAgents/com.claude.proxy.plist

# 查看狀態
launchctl list | grep claude.proxy
```

---

## ❓ 常見問題

### Q: 為什麼使用 Claude CLI 而不是直接調用 API？

A:
- ✅ Claude CLI 是官方工具，不會被封號
- ✅ 可以利用現有的 Claude Max/Team 訂閱
- ✅ 完整的工具支援
- ✅ 成本更低（Max $200/月 vs API $100+/月）

### Q: 會不會被封號？

A: 不會。Claude CLI 是 Anthropic 官方提供的工具，使用它完全符合服務條款。

### Q: 支持哪些工具？

A: 所有 Claude Code 支持的工具：
- Read, Write, Edit（文件操作）
- Bash（命令執行）
- Grep, Glob（代碼搜尋）
- WebSearch, WebFetch（網絡搜尋）
- 等等...

### Q: 性能如何？

A:
- 首次響應：約 2-3 秒
- 後續響應：約 1-2 秒
- 支持 SSE streaming，體驗流暢

### Q: 可以同時使用多個 agent 嗎？

A: 可以！代理服務器支持多個 agent 同時使用，每個對話都有獨立的歷史記錄。

### Q: 如何更新代理？

A: 重新運行 `python3 setup.py`，選擇覆蓋現有配置即可。

### Q: Claude Team 有使用限制嗎？

A:
- Claude Team 對 Opus 使用有限制（每人每天有上限）
- Claude Max 沒有限制
- 建議中高頻使用者選擇 Claude Max

---

## 🔐 安全說明

- ✅ 代理僅監聽 localhost，不對外開放
- ✅ 使用 Claude CLI 的 OAuth 認證，無需存儲密碼
- ✅ 對話歷史存儲在本地，完全私密
- ✅ 無任何數據上傳到第三方

---

## 🐛 故障排除

### 問題 1：Claude CLI 未安裝

**錯誤：**
```
❌ Claude CLI 未安裝
```

**解決方法：**
```bash
brew install claude
claude login
```

### 問題 2：Claude CLI 未登入

**錯誤：**
```
❌ Claude CLI 未登入
```

**解決方法：**
```bash
claude login
```

在瀏覽器中完成 Google OAuth 登入。

### 問題 3：代理啟動失敗

**錯誤：**
```
❌ 代理服務器測試失敗
```

**解決方法：**
1. 檢查端口 8765 是否被占用：
   ```bash
   lsof -i :8765
   ```
2. 查看日誌：
   ```bash
   cat ~/claude-proxy-workspace/proxy.log
   ```
3. 手動啟動測試：
   ```bash
   node ~/claude-proxy-workspace/claude-proxy.js
   ```

### 問題 4：OpenClaw 找不到模型

**解決方法：**
1. 確認代理正在運行
2. 重啟 OpenClaw Gateway：
   ```bash
   openclaw gateway restart
   ```
3. 檢查 models.json 配置是否正確

---

## 📊 診斷腳本

創建診斷腳本檢查系統狀態：

```bash
# 保存為 diagnose.sh
#!/bin/bash

echo "=== Claude Code Proxy 診斷 ==="
echo

echo "[1] Claude CLI"
which claude && claude --version || echo "❌ 未安裝"
echo

echo "[2] Claude 登入狀態"
claude auth whoami 2>&1 | head -3
echo

echo "[3] Node.js"
which node && node --version || echo "❌ 未安裝"
echo

echo "[4] 代理服務器"
ps aux | grep claude-proxy.js | grep -v grep || echo "❌ 未運行"
echo

echo "[5] 健康檢查"
curl -s http://localhost:8765/health | python3 -m json.tool || echo "❌ 無響應"
echo

echo "=== 診斷完成 ==="
```

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 📜 授權

MIT License

---

## 🙏 致謝

- **Anthropic** - 提供 Claude Code CLI 官方工具
- **OpenClaw** - 提供強大的 Gateway 框架
- **社群貢獻者** - 感謝所有使用和改進本項目的人

---

## 📚 相關資源

- [Claude Code CLI 官方文檔](https://docs.anthropic.com/claude/docs/claude-cli)
- [OpenClaw 文檔](https://openclaw.com/docs/)
- [Anthropic API 文檔](https://docs.anthropic.com/)

---

**Made with 💙 for the AI community**
