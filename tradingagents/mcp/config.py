"""
MCP configuration for TradingAgents
简化的配置 - 读取 .env 由 TradingAgents 自己管理
"""
import os


def get_mode() -> str:
    """Get current data mode"""
    return "online" if os.getenv("TRADINGAGENTS_ONLINE", "true").lower() == "true" else "offline"


def get_results_dir() -> str:
    """Get results directory"""
    return os.getenv("TRADINGAGENTS_RESULTS_DIR", "~/tradingagents_results")


def validate_config() -> tuple[bool, list[str]]:
    """Validate configuration - TradingAgents validates at runtime"""
    return True, []
