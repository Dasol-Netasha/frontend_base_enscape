from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud_parts.db_utils import ping_db
from app.database import get_db
from app.schemas import HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
def health_check(db: Session = Depends(get_db)) -> HealthCheck:
    ping_db(db)
    return HealthCheck(status="ok")


@router.get("/categories/{category_slug}/columns", response_model=list[schemas.CategoryColumnRead])
def list_category_columns(
    category_slug: str,
    camera_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[schemas.CategoryColumnRead]:
    return crud.get_category_columns(db, category_slug=category_slug, camera_type=camera_type)


@router.get("/categories/{category_slug}/table", response_model=schemas.CategoryTableDataRead)
def get_category_table(
    category_slug: str,
    camera_type: str | None = Query(default=None),
    filters: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> schemas.CategoryTableDataRead:
    return crud.get_category_table_data(db, category_slug=category_slug, camera_type=camera_type, filters=filters)


@router.patch("/categories/{category_slug}/columns/main-keys", status_code=204)
def update_main_keys(
    category_slug: str,
    payload: schemas.CategoryColumnMainKeysUpdate,
    camera_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> None:
    crud.update_category_column_main_keys(
        db,
        category_slug=category_slug,
        main_keys=payload.main_keys,
        camera_type=camera_type,
    )
