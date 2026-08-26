from sqlalchemy import select
from app.database.connection import engine
from app.database.base import Base
from app.database.session import SessionLocal
from app.models.device import Device

# Safe module-level imports for when these are implemented later
import app.models.user
import app.models.command
import app.models.log


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        stmt = select(Device)
        existing = db.scalars(stmt).first()
        if not existing:
            default_devices = [
                Device(name="bedroom_light", room="bedroom", category="light", status="OFF"),
                Device(name="living_room_light", room="living_room", category="light", status="OFF"),
                Device(name="kitchen_light", room="kitchen", category="light", status="OFF"),
                Device(name="fan", room="living_room", category="fan", status="OFF"),
                Device(name="ac", room="bedroom", category="ac", status="OFF"),
                Device(name="door", room="entrance", category="security", status="LOCKED"),
                Device(name="curtains", room="living_room", category="comfort", status="CLOSED"),
            ]
            db.add_all(default_devices)
            db.commit()
            print("Database seeded with default devices.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()