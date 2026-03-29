from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from .discovery import DiscoveryIndex
from .memory import ProjectMemory
from .planner import Planner
from .tool_client import ToolClient, ToolClientError


@dataclass
class Orchestrator:
    tool_client: ToolClient
    discovery: DiscoveryIndex
    planner: Planner
    memory: ProjectMemory

    def _execute_step(
        self,
        action: str,
        args: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        if action == "guide_note":
            return {"ok": True, "result": {"note": args.get("note", "")}}

        if action == "resolve_plugin":
            plugin_type = args.get("type", "instrument")
            resolved = self.discovery.resolve_plugin(args.get("query", ""), plugin_type)
            if not resolved:
                raise ToolClientError(f"could_not_resolve_plugin: {args.get('query', '')}")
            context["resolved_plugin"] = resolved
            return {"ok": True, "result": resolved}

        if action == "resolve_sample":
            resolved = self.discovery.resolve_sample(args.get("query", ""))
            if not resolved:
                raise ToolClientError(f"could_not_resolve_sample: {args.get('query', '')}")
            context["resolved_sample"] = resolved
            return {"ok": True, "result": resolved}

        if action == "resolve_track_reference":
            resolved = self.discovery.resolve_track_reference(args.get("query", ""))
            if not resolved:
                raise ToolClientError(f"could_not_resolve_track: {args.get('query', '')}")
            context["resolved_track"] = resolved
            return {"ok": True, "result": resolved}

        runtime_args = dict(args)
        if action in {"load_sample", "import_audio"} and not runtime_args.get("sample_path"):
            resolved = context.get("resolved_sample")
            if isinstance(resolved, dict):
                runtime_args["sample_path"] = resolved.get("path")

        if action in {"load_instrument", "add_effect"} and not runtime_args.get("plugin") and not runtime_args.get("effect"):
            resolved_plugin = context.get("resolved_plugin")
            if isinstance(resolved_plugin, dict):
                if action == "load_instrument":
                    runtime_args["plugin"] = resolved_plugin.get("canonical_name")
                if action == "add_effect":
                    runtime_args["effect"] = resolved_plugin.get("canonical_name")

        if "track" not in runtime_args:
            resolved_track = context.get("resolved_track")
            if isinstance(resolved_track, dict) and resolved_track.get("name"):
                runtime_args["track"] = resolved_track["name"]

        return self.tool_client.call_tool(action, runtime_args)

    def run(
        self,
        goal: str,
        *,
        project_path: Optional[str] = None,
        confirm_step: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> Dict[str, Any]:
        self.discovery.refresh(project_path=project_path)
        state = self.tool_client.get_project_state()
        preferences = self.memory.load_preferences(project_path)
        plan = self.planner.plan(goal, state=state, discovery=self.discovery, preferences=preferences)

        if plan.mode in {"clarify", "reject"}:
            payload = plan.to_dict()
            self.memory.append_journal_entry(
                project_path,
                {
                    "request": goal,
                    "plan_id": None,
                    "clarification": payload.get("clarification_question"),
                    "steps": [],
                    "resolved_entities": [],
                    "outcome": "clarify" if plan.mode == "clarify" else "reject",
                },
            )
            return payload

        flat_steps = [step for subgoal in plan.subgoals for step in subgoal.steps]
        for step in flat_steps:
            if step.confidence < self.planner.low_confidence_threshold:
                return {
                    "goal": goal,
                    "mode": "clarify",
                    "needs_clarification": True,
                    "clarification_question": (
                        f"I am only {step.confidence:.2f} confident about '{step.action}'. "
                        "Can you confirm this operation?"
                    ),
                }
            if step.risk in {"destructive", "irreversible"}:
                return {
                    "goal": goal,
                    "mode": "clarify",
                    "needs_clarification": True,
                    "clarification_question": (
                        f"'{step.action}' is marked as {step.risk}. Should I proceed?"
                    ),
                }

        step_results: List[Dict[str, Any]] = []
        resolved_entities: List[Dict[str, Any]] = []
        context: Dict[str, Any] = {}

        for subgoal in plan.subgoals:
            for step in subgoal.steps:
                if confirm_step is not None:
                    should_run = confirm_step(
                        {
                            "subgoal": subgoal.id,
                            "subgoal_title": subgoal.title,
                            "action": step.action,
                            "args": step.args,
                            "confidence": step.confidence,
                            "risk": step.risk,
                            "requires_snapshot": step.requires_snapshot,
                        }
                    )
                    if not should_run:
                        aborted = {
                            "goal": goal,
                            "mode": "plan",
                            "needs_clarification": False,
                            "status": "aborted",
                            "aborted_step": step.action,
                            "steps": step_results,
                        }
                        self.memory.append_journal_entry(
                            project_path,
                            {
                                "request": goal,
                                "clarification": None,
                                "plan_id": "p_001",
                                "steps": step_results,
                                "resolved_entities": resolved_entities,
                                "outcome": "aborted",
                            },
                        )
                        return aborted

                snapshot_id = None
                if step.requires_snapshot and step.action not in {"create_snapshot", "rollback_to_snapshot"}:
                    snapshot_resp = self.tool_client.call_tool("create_snapshot", {"label": f"pre_{step.action}"})
                    snapshot_id = snapshot_resp.get("result", {}).get("snapshot_id")

                started = time.monotonic()
                try:
                    response = self._execute_step(step.action, step.args, context)
                    elapsed_ms = int((time.monotonic() - started) * 1000)

                    if step.action.startswith("resolve_"):
                        resolved_entities.append(
                            {
                                "type": step.action,
                                "query": step.args.get("query"),
                                "result": response.get("result", {}),
                            }
                        )

                    state_after = self.tool_client.get_project_state()
                    step_results.append(
                        {
                            "subgoal": subgoal.id,
                            "action": step.action,
                            "args": step.args,
                            "result": response.get("result", {}),
                            "state_delta": response.get("state_delta", {}),
                            "latency_ms": elapsed_ms,
                            "state_after_tempo": state_after.get("tempo"),
                        }
                    )
                except ToolClientError as exc:
                    rollback_result: Dict[str, Any] = {}
                    if snapshot_id:
                        try:
                            rollback_result = self.tool_client.call_tool(
                                "rollback_to_snapshot",
                                {"snapshot_id": snapshot_id},
                            )
                        except ToolClientError:
                            rollback_result = {
                                "ok": False,
                                "error": "rollback_failed",
                            }

                    failure = {
                        "goal": goal,
                        "mode": "plan",
                        "needs_clarification": False,
                        "status": "failed",
                        "failed_step": step.action,
                        "error": str(exc),
                        "rollback": rollback_result,
                        "steps": step_results,
                    }
                    self.memory.append_journal_entry(
                        project_path,
                        {
                            "request": goal,
                            "clarification": None,
                            "plan_id": "p_001",
                            "steps": step_results,
                            "resolved_entities": resolved_entities,
                            "outcome": "failed",
                        },
                    )
                    return failure

        final_state = self.tool_client.get_project_state()
        if resolved_entities:
            last_entity = resolved_entities[-1].get("result", {})
            if isinstance(last_entity, dict):
                pref_key = "last_resolved_asset"
                if "canonical_name" in last_entity:
                    self.memory.update_preferences(project_path, {pref_key: last_entity["canonical_name"]})

        response = {
            "goal": goal,
            "mode": "plan",
            "needs_clarification": False,
            "status": "success",
            "subgoals_executed": len(plan.subgoals),
            "steps": step_results,
            "final_state": {
                "tempo": final_state.get("tempo"),
                "track_count": final_state.get("track_count"),
                "project_file": final_state.get("project_file"),
            },
        }

        self.memory.append_journal_entry(
            project_path,
            {
                "request": goal,
                "clarification": None,
                "plan_id": "p_001",
                "steps": step_results,
                "resolved_entities": resolved_entities,
                "outcome": "success",
            },
        )
        return response
