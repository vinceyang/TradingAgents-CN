# TradingAgents-CN

多智能体 LLM 股票分析框架，支持港股/美股/A股分析。

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![基于-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
pip install -e .
```

### 2. 配置

在 `.env` 文件中设置 API Key：

```bash
# 选择 LLM 提供商
TRADINGAGENTS_LLM_PROVIDER=dashscope

# API Key
DASHSCOPE_API_KEY=your-api-key
```

### 3. 命令行分析股票

```bash
# 自动识别市场（港股/美股/A股）
python -m cli.main 0700.HK           # 港股 - 腾讯
python -m cli.main AAPL              # 美股 - 苹果
python -m cli.main 600036            # A股 - 招商银行

# 指定参数
python -m cli.main 0700.HK -m hk -D 3 -p dashscope
```

**参数说明**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `-m` | 市场 (us/cn/hk/auto) | `-m hk` |
| `-d` | 分析日期 | `-d 2026-04-03` |
| `-D` | 研究深度 (1/3/5) | `-D 3` |
| `-p` | LLM 提供商 | `-p dashscope` |

## 🔌 MCP 服务（AI Agent 集成）

支持 Claude Code、OpenClaw 等 AI 工具调用。

### Claude Code 配置

创建 `~/.claude/settings.json`：

```json
{
  "mcpServers": {
    "tradingagents": {
      "command": "python",
      "args": ["-m", "tradingagents.mcp.server"],
      "env": {
        "TRADINGAGENTS_LLM_PROVIDER": "dashscope",
        "DASHSCOPE_API_KEY": "your-api-key"
      }
    }
  }
}
```

### OpenClaw 配置

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

### 可用工具

| 工具 | 说明 |
|------|------|
| `analyze_stock_full` | 完整股票分析 |
| `run_analyst_team` | 分析师团队 |
| `get_company_info` | 公司信息 |
| `get_market_data` | 市场数据 |
| `get_technical_indicators` | 技术指标 (RSI, MACD, SMA) |
| `get_fundamentals` | 基本面数据 |
| `get_stock_news` | 股票新闻 |

## 🐳 Docker 部署

```bash
docker-compose up -d
# 访问 http://localhost:8501
```

## ✨ 核心特性

- **多智能体分析**: 市场、技术、新闻、社交媒体、基本面分析师
- **多市场支持**: 港股、美股、A 股
- **多 LLM 支持**: 通义千问、DeepSeek、OpenAI、Google、Anthropic
- **辩论机制**: 牛熊双方辩论，投资经理决策
- **风险评估**: 多维度风险分析和建议
- **报告导出**: Markdown/Word/PDF 格式

## 📁 项目结构

```
tradingagents/
├── agents/              # 分析师智能体
│   └── analysts/       # 各类型分析师
├── graph/              # LangGraph 工作流
├── llm_adapters/      # LLM 适配器
├── mcp/                # MCP 服务
├── dataflows/          # 数据获取
└── tools/              # 工具函数
```

## 📖 文档

- [MCP 使用指南](docs/guides/mcp-usage-guide.md)
- [配置管理指南](docs/guides/config-management-guide.md)
- [Docker 部署指南](docs/guides/docker-deployment-guide.md)

## ⚠️ 免责声明

本框架仅用于研究和教育目的，不构成投资建议。投资有风险，决策需谨慎。

---

基于 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 开发
