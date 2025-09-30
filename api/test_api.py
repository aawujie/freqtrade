#!/usr/bin/env python3
"""
Freqtrade API 测试脚本
测试所有 API 接口的功能
"""

import requests
import json
from typing import Dict, Any
from datetime import datetime

# API 基础地址
BASE_URL = "http://localhost:8000"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
def print_test(name: str, success: bool, response: Any = None, error: str = None):
    """打印测试结果"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} {name}")
    
    if not success and error:
        print(f"  {Colors.RED}错误: {error}{Colors.END}")
    
    if response and isinstance(response, dict):
        # 只打印关键信息
        if 'success' in response:
            print(f"  success: {response.get('success')}")
        if 'message' in response:
            msg = str(response.get('message'))[:100]
            print(f"  message: {msg}")
        if 'data' in response and response['data']:
            data_str = str(response['data'])[:150]
            print(f"  data: {data_str}...")
    
    print()

def test_get(endpoint: str, name: str) -> bool:
    """测试 GET 请求"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        success = response.status_code == 200
        
        try:
            data = response.json()
            print_test(name, success, data)
        except:
            print_test(name, success, {"text": response.text[:200]})
        
        return success
    except Exception as e:
        print_test(name, False, error=str(e))
        return False

def test_post(endpoint: str, name: str, payload: Dict[str, Any] = None) -> bool:
    """测试 POST 请求"""
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=payload if payload else {},
            timeout=30
        )
        success = response.status_code == 200
        
        try:
            data = response.json()
            print_test(name, success, data)
        except:
            print_test(name, success, {"text": response.text[:200]})
        
        return success
    except Exception as e:
        print_test(name, False, error=str(e))
        return False

def run_all_tests():
    """运行所有测试"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}Freqtrade API 测试套件{Colors.END}")
    print(f"{Colors.BLUE}时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    results = []
    
    # 1. 健康检查
    print(f"{Colors.YELLOW}[基础接口]{Colors.END}")
    results.append(test_get("/health", "健康检查"))
    results.append(test_get("/", "首页"))
    
    # 2. 数据相关
    print(f"\n{Colors.YELLOW}[数据管理]{Colors.END}")
    results.append(test_get("/data/list", "列出已下载数据"))
    
    # 注意：下载数据接口可能很慢，暂时跳过
    # results.append(test_post("/data/download", "下载数据", {
    #     "pairs": ["BTC/USDT:USDT"],
    #     "timeframes": ["5m"],
    #     "days": 1
    # }))
    
    # 3. 策略相关
    print(f"\n{Colors.YELLOW}[策略管理]{Colors.END}")
    results.append(test_get("/strategies/list", "列出所有策略"))
    
    # 4. 回测相关
    print(f"\n{Colors.YELLOW}[回测功能]{Colors.END}")
    results.append(test_get("/backtest/results", "查看回测结果"))
    
    # 注意：运行回测耗时较长，可选测试
    print(f"{Colors.YELLOW}  (跳过回测运行测试 - 耗时较长){Colors.END}")
    # results.append(test_post("/backtest/run", "运行回测", {
    #     "strategy": "ichiV1",
    #     "timerange": "20250920-20250930"
    # }))
    
    # 5. 交易相关
    print(f"\n{Colors.YELLOW}[交易管理]{Colors.END}")
    results.append(test_get("/trade/status", "查看交易状态"))
    results.append(test_get("/trades/show", "查看交易记录"))
    
    # 注意：启动/停止交易会影响实际运行，跳过
    print(f"{Colors.YELLOW}  (跳过启动/停止交易测试 - 避免影响实际交易){Colors.END}")
    # results.append(test_post("/trade/start", "启动交易", {"strategy": "ichiV1"}))
    # results.append(test_post("/trade/stop", "停止交易"))
    
    # 6. 日志相关
    print(f"\n{Colors.YELLOW}[日志查看]{Colors.END}")
    results.append(test_get("/logs/recent", "查看最近日志"))
    results.append(test_get("/logs/errors", "查看错误日志"))
    
    # 7. 系统信息
    print(f"\n{Colors.YELLOW}[系统信息]{Colors.END}")
    results.append(test_get("/system/info", "查看系统信息"))
    
    # 8. 配置查看
    print(f"\n{Colors.YELLOW}[配置管理]{Colors.END}")
    results.append(test_get("/config/list", "列出所有配置文件"))
    results.append(test_get("/config/view?file_path=user_data/config_ichiV1.json", "查看 ichiV1 策略配置"))
    results.append(test_get("/config/view?file_path=user_data/configs/config_base.json", "查看基础配置"))
    
    # 统计结果
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    passed = sum(results)
    total = len(results)
    rate = (passed / total * 100) if total > 0 else 0
    
    print(f"{Colors.BLUE}测试完成:{Colors.END}")
    print(f"  总计: {total} 个测试")
    print(f"  {Colors.GREEN}通过: {passed}{Colors.END}")
    print(f"  {Colors.RED}失败: {total - passed}{Colors.END}")
    print(f"  成功率: {rate:.1f}%")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}测试过程出错: {e}{Colors.END}")
        exit(1)
