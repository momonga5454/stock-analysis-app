from fastapi import APIRouter, Depends
from db import get_db

router = APIRouter(prefix="/api/tags", tags=["tags"])


# ✅ タグ作成
@router.post("/")
def create_tag(name: str, db = Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
    db.commit()

    return {"status": "ok"}


# ✅ 一覧
@router.get("/")
def get_tags(db = Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM tags")
    return cursor.fetchall()

@router.post("/assign")
def assign_tag(
    trade_id: int,
    tag_id: int,
    db = Depends(get_db)
):
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO taggings (trade_id, tag_id)
    VALUES (?, ?)
    """, (trade_id, tag_id))

    db.commit()

    return {"status": "ok"}
