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
            recent_audit_events.append({
                "case_id": case.case_id,
                "title": case.title,
                "event_id": event.event_id,
                "action": event.action,
                "actor": event.actor,
                "details": event.details,
                "created_at": event.created_at,
            })

    recent_audit_events = sorted(
        recent_audit_events,
        key=lambda x: x["created_at"],
        reverse=True
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
        }
    }
