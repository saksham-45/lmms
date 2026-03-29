#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared import DiscoveryIndex, Orchestrator, Planner, ProjectMemory, ToolClient, ToolClientError


def build_orchestrator(sample_roots: list[str]) -> Orchestrator:
    client = ToolClient()
    discovery = DiscoveryIndex(client, sample_roots=sample_roots)
    planner = Planner()
    memory = ProjectMemory()
    return Orchestrator(client, discovery, planner, memory)


def prompt_step_confirmation(step: Dict[str, Any]) -> bool:
    print(
        f"\n[Step] {step.get('subgoal_title', step.get('subgoal'))}: "
        f"{step['action']} args={json.dumps(step.get('args', {}), ensure_ascii=True)} "
        f"(confidence={step.get('confidence', 0):.2f}, risk={step.get('risk', 'safe')})"
    )
    while True:
        choice = input("Run this step? [y/n] ").strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("Please answer y or n.")


def run_once(orchestrator: Orchestrator, goal: str, project_path: str | None, guided: bool = False) -> int:
    try:
        result = orchestrator.run(
            goal,
            project_path=project_path,
            confirm_step=prompt_step_confirmation if guided else None,
        )
    except ToolClientError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="LMMS text agent over typed AgentControl tools")
    parser.add_argument("goal", nargs="*", help="request text")
    parser.add_argument("--project-path", default=None, help="project file path for memory scoping")
    parser.add_argument("--sample-root", action="append", default=[], help="additional sample library root")
    parser.add_argument("--interactive", action="store_true", help="read goals in a loop")
    parser.add_argument(
        "--guided",
        action="store_true",
        help="confirm each planned step before execution",
    )
    args = parser.parse_args()

    orchestrator = build_orchestrator(args.sample_root)

    if args.interactive:
        print("LMMS text agent interactive mode. Type 'exit' to quit.")
        while True:
            try:
                goal = input("lmms> ").strip()
            except EOFError:
                print()
                return 0
            if not goal:
                continue
            if goal.lower() in {"exit", "quit"}:
                return 0
            rc = run_once(orchestrator, goal, args.project_path, guided=args.guided)
            if rc != 0:
                return rc
        
    goal = " ".join(args.goal).strip()
    if not goal:
        parser.error("goal is required unless --interactive is used")
    return run_once(orchestrator, goal, args.project_path, guided=args.guided)


if __name__ == "__main__":
    raise SystemExit(main())
