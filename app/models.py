from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database import Base


class Budget(Base):
    """Wedding core information table."""

    __tablename__ = "budget"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_budget: Mapped[int] = mapped_column(Integer, nullable=False)
    spent_budget: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    budget_categories: Mapped[list["BudgetCategory"]] = relationship(
        "BudgetCategory",
        back_populates="budget",
        cascade="all, delete-orphan",
    )


class BudgetCategory(Base):
    """Budget categories for weddings."""

    __tablename__ = "budget_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    budget_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("budget.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_amt: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_cost: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    budget: Mapped["Budget"] = relationship(
        "Budget", back_populates="budget_categories"
    )


class ServiceCategory(Base):
    """Service categories available."""

    __tablename__ = "service_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_desc: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    vendors: Mapped[list["Vendor"]] = relationship(
        "Vendor", back_populates="service_category"
    )


class Vendor(Base):
    """Vendors information."""

    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone1: Mapped[str] = mapped_column(String(20), nullable=False)
    phone2: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lower_range: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=False, default=0
    )
    upper_range: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=False, default=0
    )
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    service_category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("service_categories.id"),
        index=True,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    service_category: Mapped[Optional["ServiceCategory"]] = relationship(
        "ServiceCategory", back_populates="vendors"
    )
    vendor_media: Mapped[list["VendorMedia"]] = relationship(
        "VendorMedia", back_populates="vendor", cascade="all, delete-orphan"
    )


class VendorMedia(Base):
    """Media associated with vendors."""

    __tablename__ = "vendor_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    media_type: Mapped[str] = mapped_column(String(50), nullable=False)
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="vendor_media")
