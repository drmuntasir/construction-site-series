#!/usr/bin/env python3
"""Construction Site laboratory runner. Scenarios S1-S10 test Vols I-IV and Note I."""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from store import ConstructionSiteStore, Permission


@dataclass
class ScenarioResult:
    sid: str
    title: str
    prediction: str
    held: bool
    reason: str
    snapshot: dict
    volume: str


def _run_days(store: ConstructionSiteStore, days: int, step) -> None:
    for d in range(days):
        step(store, d)
        store.tick()
        store.downselect()


def s1_fluency_factory(seed: int) -> ScenarioResult:
    rng = random.Random(seed)
    store = ConstructionSiteStore("fluency", budget=8, theta=0.4, workspace=0.8)
    items = ["chain_rule", "bayes", "ltp", "holonomy"]

    def step(s: ConstructionSiteStore, d: int) -> None:
        loc = items[d % len(items)]
        s.activate(loc, fluent=True, prediction_error=rng.uniform(0.0, 0.2))
        s.capture(loc, f"reread notes on {loc}")

    _run_days(store, 8, step)
    held = store.stats["captures"] <= 1 and store.stats["tags_set"] <= 2
    return ScenarioResult("S1", "Fluency factory",
        "P3/P5: fluent low-PE exposure tags little and captures less.",
        held, f"tags={store.stats['tags_set']} captures={store.stats['captures']}",
        store.snapshot(), "Vol-I")


def s2_productive_failure_night(seed: int) -> ScenarioResult:
    store = ConstructionSiteStore("failure+night", budget=8, theta=0.35, workspace=0.95)
    episodes = [
        (True, 0.15, "the formula looks familiar"),
        (False, 0.85, "stuck on the boundary term"),
        (False, 0.70, "still cannot close the estimate"),
        (False, 0.60, "instructor key after impasse"),
    ]

    def step(s: ConstructionSiteStore, d: int) -> None:
        fluent, pe, ev = episodes[min(d, len(episodes) - 1)]
        s.activate("boundary_term", fluent=fluent, prediction_error=pe)
        if d >= 2:
            g = s.capture("boundary_term", ev)
            if g:
                s.protect("boundary_term")

    _run_days(store, 5, step)
    g = store.gists.get("boundary_term")
    held = bool(g and g.state == Permission.LOCKED and store.stats["tags_set"] >= 2)
    return ScenarioResult("S2", "Productive failure then capture",
        "P3/P4/P6: high PE tags; later resource captures and locks a gist.",
        held, f"state={g.state.value if g else 'none'} tags={store.stats['tags_set']}",
        store.snapshot(), "Vol-I/II")


def s3_archive_habit(seed: int) -> ScenarioResult:
    store = ConstructionSiteStore("archive", budget=10, theta=0.3, workspace=1.0)
    store.activate("protocol", fluent=False, prediction_error=0.8)
    store.capture("protocol", "first protocol draft alpha beta")
    store.protect("protocol")
    v0 = store.gists["protocol"].format_version
    for i in range(4):
        store.activate(f"note_{i}", fluent=True, prediction_error=0.1)
        store.tick()
    held = (store.gists["protocol"].format_version == v0 and store.stats["reopens"] == 0
            and store.stats["recaptures"] == 0)
    return ScenarioResult("S3", "Archive habit",
        "Note I: retrieve-and-append leaves format_version unchanged.",
        held, f"v={store.gists['protocol'].format_version} reopens={store.stats['reopens']}",
        store.snapshot(), "Note I")


def s4_mismatch_rewrite(seed: int) -> ScenarioResult:
    store = ConstructionSiteStore("rewrite", budget=6, theta=0.35, workspace=1.0)
    store.activate("schema", fluent=False, prediction_error=0.9)
    store.capture("schema", "old schema assumes closed system")
    store.protect("schema")
    opened = store.reopen("schema", "new evidence of open boundary flux leakage", delta=0.8)
    rec = store.recapture("schema", "new evidence of open boundary flux leakage")
    g = store.gists["schema"]
    held = opened and rec is not None and g.format_version == 1 and g.state == Permission.LOCKED
    return ScenarioResult("S4", "Mismatch-gated rewrite",
        "P10/I2/I3/I5: mismatch reopens, spends B, bumps format, re-locks.",
        held, f"opened={opened} v={g.format_version} B_left={store.budget.remaining}",
        store.snapshot(), "Note I / Vol-II")


def s5_idle_reopen_forbidden(seed: int) -> ScenarioResult:
    store = ConstructionSiteStore("idle", budget=5, theta=0.5, workspace=1.0)
    store.activate("lemma", fluent=False, prediction_error=0.7)
    store.capture("lemma", "lemma holds under smoothness")
    store.protect("lemma")
    opened = store.reopen("lemma", "lemma holds under smoothness", delta=0.05)
    held = (not opened) and store.stats["refused_reopen"] == 1 and store.stats["reopens"] == 0
    return ScenarioResult("S5", "Idle reopen refused",
        "I2: retrieval without mismatch does not destablise granite.",
        held, f"opened={opened} refused={store.stats['refused_reopen']}",
        store.snapshot(), "Note I")


def s6_budget_theatre(seed: int) -> ScenarioResult:
    store = ConstructionSiteStore("theatre", budget=1, theta=0.3, workspace=1.0)
    store.activate("stat", fluent=False, prediction_error=0.8)
    store.capture("stat", "first census table")
    store.protect("stat")
    store.reopen("stat", "revised field count contradicts table", delta=0.9)
    rec = store.recapture("stat", "revised field count contradicts table")
    store.tick(); store.tick(); store.tick()
    g = store.gists["stat"]
    held = rec is None and g.state == Permission.EXPIRED and any("I3" in b for b in store.breaches)
    return ScenarioResult("S6", "Budget theatre",
        "P6/P17/I3: a right of correction with B=0 expires the labile gist.",
        held, f"rec={rec is not None} state={g.state.value}",
        store.snapshot(), "Vol-II / Vol-IV")


def s7_constitutional_granite(seed: int) -> ScenarioResult:
    store = ConstructionSiteStore("constitution", budget=5, theta=0.2, workspace=1.0)
    store.activate("article", fluent=False, prediction_error=0.9)
    store.capture("article", "core rights clause")
    store.protect("article")
    store.mark_constitutional("article")
    opened = store.reopen("article", "political weather has changed", delta=0.99)
    held = (not opened) and store.gists["article"].state == Permission.LOCKED
    return ScenarioResult("S7", "Constitutional granite",
        "P18: declared constitutional gist refuses REOPEN even at high mismatch.",
        held, f"opened={opened} state={store.gists['article'].state.value}",
        store.snapshot(), "Vol-IV")


def s8_sampling_rules(seed: int) -> ScenarioResult:
    def fill(sampler: str) -> ConstructionSiteStore:
        s = ConstructionSiteStore(sampler, budget=12, theta=0.4, workspace=1.0, sampler=sampler)
        hard = [("measure_theory", 0.9, "hard sigma algebra impasse")]
        easy = [("slogan", 0.15, "easy slogan reread")]
        for i in range(8):
            loc, pe, ev = (hard if i % 2 == 0 else easy)[0]
            key = f"{loc}_{i}"
            s.activate(key, fluent=False, prediction_error=pe)
            g = s.capture(key, ev)
            if g:
                s.protect(key)
            s.tick()
            s.downselect(occupancy_cap=3)
        return s

    ev, en = fill("evidence"), fill("engagement")
    ev_hard = sum(1 for k, g in ev.gists.items() if g.state != Permission.EXPIRED and "measure" in k)
    en_hard = sum(1 for k, g in en.gists.items() if g.state != Permission.EXPIRED and "measure" in k)
    ev_easy = sum(1 for k, g in ev.gists.items() if g.state != Permission.EXPIRED and "slogan" in k)
    en_easy = sum(1 for k, g in en.gists.items() if g.state != Permission.EXPIRED and "slogan" in k)
    held = (ev_hard > en_hard) or (en_easy > ev_easy)
    return ScenarioResult("S8", "Named sampling rules",
        "P8/P16: engagement and evidence are different DOWNSELECT policies.",
        held, f"evidence hard/easy={ev_hard}/{ev_easy}; engagement hard/easy={en_hard}/{en_easy}",
        {"evidence": ev.snapshot(), "engagement": en.snapshot()}, "Vol-II / Vol-IV")


def s9_workspace_xi(seed: int) -> ScenarioResult:
    def run(xi: float) -> int:
        s = ConstructionSiteStore(f"xi{xi}", budget=20, theta=0.4, workspace=xi)
        captures = 0
        for i in range(16):
            loc = f"tile_{i}"
            s.activate(loc, fluent=False, prediction_error=0.7)
            if s.capture(loc, f"sparse tile {i} pattern"):
                captures += 1
            s.tick()
        return captures

    long_xi, short_xi = run(0.95), run(0.20)
    held = long_xi > short_xi
    return ScenarioResult("S9", "Workspace (correlation length)",
        "P12/P14: short xi (shuttle) captures less than long xi (on-fabric workspace).",
        held, f"long_xi captures={long_xi}; short_xi captures={short_xi}",
        {"long_xi": long_xi, "short_xi": short_xi}, "Vol-III")


def s10_sovereignty_keys(seed: int) -> ScenarioResult:
    local = ConstructionSiteStore("local_office", budget=4, theta=0.3, workspace=1.0)
    local.activate("census", fluent=False, prediction_error=0.8)
    local.capture("census", "district counts")
    local.protect("census")
    owned = local.reopen("census", "field recount disagrees", delta=0.7)
    rec = local.recapture("census", "field recount disagrees")
    foreign = ConstructionSiteStore("hosted_weights", budget=4, theta=0.9, workspace=1.0)
    foreign.activate("census", fluent=False, prediction_error=0.8)
    foreign.capture("census", "district counts")
    foreign.protect("census")
    foreign.mark_constitutional("census")
    hosted_open = foreign.reopen("census", "field recount disagrees", delta=0.7)
    held = owned and rec is not None and not hosted_open
    return ScenarioResult("S10", "Sovereignty is permission not location",
        "P15/P18: same gist, different keys — hosted+constitutional cannot recapture.",
        held, f"local_reopen={owned} local_recapture={rec is not None} hosted_reopen={hosted_open}",
        {"local": local.snapshot(), "hosted": foreign.snapshot()}, "Vol-IV")


SCENARIOS: Dict[str, Callable[[int], ScenarioResult]] = {
    "S1": s1_fluency_factory,
    "S2": s2_productive_failure_night,
    "S3": s3_archive_habit,
    "S4": s4_mismatch_rewrite,
    "S5": s5_idle_reopen_forbidden,
    "S6": s6_budget_theatre,
    "S7": s7_constitutional_granite,
    "S8": s8_sampling_rules,
    "S9": s9_workspace_xi,
    "S10": s10_sovereignty_keys,
}


def run_battery(seed: int, which: Optional[str] = None) -> List[ScenarioResult]:
    random.seed(seed)
    keys = [which] if which else list(SCENARIOS)
    if which and which not in SCENARIOS:
        raise SystemExit(f"Unknown scenario {which}. Choose from {list(SCENARIOS)}")
    return [SCENARIOS[k](seed) for k in keys]


def print_report(results: List[ScenarioResult], verbose: bool = False) -> int:
    width = 78
    print("=" * width)
    print("CONSTRUCTION SITE LABORATORY — series test report")
    print("=" * width)
    held_n = 0
    for r in results:
        mark = "PASS" if r.held else "FAIL"
        if r.held:
            held_n += 1
        print(f"\n[{mark}] {r.sid}  {r.title}   ({r.volume})")
        print(f"  Prediction : {r.prediction}")
        print(f"  Observation: {r.reason}")
        if verbose:
            print("  Snapshot   :", json.dumps(r.snapshot, indent=2)[:1200])
    print("\n" + "-" * width)
    print(f"Battery: {held_n}/{len(results)} predictions held")
    print("A FAIL is a classroom event, not a software crash.")
    print("Ask: did the scenario misspecify the claim, or did the claim miss the mechanism?")
    print("=" * width)
    return 0 if held_n == len(results) else 1


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Construction Site graduate laboratory")
    p.add_argument("--scenario", help="Run one scenario (S1-S10)")
    p.add_argument("--seed", type=int, default=11)
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--list", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.list:
        for k, fn in SCENARIOS.items():
            print(f"{k}: {fn.__name__}")
        return 0
    results = run_battery(args.seed, args.scenario)
    if args.json:
        print(json.dumps([r.__dict__ for r in results], indent=2, default=str))
        return 0
    return print_report(results, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
