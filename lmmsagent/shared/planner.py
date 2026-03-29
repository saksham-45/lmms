from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .discovery import DiscoveryIndex
from .manual_features import find_feature_areas, render_feature_area, render_feature_catalog
from .manual_playbooks import find_playbook_for_goal, list_playbooks
from .types import PlanStep, PlannerOutput, Subgoal

AMBIGUOUS_TERMS = {
    "harder",
    "texture",
    "vibe",
    "darker",
    "brighter",
    "better",
    "clean up",
    "clean",
    "that plugin",
    "some plugin",
}

CREATIVE_PHRASES = {
    "add energy to drums": "Do you want denser hits, heavier sample choice, or stronger processing?",
    "darken": "Do you want darker timbre (sample/instrument swap) or darker processing (EQ/filter)?",
    "brighten": "Do you want brighter timbre (new source) or brighter processing (EQ/exciter)?",
    "add texture": "Should texture come from ambience effects, layered samples, or a new instrument layer?",
    "hit harder": "Do you want a punchier pattern, a heavier sample, or stronger processing?",
    "muddy": "Should I clean low-mids on bass, drums, or the full mix bus first?",
}


@dataclass
class Planner:
    low_confidence_threshold: float = 0.70

    @staticmethod
    def _norm(text: str) -> str:
        return " ".join(text.lower().split())

    def _find_creative_question(self, goal: str) -> Optional[str]:
        goal_norm = self._norm(goal)
        for phrase, question in CREATIVE_PHRASES.items():
            if phrase in goal_norm:
                return question
        return None

    def _is_ambiguous(self, goal: str) -> bool:
        goal_norm = self._norm(goal)
        return any(term in goal_norm for term in AMBIGUOUS_TERMS)

    def _single_step_plan(self, goal: str, action: str, args: Dict[str, Any], confidence: float) -> PlannerOutput:
        return PlannerOutput(
            goal=goal,
            mode="plan",
            needs_clarification=False,
            subgoals=[
                Subgoal(
                    id="sg1",
                    title="Execute request",
                    steps=[
                        PlanStep(
                            action=action,
                            args=args,
                            confidence=confidence,
                            risk="safe",
                            requires_snapshot=False,
                        )
                    ],
                )
            ],
        )

    def _compose_track_oriented_plan(self, goal: str, track_query: str, operation_step: PlanStep) -> PlannerOutput:
        return PlannerOutput(
            goal=goal,
            mode="plan",
            needs_clarification=False,
            subgoals=[
                Subgoal(
                    id="sg1",
                    title="Resolve target track",
                    steps=[
                        PlanStep(
                            action="resolve_track_reference",
                            args={"query": track_query},
                            confidence=0.86,
                            risk="safe",
                            requires_snapshot=False,
                        )
                    ],
                ),
                Subgoal(id="sg2", title="Apply change", steps=[operation_step]),
            ],
        )

    def plan(
        self,
        goal: str,
        *,
        state: Dict[str, Any],
        discovery: DiscoveryIndex,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> PlannerOutput:
        text = self._norm(goal)
        if not text:
            return PlannerOutput(
                goal=goal,
                mode="reject",
                needs_clarification=False,
                clarification_question="Please provide a request.",
                subgoals=[],
            )

        if any(token in text for token in ["list playbooks", "what is possible", "what can i do", "beginner help"]):
            catalog_lines = [f"- {pb['title']} ({pb['id']})" for pb in list_playbooks()]
            return PlannerOutput(
                goal=goal,
                mode="plan",
                needs_clarification=False,
                subgoals=[
                    Subgoal(
                        id="sg1",
                        title="Beginner playbook catalog",
                        steps=[
                            PlanStep(
                                action="guide_note",
                                args={"note": "Available beginner workflows:\n" + "\n".join(catalog_lines)},
                                confidence=0.99,
                                risk="safe",
                                requires_snapshot=False,
                            )
                        ],
                    )
                ],
            )

        if any(
            token in text
            for token in [
                "manual map",
                "manual feature",
                "full manual",
                "map features",
                "all features",
                "feature map",
            ]
        ):
            matches = find_feature_areas(text, limit=3)
            note = render_feature_catalog()
            if matches:
                detail_chunks = [render_feature_area(area) for area in matches]
                note = note + "\n\n" + "\n\n".join(detail_chunks)
            return PlannerOutput(
                goal=goal,
                mode="plan",
                needs_clarification=False,
                subgoals=[
                    Subgoal(
                        id="sg1",
                        title="Manual feature mapping",
                        steps=[
                            PlanStep(
                                action="guide_note",
                                args={"note": note},
                                confidence=0.99,
                                risk="safe",
                                requires_snapshot=False,
                            )
                        ],
                    )
                ],
            )

        if "manual" in text and ("how to" in text or "where" in text or "map" in text):
            matches = find_feature_areas(text, limit=2)
            if matches:
                note = "\n\n".join([render_feature_area(area) for area in matches])
                return PlannerOutput(
                    goal=goal,
                    mode="plan",
                    needs_clarification=False,
                    subgoals=[
                        Subgoal(
                            id="sg1",
                            title="Manual-guided capability map",
                            steps=[
                                PlanStep(
                                    action="guide_note",
                                    args={"note": note},
                                    confidence=0.97,
                                    risk="safe",
                                    requires_snapshot=False,
                                )
                            ],
                        )
                    ],
                )

        playbook = find_playbook_for_goal(text)
        if playbook is not None:
            subgoals: List[Subgoal] = [
                Subgoal(
                    id="sg0",
                    title="Compatibility check",
                    steps=[
                        PlanStep(
                            action="guide_note",
                            args={
                                "note": (
                                    f"Using manual playbook '{playbook.title}' from '{playbook.manual_section}'. "
                                    + playbook.caution
                                )
                            },
                            confidence=0.99,
                            risk="safe",
                            requires_snapshot=False,
                        )
                    ],
                )
            ]
            for idx, step in enumerate(playbook.steps, start=1):
                subgoals.append(
                    Subgoal(
                        id=f"sg{idx}",
                        title=step.title,
                        steps=[
                            PlanStep(
                                action=step.action,
                                args=step.args,
                                confidence=step.confidence,
                                risk=step.risk,  # type: ignore[arg-type]
                                requires_snapshot=step.requires_snapshot,
                            )
                        ],
                    )
                )
            return PlannerOutput(goal=goal, mode="plan", needs_clarification=False, subgoals=subgoals)

        question = self._find_creative_question(text)
        if question:
            return PlannerOutput(
                goal=goal,
                mode="clarify",
                needs_clarification=True,
                clarification_question=question,
                subgoals=[],
            )

        if self._is_ambiguous(text):
            return PlannerOutput(
                goal=goal,
                mode="clarify",
                needs_clarification=True,
                clarification_question="Can you specify one target track and one exact change to apply?",
                subgoals=[],
            )

        if "tempo" in text or text.startswith("bpm"):
            tempo = next((int(tok) for tok in text.split() if tok.isdigit()), None)
            if tempo is None:
                return PlannerOutput(
                    goal=goal,
                    mode="clarify",
                    needs_clarification=True,
                    clarification_question="What BPM should I set?",
                    subgoals=[],
                )
            return self._single_step_plan(goal, "set_tempo", {"tempo": tempo}, 0.97)

        if text.startswith("show ") or text.startswith("open "):
            target = text.replace("show", "", 1).replace("open", "", 1).strip()
            return self._single_step_plan(goal, "open_tool", {"name": target}, 0.88)

        if "import midi" in text:
            path = goal.split("import midi", 1)[-1].strip()
            return self._single_step_plan(goal, "import_midi", {"path": path}, 0.92)

        if "import hydrogen" in text:
            path = goal.split("import hydrogen", 1)[-1].strip()
            return self._single_step_plan(goal, "import_hydrogen", {"path": path}, 0.92)

        if "import" in text and any(ext in text for ext in [".wav", ".mp3", ".aiff", ".flac", ".ogg"]):
            path = goal.split("import", 1)[-1].strip()
            return self._single_step_plan(goal, "import_audio", {"path": path}, 0.90)

        if text.startswith("create ") and "track" in text:
            track_type = "instrument"
            for candidate in ("sample", "instrument", "automation", "pattern"):
                if candidate in text:
                    track_type = candidate
                    break
            return self._single_step_plan(goal, "create_track", {"type": track_type}, 0.91)

        if "rename track" in text and " to " in text:
            left, right = text.split(" to ", 1)
            old_name = left.replace("rename track", "").strip()
            new_name = right.strip()
            return self._single_step_plan(
                goal,
                "rename_track",
                {"track": old_name, "new_name": new_name},
                0.89,
            )

        if "load instrument" in text:
            plugin_query = text.split("load instrument", 1)[-1].strip()
            resolved = discovery.resolve_plugin(plugin_query, "instrument")
            if not resolved:
                return PlannerOutput(
                    goal=goal,
                    mode="clarify",
                    needs_clarification=True,
                    clarification_question=f"I could not resolve '{plugin_query}'. Which instrument plugin should I load?",
                    subgoals=[],
                )
            return PlannerOutput(
                goal=goal,
                mode="plan",
                needs_clarification=False,
                subgoals=[
                    Subgoal(
                        id="sg1",
                        title="Resolve instrument plugin",
                        steps=[
                            PlanStep(
                                action="resolve_plugin",
                                args={"query": plugin_query, "type": "instrument"},
                                confidence=0.84,
                                risk="safe",
                                requires_snapshot=False,
                            )
                        ],
                    ),
                    Subgoal(
                        id="sg2",
                        title="Load instrument",
                        steps=[
                            PlanStep(
                                action="load_instrument",
                                args={"plugin": resolved["canonical_name"]},
                                confidence=0.9,
                                risk="safe",
                                requires_snapshot=True,
                            )
                        ],
                    ),
                ],
            )

        if "load sample" in text or "add sample" in text:
            sample_query = text.replace("load sample", "").replace("add sample", "").strip()
            resolved = discovery.resolve_sample(sample_query)
            if not resolved:
                return PlannerOutput(
                    goal=goal,
                    mode="clarify",
                    needs_clarification=True,
                    clarification_question=f"I could not resolve sample '{sample_query}'. Which file should I use?",
                    subgoals=[],
                )
            return PlannerOutput(
                goal=goal,
                mode="plan",
                needs_clarification=False,
                subgoals=[
                    Subgoal(
                        id="sg1",
                        title="Resolve sample asset",
                        steps=[
                            PlanStep(
                                action="resolve_sample",
                                args={"query": sample_query},
                                confidence=0.82,
                                risk="safe",
                                requires_snapshot=False,
                            )
                        ],
                    ),
                    Subgoal(
                        id="sg2",
                        title="Load sample",
                        steps=[
                            PlanStep(
                                action="load_sample",
                                args={"sample_path": resolved.get("path", sample_query)},
                                confidence=0.87,
                                risk="safe",
                                requires_snapshot=True,
                            )
                        ],
                    ),
                ],
            )

        if "add effect" in text:
            effect_name = text.split("add effect", 1)[-1].strip()
            resolved = discovery.resolve_plugin(effect_name, "effect")
            if not resolved:
                return PlannerOutput(
                    goal=goal,
                    mode="clarify",
                    needs_clarification=True,
                    clarification_question=f"Which effect plugin should I use for '{effect_name}'?",
                    subgoals=[],
                )
            step = PlanStep(
                action="add_effect",
                args={"effect": resolved["canonical_name"]},
                confidence=0.86,
                risk="safe",
                requires_snapshot=True,
            )
            return PlannerOutput(
                goal=goal,
                mode="plan",
                needs_clarification=False,
                subgoals=[Subgoal(id="sg1", title="Add effect", steps=[step])],
            )

        if "remove effect" in text:
            effect_name = text.split("remove effect", 1)[-1].strip()
            step = PlanStep(
                action="remove_effect",
                args={"effect": effect_name},
                confidence=0.78,
                risk="destructive",
                requires_snapshot=True,
            )
            return PlannerOutput(
                goal=goal,
                mode="plan",
                needs_clarification=False,
                subgoals=[Subgoal(id="sg1", title="Remove effect", steps=[step])],
            )

        if "mute" in text and "track" in text:
            target = text.split("mute", 1)[-1].replace("track", "").strip()
            step = PlanStep(
                action="mute_track",
                args={"track": target, "mute": True},
                confidence=0.83,
                risk="safe",
                requires_snapshot=False,
            )
            return self._compose_track_oriented_plan(goal, target, step)

        if "solo" in text and "track" in text:
            target = text.split("solo", 1)[-1].replace("track", "").strip()
            step = PlanStep(
                action="solo_track",
                args={"track": target, "solo": True},
                confidence=0.83,
                risk="safe",
                requires_snapshot=False,
            )
            return self._compose_track_oriented_plan(goal, target, step)

        if "undo" in text:
            return self._single_step_plan(goal, "undo_last_action", {}, 0.96)

        if "rollback" in text and "snapshot" in text:
            snapshot_id = text.split()[-1]
            return self._single_step_plan(goal, "rollback_to_snapshot", {"snapshot_id": snapshot_id}, 0.91)

        return PlannerOutput(
            goal=goal,
            mode="clarify",
            needs_clarification=True,
            clarification_question="I can execute this with typed LMMS tools. Which exact operation should I run first?",
            subgoals=[],
        )
