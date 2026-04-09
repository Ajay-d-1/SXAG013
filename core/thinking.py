"""
ThinkingFeed — Structured event system that captures agent reasoning in real-time.
Used by the research loop to emit per-step events for the Live Intelligence Feed UI.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ThinkingEvent:
    timestamp: str
    agent: str
    event_type: str
    title: str
    detail: str
    icon: str
    color: str
    progress: Optional[str] = None


class ThinkingFeed:
    AGENT_CONFIG = {
        "planner":      {"icon": "🧠", "color": "#8b5cf6"},
        "skeptic":      {"icon": "🔍", "color": "#ef4444"},
        "comparator":   {"icon": "⚖️", "color": "#f59e0b"},
        "cartographer": {"icon": "🕸️", "color": "#3b82f6"},
        "archivist":    {"icon": "📚", "color": "#10b981"},
        "loop":         {"icon": "🔄", "color": "#00f2ff"},
    }

    def __init__(self):
        self.events: list[ThinkingEvent] = []
        self._active_agent: str = ""

    def emit(self, agent: str, event_type: str, title: str,
             detail: str, progress: str = None) -> ThinkingEvent:
        cfg = self.AGENT_CONFIG.get(agent, {"icon": "⚙️", "color": "#fff"})
        event = ThinkingEvent(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            agent=agent,
            event_type=event_type,
            title=title,
            detail=detail,
            icon=cfg["icon"],
            color=cfg["color"],
            progress=progress
        )
        self.events.append(event)
        self._active_agent = agent
        return event

    def emit_planner(self, title, detail, progress=None):
        return self.emit("planner", "planning", title, detail, progress)

    def emit_skeptic(self, title, detail, progress=None):
        return self.emit("skeptic", "analysis", title, detail, progress)

    def emit_comparator(self, title, detail, progress=None):
        return self.emit("comparator", "comparison", title, detail, progress)

    def emit_cartographer(self, title, detail, progress=None):
        return self.emit("cartographer", "mapping", title, detail, progress)

    def emit_archivist(self, title, detail, progress=None):
        return self.emit("archivist", "archiving", title, detail, progress)

    def get_events(self) -> list[ThinkingEvent]:
        return self.events

    def get_active_agent(self) -> str:
        return self._active_agent

    def clear(self):
        self.events = []
        self._active_agent = ""
