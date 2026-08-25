from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class IndicatorResult:
    name: str
    value: Optional[Decimal] = None
    values: Optional[list[Decimal]] = None
    signal: Optional[str] = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TechnicalIndicators:
    @staticmethod
    def sma(prices: list[Decimal], period: int) -> Optional[Decimal]:
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / Decimal(period)

    @staticmethod
    def ema(prices: list[Decimal], period: int) -> Optional[Decimal]:
        if len(prices) < period:
            return None
        multiplier = Decimal("2") / Decimal(period + 1)
        ema = sum(prices[:period]) / Decimal(period)
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema

    @staticmethod
    def wma(prices: list[Decimal], period: int) -> Optional[Decimal]:
        if len(prices) < period:
            return None
        weights = list(range(1, period + 1))
        weighted_sum = sum(p * w for p, w in zip(prices[-period:], weights))
        return weighted_sum / sum(weights)

    @staticmethod
    def dema(prices: list[Decimal], period: int) -> Optional[Decimal]:
        if len(prices) < period:
            return None
        ema1 = TechnicalIndicators.ema(prices, period)
        if ema1 is None:
            return None
        ema2 = TechnicalIndicators.ema(prices + [ema1], period)
        if ema2 is None:
            return None
        return Decimal("2") * ema1 - ema2

    @staticmethod
    def tema(prices: list[Decimal], period: int) -> Optional[Decimal]:
        if len(prices) < period:
            return None
        ema1 = TechnicalIndicators.ema(prices, period)
        if ema1 is None:
            return None
        ema2 = TechnicalIndicators.ema(prices + [ema1], period)
        if ema2 is None:
            return None
        ema3 = TechnicalIndicators.ema(prices + [ema2], period)
        if ema3 is None:
            return None
        return Decimal("3") * ema1 - Decimal("3") * ema2 + ema3

    @staticmethod
    def rsi(prices: list[Decimal], period: int = 14) -> Optional[IndicatorResult]:
        if len(prices) < period + 1:
            return None
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else Decimal("0") for d in deltas]
        losses = [-d if d < 0 else Decimal("0") for d in deltas]
        avg_gain = sum(gains[:period]) / Decimal(period)
        avg_loss = sum(losses[:period]) / Decimal(period)
        for i in range(period, len(deltas)):
            gain = gains[i]
            loss = losses[i]
            avg_gain = (avg_gain * Decimal(period - 1) + gain) / Decimal(period)
            avg_loss = (avg_loss * Decimal(period - 1) + loss) / Decimal(period)
        if avg_loss == 0:
            rsi = Decimal("100")
        else:
            rs = avg_gain / avg_loss
            rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
        signal = "oversold" if rsi < Decimal("30") else "overbought" if rsi > Decimal("70") else "neutral"
        return IndicatorResult(name="RSI", value=rsi, signal=signal, metadata={"period": period})

    @staticmethod
    def macd(prices: list[Decimal], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[IndicatorResult]:
        if len(prices) < slow:
            return None
        ema_fast = TechnicalIndicators.ema(prices, fast)
        ema_slow = TechnicalIndicators.ema(prices, slow)
        if ema_fast is None or ema_slow is None:
            return None
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(prices[slow-1:], signal) if len(prices) >= slow + signal else macd_line
        histogram = macd_line - (signal_line if signal_line else macd_line)
        signal_str = "bullish" if histogram > 0 else "bearish"
        return IndicatorResult(name="MACD", value=macd_line, values=[macd_line, signal_line if signal_line else Decimal("0"), histogram], signal=signal_str, metadata={"fast": fast, "slow": slow, "signal": signal})

    @staticmethod
    def bollinger_bands(prices: list[Decimal], period: int = 20, std_dev: int = 2) -> Optional[IndicatorResult]:
        if len(prices) < period:
            return None
        sma = TechnicalIndicators.sma(prices, period)
        if sma is None:
            return None
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / Decimal(period)
        std = variance.sqrt()
        upper = sma + std_dev * std
        lower = sma - std_dev * std
        signal = "oversold" if prices[-1] < lower else "overbought" if prices[-1] > upper else "neutral"
        return IndicatorResult(name="BollingerBands", value=sma, values=[upper, sma, lower], signal=signal, metadata={"period": period, "std_dev": std_dev})

    @staticmethod
    def atr(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], period: int = 14) -> Optional[IndicatorResult]:
        if len(highs) < period + 1:
            return None
        tr_list = []
        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
            tr_list.append(tr)
        atr = sum(tr_list[-period:]) / Decimal(period)
        return IndicatorResult(name="ATR", value=atr, metadata={"period": period})

    @staticmethod
    def obv(prices: list[Decimal], volumes: list[Decimal]) -> Optional[IndicatorResult]:
        if len(prices) < 2 or len(prices) != len(volumes):
            return None
        obv = Decimal("0")
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                obv += volumes[i]
            elif prices[i] < prices[i-1]:
                obv -= volumes[i]
        return IndicatorResult(name="OBV", value=obv, metadata={"period": len(prices)})

    @staticmethod
    def stochastic(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], k_period: int = 14, d_period: int = 3) -> Optional[IndicatorResult]:
        if len(closes) < k_period:
            return None
        highest_high = max(highs[-k_period:])
        lowest_low = min(lows[-k_period:])
        if highest_high == lowest_low:
            k = Decimal("50")
        else:
            k = ((closes[-1] - lowest_low) / (highest_high - lowest_low)) * Decimal("100")
        signal = "oversold" if k < Decimal("20") else "overbought" if k > Decimal("80") else "neutral"
        return IndicatorResult(name="Stochastic", value=k, signal=signal, metadata={"k_period": k_period, "d_period": d_period})

    @staticmethod
    def williams_r(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], period: int = 14) -> Optional[IndicatorResult]:
        if len(closes) < period:
            return None
        highest_high = max(highs[-period:])
        lowest_low = min(lows[-period:])
        if highest_high == lowest_low:
            wr = Decimal("-50")
        else:
            wr = ((highest_high - closes[-1]) / (highest_high - lowest_low)) * Decimal("-100")
        signal = "oversold" if wr < Decimal("-80") else "overbought" if wr > Decimal("-20") else "neutral"
        return IndicatorResult(name="WilliamsR", value=wr, signal=signal, metadata={"period": period})

    @staticmethod
    def adx(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], period: int = 14) -> Optional[IndicatorResult]:
        if len(closes) < period + 1:
            return None
        tr_list = []
        plus_dm_list = []
        minus_dm_list = []
        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
            plus_dm = highs[i] - highs[i-1]
            minus_dm = lows[i-1] - lows[i]
            plus_dm = plus_dm if plus_dm > minus_dm and plus_dm > 0 else Decimal("0")
            minus_dm = minus_dm if minus_dm > plus_dm and minus_dm > 0 else Decimal("0")
            tr_list.append(tr)
            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)
        atr = sum(tr_list[-period:]) / Decimal(period)
        avg_plus_dm = sum(plus_dm_list[-period:]) / Decimal(period)
        avg_minus_dm = sum(minus_dm_list[-period:]) / Decimal(period)
        if atr == 0:
            return IndicatorResult(name="ADX", value=Decimal("0"), metadata={"period": period})
        plus_di = (avg_plus_dm / atr) * Decimal("100")
        minus_di = (avg_minus_dm / atr) * Decimal("100")
        if plus_di + minus_di == 0:
            dx = Decimal("0")
        else:
            dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * Decimal("100")
        signal = "strong_trend" if dx > Decimal("25") else "weak_trend"
        return IndicatorResult(name="ADX", value=dx, signal=signal, metadata={"period": period, "plus_di": float(plus_di), "minus_di": float(minus_di)})

    @staticmethod
    def ichimoku(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], tenkan: int = 9, kijun: int = 26, senkou: int = 52) -> Optional[IndicatorResult]:
        if len(closes) < senkou:
            return None
        tenkan_sen = (max(highs[-tenkan:]) + min(lows[-tenkan:])) / Decimal("2")
        kijun_sen = (max(highs[-kijun:]) + min(lows[-kijun:])) / Decimal("2")
        senkou_span_a = (tenkan_sen + kijun_sen) / Decimal("2")
        senkou_span_b = (max(highs[-senkou:]) + min(lows[-senkou:])) / Decimal("2")
        signal = "bullish" if closes[-1] > senkou_span_a and closes[-1] > senkou_span_b else "bearish" if closes[-1] < senkou_span_a and closes[-1] < senkou_span_b else "neutral"
        return IndicatorResult(name="Ichimoku", value=tenkan_sen, values=[tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b], signal=signal, metadata={"tenkan": tenkan, "kijun": kijun, "senkou": senkou})

    @staticmethod
    def fibonacci_retracement(high: Decimal, low: Decimal) -> dict[str, Decimal]:
        diff = high - low
        return {
            "0.0": high,
            "0.236": high - diff * Decimal("0.236"),
            "0.382": high - diff * Decimal("0.382"),
            "0.5": high - diff * Decimal("0.5"),
            "0.618": high - diff * Decimal("0.618"),
            "0.786": high - diff * Decimal("0.786"),
            "1.0": low,
        }

    @staticmethod
    def cci(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], period: int = 20) -> Optional[IndicatorResult]:
        if len(closes) < period:
            return None
        typical_prices = [(highs[i] + lows[i] + closes[i]) / Decimal("3") for i in range(len(closes))]
        sma = sum(typical_prices[-period:]) / Decimal(period)
        mean_deviation = sum(abs(tp - sma) for tp in typical_prices[-period:]) / Decimal(period)
        if mean_deviation == 0:
            return IndicatorResult(name="CCI", value=Decimal("0"), metadata={"period": period})
        cci = (typical_prices[-1] - sma) / (Decimal("0.015") * mean_deviation)
        signal = "oversold" if cci < Decimal("-100") else "overbought" if cci > Decimal("100") else "neutral"
        return IndicatorResult(name="CCI", value=cci, signal=signal, metadata={"period": period})

    @staticmethod
    def mfi(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], volumes: list[Decimal], period: int = 14) -> Optional[IndicatorResult]:
        if len(closes) < period + 1 or len(closes) != len(volumes):
            return None
        typical_prices = [(highs[i] + lows[i] + closes[i]) / Decimal("3") for i in range(len(closes))]
        money_flows = []
        for i in range(1, len(closes)):
            tp = typical_prices[i]
            tp_prev = typical_prices[i-1]
            if tp > tp_prev:
                money_flows.append(tp * volumes[i])
            else:
                money_flows.append(-tp * volumes[i])
        positive_flow = sum(mf for mf in money_flows[-period:] if mf > 0)
        negative_flow = abs(sum(mf for mf in money_flows[-period:] if mf < 0))
        if negative_flow == 0:
            mfi = Decimal("100")
        else:
            money_ratio = positive_flow / negative_flow
            mfi = Decimal("100") - (Decimal("100") / (Decimal("1") + money_ratio))
        signal = "oversold" if mfi < Decimal("20") else "overbought" if mfi > Decimal("80") else "neutral"
        return IndicatorResult(name="MFI", value=mfi, signal=signal, metadata={"period": period})

    @staticmethod
    def vwap(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], volumes: list[Decimal]) -> Optional[IndicatorResult]:
        if len(closes) < 1 or len(closes) != len(volumes):
            return None
        typical_prices = [(highs[i] + lows[i] + closes[i]) / Decimal("3") for i in range(len(closes))]
        vwap_num = sum(tp * vol for tp, vol in zip(typical_prices, volumes))
        vwap_den = sum(volumes)
        if vwap_den == 0:
            return None
        vwap = vwap_num / vwap_den
        signal = "bullish" if closes[-1] > vwap else "bearish"
        return IndicatorResult(name="VWAP", value=vwap, signal=signal, metadata={"period": len(closes)})

    @staticmethod
    def supertrend(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], period: int = 10, multiplier: float = 3.0) -> Optional[IndicatorResult]:
        if len(closes) < period + 1:
            return None
        tr_list = []
        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
            tr_list.append(tr)
        atr = sum(tr_list[-period:]) / Decimal(period)
        hl_avg = [(highs[i] + lows[i]) / Decimal("2") for i in range(len(closes))]
        upper_band = hl_avg[-1] + Decimal(str(multiplier)) * atr
        lower_band = hl_avg[-1] - Decimal(str(multiplier)) * atr
        signal = "bullish" if closes[-1] > upper_band else "bearish" if closes[-1] < lower_band else "neutral"
        return IndicatorResult(name="SuperTrend", value=upper_band, values=[upper_band, lower_band], signal=signal, metadata={"period": period, "multiplier": multiplier})

    @staticmethod
    def donchian_channel(highs: list[Decimal], lows: list[Decimal], period: int = 20) -> Optional[IndicatorResult]:
        if len(highs) < period or len(lows) < period:
            return None
        upper = max(highs[-period:])
        lower = min(lows[-period:])
        middle = (upper + lower) / Decimal("2")
        signal = "bullish" if highs[-1] >= upper else "bearish" if lows[-1] <= lower else "neutral"
        return IndicatorResult(name="DonchianChannel", value=middle, values=[upper, middle, lower], signal=signal, metadata={"period": period})

    @staticmethod
    def parabolic_sar(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], af_start: float = 0.02, af_max: float = 0.2) -> Optional[IndicatorResult]:
        if len(closes) < 2:
            return None
        sar = lows[0]
        af = af_start
        uptrend = True
        ep = highs[0]
        for i in range(1, len(closes)):
            if uptrend:
                sar = sar + af * (ep - sar)
                if lows[i] < sar:
                    uptrend = False
                    sar = ep
                    ep = lows[i]
                    af = af_start
                else:
                    if highs[i] > ep:
                        ep = highs[i]
                        af = min(af + af_start, af_max)
            else:
                sar = sar + af * (ep - sar)
                if highs[i] > sar:
                    uptrend = True
                    sar = ep
                    ep = highs[i]
                    af = af_start
                else:
                    if lows[i] < ep:
                        ep = lows[i]
                        af = min(af + af_start, af_max)
        signal = "bullish" if uptrend else "bearish"
        return IndicatorResult(name="ParabolicSAR", value=Decimal(str(sar)), signal=signal, metadata={"af": af, "uptrend": uptrend})

    @staticmethod
    def roc(prices: list[Decimal], period: int = 12) -> Optional[IndicatorResult]:
        if len(prices) < period + 1:
            return None
        roc = (prices[-1] - prices[-period - 1]) / prices[-period - 1] * Decimal("100")
        signal = "bullish" if roc > 0 else "bearish"
        return IndicatorResult(name="ROC", value=roc, signal=signal, metadata={"period": period})

    @staticmethod
    def williams_alligator(highs: list[Decimal], lows: list[Decimal], closes: list[Decimal], jaw: int = 13, teeth: int = 8, lips: int = 5) -> Optional[IndicatorResult]:
        if len(closes) < jaw:
            return None
        jaw_sma = TechnicalIndicators.sma(closes, jaw)
        teeth_sma = TechnicalIndicators.sma(closes, teeth)
        lips_sma = TechnicalIndicators.sma(closes, lips)
        if jaw_sma is None or teeth_sma is None or lips_sma is None:
            return None
        signal = "bullish" if lips_sma > teeth_sma > jaw_sma else "bearish" if lips_sma < teeth_sma < jaw_sma else "neutral"
        return IndicatorResult(name="WilliamsAlligator", value=lips_sma, values=[jaw_sma, teeth_sma, lips_sma], signal=signal, metadata={"jaw": jaw, "teeth": teeth, "lips": lips})
