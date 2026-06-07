from dataclasses import dataclass
from typing import List

@dataclass
class RoutingDecision:
    queue_name: str
    next_step: str
    requires_human_review: bool
    tags: List[str]

class RoutingEngine:
    def route(self, document_type: str, confidence: float, priority: str) -> RoutingDecision:
        requires_human_review = confidence < 0.75 or priority in {"high", "urgent"}

        if document_type == "invoice":
            return RoutingDecision("finance", "verify_amounts", requires_human_review, ["finance", "billing"])
        if document_type == "contract":
            return RoutingDecision("legal", "review_terms", True, ["legal", "contract"])
        if document_type == "hr":
            return RoutingDecision("human_resources", "review_employee_case", requires_human_review, ["hr", "internal"])
        if document_type == "support":
            return RoutingDecision("support", "triage_issue", requires_human_review, ["support", "issue"])
        if document_type == "policy":
            return RoutingDecision("compliance", "review_policy", True, ["policy", "compliance"])

        return RoutingDecision("general", "manual_review", True, ["general"])
