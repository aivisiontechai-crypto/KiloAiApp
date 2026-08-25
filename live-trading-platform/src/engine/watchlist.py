from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Watchlist:
    id: str
    name: str
    symbols: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)


class WatchlistManager:
    def __init__(self) -> None:
        self._watchlists: dict[str, Watchlist] = {}
        self._next_id = 1

    def create_watchlist(self, name: str, symbols: list[str] = None) -> Watchlist:
        watchlist = Watchlist(
            id=str(self._next_id),
            name=name,
            symbols=symbols or [],
        )
        self._next_id += 1
        self._watchlists[watchlist.id] = watchlist
        logger.info("Created watchlist: %s", name)
        return watchlist

    def add_symbol(self, watchlist_id: str, symbol: str) -> bool:
        watchlist = self._watchlists.get(watchlist_id)
        if not watchlist:
            return False
        if symbol not in watchlist.symbols:
            watchlist.symbols.append(symbol)
        return True

    def remove_symbol(self, watchlist_id: str, symbol: str) -> bool:
        watchlist = self._watchlists.get(watchlist_id)
        if not watchlist:
            return False
        if symbol in watchlist.symbols:
            watchlist.symbols.remove(symbol)
        return True

    def get_watchlist(self, watchlist_id: str) -> Optional[Watchlist]:
        return self._watchlists.get(watchlist_id)

    def get_all_watchlists(self) -> list[Watchlist]:
        return list(self._watchlists.values())

    def delete_watchlist(self, watchlist_id: str) -> bool:
        if watchlist_id in self._watchlists:
            del self._watchlists[watchlist_id]
            return True
        return False
