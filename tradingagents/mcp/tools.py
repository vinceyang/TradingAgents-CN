"""
MCP tools for TradingAgents
"""
import json
import os
from datetime import datetime
from typing import Any, Optional

import pandas as pd
from mcp.types import Tool, TextContent

from .config import get_mode, get_results_dir


# ============================================================================
# Tool Definitions
# ============================================================================

def get_tools() -> list[Tool]:
    """Return all available MCP tools"""
    tools = []

    # Layer 3: Complete flow
    tools.extend(_get_layer3_tools())

    # Layer 2: Phase tools
    tools.extend(_get_layer2_tools())

    # Layer 1: Atomic tools
    tools.extend(_get_layer1_tools())

    return tools


def _get_layer3_tools() -> list[Tool]:
    """Get Layer 3 tools (complete flow)"""
    return [
        Tool(
            name="analyze_stock_full",
            description="""Execute complete stock analysis with all agents.
            Returns comprehensive analysis report including analyst team reports,
            research debate, trading plan, and risk assessment.
            Returns JSON with decision (BUY/SELL/HOLD), key_points, and report_file.
            """,
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol, e.g., AAPL, TSLA, NVDA"
                    },
                    "date": {
                        "type": "string",
                        "description": "Analysis date in YYYY-MM-DD format. Use today if not specified."
                    },
                    "analysts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Which analysts to use",
                        "default": ["market", "news", "social", "fundamentals"]
                    },
                    "depth": {
                        "type": "string",
                        "description": "Research depth - affects debate rounds",
                        "default": "medium",
                        "enum": ["shallow", "medium", "deep"]
                    }
                },
                "required": ["ticker"]
            }
        ),
    ]


def _get_layer2_tools() -> list[Tool]:
    """Get Layer 2 tools (phase tools)"""
    return [
        Tool(
            name="run_analyst_team",
            description="Run analyst team to generate individual reports",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker"},
                    "date": {
                        "type": "string",
                        "description": "Analysis date (YYYY-MM-DD)",
                    },
                    "analysts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Which analysts to run",
                        "default": ["market", "news", "social", "fundamentals"]
                    }
                },
                "required": ["ticker"]
            }
        ),
    ]


def _get_layer1_tools() -> list[Tool]:
    """Get Layer 1 tools (atomic data tools)"""
    return [
        Tool(
            name="get_market_data",
            description="Get market price data from Yahoo Finance",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"}
                },
                "required": ["ticker", "start_date", "end_date"]
            }
        ),
        Tool(
            name="get_stock_news",
            description="Get recent news for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "date": {"type": "string"},
                    "days": {"type": "integer", "default": 7}
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_technical_indicators",
            description="Get technical indicators (RSI, MACD, SMA, EMA, Bollinger, ATR)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "indicator": {
                        "type": "string",
                        "description": "Technical indicator name",
                        "enum": ["RSI", "MACD", "SMA", "EMA", "BOLL", "ATR", "VWAP", "STOCH"]
                    },
                    "date": {"type": "string"},
                    "days": {"type": "integer", "default": 30}
                },
                "required": ["ticker", "indicator"]
            }
        ),
        Tool(
            name="get_fundamentals",
            description="Get fundamental data (balance sheet, income statement, cash flow)",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "date": {"type": "string"},
                    "statement_type": {
                        "type": "string",
                        "enum": ["balance_sheet", "income", "cashflow", "all"]
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_company_info",
            description="Get company basic information",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"}
                },
                "required": ["ticker"]
            }
        ),
    ]


# ============================================================================
# Tool Execution
# ============================================================================

async def call_tool(
    name: str,
    arguments: dict[str, Any]
) -> list[TextContent]:
    """Execute a tool and return results"""
    try:
        if name == "analyze_stock_full":
            return await _analyze_stock_full(**arguments)
        elif name == "run_analyst_team":
            return await _run_analyst_team(**arguments)
        elif name == "get_market_data":
            return await _get_market_data(**arguments)
        elif name == "get_stock_news":
            return await _get_stock_news(**arguments)
        elif name == "get_technical_indicators":
            return await _get_technical_indicators(**arguments)
        elif name == "get_fundamentals":
            return await _get_fundamentals(**arguments)
        elif name == "get_company_info":
            return await _get_company_info(**arguments)
        else:
            return _error_result(f"Unknown tool: {name}", "UNKNOWN_TOOL")
    except Exception as e:
        return _error_result(str(e), "EXECUTION_ERROR")


def _error_result(message: str, code: str) -> list[TextContent]:
    """Create error result"""
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": False,
            "error": {
                "code": code,
                "message": message
            }
        }, ensure_ascii=False)
    )]


def _success_result(data: dict) -> list[TextContent]:
    """Create success result"""
    return [TextContent(
        type="text",
        text=json.dumps(data, ensure_ascii=False, indent=2, default=str)
    )]


# ============================================================================
# Layer 3: Complete Flow
# ============================================================================

def _get_llm_config() -> dict:
    """Get LLM config from environment variables"""
    from tradingagents.default_config import DEFAULT_CONFIG
    cfg = DEFAULT_CONFIG.copy()

    provider = os.getenv("TRADINGAGENTS_LLM_PROVIDER", "openai").lower()

    # Map provider to config
    if provider in ("dashscope", "qianwen", "alibaba", "阿里百炼"):
        cfg["llm_provider"] = "dashscope"
        cfg["backend_url"] = os.getenv("TRADINGAGENTS_BACKEND_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        cfg["deep_think_llm"] = os.getenv("TRADINGAGENTS_DEEP_MODEL", "qwen-plus")
        cfg["quick_think_llm"] = os.getenv("TRADINGAGENTS_QUICK_MODEL", "qwen-plus")
    elif provider == "deepseek":
        cfg["llm_provider"] = "deepseek"
        cfg["backend_url"] = os.getenv("TRADINGAGENTS_BACKEND_URL", "https://api.deepseek.com")
        cfg["deep_think_llm"] = os.getenv("TRADINGAGENTS_DEEP_MODEL", "deepseek-reasoner")
        cfg["quick_think_llm"] = os.getenv("TRADINGAGENTS_QUICK_MODEL", "deepseek-chat")
    elif provider == "anthropic":
        cfg["llm_provider"] = "anthropic"
        cfg["backend_url"] = os.getenv("TRADINGAGENTS_BACKEND_URL", "https://api.anthropic.com/")
    elif provider == "google":
        cfg["llm_provider"] = "google"
        cfg["backend_url"] = os.getenv("TRADINGAGENTS_BACKEND_URL", "https://generativelanguage.googleapis.com/v1")
    else:
        # Default to openai-compatible
        cfg["llm_provider"] = "openai"
        cfg["backend_url"] = os.getenv("TRADINGAGENTS_BACKEND_URL", "https://api.openai.com/v1")
        cfg["deep_think_llm"] = os.getenv("TRADINGAGENTS_DEEP_MODEL", "gpt-4o-mini")
        cfg["quick_think_llm"] = os.getenv("TRADINGAGENTS_QUICK_MODEL", "gpt-4o-mini")

    return cfg


async def _analyze_stock_full(
    ticker: str,
    date: Optional[str] = None,
    analysts: Optional[list] = None,
    depth: str = "medium"
) -> list[TextContent]:
    """Execute complete stock analysis"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    if analysts is None:
        analysts = ["market", "news", "social", "fundamentals"]

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph

        cfg = _get_llm_config()
        cfg["online_tools"] = get_mode() == "online"

        # Map depth to rounds
        depth_rounds = {"shallow": 1, "medium": 3, "deep": 5}
        cfg["max_debate_rounds"] = depth_rounds.get(depth, 3)
        cfg["max_risk_discuss_rounds"] = depth_rounds.get(depth, 3)

        # Map analyst names
        analyst_map = {
            "market": "market",
            "news": "news",
            "social": "social",
            "fundamentals": "fundamentals"
        }
        types = [analyst_map.get(a, a) for a in analysts if a in analyst_map]

        graph = TradingAgentsGraph(types, config=cfg, debug=False)
        state, decision = graph.propagate(ticker.upper(), date)

        # Extract results
        result = {
            "success": True,
            "ticker": ticker.upper(),
            "date": date,
            "decision": decision,
            "analysts": analysts,
            "depth": depth,
            "state": {
                "market_report": state.get("market_report", "")[:500] if state.get("market_report") else "",
                "fundamentals_report": state.get("fundamentals_report", "")[:500] if state.get("fundamentals_report") else "",
                "final_trade_decision": state.get("final_trade_decision", "")[:500] if state.get("final_trade_decision") else "",
            }
        }

        return _success_result(result)

    except ImportError as e:
        return _error_result(str(e), "IMPORT_ERROR")
    except Exception as e:
        return _error_result(str(e), "ANALYSIS_ERROR")


async def _run_analyst_team(
    ticker: str,
    date: Optional[str] = None,
    analysts: Optional[list] = None
) -> list[TextContent]:
    """Run analyst team"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    if analysts is None:
        analysts = ["market", "news", "social", "fundamentals"]

    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        cfg = DEFAULT_CONFIG.copy()
        cfg["online_tools"] = get_mode() == "online"

        analyst_map = {
            "market": "market",
            "news": "news",
            "social": "social",
            "fundamentals": "fundamentals"
        }
        types = [analyst_map.get(a, a) for a in analysts if a in analyst_map]

        graph = TradingAgentsGraph(types, config=cfg, debug=False)
        state, _ = graph.propagate(ticker.upper(), date)

        result = {
            "success": True,
            "ticker": ticker.upper(),
            "date": date,
            "reports": {
                "market": state.get("market_report", "")[:500] if state.get("market_report") else "",
                "fundamentals": state.get("fundamentals_report", "")[:500] if state.get("fundamentals_report") else "",
                "news": state.get("news_report", "")[:500] if state.get("news_report") else "",
                "social": state.get("sentiment_report", "")[:500] if state.get("sentiment_report") else "",
            }
        }

        return _success_result(result)

    except Exception as e:
        return _error_result(str(e), "ANALYSIS_ERROR")


# ============================================================================
# Layer 1: Atomic Data Tools
# ============================================================================

async def _get_market_data(
    ticker: str,
    start_date: str,
    end_date: str
) -> list[TextContent]:
    """Get market data from Yahoo Finance"""
    try:
        import yfinance as yf

        data = yf.download(ticker.upper(), start=start_date, end=end_date, progress=False)

        if data.empty:
            return _error_result("No data available for this period", "NO_DATA")

        close_col = data["Close"]
        if isinstance(close_col, pd.DataFrame):
            close_col = close_col.iloc[:, 0]
        volume_col = data["Volume"]
        if isinstance(volume_col, pd.DataFrame):
            volume_col = volume_col.iloc[:, 0]

        result = {
            "success": True,
            "source": "Yahoo Finance",
            "ticker": ticker.upper(),
            "start_date": start_date,
            "end_date": end_date,
            "records": len(data),
            "latest": {
                "close": float(close_col.iloc[-1]) if len(close_col) > 0 else None,
                "volume": int(volume_col.iloc[-1]) if len(volume_col) > 0 else None,
            },
            "summary": {
                "avg_close": float(close_col.mean()) if len(close_col) > 0 else None,
                "max_close": float(close_col.max()) if len(close_col) > 0 else None,
                "min_close": float(close_col.min()) if len(close_col) > 0 else None,
            }
        }

        return _success_result(result)

    except ImportError:
        return _error_result("yfinance not installed", "IMPORT_ERROR")
    except Exception as e:
        return _error_result(str(e), "DATA_ERROR")


async def _get_stock_news(
    ticker: str,
    date: Optional[str] = None,
    days: int = 7
) -> list[TextContent]:
    """Get stock news from Yahoo Finance or Finnhub"""
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker.upper())

        # 获取新闻
        news = stock.news

        if not news or len(news) == 0:
            return _success_result({
                "success": True,
                "source": "Yahoo Finance",
                "ticker": ticker.upper(),
                "count": 0,
                "news": [],
                "message": "No recent news available"
            })

        # 格式化新闻列表
        formatted_news = []
        for item in news[:days]:
            formatted_news.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", ""),
                "link": item.get("link", ""),
                "published": item.get("published", ""),
            })

        return _success_result({
            "success": True,
            "source": "Yahoo Finance",
            "ticker": ticker.upper(),
            "count": len(formatted_news),
            "news": formatted_news
        })

    except ImportError:
        return _error_result("yfinance not installed", "IMPORT_ERROR")
    except Exception as e:
        return _error_result(str(e), "NEWS_ERROR")


async def _get_technical_indicators(
    ticker: str,
    indicator: str,
    date: Optional[str] = None,
    days: int = 30
) -> list[TextContent]:
    """Get technical indicators"""
    try:
        import yfinance as yf

        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        start_date = end_date - pd.Timedelta(days=days + 50)
        data = yf.download(ticker.upper(), start=start_date, end=end_date, progress=False)

        if data.empty:
            return _error_result("No data available", "NO_DATA")

        close = data["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        results = {}

        if indicator.upper() == "SMA":
            results["sma_20"] = float(close.rolling(window=20).mean().iloc[-1])
            results["sma_50"] = float(close.rolling(window=50).mean().iloc[-1]) if len(close) >= 50 else None
        elif indicator.upper() == "EMA":
            results["ema_12"] = float(close.ewm(span=12).mean().iloc[-1])
            results["ema_26"] = float(close.ewm(span=26).mean().iloc[-1])
        elif indicator.upper() == "RSI":
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            results["rsi"] = float(rsi.iloc[-1])

        return _success_result({
            "success": True,
            "ticker": ticker.upper(),
            "indicator": indicator.upper(),
            "results": results
        })

    except Exception as e:
        return _error_result(str(e), "INDICATOR_ERROR")


async def _get_fundamentals(
    ticker: str,
    date: Optional[str] = None,
    statement_type: str = "all"
) -> list[TextContent]:
    """Get fundamental data"""
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker.upper())

        result = {
            "success": True,
            "source": "Yahoo Finance",
            "ticker": ticker.upper(),
        }

        try:
            info = stock.info
            result["info"] = {
                "company_name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
            }
        except:
            result["info"] = "Not available"

        return _success_result(result)

    except Exception as e:
        return _error_result(str(e), "FUNDAMENTAL_ERROR")


async def _get_company_info(
    ticker: str
) -> list[TextContent]:
    """Get company basic information"""
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker.upper())
        info = stock.info

        if not info or "regularMarketPrice" not in info:
            return _error_result("Company info not available", "NO_DATA")

        result = {
            "success": True,
            "source": "Yahoo Finance",
            "ticker": ticker.upper(),
            "company": {
                "name": info.get("longName", info.get("shortName", "")),
                "exchange": info.get("exchange", ""),
                "currency": info.get("currency", ""),
            },
            "market": {
                "price": info.get("regularMarketPrice", 0),
                "previous_close": info.get("regularMarketPreviousClose", 0),
                "volume": info.get("regularMarketVolume", 0),
            },
            "valuation": {
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "eps": info.get("trailingEps", 0),
            },
            "52_week": {
                "high": info.get("fiftyTwoWeekHigh", 0),
                "low": info.get("fiftyTwoWeekLow", 0),
            },
        }

        return _success_result(result)

    except Exception as e:
        return _error_result(str(e), "INFO_ERROR")
