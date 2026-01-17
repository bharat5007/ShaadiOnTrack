from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Budget(Base):
    """Wedding core information table."""
    __tablename__ = "budget"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    total_budget = Column(Integer)
    spent_budget = Column(Integer, default=0)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    budget_categories = relationship(
        "BudgetCategory",
        back_populates="budget",
        cascade="all, delete-orphan",
    )
    budget_vendor_maps = relationship(
        "BudgetVendorMap",
        back_populates="budget",
        cascade="all, delete-orphan",
    )


class BudgetCategory(Base):
    """Budget categories for weddings."""
    __tablename__ = "budget_categories"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budget.id", ondelete="CASCADE"), nullable=False, index=True)
    budget_cat = Column(Integer)
    budget_amt = Column(Integer)
    actual_cost = Column(Integer)
    remaining = Column(Integer)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    budget = relationship("Budget", back_populates="budget_categories")
    budget_vendor_maps = relationship(
        "BudgetVendorMap",
        back_populates="budget_category",
        cascade="all, delete-orphan",
    )


class ServiceCategory(Base):
    """Service categories available."""
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendors = relationship("Vendor", back_populates="service_category")


class Vendor(Base):
    """Vendors information."""
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phones = Column(String(255))
    address = Column(String(500))
    emails = Column(String(255))
    meta = Column(JSON)
    is_active = Column(Boolean, default=True)
    service_categories = Column(Integer, ForeignKey("service_categories.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service_category = relationship("ServiceCategory", back_populates="vendors")
    vendor_media = relationship("VendorMedia", back_populates="vendor", cascade="all, delete-orphan")
    budget_vendor_maps = relationship("BudgetVendorMap", back_populates="vendor", cascade="all, delete-orphan")


class VendorMedia(Base):
    """Media associated with vendors."""
    __tablename__ = "vendor_media"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(String(50))
    type = Column(String(100))
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="vendor_media")


class BudgetVendorMap(Base):
    """Mapping between budgets and vendors."""
    __tablename__ = "budget_vendor_map"

    id = Column(Integer, primary_key=True, index=True)

    budget_category_id = Column(
        Integer,
        ForeignKey("budget_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vendor_id = Column(
        Integer,
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    budget_id = Column(
        Integer,
        ForeignKey("budget.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    meta = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    budget_category = relationship("BudgetCategory", back_populates="budget_vendor_maps")
    vendor = relationship("Vendor", back_populates="budget_vendor_maps")
    budget = relationship("Budget", back_populates="budget_vendor_maps")
