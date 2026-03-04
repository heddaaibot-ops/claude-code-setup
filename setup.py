#!/usr/bin/env python3
"""
Claude Code CLI 反向代理自動配置工具
讓你使用 Claude Max/Team 訂閱免費運行 Claude Opus 4-6 for OpenClaw
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path

class Colors:
    """終端顏色"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(step_num, title):
    """打印步驟標題"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[步驟 {step_num}] {title}{Colors.END}")

def print_success(msg):
    """打印成功消息"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    """打印錯誤消息"""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def check_dependencies():
    """檢查必要的依賴"""
    print_step(1, "檢查系統依賴")

    # 檢查 Claude CLI
    result = subprocess.run(["which", "claude"], capture_output=True)
    if result.returncode != 0:
        print_error("Claude CLI 未安裝")
        print_info("請先安裝 Claude CLI:")
        print_info("  brew install claude")
        print_info("  claude login")
        return False

    claude_path = result.stdout.decode().strip()
    print_success(f"Claude CLI 已安裝: {claude_path}")

    # 檢查是否已登入
    result = subprocess.run(["claude", "auth", "whoami"], capture_output=True)
    if result.returncode != 0:
        print_error("Claude CLI 未登入")
        print_info("請先登入 Claude:")
        print_info("  claude login")
        return False

    print_success("Claude CLI 已登入")

    # 檢查 Node.js
    result = subprocess.run(["which", "node"], capture_output=True)
    if result.returncode != 0:
        print_error("Node.js 未安裝")
        print_info("請先安裝 Node.js:")
        print_info("  brew install node")
        return False

    node_version = subprocess.run(["node", "--version"], capture_output=True).stdout.decode().strip()
    print_success(f"Node.js 已安裝: {node_version}")

    return True

def get_claude_cli_path():
    """獲取 Claude CLI 路徑"""
    result = subprocess.run(["which", "claude"], capture_output=True)
    return result.stdout.decode().strip()

def create_workspace():
    """創建工作目錄"""
    print_step(2, "創建工作目錄")

    home = Path.home()
    workspace = home / "claude-proxy-workspace"

    if workspace.exists():
        print_warning(f"工作目錄已存在: {workspace}")
        response = input(f"{Colors.YELLOW}是否覆蓋? (y/N): {Colors.END}").strip().lower()
        if response != 'y':
            print_info("使用現有工作目錄")
            return str(workspace)
        shutil.rmtree(workspace)

    workspace.mkdir(parents=True, exist_ok=True)
    print_success(f"工作目錄已創建: {workspace}")

    # 創建子目錄
    (workspace / "memory").mkdir(exist_ok=True)
    (workspace / "memory" / "語義記憶").mkdir(exist_ok=True)
    (workspace / "history").mkdir(exist_ok=True)

    # 創建 README
    readme = workspace / "README.md"
    readme.write_text("""# Claude Code Proxy Workspace

這是 Claude Code CLI 反向代理的工作目錄。

## 目錄結構

- `memory/` - 長期記憶存儲
- `history/` - 對話歷史
- `bootstrap.md` - Claude 啟動時的系統提示

## 注意事項

- 不要手動修改 history 目錄下的文件
- 可以自定義 bootstrap.md 來調整 Claude 的行為
""")

    # 創建 bootstrap.md
    bootstrap = workspace / "bootstrap.md"
    bootstrap.write_text("""# System Bootstrap

你是一個專業的 AI 助手，通過 Claude Code CLI 運行。

## 能力

- 完整的文件操作（Read, Write, Edit）
- 執行 Bash 命令
- 搜尋代碼（Grep, Glob）
- 其他所有 Claude Code 工具

## 工作原則

1. 仔細理解用戶需求
2. 使用適當的工具完成任務
3. 保持專業和友善
4. 如有疑問，主動詢問澄清

開始工作吧！
""")

    print_success("工作目錄結構已創建")
    return str(workspace)

def create_proxy_server(workspace_path, claude_cli_path):
    """創建 Node.js 代理服務器"""
    print_step(3, "創建代理服務器")

    proxy_code = f'''#!/usr/bin/env node

/**
 * Claude Code CLI Proxy Server
 *
 * 將 Anthropic Messages API 轉換為 Claude CLI 調用
 * 支持完整的工具使用和 SSE streaming
 */

const http = require('http');
const {{ spawn }} = require('child_process');
const fs = require('fs');
const path = require('path');

const PORT = 8765;
const CLAUDE_CLI = '{claude_cli_path}';
const WORKSPACE = '{workspace_path}';
const HISTORY_DIR = path.join(WORKSPACE, 'history');
const MEMORY_DIR = path.join(WORKSPACE, 'memory', '語義記憶');

// 對話歷史管理
const conversationHistory = new Map();
const chatLastActivity = new Map();
const MAX_HISTORY_MESSAGES = 10;
const MAX_INACTIVE_TIME = 24 * 60 * 60 * 1000;

/**
 * 確保目錄存在
 */
function ensureDir(dir) {{
  if (!fs.existsSync(dir)) {{
    fs.mkdirSync(dir, {{ recursive: true }});
  }}
}}

/**
 * 加載對話歷史
 */
function loadHistory(chatId) {{
  try {{
    const filePath = path.join(HISTORY_DIR, `${{chatId}}.json`);
    if (fs.existsSync(filePath)) {{
      const data = fs.readFileSync(filePath, 'utf8');
      const fullHistory = JSON.parse(data);
      return fullHistory.slice(-MAX_HISTORY_MESSAGES);
    }}
  }} catch (err) {{
    console.error('[History] Error loading:', err.message);
  }}
  return [];
}}

/**
 * 保存對話歷史
 */
function saveHistory(chatId, messages) {{
  try {{
    ensureDir(HISTORY_DIR);
    const filePath = path.join(HISTORY_DIR, `${{chatId}}.json`);

    let fullHistory = [];
    if (fs.existsSync(filePath)) {{
      const data = fs.readFileSync(filePath, 'utf8');
      fullHistory = JSON.parse(data);
    }}

    fullHistory.push(...messages);
    fs.writeFileSync(filePath, JSON.stringify(fullHistory, null, 2));
  }} catch (err) {{
    console.error('[History] Error saving:', err.message);
  }}
}}

/**
 * 添加到歷史
 */
function addToHistory(chatId, role, content) {{
  chatLastActivity.set(chatId, Date.now());

  if (!conversationHistory.has(chatId)) {{
    const history = loadHistory(chatId);
    conversationHistory.set(chatId, history);
  }}

  const history = conversationHistory.get(chatId);
  const message = {{ role, content, timestamp: Date.now() }};
  history.push(message);

  if (history.length > MAX_HISTORY_MESSAGES) {{
    const toSave = history.splice(0, history.length - MAX_HISTORY_MESSAGES);
    saveHistory(chatId, toSave);
  }}
}}

/**
 * 獲取歷史
 */
function getHistory(chatId) {{
  if (!conversationHistory.has(chatId)) {{
    const history = loadHistory(chatId);
    conversationHistory.set(chatId, history);
  }}
  return conversationHistory.get(chatId) || [];
}}

/**
 * 清理不活躍的對話
 */
function cleanupInactive() {{
  const now = Date.now();
  for (const [chatId, lastActivity] of chatLastActivity.entries()) {{
    if (now - lastActivity > MAX_INACTIVE_TIME) {{
      const history = conversationHistory.get(chatId);
      if (history && history.length > 0) {{
        saveHistory(chatId, history);
      }}
      conversationHistory.delete(chatId);
      chatLastActivity.delete(chatId);
      console.log(`[Cleanup] Removed inactive chat ${{chatId}}`);
    }}
  }}
}}

setInterval(cleanupInactive, 60 * 60 * 1000);

/**
 * 構建 Claude CLI 命令的 prompt
 */
function buildPrompt(chatId, newMessage) {{
  const history = getHistory(chatId);
  let prompt = '';

  // 添加歷史對話
  for (const msg of history) {{
    if (msg.role === 'user') {{
      prompt += `User: ${{msg.content}}\\n\\n`;
    }} else if (msg.role === 'assistant') {{
      prompt += `Assistant: ${{msg.content}}\\n\\n`;
    }}
  }}

  // 添加新消息
  prompt += `User: ${{newMessage}}\\n\\n`;

  return prompt;
}}

/**
 * 調用 Claude CLI
 */
function callClaudeCLI(prompt, onData, onEnd, onError) {{
  const args = [
    '--print',
    '--dangerously-skip-permissions',
    prompt
  ];

  console.log('[CLI] Spawning Claude CLI...');
  const child = spawn(CLAUDE_CLI, args, {{
    cwd: WORKSPACE,
    env: {{ ...process.env }}
  }});

  let output = '';
  let errorOutput = '';

  child.stdout.on('data', (data) => {{
    const chunk = data.toString();
    output += chunk;
    onData(chunk);
  }});

  child.stderr.on('data', (data) => {{
    errorOutput += data.toString();
    console.error('[CLI] stderr:', data.toString());
  }});

  child.on('close', (code) => {{
    if (code === 0) {{
      onEnd(output);
    }} else {{
      onError(new Error(`CLI exited with code ${{code}}: ${{errorOutput}}`));
    }}
  }});

  child.on('error', onError);

  return child;
}}

/**
 * 處理 /v1/messages 請求
 */
function handleMessagesRequest(req, res) {{
  let body = '';

  req.on('data', chunk => {{
    body += chunk.toString();
  }});

  req.on('end', () => {{
    try {{
      const data = JSON.parse(body);
      const messages = data.messages || [];
      const stream = data.stream !== false;

      // 提取 chatId（從 metadata 或生成默認值）
      const chatId = data.metadata?.user_id || 'default';

      // 獲取最後一條用戶消息
      const lastUserMessage = messages.filter(m => m.role === 'user').pop();
      if (!lastUserMessage) {{
        res.writeHead(400, {{ 'Content-Type': 'application/json' }});
        res.end(JSON.stringify({{ error: 'No user message found' }}));
        return;
      }}

      const userContent = typeof lastUserMessage.content === 'string'
        ? lastUserMessage.content
        : lastUserMessage.content.map(c => c.text || '').join('\\n');

      // 構建 prompt
      const prompt = buildPrompt(chatId, userContent);

      // 添加用戶消息到歷史
      addToHistory(chatId, 'user', userContent);

      if (stream) {{
        // SSE streaming
        res.writeHead(200, {{
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive'
        }});

        let assistantContent = '';

        callClaudeCLI(
          prompt,
          (chunk) => {{
            assistantContent += chunk;
            const event = {{
              type: 'content_block_delta',
              delta: {{ type: 'text_delta', text: chunk }}
            }};
            res.write(`data: ${{JSON.stringify(event)}}\\n\\n`);
          }},
          (fullOutput) => {{
            addToHistory(chatId, 'assistant', assistantContent);
            const endEvent = {{ type: 'message_stop' }};
            res.write(`data: ${{JSON.stringify(endEvent)}}\\n\\n`);
            res.end();
          }},
          (error) => {{
            console.error('[Error]', error.message);
            const errorEvent = {{ type: 'error', error: error.message }};
            res.write(`data: ${{JSON.stringify(errorEvent)}}\\n\\n`);
            res.end();
          }}
        );
      }} else {{
        // Non-streaming
        callClaudeCLI(
          prompt,
          () => {{}},
          (output) => {{
            addToHistory(chatId, 'assistant', output);
            const response = {{
              id: `msg-${{Date.now()}}`,
              type: 'message',
              role: 'assistant',
              content: [{{ type: 'text', text: output }}],
              model: 'claude-opus-4',
              stop_reason: 'end_turn',
              usage: {{ input_tokens: 0, output_tokens: 0 }}
            }};
            res.writeHead(200, {{ 'Content-Type': 'application/json' }});
            res.end(JSON.stringify(response));
          }},
          (error) => {{
            res.writeHead(500, {{ 'Content-Type': 'application/json' }});
            res.end(JSON.stringify({{ error: error.message }}));
          }}
        );
      }}
    }} catch (err) {{
      console.error('[Error] Request handling failed:', err);
      res.writeHead(400, {{ 'Content-Type': 'application/json' }});
      res.end(JSON.stringify({{ error: err.message }}));
    }}
  }});
}}

/**
 * HTTP Server
 */
const server = http.createServer((req, res) => {{
  console.log(`[HTTP] ${{req.method}} ${{req.url}}`);

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, anthropic-version, x-api-key');

  if (req.method === 'OPTIONS') {{
    res.writeHead(204);
    res.end();
    return;
  }}

  if (req.url === '/v1/messages' && req.method === 'POST') {{
    handleMessagesRequest(req, res);
  }} else if (req.url === '/health' && req.method === 'GET') {{
    res.writeHead(200, {{ 'Content-Type': 'application/json' }});
    res.end(JSON.stringify({{
      status: 'ok',
      proxy: 'claude-cli-proxy',
      workspace: WORKSPACE
    }}));
  }} else {{
    res.writeHead(404, {{ 'Content-Type': 'application/json' }});
    res.end(JSON.stringify({{ error: 'Not found' }}));
  }}
}});

server.timeout = 600000;
server.listen(PORT, '127.0.0.1', () => {{
  console.log(`[SERVER] Claude CLI Proxy running on http://127.0.0.1:${{PORT}}`);
  console.log('[SERVER] Workspace:', WORKSPACE);
  console.log('[SERVER] Claude CLI:', CLAUDE_CLI);
  console.log('[SERVER] Ready!');
}});

process.on('SIGINT', () => {{
  console.log('\\n[SERVER] Shutting down...');
  server.close();
  process.exit(0);
}});
'''

    proxy_file = Path(workspace_path) / "claude-proxy.js"
    proxy_file.write_text(proxy_code)
    proxy_file.chmod(0o755)

    print_success(f"代理服務器已創建: {proxy_file}")
    return str(proxy_file)

def test_proxy(proxy_file):
    """測試代理服務器"""
    print_step(4, "測試代理服務器")

    print_info("啟動代理服務器...")

    # 在後台啟動
    log_file = Path(proxy_file).parent / "proxy.log"
    with open(log_file, "w") as f:
        process = subprocess.Popen(
            ["node", proxy_file],
            stdout=f,
            stderr=subprocess.STDOUT
        )

    import time
    time.sleep(3)

    # 測試健康檢查
    try:
        import urllib.request
        response = urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=5)
        data = json.loads(response.read())
        print_success(f"代理服務器運行正常: {data['status']}")
        return process.pid
    except Exception as e:
        print_error(f"代理服務器測試失敗: {e}")
        process.kill()
        return None

def configure_agent(agent_name, workspace_path):
    """配置 OpenClaw Agent"""
    print_step(5, f"配置 OpenClaw Agent: {agent_name}")

    models_json_path = Path.home() / ".openclaw" / "agents" / agent_name / "agent" / "models.json"

    if not models_json_path.parent.exists():
        print_error(f"Agent 目錄不存在: {models_json_path.parent}")
        return False

    # 讀取現有配置
    if models_json_path.exists():
        with open(models_json_path, "r") as f:
            config = json.load(f)
    else:
        config = {{"providers": {{}}}}

    # 添加 claude-local provider
    config["providers"]["claude-local"] = {{
        "baseUrl": "http://127.0.0.1:8765",
        "api": "anthropic-messages",
        "apiKey": "sk-ant-dummy-key-for-local-proxy",
        "models": [
            {{
                "id": "claude-opus-4",
                "name": "Claude Opus 4 (Local)",
                "contextWindow": 200000,
                "maxTokens": 8192,
                "reasoning": False,
                "input": ["text", "image"],
                "cost": {{
                    "input": 0,
                    "output": 0,
                    "cacheRead": 0,
                    "cacheWrite": 0
                }},
                "api": "anthropic-messages"
            }}
        ]
    }}

    # 寫回配置
    with open(models_json_path, "w") as f:
        json.dump(config, f, indent=2)

    print_success(f"已更新 {agent_name} 的配置")
    print_info(f"配置文件: {models_json_path}")
    return True

def create_launchagent(proxy_file):
    """創建 LaunchAgent 實現開機自動啟動"""
    print_step(6, "配置自動啟動（可選）")

    response = input(f"{Colors.YELLOW}是否配置開機自動啟動? (y/N): {Colors.END}").strip().lower()
    if response != 'y':
        print_info("跳過自動啟動配置")
        return

    plist_path = Path.home() / "Library" / "LaunchAgents" / "com.claude.proxy.plist"
    plist_path.parent.mkdir(parents=True, exist_ok=True)

    node_path = subprocess.run(["which", "node"], capture_output=True).stdout.decode().strip()
    log_file = Path(proxy_file).parent / "proxy.log"

    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.proxy</string>
    <key>ProgramArguments</key>
    <array>
        <string>{node_path}</string>
        <string>{proxy_file}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{log_file}</string>
    <key>StandardErrorPath</key>
    <string>{log_file}</string>
</dict>
</plist>
'''

    plist_path.write_text(plist_content)

    # 載入 LaunchAgent
    subprocess.run(["launchctl", "load", str(plist_path)])

    print_success(f"LaunchAgent 已創建: {plist_path}")
    print_info("代理服務器將在開機時自動啟動")

def main():
    """主函數"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Claude Code CLI 反向代理自動配置工具{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

    # 檢查依賴
    if not check_dependencies():
        sys.exit(1)

    # 創建工作目錄
    workspace_path = create_workspace()

    # 獲取 Claude CLI 路徑
    claude_cli_path = get_claude_cli_path()

    # 創建代理服務器
    proxy_file = create_proxy_server(workspace_path, claude_cli_path)

    # 測試代理
    proxy_pid = test_proxy(proxy_file)
    if not proxy_pid:
        print_error("代理服務器啟動失敗")
        sys.exit(1)

    # 配置 agents
    print(f"\n{Colors.BOLD}請輸入要配置的 agent 名稱（多個用逗號分隔）：{Colors.END}")
    agent_input = input(f"{Colors.YELLOW}> {Colors.END}").strip()

    agents = [a.strip() for a in agent_input.split(",") if a.strip()]

    if agents:
        for agent in agents:
            configure_agent(agent, workspace_path)

    # 創建 LaunchAgent
    create_launchagent(proxy_file)

    # 完成
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ 配置完成！{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.END}\n")

    print(f"{Colors.BOLD}配置摘要：{Colors.END}")
    print(f"  • 工作目錄: {workspace_path}")
    print(f"  • 代理服務器: {proxy_file}")
    print(f"  • 代理端口: 8765")
    print(f"  • 已配置的 agents: {', '.join(agents) if agents else '無'}")

    print(f"\n{Colors.BOLD}使用方法：{Colors.END}")
    print(f"  在 OpenClaw 中選擇 'Claude Opus 4 (Local)' 模型即可使用")

    print(f"\n{Colors.BOLD}管理命令：{Colors.END}")
    print(f"  • 啟動代理: node {proxy_file}")
    print(f"  • 停止代理: pkill -f claude-proxy.js")
    print(f"  • 查看日誌: tail -f {Path(proxy_file).parent}/proxy.log")

    print(f"\n{Colors.BOLD}代理進程 ID: {proxy_pid}{Colors.END}\n")

if __name__ == "__main__":
    main()
