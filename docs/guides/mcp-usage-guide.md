# MCP 服务使用指南

## 概述

TradingAgents-CN 内置 MCP (Model Context Protocol) 服务，可以被 Claude Code、OpenClaw 等 AI 工具直接调用，无需通过命令行界面。

## 功能特点

- **标准化接口**: 基于 MCP 协议，与 AI Agent 无缝集成
- **完整分析能力**: 支持 Layer 1/2/3 所有工具
- **统一配置**: 复用 `.env` 中的所有配置
- **多种部署方式**: 支持 Claude Code、OpenClaw 等客户端
- **CLI 友好**: 同时支持命令行直接分析股票

## 快速开始

### 1. 安装

```bash
cd TradingAgents-CN
pip install -e .
```

### 2. 配置

在 `.env` 文件中设置：

```bash
# 选择 LLM 提供商
TRADINGAGENTS_LLM_PROVIDER=dashscope

# 设置 API Key
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

支持的 LLM 提供商：

| 提供商 | LLM Provider | 默认模型 | API 端点 |
|--------|-------------|----------|----------|
| 通义千问 | dashscope | qwen-plus | dashscope.aliyuncs.com/compatible-mode/v1 |
| DeepSeek | deepseek | deepseek-chat | api.deepseek.com |
| OpenAI | openai | gpt-4o-mini | api.openai.com/v1 |

### 3. 命令行直接分析

无需交互，直接分析股票：

```bash
# 自动识别市场（美股/港股/A股）
python -m cli.main 0700.HK           # 港股
python -m cli.main AAPL              # 美股
python -m cli.main 600036            # A股

# 指定参数
python -m cli.main 0700.HK -m hk -D 3 -p dashscope
```

参数说明：
- `-m, --market`: 市场类型 (us/cn/hk/auto)
- `-d, --date`: 分析日期 (YYYY-MM-DD)
- `-D, --depth`: 研究深度 (1=浅, 3=中, 5=深)
- `-p, --provider`: LLM 提供商 (dashscope/openai/deepseek/google/anthropic)
- `-a, --analysts`: 分析师 (market/social/news/fundamentals)

### 4. 启动 MCP 服务

```bash
tradingagents-mcp
```

服务启动后显示：
```
TradingAgents MCP Server
Mode: online
Use with Claude Code or OpenClaw MCP client
```

## AI 客户端配置

### Claude Code

在 Claude Code 中连接 MCP server：

1. 运行 `/mcp` 命令
2. 选择 `tradingagents` 并连接

### OpenClaw

在 OpenClaw 中配置：

```json
{
  "mcpServers": {
    "tradingagents": {
      "command": "tradingagents-mcp",
      "args": []
    }
  }
}
```

或使用 Python 方式：

```json
{
  "mcpServers": {
    "tradingagents": {
      "command": "python",
      "args": ["-m", "tradingagents.mcp.server"]
    }
  }
}
```

## 可用工具

### Layer 3: 完整分析

| 工具 | 说明 |
|------|------|
| `analyze_stock_full` | 执行完整股票分析，返回决策和报告 |

### Layer 2: 阶段工具

| 工具 | 说明 |
|------|------|
| `run_analyst_team` | 运行分析师团队生成报告 |

### Layer 1: 原子数据工具

| 工具 | 说明 |
|------|------|
| `get_company_info` | 获取公司基本信息 |
| `get_market_data` | 获取市场行情数据 |
| `get_technical_indicators` | 获取技术指标 (RSI, MACD, SMA 等) |
| `get_fundamentals` | 获取基本面数据 |
| `get_stock_news` | 获取股票新闻 |

## 使用示例

### 完整股票分析

```python
# Claude Code 中调用
/analyze_stock_full ticker=TCEHY analysts=["market", "fundamentals"] depth=shallow
```

### 获取公司信息

```python
# 获取腾讯公司信息
/get_company_info ticker=TCEHY
```

### 获取技术指标

```python
# 获取 RSI 指标
/get_technical_indicators ticker=TCEHY indicator=RSI days=30
```

## 常见问题

### Q: MCP 服务启动失败

确保已安装 `mcp` 包：

```bash
pip install mcp>=1.0.0
```

### Q: API 认证失败

检查 `.env` 中的 API Key 是否正确：

```bash
grep API_KEY .env
```

### Q: 分析报 401 错误

确保 `TRADINGAGENTS_LLM_PROVIDER` 设置正确：

```bash
export TRADINGAGENTS_LLM_PROVIDER=dashscope
```

### Q: 使用什么模型

默认使用 `qwen-plus`。如需自定义：

```bash
export TRADINGAGENTS_DEEP_MODEL=qwen-plus
export TRADINGAGENTS_QUICK_MODEL=qwen-plus
```

## 技术细节

### 配置优先级

1. 环境变量 `TRADINGAGENTS_*`
2. `.env` 文件
3. 默认值

### MCP 模块位置

```
tradingagents/
└── mcp/
    ├── __init__.py
    ├── config.py      # 配置管理
    ├── server.py      # MCP 服务端
    └── tools.py       # 工具实现
```

### 命令行入口

```bash
# 方式1: 直接命令
tradingagents-mcp

# 方式2: Python 模块
python -m tradingagents.mcp.server

# 方式3: Claude Code 中
/mcp  # 然后选择 tradingagents
```

## 测试示例

### 腾讯控股分析

```bash
# 港股分析
python -m cli.main 0700.HK -m hk --depth 1

# 美股分析
python -m cli.main NVDA -m us --depth 1

# A股分析
python -m cli.main 600036 -m cn --depth 1
```

## 已知问题

### 1. API URL 配置

确保 `.env` 或 CLI 参数中的 DashScope URL 使用 `/compatible-mode/v1`：

```bash
# ✅ 正确
https://dashscope.aliyuncs.com/compatible-mode/v1

# ❌ 错误（会导致 404）
https://dashscope.aliyuncs.com/api/v1
```

### 2. API Key 验证

系统会验证 API Key 是否为有效值（排除占位符如 `your_key_here`）。确保 `.env` 中的 Key 是真实有效的。

## 架构说明

```
tradingagents/
├── mcp/                    # MCP 服务模块
│   ├── server.py          # stdio server
│   ├── tools.py           # 工具实现 (Layer 1/2/3)
│   └── config.py          # 配置管理
├── agents/                # 分析师 agents
│   └── analysts/         # 各类型分析师
├── graph/                # LangGraph 工作流
│   └── trading_graph.py  # 主分析图
└── llm_adapters/        # LLM 适配器
    └── dashscope_openai_adapter.py
```
