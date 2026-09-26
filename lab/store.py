#!/usr/bin/env python3
"""Construction Site laboratory store: TagChart, Gist, WriteBudget, I1-I5 operations."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class Permission(str, Enum):
    LABILE = "labile"
    LOCKED = "locked"
    EXPIRED = "expired"


class ContractBreach(Exception):
    """Raised when an implementation would violate I1-I5."""


@dataclass
class TagChart:
    id: str
    location: str
    lifetime: int
    permission: Permission = Permission.LABILE
    strength: float = 0.0
    prediction_error: float = 0.0
    born_at: int = 0


@dataclass
class Gist:
    id: str
    payload: str
    format_version: int = 0
    protection: float = 0.0
    state: Permission = Permission.LABILE
    constitutional: bool = False
    parent_refs: List[str] = field(default_factory=list)
    born_at: int = 0
    window_left: int = 0
    prediction_error: float = 0.0


@dataclass
class WriteBudget:
    remaining: float
    unit: str = "writes"

    def spend(self, cost: float = 1.0) -> None:
        if self.remaining < cost:
            raise ContractBreach("I3: recapture/capture spends B; B exhausted")
        self.remaining -= cost


@dataclass
class MismatchReport:
    query: str
    gist_id: str
    delta: float
    theta: float
    evidence: str

    @property
    def exceeds(self) -> bool:
        return self.delta > self.theta


@dataclass
class Event:
    t: int
    op: str
    detail: str


class ConstructionSiteStore:
    """Minimum learner that can obey or breach I1-I5."""

    def __init__(self, name: str, budget: float, theta: float, tag_lifetime: int = 3,
                 recapture_window: int = 2, workspace: float = 1.0, sampler: str = "evidence") -> None:
        self.name = name
        self.budget = WriteBudget(budget)
        self.theta = theta
        self.tag_lifetime = tag_lifetime
        self.recapture_window = recapture_window
        self.workspace = max(0.05, min(1.0, workspace))
        self.sampler = sampler
        self.t = 0
        self.tags: Dict[str, TagChart] = {}
        self.gists: Dict[str, Gist] = {}
        self.log: List[Event] = []
        self.breaches: List[str] = []
        self.stats = {
            "activations": 0, "tags_set": 0, "captures": 0, "protects": 0,
            "reopens": 0, "recaptures": 0, "expires": 0, "downselects": 0,
            "refused_reopen": 0, "format_bumps": 0, "budget_spent": 0.0,
        }

    def _note(self, op: str, detail: str) -> None:
        self.log.append(Event(self.t, op, detail))

    def tick(self) -> None:
        self.t += 1
        for tag in list(self.tags.values()):
            if tag.permission == Permission.LABILE and self.t - tag.born_at >= tag.lifetime:
                tag.permission = Permission.EXPIRED
                self.stats["expires"] += 1
                self._note("EXPIRE", f"tag {tag.id}")
        for gist in list(self.gists.values()):
            if gist.state == Permission.LABILE and gist.window_left <= 0:
                gist.state = Permission.EXPIRED
                self.stats["expires"] += 1
                self._note("EXPIRE", f"gist {gist.id}")
            elif gist.state == Permission.LABILE:
                gist.window_left -= 1

    def address(self, query: str) -> Tuple[str, Optional[object]]:
        if query in self.gists and self.gists[query].state != Permission.EXPIRED:
            return "gist", self.gists[query]
        if query in self.tags and self.tags[query].permission != Permission.EXPIRED:
            return "tag", self.tags[query]
        return "miss", None

    def activate(self, location: str, fluent: bool, prediction_error: float) -> Optional[TagChart]:
        self.stats["activations"] += 1
        if fluent and prediction_error < 0.25:
            self._note("ACTIVATE", f"{location} fluent, no tag")
            return None
        tag = TagChart(id=location, location=location, lifetime=self.tag_lifetime,
                       strength=prediction_error * self.workspace,
                       prediction_error=prediction_error, born_at=self.t)
        self.tags[location] = tag
        self.stats["tags_set"] += 1
        self._note("TAG", f"{location} pe={prediction_error:.2f}")
        return tag

    def capture(self, location: str, evidence: str) -> Optional[Gist]:
        kind, obj = self.address(location)
        if kind != "tag":
            self._note("CAPTURE_FAIL", f"no live tag at {location}")
            return None
        tag: TagChart = obj  # type: ignore
        if tag.permission != Permission.LABILE:
            return None
        if random.random() > self.workspace:
            self._note("CAPTURE_MISS", f"window miss at {location} (short xi)")
            return None
        try:
            self.budget.spend(1.0)
        except ContractBreach as exc:
            self.breaches.append(str(exc))
            self._note("CAPTURE_FAIL", "B exhausted")
            return None
        self.stats["budget_spent"] += 1.0
        gist = Gist(id=location, payload=self._gistify(evidence, version=0), format_version=0,
                    parent_refs=[tag.id], born_at=self.t, window_left=self.recapture_window,
                    state=Permission.LABILE, prediction_error=tag.prediction_error)
        self.gists[location] = gist
        tag.permission = Permission.EXPIRED
        self.stats["captures"] += 1
        self._note("CAPTURE", f"{location} -> gist v0")
        return gist

    def protect(self, location: str, kappa: float = 1.0) -> None:
        gist = self.gists.get(location)
        if not gist or gist.state == Permission.EXPIRED:
            return
        gist.state = Permission.LOCKED
        gist.protection = kappa
        self.stats["protects"] += 1
        self._note("PROTECT", f"{location} kappa={kappa}")

    def reopen(self, location: str, evidence: str, delta: Optional[float] = None) -> bool:
        gist = self.gists.get(location)
        if not gist or gist.state == Permission.EXPIRED:
            return False
        if gist.constitutional:
            self.stats["refused_reopen"] += 1
            self._note("REOPEN_REFUSED", f"{location} constitutional (P18)")
            return False
        if gist.state != Permission.LOCKED:
            self.breaches.append("I2: REOPEN requires locked gist + mismatch")
            self._note("BREACH", "I2 unearned reopen")
            return False
        if delta is None:
            delta = self._mismatch(gist.payload, evidence)
        report = MismatchReport(location, location, delta, self.theta, evidence)
        if not report.exceeds:
            self.stats["refused_reopen"] += 1
            self._note("REOPEN_REFUSED", f"{location} d={delta:.2f} <= theta={self.theta}")
            return False
        gist.state = Permission.LABILE
        gist.protection *= 0.5
        gist.window_left = self.recapture_window
        self.stats["reopens"] += 1
        self._note("REOPEN", f"{location} d={delta:.2f}")
        return True

    def recapture(self, location: str, evidence: str) -> Optional[Gist]:
        gist = self.gists.get(location)
        if not gist or gist.state != Permission.LABILE:
            self._note("RECAPTURE_FAIL", f"{location} not labile")
            return None
        new_payload = self._gistify(evidence, version=gist.format_version + 1)
        if new_payload == gist.payload:
            self.breaches.append("I5: copy is not a consolidation")
            self._note("BREACH", "I5 byte-identical recapture")
            return None
        try:
            self.budget.spend(1.0)
        except ContractBreach as exc:
            self.breaches.append(str(exc))
            self._note("RECAPTURE_FAIL", "B exhausted; gist will expire")
            return None
        self.stats["budget_spent"] += 1.0
        gist.payload = new_payload
        gist.format_version += 1
        gist.parent_refs.append(f"ev@{self.t}")
        self.stats["recaptures"] += 1
        self.stats["format_bumps"] += 1
        self._note("RECAPTURE", f"{location} -> v{gist.format_version}")
        self.protect(location)
        return gist

    def downselect(self, occupancy_cap: int = 6) -> None:
        live = [g for g in self.gists.values() if g.state != Permission.EXPIRED]
        if len(live) <= occupancy_cap:
            return
        if self.sampler == "engagement":
            live.sort(key=lambda g: -self._pe_of(g))
        else:
            live.sort(key=lambda g: (len(g.parent_refs), g.format_version, self._pe_of(g)))
        victim = live[0]
        if victim.constitutional:
            return
        victim.state = Permission.EXPIRED
        self.stats["downselects"] += 1
        self._note("DOWNSELECT", f"{victim.id} via {self.sampler}")

    def mark_constitutional(self, location: str) -> None:
        gist = self.gists.get(location)
        if gist:
            gist.constitutional = True
            self._note("CONSTITUTIONAL", location)

    def _gistify(self, evidence: str, version: int) -> str:
        tokens = [tok for tok in evidence.lower().replace(",", " ").split() if tok]
        core = " ".join(sorted(set(tokens))[:6])
        return f"GIST:v{version}:{core}"

    def _mismatch(self, payload: str, evidence: str) -> float:
        a = set(payload.split(":"))
        b = set(evidence.lower().split())
        if not b:
            return 0.0
        return 1.0 - (len(a & b) / max(1, len(b)))

    def _pe_of(self, gist: Gist) -> float:
        return gist.prediction_error

    def snapshot(self) -> dict:
        live_gists = [g for g in self.gists.values() if g.state != Permission.EXPIRED]
        return {
            "name": self.name,
            "t": self.t,
            "budget_left": round(self.budget.remaining, 2),
            "theta": self.theta,
            "workspace": self.workspace,
            "sampler": self.sampler,
            "live_gists": len(live_gists),
            "locked": sum(1 for g in live_gists if g.state == Permission.LOCKED),
            "max_version": max((g.format_version for g in live_gists), default=0),
            "stats": dict(self.stats),
            "breaches": list(self.breaches),
        }
