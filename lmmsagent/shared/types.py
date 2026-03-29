from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

RiskLevel = Literal["safe", "destructive", "irreversible"]
PlannerMode = Literal["plan", "clarify", "reject"]


@dataclass
class PlanStep:
    action: str
    args: Dict[str, Any]
    confidence: float
    risk: RiskLevel
    requires_snapshot: bool


@dataclass
class Subgoal:
    id: str
    title: str
    steps: List[PlanStep] = field(default_factory=list)


@dataclass
class PlannerOutput:
    goal: str
    mode: PlannerMode
    needs_clarification: bool
    clarification_question: Optional[str] = None
    subgoals: List[Subgoal] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "goal": self.goal,
            "mode": self.mode,
            "needs_clarification": self.needs_clarification,
            "subgoals": [
                {
                    "id": subgoal.id,
                    "title": subgoal.title,
                    "steps": [
                        {
                            "action": step.action,
                            "args": step.args,
                            "confidence": round(step.confidence, 3),
                            "risk": step.risk,
                            "requires_snapshot": step.requires_snapshot,
                        }
                        for step in subgoal.steps
                    ],
                }
                for subgoal in self.subgoals
            ],
        }
        if self.clarification_question:
            payload["clarification_question"] = self.clarification_question
        return payload
