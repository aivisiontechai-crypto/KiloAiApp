from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    id: str
    title: str
    event_time: datetime
    impact: str
    currency: str
    forecast: Optional[str] = None
    previous: Optional[str] = None
    actual: Optional[str] = None


class EconomicCalendar:
    def __init__(self):
        self._events: list[CalendarEvent] = []
        self._next_id = 1

    def add_event(
        self,
        title: str,
        event_time: datetime,
        impact: str,
        currency: str,
        forecast: Optional[str] = None,
        previous: Optional[str] = None,
        actual: Optional[str] = None,
    ) -> CalendarEvent:
        event = CalendarEvent(
            id=str(self._next_id),
            title=title,
            event_time=event_time,
            impact=impact,
            currency=currency,
            forecast=forecast,
            previous=previous,
            actual=actual,
        )
        self._next_id += 1
        self._events.append(event)
        return event

    def get_upcoming(self, hours: int = 24) -> list[dict]:
        now = datetime.utcnow()
        cutoff = now + timedelta(hours=hours)
        upcoming = [e for e in self._events if now <= e.event_time <= cutoff]
        upcoming.sort(key=lambda e: e.event_time)
        return [self._event_to_dict(e) for e in upcoming]

    def get_events_by_currency(self, currency: str) -> list[dict]:
        events = [e for e in self._events if e.currency == currency]
        events.sort(key=lambda e: e.event_time)
        return [self._event_to_dict(e) for e in events]

    def _event_to_dict(self, event: CalendarEvent) -> dict:
        return {
            "id": event.id,
            "title": event.title,
            "event_time": event.event_time.isoformat(),
            "impact": event.impact,
            "currency": event.currency,
            "forecast": event.forecast,
            "previous": event.previous,
            "actual": event.actual,
        }

    def seed_sample_events(self):
        now = datetime.utcnow()
        self.add_event("Fed Interest Rate Decision", now + timedelta(hours=2), "high", "USD", "5.25%", "5.25%")
        self.add_event("ECB Policy Meeting", now + timedelta(hours=5), "high", "EUR", "4.00%", "4.00%")
        self.add_event("CPI MoM", now + timedelta(hours=8), "high", "USD", "0.3%", "0.2%")
        self.add_event("Unemployment Claims", now + timedelta(hours=12), "medium", "USD", "230K", "228K")
        self.add_event("GDP QoQ", now + timedelta(hours=24), "high", "USD", "2.1%", "2.0%")
