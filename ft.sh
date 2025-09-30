#!/bin/bash
# Freqtrade 常用命令快捷脚本
# 用法: ./ft.sh <命令> [参数]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Docker 容器名
CONTAINER="freqtrade"

# 帮助信息
show_help() {
    echo -e "${GREEN}Freqtrade 快捷命令工具${NC}"
    echo ""
    echo "用法: ./ft.sh <命令> [参数]"
    echo ""
    echo -e "${YELLOW}📊 交易命令:${NC}"
    echo "  trade <策略>              启动实盘/模拟交易"
    echo "  stop                      停止交易"
    echo "  status                    查看交易状态"
    echo ""
    echo -e "${YELLOW}🔙 回测命令:${NC}"
    echo "  bt <策略> [时间范围]       回测（默认最近30天）"
    echo "  bt-quick <策略>           快速回测（最近7天）"
    echo ""
    echo -e "${YELLOW}💾 数据命令:${NC}"
    echo "  dl <交易对> [天数]         下载数据（默认30天）"
    echo "  dl-all                    下载配置中的所有交易对"
    echo "  list-data                 查看已下载的数据"
    echo ""
    echo -e "${YELLOW}📈 绘图命令:${NC}"
    echo "  plot <策略> <交易对>       生成K线图"
    echo "  plot-profit <策略>        生成收益图"
    echo ""
    echo -e "${YELLOW}📝 日志命令:${NC}"
    echo "  logs [行数]               查看日志（默认100行）"
    echo "  logs-live                 实时查看日志"
    echo "  logs-error                只看错误日志"
    echo ""
    echo -e "${YELLOW}🔍 查询命令:${NC}"
    echo "  show-config <配置文件>     显示配置"
    echo "  list-strategies           列出所有策略"
    echo "  show-trades <策略>        显示交易记录"
    echo ""
    echo -e "${YELLOW}🛠️  工具命令:${NC}"
    echo "  shell                     进入容器shell"
    echo "  restart                   重启容器"
    echo "  version                   查看版本"
    echo ""
    echo "示例:"
    echo "  ./ft.sh trade ichiV1"
    echo "  ./ft.sh bt DoubleMAStrategy 20240901-20240930"
    echo "  ./ft.sh dl BTC/USDT:USDT 30"
    echo "  ./ft.sh plot ichiV1 BTC/USDT:USDT"
}

# 检查容器是否运行
check_container() {
    if ! docker ps | grep -q $CONTAINER; then
        echo -e "${RED}❌ 容器 $CONTAINER 未运行${NC}"
        echo "请先启动: docker compose up -d"
        exit 1
    fi
}

# 获取配置文件路径
get_config() {
    local strategy=$1
    case $strategy in
        ichiV1)
            echo "user_data/config_ichiV1.json"
            ;;
        DoubleMAStrategy|double_ma)
            echo "user_data/config_double_ma.json"
            ;;
        *)
            echo "user_data/config_ichiV1.json"
            ;;
    esac
}

# 主命令处理
case "${1}" in
    # 交易命令
    trade)
        check_container
        STRATEGY=${2:-ichiV1}
        CONFIG=$(get_config $STRATEGY)
        echo -e "${GREEN}🚀 启动交易: $STRATEGY${NC}"
        docker exec -it $CONTAINER freqtrade trade \
            -c /freqtrade/$CONFIG \
            --strategy $STRATEGY
        ;;
    
    stop)
        check_container
        echo -e "${YELLOW}⏸️  停止交易...${NC}"
        docker exec $CONTAINER pkill -f freqtrade || echo "没有运行的交易进程"
        ;;
    
    status)
        check_container
        echo -e "${BLUE}📊 交易状态:${NC}"
        docker exec $CONTAINER freqtrade status
        ;;
    
    # 回测命令
    bt|backtest)
        check_container
        STRATEGY=${2:-ichiV1}
        CONFIG=$(get_config $STRATEGY)
        TIMERANGE=${3:-$(date -u -d '30 days ago' +%Y%m%d)-$(date -u +%Y%m%d)}
        echo -e "${GREEN}🔙 回测: $STRATEGY (时间: $TIMERANGE)${NC}"
        docker exec $CONTAINER freqtrade backtesting \
            -c /freqtrade/$CONFIG \
            --strategy $STRATEGY \
            --timerange $TIMERANGE
        ;;
    
    bt-quick)
        check_container
        STRATEGY=${2:-ichiV1}
        CONFIG=$(get_config $STRATEGY)
        TIMERANGE=$(date -u -d '7 days ago' +%Y%m%d)-$(date -u +%Y%m%d)
        echo -e "${GREEN}⚡ 快速回测: $STRATEGY (最近7天)${NC}"
        docker exec $CONTAINER freqtrade backtesting \
            -c /freqtrade/$CONFIG \
            --strategy $STRATEGY \
            --timerange $TIMERANGE
        ;;
    
    # 数据下载
    dl|download)
        check_container
        PAIR=${2:-BTC/USDT:USDT}
        DAYS=${3:-30}
        echo -e "${GREEN}💾 下载数据: $PAIR (最近 $DAYS 天)${NC}"
        docker exec $CONTAINER freqtrade download-data \
            --exchange binance \
            --pairs $PAIR \
            --timeframes 5m 1h \
            --days $DAYS
        ;;
    
    dl-all)
        check_container
        CONFIG=${2:-user_data/config_ichiV1.json}
        echo -e "${GREEN}💾 下载配置中的所有交易对...${NC}"
        docker exec $CONTAINER freqtrade download-data \
            -c /freqtrade/$CONFIG \
            --timeframes 5m 1h \
            --days 30
        ;;
    
    list-data)
        check_container
        echo -e "${BLUE}📊 已下载的数据:${NC}"
        docker exec $CONTAINER freqtrade list-data --show-timerange
        ;;
    
    # 绘图命令
    plot)
        check_container
        STRATEGY=${2:-ichiV1}
        PAIR=${3:-BTC/USDT:USDT}
        CONFIG=$(get_config $STRATEGY)
        echo -e "${GREEN}📈 生成K线图: $STRATEGY - $PAIR${NC}"
        docker exec $CONTAINER freqtrade plot-dataframe \
            -c /freqtrade/$CONFIG \
            --strategy $STRATEGY \
            --pairs $PAIR
        echo -e "${GREEN}✅ 图表已生成到: user_data/plot/${NC}"
        ;;
    
    plot-profit)
        check_container
        STRATEGY=${2:-ichiV1}
        CONFIG=$(get_config $STRATEGY)
        echo -e "${GREEN}💰 生成收益图: $STRATEGY${NC}"
        docker exec $CONTAINER freqtrade plot-profit \
            -c /freqtrade/$CONFIG
        ;;
    
    # 日志命令
    logs)
        LINES=${2:-100}
        echo -e "${BLUE}📝 查看日志 (最后 $LINES 行):${NC}"
        docker logs --tail=$LINES $CONTAINER
        ;;
    
    logs-live)
        echo -e "${BLUE}📝 实时日志 (Ctrl+C 退出):${NC}"
        docker logs -f $CONTAINER
        ;;
    
    logs-error)
        echo -e "${RED}❌ 错误日志:${NC}"
        docker logs $CONTAINER 2>&1 | grep -i error | tail -50
        ;;
    
    # 查询命令
    show-config)
        check_container
        CONFIG=${2:-user_data/config_ichiV1.json}
        echo -e "${BLUE}⚙️  配置详情:${NC}"
        docker exec $CONTAINER freqtrade show-config \
            -c /freqtrade/$CONFIG
        ;;
    
    list-strategies)
        check_container
        echo -e "${BLUE}📈 可用策略:${NC}"
        docker exec $CONTAINER freqtrade list-strategies \
            --userdir /freqtrade/user_data
        ;;
    
    show-trades)
        check_container
        STRATEGY=${2:-ichiV1}
        CONFIG=$(get_config $STRATEGY)
        echo -e "${BLUE}💼 交易记录:${NC}"
        docker exec $CONTAINER freqtrade show-trades \
            -c /freqtrade/$CONFIG
        ;;
    
    # 工具命令
    shell)
        check_container
        echo -e "${GREEN}🐚 进入容器 shell (输入 exit 退出)${NC}"
        docker exec -it $CONTAINER /bin/bash
        ;;
    
    restart)
        echo -e "${YELLOW}🔄 重启容器...${NC}"
        docker compose restart
        echo -e "${GREEN}✅ 重启完成${NC}"
        ;;
    
    version)
        check_container
        echo -e "${BLUE}📦 Freqtrade 版本:${NC}"
        docker exec $CONTAINER freqtrade --version
        ;;
    
    # 帮助
    help|--help|-h|"")
        show_help
        ;;
    
    *)
        echo -e "${RED}❌ 未知命令: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
