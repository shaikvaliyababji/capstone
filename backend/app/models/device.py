from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    room: Mapped[str] = mapped_column(String(100), nullable=False)

    category: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        default="OFF",
        nullable=False
    )

    # Older tutorials use
    # id = Column(Integer, primary_key=True)
    # We'll use the new style of type annotations for SQLAlchemy 2.0
    # id: Mapped[int] = mapped_column(...)