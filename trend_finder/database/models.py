"""SQLAlchemy models for collected trend snapshots."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for database models."""


class TrendSnapshot(Base):
    """A point-in-time collection from a single source and country."""

    __tablename__ = "trend_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40), index=True)
    country_code: Mapped[str] = mapped_column(String(2), index=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    items: Mapped[list["TrendRecord"]] = relationship(
        back_populates="snapshot", cascade="all, delete-orphan"
    )


class TrendRecord(Base):
    """A normalized trend item belonging to one stored snapshot."""

    __tablename__ = "trend_records"
    __table_args__ = (UniqueConstraint("snapshot_id", "title", name="uq_snapshot_trend_title"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("trend_snapshots.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    metric: Mapped[str] = mapped_column(String(120), default="")
    metric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    snapshot: Mapped[TrendSnapshot] = relationship(back_populates="items")
