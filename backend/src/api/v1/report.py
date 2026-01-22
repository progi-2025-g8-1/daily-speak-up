from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID
from pydantic import BaseModel, Field

from ..deps import get_current_user
from ...models import User, Speech, Report
from ...db import get_db

router = APIRouter(prefix="/speech", tags=["Reports"])


class ReportCreateRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


@router.post('/{speech_id}/report', status_code=status.HTTP_201_CREATED)
async def create_report(
    speech_id: UUID,
    report_request: ReportCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a report for a speech."""
    # Check if speech exists
    speech = db.query(Speech).filter(Speech.id == speech_id).first()
    if not speech:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speech not found"
        )

    # Prevent self-reporting
    if speech.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot report your own speech"
        )

    # Check for duplicate report from same user on same speech
    existing_report = db.query(Report).filter(
        Report.speech_id == speech_id,
        Report.reported_by == user.id
    ).first()

    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reported this speech"
        )

    # Create the report
    report = Report(
        speech_id=speech_id,
        reported_by=user.id,
        reason=report_request.reason.strip()
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Report submitted successfully",
            "report_id": str(report.id)
        }
    )
