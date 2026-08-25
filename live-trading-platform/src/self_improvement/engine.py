from __future__ import annotations

import copy
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ImprovementAction:
    timestamp: datetime
    strategy: str
    action: str
    parameters: dict
    reason: str
    metric: str
    version: int = 1


class SelfImprovementEngine:
    def __init__(self, evaluation_interval_hours: int = 24, health_monitor=None) -> None:
        self.evaluation_interval_hours = evaluation_interval_hours
        self.health_monitor = health_monitor
        self._strategies: dict[str, Any] = {}
        self._history: list[ImprovementAction] = []
        self._versions: dict[str, list[dict]] = {}

    def register_strategy(self, strategy) -> None:
        self._strategies[strategy.name] = strategy
        self._versions[strategy.name] = [copy.deepcopy(strategy.parameters)]

    def evaluate_and_improve(self, metrics: dict) -> None:
        for name, strategy in self._strategies.items():
            if self.health_monitor and not self.health_monitor._is_healthy(name):
                continue
            metric = metrics.get(name, {})
            pnl = metric.get("pnl", 0.0)
            if pnl < 0:
                old_params = copy.deepcopy(strategy.parameters)
                for key in strategy.parameters:
                    strategy.parameters[key] = strategy.parameters[key] * 0.9
                self._log_action(name, "adjust", strategy.parameters, "negative_pnl", "pnl")
                self._versions[name].append(copy.deepcopy(strategy.parameters))

    def auto_rollback_unhealthy(self) -> None:
        if not self.health_monitor:
            return
        for name in list(self._strategies.keys()):
            if not self.health_monitor._is_healthy(name) and len(self._versions.get(name, [])) > 1:
                self.rollback(name, len(self._versions[name]) - 2)
                self.health_monitor.reset(name, 100000.0)
                self._log_action(name, "rollback", self._strategies[name].parameters, "unhealthy", "health")

    def deploy_parameters(self, name: str, parameters: dict) -> bool:
        strategy = self._strategies.get(name)
        if not strategy:
            return False
        old_params = copy.deepcopy(strategy.parameters)
        strategy.parameters.update(parameters)
        self._versions[name].append(copy.deepcopy(strategy.parameters))
        self._log_action(name, "deploy", strategy.parameters, "manual", "manual")
        return True

    def rollback(self, name: str, version: int) -> bool:
        strategy = self._strategies.get(name)
        versions = self._versions.get(name, [])
        if not strategy or version < 0 or version >= len(versions):
            return False
        strategy.parameters = copy.deepcopy(versions[version])
        self._log_action(name, "rollback", strategy.parameters, "rollback", "version")
        return True

    def get_history(self) -> list[dict]:
        return [
            {
                "timestamp": a.timestamp.isoformat(),
                "strategy": a.strategy,
                "action": a.action,
                "parameters": a.parameters,
                "reason": a.reason,
                "metric": a.metric,
                "version": a.version,
            }
            for a in self._history
        ]

    def _log_action(self, strategy: str, action: str, parameters: dict, reason: str, metric: str) -> None:
        self._history.append(ImprovementAction(
            timestamp=datetime.utcnow(),
            strategy=strategy,
            action=action,
            parameters=parameters,
            reason=reason,
            metric=metric,
            version=len(self._history) + 1,
        ))
