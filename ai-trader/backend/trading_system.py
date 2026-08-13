"""
AI Trader Backend - Agent Swarm Trading System
"""
import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import math

# ============================================================================
# DATA MODELS
# ============================================================================

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class AgentType(Enum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    SENTIMENT = "sentiment"
    RISK = "risk"
    QUANTITATIVE = "quantitative"
    COORDINATOR = "coordinator"

@dataclass
class MarketData:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: float
    high_24h: float
    low_24h: float
    market_cap: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AgentAnalysis:
    agent_type: AgentType
    symbol: str
    signal: SignalType
    confidence: float
    reasoning: str
    metrics: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SwarmPrediction:
    symbol: str
    prediction: SignalType
    confidence: float
    price_target: float
    time_horizon: str
    agent_votes: Dict[str, float]
    consensus_reasoning: str
    risk_score: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Portfolio:
    cash: float
    holdings: Dict[str, float]
    total_value: float
    daily_pnl: float
    total_pnl: float
    win_rate: float
    trades: int

# ============================================================================
# AGENT SWARM SYSTEM
# ============================================================================

class BaseAgent:
    def __init__(self, name: str, agent_type: AgentType):
        self.name = name
        self.agent_type = agent_type
        self.weight = 1.0
        self.accuracy = random.uniform(0.65, 0.85)

    async def analyze(self, market_data: MarketData) -> AgentAnalysis:
        raise NotImplementedError

class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__("Technical Analyst", AgentType.TECHNICAL)
        self.weight = 1.2
        self.accuracy = 0.78

    async def analyze(self, market_data: MarketData) -> AgentAnalysis:
        await asyncio.sleep(0.1)
        
        # Simulate technical indicators
        rsi = random.uniform(20, 80)
        macd = random.uniform(-2, 2)
        ma_cross = random.choice([-1, 0, 1])
        bollinger = random.uniform(-1, 1)
        
        score = 0
        reasons = []
        
        if rsi < 30:
            score += 2
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            score -= 2
            reasons.append(f"RSI overbought ({rsi:.1f})")
        
        score += macd * 1.5
        score += ma_cross * 1.2
        score += bollinger * 0.8
        
        if score > 2:
            signal = SignalType.STRONG_BUY
        elif score > 0.5:
            signal = SignalType.BUY
        elif score < -2:
            signal = SignalType.STRONG_SELL
        elif score < -0.5:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        confidence = min(0.95, self.accuracy + abs(score) * 0.05)
        
        return AgentAnalysis(
            agent_type=self.agent_type,
            symbol=market_data.symbol,
            signal=signal,
            confidence=confidence,
            reasoning=f"Technical: {'; '.join(reasons)}. Score: {score:.2f}",
            metrics={"rsi": rsi, "macd": macd, "ma_cross": ma_cross, "bollinger": bollinger, "score": score}
        )

class FundamentalAgent(BaseAgent):
    def __init__(self):
        super().__init__("Fundamental Analyst", AgentType.FUNDAMENTAL)
        self.weight = 1.0
        self.accuracy = 0.72

    async def analyze(self, market_data: MarketData) -> AgentAnalysis:
        await asyncio.sleep(0.15)
        
        pe_ratio = random.uniform(10, 50)
        revenue_growth = random.uniform(-5, 30)
        profit_margin = random.uniform(5, 25)
        debt_ratio = random.uniform(0.1, 0.8)
        
        score = 0
        reasons = []
        
        if pe_ratio < 20:
            score += 1.5
            reasons.append(f"Reasonable P/E ({pe_ratio:.1f})")
        elif pe_ratio > 35:
            score -= 1
            reasons.append(f"High P/E ({pe_ratio:.1f})")
        
        score += revenue_growth * 0.1
        score += profit_margin * 0.05
        score -= debt_ratio * 0.5
        
        if score > 1.5:
            signal = SignalType.STRONG_BUY
        elif score > 0.5:
            signal = SignalType.BUY
        elif score < -1.5:
            signal = SignalType.STRONG_SELL
        elif score < -0.5:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        confidence = min(0.90, self.accuracy + abs(score) * 0.04)
        
        return AgentAnalysis(
            agent_type=self.agent_type,
            symbol=market_data.symbol,
            signal=signal,
            confidence=confidence,
            reasoning=f"Fundamental: {'; '.join(reasons)}. Score: {score:.2f}",
            metrics={"pe_ratio": pe_ratio, "revenue_growth": revenue_growth, "profit_margin": profit_margin, "debt_ratio": debt_ratio, "score": score}
        )

class SentimentAgent(BaseAgent):
    def __init__(self):
        super().__init__("Sentiment Analyst", AgentType.SENTIMENT)
        self.weight = 0.8
        self.accuracy = 0.70

    async def analyze(self, market_data: MarketData) -> AgentAnalysis:
        await asyncio.sleep(0.12)
        
        news_sentiment = random.uniform(-1, 1)
        social_media = random.uniform(-1, 1)
        fear_greed = random.uniform(0, 100)
        analyst_rating = random.uniform(1, 5)
        
        score = news_sentiment * 0.4 + social_media * 0.3 + (fear_greed - 50) / 50 * 0.3
        score += (analyst_rating - 3) * 0.2
        
        reasons = []
        if news_sentiment > 0.5:
            reasons.append("Positive news sentiment")
        elif news_sentiment < -0.5:
            reasons.append("Negative news sentiment")
        
        if fear_greed > 70:
            reasons.append("Greedy market")
        elif fear_greed < 30:
            reasons.append("Fearful market")
        
        if score > 0.5:
            signal = SignalType.BUY
        elif score > 1.0:
            signal = SignalType.STRONG_BUY
        elif score < -0.5:
            signal = SignalType.SELL
        elif score < -1.0:
            signal = SignalType.STRONG_SELL
        else:
            signal = SignalType.HOLD
        
        confidence = min(0.88, self.accuracy + abs(score) * 0.06)
        
        return AgentAnalysis(
            agent_type=self.agent_type,
            symbol=market_data.symbol,
            signal=signal,
            confidence=confidence,
            reasoning=f"Sentiment: {'; '.join(reasons)}. Score: {score:.2f}",
            metrics={"news_sentiment": news_sentiment, "social_media": social_media, "fear_greed": fear_greed, "analyst_rating": analyst_rating, "score": score}
        )

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("Risk Manager", AgentType.RISK)
        self.weight = 1.5
        self.accuracy = 0.80

    async def analyze(self, market_data: MarketData) -> AgentAnalysis:
        await asyncio.sleep(0.08)
        
        volatility = random.uniform(0.1, 0.5)
        beta = random.uniform(0.5, 2.0)
        var_95 = random.uniform(0.02, 0.1)
        correlation = random.uniform(-0.5, 1.0)
        
        risk_score = volatility * 0.4 + abs(beta - 1) * 0.3 + var_95 * 5 + (1 - correlation) * 0.3
        
        if risk_score < 0.3:
            signal = SignalType.STRONG_BUY
            reasons = ["Low risk profile", "Favorable risk-adjusted returns"]
        elif risk_score < 0.5:
            signal = SignalType.BUY
            reasons = ["Moderate risk", "Acceptable risk-reward ratio"]
        elif risk_score < 0.7:
            signal = SignalType.HOLD
            reasons = ["Elevated risk", "Caution advised"]
        else:
            signal = SignalType.SELL
            reasons = ["High risk detected", "Consider reducing exposure"]
        
        confidence = min(0.92, self.accuracy + (1 - risk_score) * 0.1)
        
        return AgentAnalysis(
            agent_type=self.agent_type,
            symbol=market_data.symbol,
            signal=signal,
            confidence=confidence,
            reasoning=f"Risk: {'; '.join(reasons)}. Risk Score: {risk_score:.2f}",
            metrics={"volatility": volatility, "beta": beta, "var_95": var_95, "correlation": correlation, "risk_score": risk_score}
        )

class QuantitativeAgent(BaseAgent):
    def __init__(self):
        super().__init__("Quantitative Model", AgentType.QUANTITATIVE)
        self.weight = 1.3
        self.accuracy = 0.75

    async def analyze(self, market_data: MarketData) -> AgentAnalysis:
        await asyncio.sleep(0.14)
        
        momentum = random.uniform(-1, 1)
        mean_reversion = random.uniform(-1, 1)
        seasonality = random.uniform(-0.5, 0.5)
        liquidity = random.uniform(0.3, 1.0)
        
        score = momentum * 0.5 + mean_reversion * 0.3 + seasonality * 0.2
        score += liquidity * 0.3
        
        reasons = []
        if momentum > 0.3:
            reasons.append("Strong momentum")
        elif momentum < -0.3:
            reasons.append("Weak momentum")
        
        if liquidity > 0.7:
            reasons.append("High liquidity")
        
        if score > 0.6:
            signal = SignalType.STRONG_BUY
        elif score > 0.2:
            signal = SignalType.BUY
        elif score < -0.6:
            signal = SignalType.STRONG_SELL
        elif score < -0.2:
            signal = SignalType.SELL
        else:
            signal = SignalType.HOLD
        
        confidence = min(0.93, self.accuracy + abs(score) * 0.08)
        
        return AgentAnalysis(
            agent_type=self.agent_type,
            symbol=market_data.symbol,
            signal=signal,
            confidence=confidence,
            reasoning=f"Quant: {'; '.join(reasons)}. Score: {score:.2f}",
            metrics={"momentum": momentum, "mean_reversion": mean_reversion, "seasonality": seasonality, "liquidity": liquidity, "score": score}
        )

class CoordinatorAgent:
    def __init__(self):
        self.name = "Coordinator"
        self.agents: List[BaseAgent] = [
            TechnicalAgent(),
            FundamentalAgent(),
            SentimentAgent(),
            RiskAgent(),
            QuantitativeAgent()
        ]

    async def run_swarm(self, market_data_list: List[MarketData]) -> List[SwarmPrediction]:
        tasks = []
        for market_data in market_data_list:
            for agent in self.agents:
                tasks.append(agent.analyze(market_data))
        
        analyses = await asyncio.gather(*tasks)
        
        predictions = []
        for market_data in market_data_list:
            symbol_analyses = [a for a in analyses if a.symbol == market_data.symbol]
            prediction = self._consensus(market_data, symbol_analyses)
            predictions.append(prediction)
        
        return predictions

    def _consensus(self, market_data: MarketData, analyses: List[AgentAnalysis]) -> SwarmPrediction:
        votes = {}
        for analysis in analyses:
            agent_name = analysis.agent_type.value
            weight = next(a.weight for a in self.agents if a.agent_type == analysis.agent_type)
            votes[agent_name] = analysis.confidence * weight
        
        weighted_signals = {}
        for analysis in analyses:
            signal_value = self._signal_to_value(analysis.signal)
            weight = next(a.weight for a in self.agents if a.agent_type == analysis.agent_type)
            weighted_signals[analysis.agent_type.value] = signal_value * weight * analysis.confidence
        
        consensus_score = sum(weighted_signals.values())
        prediction_signal = self._value_to_signal(consensus_score)
        
        price_target = market_data.price * (1 + consensus_score * 0.15)
        risk_score = sum(a.metrics.get("risk_score", 0.5) for a in analyses if a.agent_type == AgentType.RISK) / len(analyses)
        
        reasons = [a.reasoning for a in analyses]
        consensus_reasoning = " | ".join(reasons[:3])
        
        return SwarmPrediction(
            symbol=market_data.symbol,
            prediction=prediction_signal,
            confidence=sum(votes.values()) / len(votes),
            price_target=price_target,
            time_horizon="24h",
            agent_votes=votes,
            consensus_reasoning=consensus_reasoning,
            risk_score=min(1.0, risk_score)
        )

    def _signal_to_value(self, signal: SignalType) -> float:
        mapping = {
            SignalType.STRONG_BUY: 2.0,
            SignalType.BUY: 1.0,
            SignalType.HOLD: 0.0,
            SignalType.SELL: -1.0,
            SignalType.STRONG_SELL: -2.0
        }
        return mapping.get(signal, 0.0)

    def _value_to_signal(self, value: float) -> SignalType:
        if value > 1.5:
            return SignalType.STRONG_BUY
        elif value > 0.5:
            return SignalType.BUY
        elif value < -1.5:
            return SignalType.STRONG_SELL
        elif value < -0.5:
            return SignalType.SELL
        return SignalType.HOLD

# ============================================================================
# MARKET DATA SERVICE
# ============================================================================

class MarketDataService:
    def __init__(self):
        self.symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        self.base_prices = {
            "BTC/USDT": 65000, "ETH/USDT": 3500, "SOL/USDT": 145,
            "AAPL": 175, "GOOGL": 140, "MSFT": 420, "AMZN": 185, "TSLA": 250
        }
        self.price_history = {s: [] for s in self.symbols}

    def get_market_data(self) -> List[MarketData]:
        market_data = []
        for symbol in self.symbols:
            base = self.base_prices[symbol]
            change = random.uniform(-0.05, 0.05)
            price = base * (1 + change)
            base_prices = self.base_prices[symbol] = price
            
            change_24h = random.uniform(-0.1, 0.1)
            high = price * random.uniform(1.01, 1.05)
            low = price * random.uniform(0.95, 0.99)
            volume = random.uniform(1e6, 1e9)
            market_cap = price * random.uniform(1e8, 1e12)
            
            market_data.append(MarketData(
                symbol=symbol,
                price=price,
                change=change_24h,
                change_percent=change_24h * 100,
                volume=volume,
                high_24h=high,
                low_24h=low,
                market_cap=market_cap
            ))
        return market_data

# ============================================================================
# PORTFOLIO MANAGER
# ============================================================================

class PortfolioManager:
    def __init__(self):
        self.initial_cash = 1000000.0
        self.cash = self.initial_cash
        self.holdings = {}
        self.trade_history = []
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.trades = 0
        self.wins = 0

    def execute_trade(self, symbol: str, action: str, price: float, quantity: float = 1.0):
        if action == "BUY":
            cost = price * quantity
            if cost <= self.cash:
                self.cash -= cost
                self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
                self.trades += 1
                self.trade_history.append({
                    "symbol": symbol, "action": action, "price": price,
                    "quantity": quantity, "timestamp": datetime.now().isoformat()
                })
                return True
        elif action == "SELL":
            if self.holdings.get(symbol, 0) >= quantity:
                self.cash += price * quantity
                self.holdings[symbol] -= quantity
                self.trades += 1
                self.trade_history.append({
                    "symbol": symbol, "action": action, "price": price,
                    "quantity": quantity, "timestamp": datetime.now().isoformat()
                })
                return True
        return False

    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Portfolio:
        holdings_value = sum(qty * current_prices.get(symbol, 0) for symbol, qty in self.holdings.items())
        total_value = self.cash + holdings_value
        win_rate = (self.wins / self.trades * 100) if self.trades > 0 else 0
        
        return Portfolio(
            cash=self.cash,
            holdings=self.holdings.copy(),
            total_value=total_value,
            daily_pnl=self.daily_pnl,
            total_pnl=total_value - self.initial_cash,
            win_rate=win_rate,
            trades=self.trades
        )

# ============================================================================
# API ROUTES (FastAPI-compatible)
# ============================================================================

class TradingSystem:
    def __init__(self):
        self.coordinator = CoordinatorAgent()
        self.market_service = MarketDataService()
        self.portfolio = PortfolioManager()
        self.predictions: List[SwarmPrediction] = []
        self.is_running = False

    async def run_analysis(self) -> Dict:
        market_data = self.market_service.get_market_data()
        predictions = await self.coordinator.run_swarm(market_data)
        self.predictions = predictions
        
        current_prices = {d.symbol: d.price for d in market_data}
        portfolio = self.portfolio.get_portfolio_value(current_prices)
        
        return {
            "predictions": [self._prediction_to_dict(p) for p in predictions],
            "market_data": [self._market_to_dict(d) for d in market_data],
            "portfolio": self._portfolio_to_dict(portfolio),
            "timestamp": datetime.now().isoformat()
        }

    def get_performance_history(self) -> List[Dict]:
        return self.portfolio.trade_history[-50:]

    def _prediction_to_dict(self, p: SwarmPrediction) -> Dict:
        return {
            "symbol": p.symbol,
            "prediction": p.prediction.value,
            "confidence": round(p.confidence, 2),
            "price_target": round(p.price_target, 2),
            "time_horizon": p.time_horizon,
            "agent_votes": {k: round(v, 2) for k, v in p.agent_votes.items()},
            "reasoning": p.consensus_reasoning,
            "risk_score": round(p.risk_score, 2),
            "timestamp": p.timestamp.isoformat()
        }

    def _market_to_dict(self, m: MarketData) -> Dict:
        return {
            "symbol": m.symbol,
            "price": round(m.price, 2),
            "change": round(m.change, 4),
            "change_percent": round(m.change_percent, 2),
            "volume": round(m.volume, 0),
            "high_24h": round(m.high_24h, 2),
            "low_24h": round(m.low_24h, 2),
            "market_cap": round(m.market_cap, 0)
        }

    def _portfolio_to_dict(self, p: Portfolio) -> Dict:
        return {
            "cash": round(p.cash, 2),
            "holdings": {k: round(v, 4) for k, v in p.holdings.items()},
            "total_value": round(p.total_value, 2),
            "daily_pnl": round(p.daily_pnl, 2),
            "total_pnl": round(p.total_pnl, 2),
            "win_rate": round(p.win_rate, 1),
            "trades": p.trades
        }

# Global instance
trading_system = TradingSystem()
