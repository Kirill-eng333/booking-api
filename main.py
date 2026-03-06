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


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/add_booking", summary="Добавить бронирование")
def add_booking(
    room: str,
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db)
):

    existing_booking = db.query(Booking).filter(
        Booking.room == room,
        Booking.start_time < end_time,
        Booking.end_time > start_time
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=400,
            detail="УЖЕ ЗАНЯТО"
        )

    new_booking = Booking(
        room=room,
        start_time=start_time,
        end_time=end_time
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {
        "message": "записался",
        "id": new_booking.id,
        "room": new_booking.room,
        "start_time": new_booking.start_time,
        "end_time": new_booking.end_time
    }


@app.delete("/delete_booking/{booking_id}", summary="Удалить бронирование")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):

    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    db.delete(booking)
    db.commit()

    return {"message": "удалил бронь"}
