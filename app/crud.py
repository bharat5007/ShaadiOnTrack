from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud_base import CRUDBase
from app.models import (
    Budget,
    BudgetCategory,
    ServiceCategory,
    Vendor,
    VendorMedia,
    BudgetVendorMap
)


class CRUDWeddingCore(CRUDBase[Budget]):
    """CRUD operations for Wedding Core."""
    
    def get_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Budget]:
        """Get all weddings for a specific user."""
        return db.query(Budget).filter(
            Budget.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def count_by_user(self, db: Session, user_id: int) -> int:
        """Count weddings for a specific user."""
        return db.query(Budget).filter(
            Budget.user_id == user_id
        ).count()
    
    def create_for_user(
        self,
        db: Session,
        user_id: int,
        obj_in: dict
    ) -> Budget:
        """Create a wedding for a specific user."""
        obj_in["user_id"] = user_id
        return self.create(db, obj_in)


class CRUDBudgetCategory(CRUDBase[BudgetCategory]):
    """CRUD operations for Budget Category."""
    
    def get_by_wedding(
        self,
        db: Session,
        wedding_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[BudgetCategory]:
        """Get all budget categories for a specific wedding."""
        return db.query(BudgetCategory).filter(
            BudgetCategory.wedding_id == wedding_id
        ).offset(skip).limit(limit).all()
    
    def count_by_wedding(self, db: Session, wedding_id: int) -> int:
        """Count budget categories for a specific wedding."""
        return db.query(BudgetCategory).filter(
            BudgetCategory.wedding_id == wedding_id
        ).count()


class CRUDServiceCategory(CRUDBase[ServiceCategory]):
    """CRUD operations for Service Category."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[ServiceCategory]:
        """Get service category by name."""
        return db.query(ServiceCategory).filter(
            ServiceCategory.name == name
        ).first()


class CRUDVendor(CRUDBase[Vendor]):
    """CRUD operations for Vendor."""
    
    def get_by_service_category(
        self,
        db: Session,
        service_category_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vendor]:
        """Get all vendors for a specific service category."""
        return db.query(Vendor).filter(
            Vendor.service_categories == service_category_id
        ).offset(skip).limit(limit).all()
    
    def search_by_name(
        self,
        db: Session,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vendor]:
        """Search vendors by name."""
        return db.query(Vendor).filter(
            Vendor.name.ilike(f"%{name}%")
        ).offset(skip).limit(limit).all()


class CRUDVendorMedia(CRUDBase[VendorMedia]):
    """CRUD operations for Vendor Media."""
    
    def get_by_vendor(
        self,
        db: Session,
        vendor_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[VendorMedia]:
        """Get all media for a specific vendor."""
        return db.query(VendorMedia).filter(
            VendorMedia.vendor_id == vendor_id
        ).offset(skip).limit(limit).all()


class CRUDBudgetVendorMap(CRUDBase[BudgetVendorMap]):
    """CRUD operations for Budget Vendor Map."""
    
    def get_by_wedding(
        self,
        db: Session,
        wedding_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[BudgetVendorMap]:
        """Get all budget-vendor mappings for a specific wedding."""
        return db.query(BudgetVendorMap).filter(
            BudgetVendorMap.wedding_id == wedding_id
        ).offset(skip).limit(limit).all()
    
    def get_by_budget(
        self,
        db: Session,
        budget_id: int
    ) -> List[BudgetVendorMap]:
        """Get all vendors mapped to a specific budget."""
        return db.query(BudgetVendorMap).filter(
            BudgetVendorMap.budget_id == budget_id
        ).all()
    
    def get_by_vendor(
        self,
        db: Session,
        vendor_id: int
    ) -> List[BudgetVendorMap]:
        """Get all budgets mapped to a specific vendor."""
        return db.query(BudgetVendorMap).filter(
            BudgetVendorMap.vendor_id == vendor_id
        ).all()


# Create CRUD instances
wedding_core_crud = CRUDWeddingCore(Budget)
budget_category_crud = CRUDBudgetCategory(BudgetCategory)
service_category_crud = CRUDServiceCategory(ServiceCategory)
vendor_crud = CRUDVendor(Vendor)
vendor_media_crud = CRUDVendorMedia(VendorMedia)
budget_vendor_map_crud = CRUDBudgetVendorMap(BudgetVendorMap)