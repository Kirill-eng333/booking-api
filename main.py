from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, DateTime, String, create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from datetime import datetime


DATABASE_URL = "sqlite:///./booking.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


app = FastAPI(
    title="Система бронирования кабинетов",
    description="API для добавления и удаления бронирований",
    version="1.0"
)

class Бронирование(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    кабинет = Column(String)
    время_начала = Column(DateTime)
    время_окончания = Column(DateTime)


Base.metadata.create_all(bind=engine)


def получить_бд():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/добавить_бронь", summary="Добавить бронирование")
def добавить_бронь(
    кабинет: str,
    время_начала: datetime,
    время_окончания: datetime,
    db: Session = Depends(получить_бд)
):
    новая_бронь = Бронирование(
        кабинет=кабинет,
        время_начала=время_начала,
        время_окончания=время_окончания
    )

    db.add(новая_бронь)
    db.commit()
    db.refresh(новая_бронь)

    return {
        "сообщение": "Бронирование успешно добавлено",
        "данные": новая_бронь
    }



@app.delete("/удалить_бронь/{id}", summary="Удалить бронирование")
def удалить_бронь(id: int, db: Session = Depends(получить_бд)):
    бронь = db.query(Бронирование).filter(Бронирование.id == id).first()

    if not бронь:
        raise HTTPException(
            status_code=404,
            detail="Бронирование не найдено"
        )

    db.delete(бронь)
    db.commit()

    return {"сообщение": "Бронирование успешно удалено"}