# paste the full corrected cases.py code here
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime

import json
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/cases", tags=["cases"])


class CaseStatus(str, Enum):
    new = "new"
    classified = "classified"
    review_pending = "review_pending"
    approved = "approved"
    rejected = "rejected"
    closed = "closed"


class CasePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    document_type: str
    summary: Optional[str] = None


class AuditEvent(BaseModel):
    event_id: str
    action: str
    actor: str
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class Case(BaseModel):
    case_id: str
    title: str
    description: Optional[str] = None
    document: DocumentInfo
    status: CaseStatus = CaseStatus.new
    priority: CasePriority = CasePriority.medium
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
    audit_trail: List[AuditEvent] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime] = None


class CaseCreateRequest(BaseModel):
    title: str
    document_id: str
    filename: str
    document_text: str
    description: Optional[str] = None
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class NoteCreateRequest(BaseModel):
    note: str


class AssignRequest(BaseModel):
    owner: str


class StatusUpdateRequest(BaseModel):
    status: CaseStatus


class ClassifierResult(BaseModel):
    document_type: str
    confidence: float
    suggested_priority: str
    suggested_queue: str
    reason: str


class RoutingResult(BaseModel):
    queue_name: str
    next_step: str
    requires_human_review: bool
    tags: List[str]


class CaseStore:
    def __init__(self) -> None:
        self._cases: Dict[str, Case] = {}

    def add_case(self, case: Case) -> Case:
        self._cases[case.case_id] = case
        return case

    def get_case(self, case_id: str) -> Optional[Case]:
        return self._cases.get(case_id)

    def list_cases(self) -> List[Case]:
        return list(self._cases.values())

    def update_case(self, case: Case) -> Case:
        self._cases[case.case_id] = case
        return case


store = CaseStore()


def classify_document(text: str, tags: List[str]) -> ClassifierResult:
    lowered = text.lower()
    keywords = ["contract", "agreement", "terms", "conditions"]
    matched = sum(1 for kw in keywords if kw in lowered)

    if matched >= 2:
        return ClassifierResult(
            document_type="contract",
            confidence=0.95,
            suggested_priority="high",
            suggested_queue="legal",
            reason=f"Matched {matched} keywords for contract",
        )

    if "invoice" in lowered or "payment" in lowered:
        return ClassifierResult(
            document_type="invoice",
            confidence=0.90,
            suggested_priority="medium",
            suggested_queue="finance",
            reason="Matched invoice/payment keywords",
        )

    return ClassifierResult(
        document_type="general",
        confidence=0.60,
        suggested_priority="medium",
        suggested_queue="general",
        reason="No strong keyword match",
    )


def route_case(classification: ClassifierResult) -> RoutingResult:
    if classification.suggested_queue == "legal":
        return RoutingResult(
            queue_name="legal",
            next_step="review_terms",
            requires_human_review=True,
            tags=["legal", "contract"],
        )
    if classification.suggested_queue == "finance":
        return RoutingResult(
            queue_name="finance",
            next_step="verify_payment_details",
            requires_human_review=True,
            tags=["finance", "invoice"],
        )
    return RoutingResult(
        queue_name="general",
        next_step="manual_triage",
        requires_human_review=True,
        tags=["general"],
    )


def add_audit_event(case: Case, action: str, actor: str, details: Dict[str, Any]) -> None:
    case.audit_trail.append(
        AuditEvent(
            event_id=str(uuid4()),
            action=action,
            actor=actor,
            details=details,
            created_at=datetime.utcnow(),
        )
    )
    case.updated_at = datetime.utcnow()
class QueueCreateRequest(BaseModel):
    reference: str
    title: str
    document_id: str
    filename: str
    document_text: str
    description: Optional[str] = None
    owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class QueueResponse(BaseModel):
    success: bool
    message: str
    reference: str
    case_id: str
    case: Dict[str, Any]


@router.post("/classify")
async def classify_case(payload: CaseCreateRequest):
    classification = classify_document(payload.document_text, payload.tags)
    routing = route_case(classification)

    case_id = str(uuid4())
    now = datetime.utcnow()

    case = Case(
        case_id=case_id,
        title=payload.title,
        description=payload.description,
        document=DocumentInfo(
            document_id=payload.document_id,
            filename=payload.filename,
            document_type=classification.document_type,
            summary=None,
        ),
        status=CaseStatus.review_pending,
        priority=CasePriority(classification.suggested_priority),
        owner=payload.owner or routing.queue_name,
        tags=list(dict.fromkeys([*routing.tags, *payload.tags])),
        notes=[],
        audit_trail=[],
        created_at=now,
        updated_at=now,
        due_at=None,
    )

    add_audit_event(
        case,
        "case_created",
        "system",
        {"title": payload.title, "document_type": classification.document_type},
    )
    add_audit_event(case, "status_updated", "classifier", {"status": "classified"})
    add_audit_event(case, "owner_assigned", "router", {"owner": case.owner})
    add_audit_event(case, "status_updated", "router", {"status": "review_pending"})

    store.add_case(case)

    return {
        "success": True,
        "classification": classification.model_dump(),
        "routing": routing.model_dump(),
        "case": case.model_dump(),
    }


@router.post("/manual")
async def create_manual_case(payload: CaseCreateRequest):
    now = datetime.utcnow()
    case = Case(
        case_id=str(uuid4()),
        title=payload.title,
        description=payload.description,
        document=DocumentInfo(
            document_id=payload.document_id,
            filename=payload.filename,
            document_type="manual",
            summary=None,
        ),
        status=CaseStatus.new,
        priority=CasePriority.medium,
        owner=payload.owner,
        tags=payload.tags,
        notes=[],
        audit_trail=[],
        created_at=now,
        updated_at=now,
        due_at=None,
    )

@router.post("/queue")
async def create_queue_item(payload: QueueCreateRequest):
    existing = None
    for case in store.list_cases():
        if case.document.document_id == payload.reference or case.case_id == payload.reference:
            existing = case
            break

    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Duplicate reference",
                "reference": payload.reference,
                "case_id": existing.case_id,
            },
        )

    classification = classify_document(payload.document_text, payload.tags)
    routing = route_case(classification)

    now = datetime.utcnow()
    case = Case(
        case_id=str(uuid4()),
        title=payload.title,
        description=payload.description,
        document=DocumentInfo(
            document_id=payload.reference,
            filename=payload.filename,
            document_type=classification.document_type,
            summary=None,
        ),
        status=CaseStatus.review_pending,
        priority=CasePriority(classification.suggested_priority),
        owner=payload.owner or routing.queue_name,
        tags=list(dict.fromkeys([*routing.tags, *payload.tags])),
        notes=[],
        audit_trail=[],
        created_at=now,
        updated_at=now,
        due_at=None,
    )

    add_audit_event(
        case,
        "queue_item_created",
        "system",
        {"reference": payload.reference, "queue_name": routing.queue_name},
    )
    add_audit_event(case, "status_updated", "queue", {"status": "review_pending"})

    store.add_case(case)

    return {
        "success": True,
        "message": "Queue item created",
        "reference": payload.reference,
        "case_id": case.case_id,
        "case": case.model_dump(),
    }


@router.get("/dashboard/summary", summary="Get dashboard summary")
async def dashboard_summary():
    cases = store.list_cases()

    status_counts = {}
    priority_counts = {}

    for case in cases:
        status_key = case.status.value
        priority_key = case.priority.value
        status_counts[status_key] = status_counts.get(status_key, 0) + 1
        priority_counts[priority_key] = priority_counts.get(priority_key, 0) + 1

    recent_cases = sorted(cases, key=lambda x: x.updated_at, reverse=True)[:5]

    recent_audit_events = []
    for case in sorted(cases, key=lambda x: x.updated_at, reverse=True):
        for event in case.audit_trail[-2:]:
            recent_audit_events.append(
                {
                    "case_id": case.case_id,
                    "title": case.title,
                    "event_id": event.event_id,
                    "action": event.action,
                    "actor": event.actor,
                    "details": event.details,
                    "created_at": event.created_at,
                }
            )

    recent_audit_events = sorted(
        recent_audit_events, key=lambda x: x["created_at"], reverse=True
    )[:10]

    return {
        "success": True,
        "summary": {
            "total_cases": len(cases),
            "status_counts": status_counts,
            "priority_counts": priority_counts,
            "recent_cases": [
                {
                    "case_id": case.case_id,
                    "title": case.title,
                    "status": case.status.value,
                    "priority": case.priority.value,
                    "owner": case.owner,
                    "updated_at": case.updated_at,
                }
                for case in recent_cases
            ],
            "recent_audit_events": recent_audit_events,
        },
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    cases = store.list_cases()

    status_counts = {}
    priority_counts = {}

    for case in cases:
        status_counts[case.status.value] = status_counts.get(case.status.value, 0) + 1
        priority_counts[case.priority.value] = priority_counts.get(case.priority.value, 0) + 1

    recent_cases = sorted(cases, key=lambda x: x.updated_at, reverse=True)[:5]

    recent_audit_events = []
    for case in sorted(cases, key=lambda x: x.updated_at, reverse=True):
        for event in case.audit_trail[-2:]:
            recent_audit_events.append((case, event))

    recent_audit_events = recent_audit_events[:10]

    html = f"""
    <html>
    <head>
        <title>Case Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f7f7f7;
                color: #222;
            }}
            .container {{
                max-width: 1100px;
                margin: auto;
            }}
            h1 {{
                margin-bottom: 20px;
            }}
            .cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px;
                margin-bottom: 24px;
            }}
            .card {{
                background: white;
                padding: 16px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}
            .card h3 {{
                margin: 0 0 8px 0;
                font-size: 16px;
                color: #555;
            }}
            .card p {{
                margin: 0;
                font-size: 28px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                margin-bottom: 24px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                border-radius: 12px;
                overflow: hidden;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }}
            th {{
                background: #fafafa;
            }}
            .section {{
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Case Management Dashboard</h1>

            <div class="cards">
                <div class="card">
                    <h3>Total Cases</h3>
                    <p>{len(cases)}</p>
                </div>
                <div class="card">
                    <h3>New</h3>
                    <p>{status_counts.get("new", 0)}</p>
                </div>
                <div class="card">
                    <h3>Review Pending</h3>
                    <p>{status_counts.get("review_pending", 0)}</p>
                </div>
                <div class="card">
                    <h3>High Priority</h3>
                    <p>{priority_counts.get("high", 0)}</p>
                </div>
                <div class="card">
                    <h3>Urgent</h3>
                    <p>{priority_counts.get("urgent", 0)}</p>
                </div>
            </div>

            <div class="section">
                <h2>Recent Cases</h2>
                <table>
                    <tr>
                        <th>Case ID</th>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Priority</th>
                        <th>Owner</th>
                    </tr>
                    {''.join(f"<tr><td>{c.case_id}</td><td>{c.title}</td><td>{c.status.value}</td><td>{c.priority.value}</td><td>{c.owner or ''}</td></tr>" for c in recent_cases)}
                </table>
            </div>

            <div class="section">
                <h2>Recent Audit Events</h2>
                <table>
                    <tr>
                        <th>Case</th>
                        <th>Action</th>
                        <th>Actor</th>
                        <th>Time</th>
                    </tr>
                    {''.join(f"<tr><td>{c.title}</td><td>{e.action}</td><td>{e.actor}</td><td>{e.created_at}</td></tr>" for c, e in recent_audit_events)}
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/")
async def list_cases(
    status: Optional[CaseStatus] = None,
    priority: Optional[CasePriority] = None,
    owner: Optional[str] = None,
    tag: Optional[str] = None,
):
    cases = store.list_cases()

    if status is not None:
        cases = [c for c in cases if c.status == status]
    if priority is not None:
        cases = [c for c in cases if c.priority == priority]
    if owner is not None:
        cases = [c for c in cases if c.owner == owner]
    if tag is not None:
        cases = [c for c in cases if tag in c.tags]

    return {
        "success": True,
        "count": len(cases),
        "cases": [case.model_dump() for case in cases],
    }


@router.get("/{case_id}")
async def get_case(case_id: str):
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"success": True, "case": case.model_dump()}


@router.get("/{case_id}/audit")
async def get_case_audit(case_id: str):
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "success": True,
        "case_id": case.case_id,
        "title": case.title,
        "audit_trail": [event.model_dump() for event in case.audit_trail],
        "count": len(case.audit_trail),
    }


@router.post("/{case_id}/notes")
async def add_note(case_id: str, payload: NoteCreateRequest):
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.notes.append(payload.note)
    add_audit_event(case, "note_added", "user", {"note": payload.note})
    store.update_case(case)
    return {"success": True, "case": case.model_dump()}


@router.post("/{case_id}/assign")
async def assign_case(case_id: str, payload: AssignRequest):
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.owner = payload.owner
    add_audit_event(case, "owner_assigned", "user", {"owner": payload.owner})
    store.update_case(case)
    return {"success": True, "case": case.model_dump()}


@router.patch("/{case_id}/status")
async def update_status(case_id: str, payload: StatusUpdateRequest):
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = payload.status
    add_audit_event(case, "status_updated", "user", {"status": payload.status.value})
    store.update_case(case)
    return {"success": True, "case": case.model_dump()}
