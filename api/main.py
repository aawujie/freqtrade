#!/usr/bin/env python3
"""
Freqtrade API Wrapper
封装 Freqtrade 命令为 REST API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List
import subprocess
import json
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="Freqtrade API",
    description="Freqtrade 命令行工具的 REST API 封装",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
CONTAINER_NAME = "freqtrade"
BASE_PATH = Path("/Users/apple/code/freqtrade-ws")

# ==================== 数据模型 ====================

class TradeRequest(BaseModel):
    strategy: str = "ichiV1"
    config: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"strategy": "ichiV1"},
                {"strategy": "DoubleMAStrategy"}
            ]
        }
    }

class BacktestRequest(BaseModel):
    strategy: str = "ichiV1"
    timerange: Optional[str] = None
    config: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "strategy": "ichiV1",
                    "timerange": "20240901-20240930"
                },
                {
                    "strategy": "DoubleMAStrategy",
                    "timerange": "20240801-20241231"
                }
            ]
        }
    }

class DownloadDataRequest(BaseModel):
    pairs: List[str] = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
    timeframes: List[str] = ["5m", "1h"]
    days: int = 30
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "pairs": ["BTC/USDT:USDT", "ETH/USDT:USDT"],
                    "timeframes": ["5m", "1h"],
                    "days": 30
                },
                {
                    "pairs": ["BTC/USDT:USDT"],
                    "timeframes": ["5m"],
                    "days": 7
                }
            ]
        }
    }

class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# ==================== 工具函数 ====================

def run_command(cmd: List[str], timeout: int = 300, clear_env: bool = False) -> dict:
    """执行 shell 命令"""
    try:
        env = None
        if clear_env:
            # 清除 Freqtrade 环境变量，避免配置验证
            env = {k: v for k, v in subprocess.os.environ.items() 
                   if not k.startswith('FREQTRADE__')}
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=BASE_PATH,
            env=env
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "命令执行超时",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def get_config_path(strategy: str) -> str:
    """获取策略对应的配置文件路径"""
    config_map = {
        "ichiV1": "user_data/config_ichiV1.json",
        "DoubleMAStrategy": "user_data/config_double_ma.json",
        "double_ma": "user_data/config_double_ma.json",
    }
    return config_map.get(strategy, "user_data/config_ichiV1.json")

# 挂载静态文件
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# ==================== API 端点 ====================

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    index_file = static_path / "index.html"
    if index_file.exists():
        return index_file.read_text()
    return {
        "name": "Freqtrade API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    # 检查容器是否运行
    result = run_command(["docker", "ps", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Status}}"])
    is_running = result["success"] and result["stdout"].strip() != ""
    
    return {
        "status": "healthy" if is_running else "unhealthy",
        "container": CONTAINER_NAME,
        "container_running": is_running,
        "timestamp": datetime.now().isoformat()
    }

# ==================== 交易控制 ====================

@app.post("/trade/start", response_model=CommandResponse)
async def start_trade(request: TradeRequest, background_tasks: BackgroundTasks):
    """启动交易"""
    config = request.config or get_config_path(request.strategy)
    
    # 在后台启动（因为会一直运行）
    def _start_trade():
        cmd = [
            "docker", "exec", CONTAINER_NAME,
            "freqtrade", "trade",
            "-c", f"/freqtrade/{config}",
            "--strategy", request.strategy
        ]
        run_command(cmd, timeout=10)
    
    background_tasks.add_task(_start_trade)
    
    return CommandResponse(
        success=True,
        message=f"交易已在后台启动: {request.strategy}",
        data={"strategy": request.strategy, "config": config}
    )

@app.post("/trade/stop", response_model=CommandResponse)
async def stop_trade():
    """停止交易"""
    result = run_command([
        "docker", "exec", CONTAINER_NAME,
        "pkill", "-f", "freqtrade"
    ])
    
    return CommandResponse(
        success=True,
        message="交易已停止" if result["success"] else "没有运行的交易进程",
        data={"stopped": result["success"]}
    )

@app.get("/trade/status")
async def get_status():
    """获取交易状态"""
    # 获取容器状态
    container_result = run_command([
        "docker", "ps", "--filter", f"name={CONTAINER_NAME}",
        "--format", "{{.Names}}\t{{.Status}}"
    ])
    
    # 获取最近日志
    logs_result = run_command([
        "docker", "logs", "--tail=20", CONTAINER_NAME
    ])
    
    # 检查是否有 heartbeat
    is_running = "Bot heartbeat" in logs_result.get("stdout", "") or \
                 "Bot heartbeat" in logs_result.get("stderr", "")
    
    return {
        "container_status": container_result.get("stdout", "").strip(),
        "bot_running": is_running,
        "recent_logs": logs_result.get("stdout", "").split("\n")[-10:],
        "timestamp": datetime.now().isoformat()
    }

# ==================== 回测 ====================

@app.post("/backtest/run", response_model=CommandResponse)
async def run_backtest(request: BacktestRequest):
    """运行回测"""
    config = request.config or get_config_path(request.strategy)
    
    cmd = [
        "docker", "exec", CONTAINER_NAME,
        "freqtrade", "backtesting",
        "-c", f"/freqtrade/{config}",
        "--strategy", request.strategy
    ]
    
    if request.timerange:
        cmd.extend(["--timerange", request.timerange])
    
    result = run_command(cmd, timeout=600)  # 回测可能需要更长时间
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])
    
    return CommandResponse(
        success=True,
        message="回测完成",
        data={
            "strategy": request.strategy,
            "timerange": request.timerange,
            "output": result["stdout"]
        }
    )

@app.get("/backtest/results")
async def get_backtest_results():
    """获取最新的回测结果"""
    results_path = BASE_PATH / "user_data" / "backtest_results" / ".last_result.json"
    
    if not results_path.exists():
        raise HTTPException(status_code=404, detail="没有找到回测结果")
    
    try:
        with open(results_path, 'r') as f:
            data = json.load(f)
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.fromtimestamp(results_path.stat().st_mtime).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取回测结果失败: {str(e)}")

# ==================== 数据管理 ====================

@app.post("/data/download", response_model=CommandResponse)
async def download_data(request: DownloadDataRequest):
    """下载交易数据（暂时禁用，请使用命令行）"""
    return CommandResponse(
        success=False,
        message="下载数据功能暂时禁用，请直接使用命令行：docker exec <container> freqtrade download-data --exchange binance --trading-mode futures --pairs BTC/USDT:USDT --timeframes 5m 1h --days 30",
        data=None
    )

@app.get("/data/list")
async def list_data():
    """列出已下载的数据"""
    result = run_command([
        "docker", "exec", CONTAINER_NAME,
        "freqtrade", "list-data",
        "-c", "/freqtrade/user_data/config_ichiV1.json",
        "--show-timerange"
    ])
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])
    
    return {
        "success": True,
        "data": result["stdout"],
        "timestamp": datetime.now().isoformat()
    }

# ==================== 策略管理 ====================

@app.get("/strategies/list")
async def list_strategies():
    """列出所有可用策略"""
    result = run_command([
        "docker", "exec", CONTAINER_NAME,
        "freqtrade", "list-strategies",
        "--userdir", "/freqtrade/user_data"
    ])
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])
    
    # 解析策略列表
    strategies = []
    for line in result["stdout"].split("\n"):
        line = line.strip()
        if line and not line.startswith("Found") and not line.startswith("Strategy"):
            strategies.append(line)
    
    return {
        "success": True,
        "strategies": strategies,
        "count": len(strategies)
    }

# ==================== 日志 ====================

@app.get("/logs/recent")
async def get_recent_logs(lines: int = 100):
    """获取最近的日志"""
    result = run_command([
        "docker", "logs", "--tail", str(lines), CONTAINER_NAME
    ])
    
    return {
        "success": True,
        "logs": result["stdout"] + result["stderr"],
        "lines": lines,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/logs/errors")
async def get_error_logs():
    """获取错误日志"""
    result = run_command([
        "docker", "logs", "--tail", "200", CONTAINER_NAME
    ])
    
    all_logs = result["stdout"] + result["stderr"]
    error_lines = [line for line in all_logs.split("\n") if "ERROR" in line or "Error" in line]
    
    return {
        "success": True,
        "errors": error_lines,
        "count": len(error_lines),
        "timestamp": datetime.now().isoformat()
    }

# ==================== 交易记录 ====================

@app.get("/trades/show")
async def show_trades(strategy: str = "ichiV1"):
    """显示交易记录"""
    config = get_config_path(strategy)
    
    result = run_command([
        "docker", "exec", CONTAINER_NAME,
        "freqtrade", "show-trades",
        "-c", f"/freqtrade/{config}"
    ])
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["stderr"])
    
    return {
        "success": True,
        "data": result["stdout"],
        "strategy": strategy,
        "timestamp": datetime.now().isoformat()
    }

# ==================== 系统信息 ====================

@app.get("/system/info")
async def get_system_info():
    """获取系统信息"""
    # Docker 容器状态
    container_result = run_command([
        "docker", "inspect", CONTAINER_NAME, "--format", "{{json .State}}"
    ])
    
    container_state = {}
    if container_result["success"]:
        try:
            container_state = json.loads(container_result["stdout"])
        except:
            pass
    
    # Freqtrade 版本
    version_result = run_command([
        "docker", "exec", CONTAINER_NAME,
        "freqtrade", "--version"
    ])
    
    return {
        "container": {
            "name": CONTAINER_NAME,
            "state": container_state.get("Status", "unknown"),
            "running": container_state.get("Running", False),
        },
        "freqtrade_version": version_result.get("stdout", "").strip(),
        "api_version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
