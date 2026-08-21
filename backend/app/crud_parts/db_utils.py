from sqlalchemy import text
from sqlalchemy.orm import Session


def ping_db(db: Session) -> None:
    db.execute(text("SELECT 1"))
