from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "cases.json")


class Case(BaseModel):
    id: int
    title: str
    status: str = "open"


def load_cases_from_file() -> List[Case]:
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Case(**item) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_cases_to_file(cases: List[Case]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([case.model_dump() for case in cases], f, indent=2, ensure_ascii=False)


cases: List[Case] = load_cases_from_file()


@app.get("/cases")
def get_cases():
    return cases


@app.get("/cases/{case_id}")
def get_case(case_id: int):
    for case in cases:
        if case.id == case_id:
            return case
    raise HTTPException(status_code=404, detail="Case not found")


@app.post("/cases")
def create_case(case: Case):
    for existing in cases:
        if existing.id == case.id:
            raise HTTPException(status_code=400, detail="Case ID already exists")

    cases.append(case)
    save_cases_to_file(cases)
    return {"message": "Case created", "case": case}


@app.put("/cases/{case_id}")
def update_case(case_id: int, updated_case: Case):
    for index, case in enumerate(cases):
        if case.id == case_id:
            cases[index] = updated_case
            save_cases_to_file(cases)
            return {"message": "Case updated", "case": updated_case}
    raise HTTPException(status_code=404, detail="Case not found")


@app.delete("/cases/{case_id}")
def delete_case(case_id: int):
    for index, case in enumerate(cases):
        if case.id == case_id:
            removed = cases.pop(index)
            save_cases_to_file(cases)
            return {"message": "Case deleted", "case": removed}
    raise HTTPException(status_code=404, detail="Case not found")
