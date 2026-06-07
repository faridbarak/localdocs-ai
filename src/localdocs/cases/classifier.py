from dataclasses import dataclass

@dataclass
class ClassificationResult:
    document_type: str
    confidence: float
    suggested_priority: str
    suggested_queue: str
    reason: str

class DocumentClassifier:
    def __init__(self):
        self.rules = {
            "invoice": {"keywords": ["invoice", "amount due", "payment terms", "billing"], "priority": "high", "queue": "finance"},
            "contract": {"keywords": ["agreement", "contract", "party", "terms and conditions"], "priority": "high", "queue": "legal"},
            "hr": {"keywords": ["employee", "salary", "benefits", "onboarding", "hr"], "priority": "medium", "queue": "human_resources"},
            "support": {"keywords": ["issue", "error", "bug", "problem", "support"], "priority": "high", "queue": "support"},
            "policy": {"keywords": ["policy", "procedure", "compliance", "guideline"], "priority": "medium", "queue": "compliance"},
            "general": {"keywords": [], "priority": "medium", "queue": "general"},
        }

    def classify(self, text: str, filename: str = "") -> ClassificationResult:
        content = f"{filename} {text}".lower()
        best_type = "general"
        best_score = 0
        best_rule = self.rules["general"]

        for doc_type, rule in self.rules.items():
            if doc_type == "general":
                continue
            score = sum(1 for kw in rule["keywords"] if kw in content)
            if score > best_score:
                best_score = score
                best_type = doc_type
                best_rule = rule

        confidence = 0.45 if best_type == "general" else min(0.95, 0.55 + (best_score * 0.15))
        reason = f"Matched {best_score} keywords for {best_type}" if best_type != "general" else "No strong keyword match found"

        return ClassificationResult(
            document_type=best_type,
            confidence=confidence,
            suggested_priority=best_rule["priority"],
            suggested_queue=best_rule["queue"],
            reason=reason,
        )
