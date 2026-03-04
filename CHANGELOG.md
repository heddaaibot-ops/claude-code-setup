# 更新日誌

## [1.0.0] - 2026-03-04

### 新增
- ✨ 初始版本發布
- 🚀 全自動配置 Claude Code CLI 反向代理
- 📝 完整的對話歷史管理系統
- 💾 自動保存對話到本地文件
- 🔄 支持 SSE streaming
- 🛠 完整的工具支援（Read, Write, Bash, Grep, Glob 等）
- 📊 19 項系統診斷檢查
- 📚 完整的中文文檔
- 🎨 彩色終端輸出
- 🔐 LaunchAgent 自動啟動配置

### 特性
- ⚡️ 使用官方 Claude Code CLI（無封號風險）
- 💰 利用 Claude Max/Team 訂閱（免費使用 Opus 4-6）
- 🧠 智能對話歷史管理
  - 短期記憶：記憶體保留最近 10 條
  - 長期記憶：自動持久化到文件
  - 自動清理：24 小時無活動自動清理
- 🎯 一鍵安裝配置
- 🔧 支持多 Agent 配置
- 📈 完整的日誌系統

### 技術細節
- 代理端口：8765
- API 格式：Anthropic Messages API
- CLI 工具：Claude Code CLI (官方)
- 運行時：Node.js
- 支持平台：macOS (未來支持 Linux)

### 文檔
- README.md - 完整技術文檔
- QUICKSTART.md - 3分鐘快速上手
- LICENSE - MIT 授權
- CHANGELOG.md - 本文件

### 工具
- setup.py - Python 配置腳本
- diagnose.sh - Bash 診斷工具
- skill.json - Skill 元數據

---

## 未來計劃

### [1.1.0] - 計劃中
- [ ] 支持 Linux 平台
- [ ] 添加記憶提煉功能
- [ ] Web 管理面板
- [ ] 支持自定義端口
- [ ] 添加使用統計
- [ ] 性能優化

### [1.2.0] - 計劃中
- [ ] Windows 支持
- [ ] Docker 部署
- [ ] 多帳號支援
- [ ] GUI 配置工具
- [ ] 自動更新檢查

---

## 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 授權

MIT License - 詳見 LICENSE 文件

---

最後更新：2026-03-04
