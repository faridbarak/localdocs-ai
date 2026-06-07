from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from .models import CaseRecord, CaseStatus, CasePriority, CaseDocument, CaseNote, AuditEvent

class CaseStore:
    def __init__(self):
        self._cases: Dict[str, CaseRecord] = {}

    def create_case(self, title: str, document_id: str, filename: str, document_type: str = "general",
                    description: Optional[str] = None, priority: CasePriority = CasePriority.MEDIUM,
                    owner: Optional[str] = None, tags: Optional[List[str]] = None) -> CaseRecord:
        case_id = str(uuid4())
        now = datetime.utcnow()

        case = CaseRecord(
            case_id=case_id,
            title=title,
            description=description,
            document=CaseDocument(
                document_id=document_id,
                filename=filename,
                document_type=document_type,
            ),
            status=CaseStatus.NEW,
            priority=priority,
            owner=owner,
            tags=tags or [],
            notes=[],
            audit_trail=[
                AuditEvent(
                    event_id=str(uuid4()),
                    action="case_created",
                    actor="system",
                    details={"title": title, "document_type": document_type},
                    created_at=now,
                )
            ],
            created_at=now,
            updated_at=now,
        )
        self._cases[case_id] = case
        return case

    def get_case(self, case_id: str) -> Optional[CaseRecord]:
        return self._cases.get(case_id)

    def list_cases(self) -> List[CaseRecord]:
        return list(self._cases.values())

    def update_status(self, case_id: str, status: CaseStatus, actor: str = "system") -> Optional[CaseRecord]:
        case = self._cases.get(case_id)
        if not case:
            return None
        case.status = status
        case.updated_at = datetime.utcnow()
        case.audit_trail.append(
            AuditEvent(
                event_id=str(uuid4()),
                action="status_updated",
                actor=actor,
                details={"status": status.value},
            )
        )
        return case

    def add_note(self, case_id: str, author: str, message: str) -> Optional[CaseRecord]:
        case = self._cases.get(case_id)
        if not case:
            return None
        case.notes.append(
            CaseNote(
                note_id=str(uuid4()),
                author=author,
                message=message,
            )
        )
        case.updated_at = datetime.utcnow()
        case.audit_trail.append(
            AuditEvent(
                event_id=str(uuid4()),
                action="note_added",
                actor=author,
                details={"message_preview": message[:80]},
            )
        )
        return case

    def assign_owner(self, case_id: str, owner: str, actor: str = "system") -> Optional[CaseRecord]:
        case = self._cases.get(case_id)
        if not case:
            return None
        case.owner = owner
        case.updated_at = datetime.utcnow()
        case.audit_trail.append(
            AuditEvent(
                event_id=str(uuid4()),
                action="owner_assigned",
                actor=actor,
                details={"owner": owner},
            )
        )
        return case
