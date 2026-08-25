from __future__ import annotations

import asyncio
import json
import logging
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data.adapters.kraken_adapter import KrakenAdapter
from src.data.manager import DataManager
from src.data.models import AssetClass
from src.engine.alerts import AlertCondition, AlertManager
from src.engine.autonomous_trader import AutonomousTrader, RiskManager
from src.engine.execution_engine import ExecutionEngine
from src.engine.news import NewsSentimentEngine
from src.engine.options import OptionsEngine
from src.engine.performance import PerformanceAttribution
from src.engine.risk import RiskAnalyzer
from src.engine.watchlist import WatchlistManager
from src.portfolio.portfolio import Portfolio
from src.self_improvement.engine import SelfImprovementEngine
from src.self_improvement.health_monitor import StrategyHealthMonitor
from src.strategies.momentum_strategy import MomentumStrategy
from src.strategies.strategies import MovingAverageCrossover

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

running = False
trader = None
data_manager = None
alert_manager = None
watchlist_manager = None
websocket_connections = set()


def json_dumps(obj):
    return json.dumps(obj, default=str)


async def start_server(host: str = "0.0.0.0", port: int = 9000) -> None:
    server = await asyncio.start_server(handle_client, host, port)
    logger.info("Web server listening on %s:%s", host, port)
    async with server:
        await server.serve_forever()


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    global trader, data_manager, running, alert_manager, watchlist_manager
    try:
        request = await reader.read(65536)
        if not request:
            return
        request_line = request.split(b"\r\n")[0].decode("utf-8", errors="replace")
        parts = request_line.split(" ")
        if len(parts) < 2:
            writer.close()
            return
        method, path = parts[0], parts[1]
        body = request.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in request else b""

        if "Upgrade: websocket" in request.decode("utf-8", errors="replace").lower():
            await handle_websocket(reader, writer)
            return

        if path == "/" and method == "GET":
            html = Path("web/templates/index.html").read_text()
            body_out = html.encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/status" and method == "GET":
            result = {
                "status": "running" if running else "stopped",
                "adapters": {},
                "running": running,
            }
            if data_manager:
                for ac, adapter in data_manager.get_adapters_by_asset_class().items():
                    result["adapters"][ac.value] = "healthy"
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/portfolio" and method == "GET":
            if not trader:
                result = {"total_value": 0, "positions": [], "trades": []}
            else:
                total = float(trader.portfolio.get_total_value())
                positions = []
                for ac, pos_list in trader.portfolio.get_positions().items():
                    positions.extend(pos_list)
                trades = []
                for ac, trade_list in trader.portfolio.get_trades().items():
                    trades.extend(trade_list)
                result = {"total_value": total, "positions": positions, "trades": trades}
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/prices" and method == "GET":
            result = []
            if trader:
                for symbol, price in trader._last_price.items():
                    result.append({"symbol": symbol, "price": float(price.value), "bid": float(price.bid) if price.bid else None, "ask": float(price.ask) if price.ask else None})
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/trades" and method == "GET":
            if not trader:
                result = []
            else:
                result = []
                for ac, trade_list in trader.portfolio.get_trades().items():
                    result.extend(trade_list)
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/orders" and method == "GET":
            if not trader:
                result = []
            else:
                result = trader.engine.get_active_orders()
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/positions" and method == "GET":
            result = []
            if trader:
                for ac, pos_list in trader.portfolio.get_positions().items():
                    result.extend(pos_list)
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/start" and method == "POST":
            if running:
                result = {"status": "already_running"}
            else:
                try:
                    data = json.loads(body.decode()) if body else {}
                except json.JSONDecodeError:
                    result = {"error": "Invalid JSON body"}
                    body_out = json_dumps(result).encode()
                    writer.write(b"HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
                    await writer.drain()
                    writer.close()
                    return
                assets = data.get("assets", ["crypto"])
                crypto_symbols = data.get("crypto_symbols", ["BTC-USD"])
                data_manager = DataManager()
                if "crypto" in assets:
                    crypto_adapter = KrakenAdapter(crypto_symbols)
                    data_manager.register_adapter(crypto_adapter)
                portfolio = Portfolio({AssetClass.CRYPTO: (Decimal("50000"), "USD")})
                engine = ExecutionEngine(portfolio)
                risk_manager = RiskManager(max_position_size=Decimal("0.1"), max_open_orders=10)
                strategies = []
                if "crypto" in assets:
                    strategies.append(MovingAverageCrossover(name="MA_Crossover_BTC", asset_class=AssetClass.CRYPTO, symbols=crypto_symbols, parameters={"fast_period": 10, "slow_period": 30}))
                    strategies.append(MomentumStrategy(name="Momentum_ETH", asset_class=AssetClass.CRYPTO, symbols=crypto_symbols, parameters={"roc_period": 14, "threshold": 0.02}))
                trader = AutonomousTrader(data_manager, portfolio, engine, strategies, risk_manager, improvement_engine=improvement_engine, health_monitor=health_monitor, alert_manager=alert_manager, watchlist_manager=watchlist_manager, risk_analyzer=RiskAnalyzer(), news_engine=NewsSentimentEngine())
                health_monitor = StrategyHealthMonitor()
                improvement_engine = SelfImprovementEngine(evaluation_interval_hours=24, health_monitor=health_monitor)
                alert_manager = AlertManager()
                watchlist_manager = WatchlistManager()
                for s in strategies:
                    improvement_engine.register_strategy(s)
                asyncio.create_task(data_manager.start())
                asyncio.create_task(trader.start())
                asyncio.create_task(_price_loop())
                asyncio.create_task(_autonomous_loop())
                asyncio.create_task(_dashboard_broadcast_loop())
                running = True
                result = {"status": "started"}
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/stop" and method == "POST":
            if trader:
                await trader.stop()
                trader = None
            if data_manager:
                await data_manager.stop()
                data_manager = None
            running = False
            result = {"status": "stopped"}
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/strategy/health" and method == "GET":
            if not trader:
                result = []
            else:
                result = trader.get_strategy_health()
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/strategy/deploy" and method == "POST":
            if not trader:
                result = {"error": "Trader not running"}
            else:
                data = json.loads(body.decode()) if body else {}
                strategy_name = data.get("strategy_name")
                parameters = data.get("parameters", {})
                if not strategy_name:
                    result = {"error": "strategy_name required"}
                else:
                    success = trader.deploy_strategy(strategy_name, parameters)
                    result = {"deployed": success, "strategy": strategy_name}
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/improvements" and method == "GET":
            if not trader or not trader.improvement_engine:
                result = []
            else:
                result = trader.improvement_engine.get_history()
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/alerts" and method == "GET":
            if not trader or not trader.alert_manager:
                result = []
            else:
                result = [{"id": a.id, "symbol": a.symbol, "type": a.alert_type.value, "condition": a.condition.value, "threshold": float(a.threshold), "status": a.current_status.value, "message": a.message} for a in trader.alert_manager.get_all_alerts()]
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/alerts" and method == "POST":
            if not trader or not trader.alert_manager:
                result = {"error": "Alert manager not available"}
            else:
                data = json.loads(body.decode()) if body else {}
                alert_type = data.get("type", "price")
                symbol = data.get("symbol")
                condition = data.get("condition")
                threshold = data.get("threshold")
                if not symbol or not condition or threshold is None:
                    result = {"error": "symbol, condition, and threshold required"}
                else:
                    try:
                        threshold_dec = Decimal(str(threshold))
                        condition_enum = AlertCondition(condition)
                        if alert_type == "price":
                            alert = trader.alert_manager.create_price_alert(symbol, condition_enum, threshold_dec)
                        else:
                            alert = trader.alert_manager.create_indicator_alert(symbol, condition_enum, threshold_dec, data.get("indicator", "unknown"))
                        result = {"id": alert.id, "status": "created"}
                    except Exception as exc:
                        result = {"error": str(exc)}
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/export/trades.csv" and method == "GET":
            if not trader:
                result = "Symbol,Time,Side,Quantity,Price,Fee,PnL\n"
            else:
                rows = ["Symbol,Time,Side,Quantity,Price,Fee,PnL"]
                for ac, trade_list in trader.portfolio.get_trades().items():
                    for t in trade_list:
                        rows.append(f"{t['symbol']},{t['timestamp']},{t['side']},{t['quantity']},{t['price']},{t['fee']},{t['pnl']}")
                result = "\n".join(rows) + "\n"
            body_out = result.encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/csv\r\nContent-Disposition: attachment; filename=trades.csv\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/watchlists" and method == "GET":
            if not trader or not trader.watchlist_manager:
                result = []
            else:
                result = [{"id": w.id, "name": w.name, "symbols": w.symbols} for w in trader.watchlist_manager.get_all_watchlists()]
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/watchlists" and method == "POST":
            if not trader or not trader.watchlist_manager:
                result = {"error": "Watchlist manager not available"}
            else:
                data = json.loads(body.decode()) if body else {}
                name = data.get("name")
                symbols = data.get("symbols", [])
                if not name:
                    result = {"error": "name required"}
                else:
                    watchlist = trader.watchlist_manager.create_watchlist(name, symbols)
                    result = {"id": watchlist.id, "name": watchlist.name, "symbols": watchlist.symbols}
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/orderbook" and method == "GET":
            symbol = request_line.split("?")[1].split("=")[1] if "?" in request_line else "BTC-USD"
            depth = int(request_line.split("depth=")[1].split(" ")[0]) if "depth=" in request_line else 10
            result = {"bids": [], "asks": []}
            if trader and data_manager:
                adapter = data_manager.get_adapter(AssetClass.CRYPTO)
                if adapter:
                    book = await adapter.get_order_book(symbol, depth)
                    if book:
                        result = {
                            "symbol": book.symbol,
                            "bids": [{"price": float(b.price), "quantity": float(b.quantity), "orders": b.order_count} for b in book.bids],
                            "asks": [{"price": float(a.price), "quantity": float(a.quantity), "orders": a.order_count} for a in book.asks],
                            "timestamp": book.timestamp.isoformat(),
                        }
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/risk" and method == "GET":
            result = {}
            if trader:
                analyzer = RiskAnalyzer()
                trades_by_ac = trader.portfolio.get_trades()
                all_trades = []
                for ac, trades in trades_by_ac.items():
                    all_trades.extend(trades)
                current_prices = {s: float(p.value) for s, p in trader._last_price.items()}
                metrics = analyzer.analyze_portfolio(all_trades, current_prices)
                result = {
                    "var_95": metrics.var_95,
                    "var_99": metrics.var_99,
                    "stress_test_loss": metrics.stress_test_loss,
                    "beta": metrics.beta,
                    "correlation": metrics.correlation,
                }
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/news" and method == "GET":
            result = []
            if trader:
                for symbol in list(trader._last_price.keys()):
                    news = trader.news_engine.fetch_news(symbol, 3)
                    for item in news:
                        result.append({
                            "id": item.id,
                            "symbol": item.symbol,
                            "title": item.title,
                            "source": item.source,
                            "sentiment": item.sentiment,
                            "timestamp": item.timestamp.isoformat(),
                        })
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/options/greeks" and method == "GET":
            result = {}
            if trader:
                options_engine = OptionsEngine()
                current_prices = {s: float(p.value) for s, p in trader._last_price.items()}
                result = options_engine.calculate_portfolio_greeks(current_prices)
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/ai/monte-carlo" and method == "GET":
            result = {}
            if trader and data_manager:
                try:
                    from src.ai.monte_carlo import MonteCarloBacktester
                    adapter = data_manager.get_adapter(AssetClass.CRYPTO)
                    if adapter:
                        import asyncio as _asyncio
                        loop = _asyncio.get_event_loop()
                        candles = loop.run_until_complete(adapter.get_historical_candles("BTC-USD", limit=100))
                        if candles:
                            backtest = BacktestEngine()
                            mc = MonteCarloBacktester(backtest, simulations=500)
                            mc_result = mc.run_monte_carlo(None, candles, AssetClass.CRYPTO)
                            result = {
                                "expected_return": mc_result.expected_return,
                                "std_dev": mc_result.std_dev,
                                "median_return": mc_result.median_return,
                                "percentile_5": mc_result.percentile_5,
                                "percentile_95": mc_result.percentile_95,
                                "max_drawdown_avg": mc_result.max_drawdown_avg,
                                "success_probability": mc_result.success_probability,
                            }
                except Exception as exc:
                    logger.error("Monte Carlo error: %s", exc)
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        elif path == "/api/performance" and method == "GET":
            result = {}
            if trader:
                perf = PerformanceAttribution()
                all_trades = []
                for ac, trade_list in trader.portfolio.get_trades().items():
                    all_trades.extend(trade_list)
                metrics = perf.calculate_metrics(all_trades)
                result = {
                    "total_return": metrics.total_return,
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "sortino_ratio": metrics.sortino_ratio,
                    "calmar_ratio": metrics.calmar_ratio,
                    "max_drawdown": metrics.max_drawdown,
                    "win_rate": metrics.win_rate,
                    "profit_factor": metrics.profit_factor,
                    "avg_win": metrics.avg_win,
                    "avg_loss": metrics.avg_loss,
                    "total_trades": metrics.total_trades,
                    "winning_trades": metrics.winning_trades,
                    "losing_trades": metrics.losing_trades,
                }
            body_out = json_dumps(result).encode()
            writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body_out)).encode() + b"\r\n\r\n" + body_out)
            await writer.drain()

        else:
            writer.write(b"HTTP/1.1 404 Not Found\r\n\r\n")
            await writer.drain()
    except Exception as e:
        logger.error("Request error: %s", e)
    finally:
        writer.close()


async def handle_websocket(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    global websocket_connections
    websocket_connections.add(writer)
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
    finally:
        websocket_connections.discard(writer)
        try:
            writer.close()
        except Exception:
            pass


async def broadcast_ws(message: dict) -> None:
    global websocket_connections
    data = json_dumps(message).encode() + b"\n"
    for ws in list(websocket_connections):
        try:
            ws.write(data)
            await ws.drain()
        except Exception:
            websocket_connections.discard(ws)


async def _price_loop() -> None:
    while True:
        try:
            if trader and data_manager:
                for ac, adapter in data_manager.get_adapters_by_asset_class().items():
                    for symbol in adapter.symbols:
                        try:
                            import asyncio as _asyncio
                            candles = await adapter.get_historical_candles(symbol, limit=1)
                            if candles:
                                price = candles[-1].close
                                from src.data.models import Price
                                p = Price(symbol=symbol, value=price, timestamp=datetime.utcnow(), asset_class=ac)
                                trader.update_price(p)
                                await broadcast_ws({"type": "price", "data": {"symbol": symbol, "price": float(price)}})
                        except Exception as exc:
                            logger.error("Price loop error: %s", exc)
            await asyncio.sleep(2)
        except Exception as exc:
            logger.error("Price loop fatal: %s", exc)
            await asyncio.sleep(2)


async def _autonomous_loop() -> None:
    while True:
        try:
            if trader:
                trader.process_signals()
            await asyncio.sleep(5)
        except Exception as exc:
            logger.error("Autonomous loop error: %s", exc)
            await asyncio.sleep(5)


async def _dashboard_broadcast_loop() -> None:
    while True:
        try:
            if trader:
                positions = []
                for ac, pos_list in trader.portfolio.get_positions().items():
                    positions.extend(pos_list)
                trades = []
                for ac, trade_list in trader.portfolio.get_trades().items():
                    trades.extend(trade_list[-20:])
                orders = trader.engine.get_active_orders()
                improvements = trader.improvement_engine.get_history()[-20:] if trader.improvement_engine else []
                health = trader.get_strategy_health()
                risk = {}
                if trader.risk_analyzer:
                    current_prices = {s: float(p.value) for s, p in trader._last_price.items()}
                    all_trades = []
                    for ac, trade_list in trader.portfolio.get_trades().items():
                        all_trades.extend(trade_list)
                    risk_metrics = trader.risk_analyzer.analyze_portfolio(all_trades, current_prices)
                    risk = {
                        "var_95": risk_metrics.var_95,
                        "var_99": risk_metrics.var_99,
                        "stress_test_loss": risk_metrics.stress_test_loss,
                        "beta": risk_metrics.beta,
                        "correlation": risk_metrics.correlation,
                    }
                news = []
                if trader.news_engine:
                    for symbol in list(trader._last_price.keys()):
                        news.extend(trader.news_engine.fetch_news(symbol, 2))
                options_data = {}
                if hasattr(trader, 'risk_analyzer'):
                    current_prices = {s: float(p.value) for s, p in trader._last_price.items()}
                    options_engine = OptionsEngine()
                    options_data = options_engine.calculate_portfolio_greeks(current_prices)
                monte_carlo_data = {}
                if data_manager:
                    try:
                        adapter = data_manager.get_adapter(AssetClass.CRYPTO)
                        if adapter:
                            import asyncio as _asyncio
                            loop = _asyncio.get_event_loop()
                            candles = loop.run_until_complete(adapter.get_historical_candles("BTC-USD", limit=100))
                            if candles:
                                from src.ai.backtest_engine import BacktestEngine
                                from src.ai.monte_carlo import MonteCarloBacktester
                                backtest = BacktestEngine()
                                mc = MonteCarloBacktester(backtest, simulations=500)
                                mc_result = mc.run_monte_carlo(None, candles, AssetClass.CRYPTO)
                                monte_carlo_data = {
                                    "expected_return": mc_result.expected_return,
                                    "median_return": mc_result.median_return,
                                    "percentile_5": mc_result.percentile_5,
                                    "percentile_95": mc_result.percentile_95,
                                    "max_drawdown_avg": mc_result.max_drawdown_avg,
                                    "success_probability": mc_result.success_probability,
                                }
                    except Exception as exc:
                        logger.error("Monte Carlo error: %s", exc)
                performance_data = {}
                try:
                    from src.engine.performance import PerformanceAttribution
                    perf = PerformanceAttribution()
                    all_trades = []
                    for ac, trade_list in trader.portfolio.get_trades().items():
                        all_trades.extend(trade_list)
                    metrics = perf.calculate_metrics(all_trades)
                    performance_data = {
                        "total_return": metrics.total_return,
                        "sharpe_ratio": metrics.sharpe_ratio,
                        "sortino_ratio": metrics.sortino_ratio,
                        "calmar_ratio": metrics.calmar_ratio,
                        "max_drawdown": metrics.max_drawdown,
                        "win_rate": metrics.win_rate,
                        "profit_factor": metrics.profit_factor,
                        "avg_win": metrics.avg_win,
                        "avg_loss": metrics.avg_loss,
                        "total_trades": metrics.total_trades,
                        "winning_trades": metrics.winning_trades,
                        "losing_trades": metrics.losing_trades,
                        "max_consecutive_wins": metrics.max_consecutive_wins,
                        "max_consecutive_losses": metrics.max_consecutive_losses,
                    }
                except Exception as exc:
                    logger.error("Performance error: %s", exc)
                await broadcast_ws({
                    "type": "dashboard",
                    "data": {
                        "positions": positions,
                        "trades": trades,
                        "orders": orders,
                        "improvements": improvements,
                        "health": health,
                        "risk": risk,
                        "news": [{"id": n.id, "symbol": n.symbol, "title": n.title, "source": n.source, "sentiment": n.sentiment, "timestamp": n.timestamp.isoformat()} for n in news],
                        "options": options_data,
                        "monte_carlo": monte_carlo_data,
                        "performance": performance_data,
                    },
                })
            await asyncio.sleep(2)
        except Exception as exc:
            logger.error("Dashboard broadcast error: %s", exc)
            await asyncio.sleep(2)
