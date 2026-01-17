from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


# Wedding Core Schemas
class WeddingCoreBase(BaseModel):
    """Base schema for Wedding."""
    name: str = Field(..., min_length=1, max_length=255)
    total_budget: Optional[int] = None
    spent_budget: Optional[int] = 0


class WeddingCoreCreate(WeddingCoreBase):
    """Schema for creating a wedding."""
    pass


class WeddingCoreUpdate(BaseModel):
    """Schema for updating a wedding."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    total_budget: Optional[int] = None
    spent_budget: Optional[int] = None


class WeddingCoreResponse(WeddingCoreBase):
    """Schema for wedding response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Budget Category Schemas
class BudgetCategoryBase(BaseModel):
    """Base schema for Budget Category."""
    budget_cat: Optional[int] = None
    budget_amt: Optional[int] = None
    actual_cost: Optional[int] = None
    remaining: Optional[int] = None


class BudgetCategoryCreate(BudgetCategoryBase):
    """Schema for creating a budget category."""
    wedding_id: int


class BudgetCategoryUpdate(BaseModel):
    """Schema for updating a budget category."""
    budget_cat: Optional[int] = None
    budget_amt: Optional[int] = None
    actual_cost: Optional[int] = None
    remaining: Optional[int] = None


class BudgetCategoryResponse(BudgetCategoryBase):
    """Schema for budget category response."""
    id: int
    wedding_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Service Category Schemas
class ServiceCategoryBase(BaseModel):
    """Base schema for Service Category."""
    name: str = Field(..., min_length=1, max_length=255)
    short_desc: str
    description: str
    percentage: int = None
    meta: Optional[dict] = None


class ServiceCategoryCreate(ServiceCategoryBase):
    """Schema for creating a service category."""
    pass


class ServiceCategoryUpdate(BaseModel):
    """Schema for updating a service category."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    meta: Optional[str] = None


class ServiceCategoryResponse(ServiceCategoryBase):
    """Schema for service category response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Vendor Schemas
class VendorBase(BaseModel):
    """Base schema for Vendor."""
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    emails: Optional[str] = Field(None, max_length=255)
    meta: Optional[str] = None
    service_categories: Optional[int] = None


class VendorCreate(VendorBase):
    name: str = Field(..., min_length=1, max_length=255)
    phone1: str = Field(max_length=255)
    phone2: Optional[str] = Field(max_length=255)
    address: str = Field(max_length=500)
    email: Optional[str] = Field(max_length=255)
    lower_range: int
    upper_range: int
    meta: Optional[dict] = None
    service_type: str


class VendorUpdate(BaseModel):
    """Schema for updating a vendor."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phones: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    emails: Optional[str] = Field(None, max_length=255)
    metadatas: Optional[str] = None
    service_categories: Optional[int] = None


class VendorResponse(VendorBase):
    """Schema for vendor response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Vendor Media Schemas
class VendorMediaBase(BaseModel):
    """Base schema for Vendor Media."""
    media_type: Optional[str] = Field(None, max_length=50)
    type: Optional[str] = Field(None, max_length=100)


class VendorMediaCreate(VendorMediaBase):
    """Schema for creating vendor media."""
    vendor_id: int


class VendorMediaUpdate(BaseModel):
    """Schema for updating vendor media."""
    media_type: Optional[str] = Field(None, max_length=50)
    type: Optional[str] = Field(None, max_length=100)


class VendorMediaResponse(VendorMediaBase):
    """Schema for vendor media response."""
    id: int
    vendor_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Budget Vendor Map Schemas
class BudgetVendorMapBase(BaseModel):
    """Base schema for Budget Vendor Map."""
    budget_id: int
    vendor_id: int
    wedding_id: int


class BudgetVendorMapCreate(BudgetVendorMapBase):
    """Schema for creating budget vendor map."""
    pass


class BudgetVendorMapUpdate(BaseModel):
    """Schema for updating budget vendor map."""
    budget_id: Optional[int] = None
    vendor_id: Optional[int] = None
    wedding_id: Optional[int] = None


class BudgetVendorMapResponse(BudgetVendorMapBase):
    """Schema for budget vendor map response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Pagination Schema
class PaginatedResponse(BaseModel):
    """Schema for paginated responses."""
    total: int
    page: int
    page_size: int
    items: List[dict]
    
class VendorQueryParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=100)
    service_name: Optional[str] = None
    service_id: Optional[str] = None
    name: Optional[str] = None
    vendor_id: Optional[str] = None
    
class VendorUpdate(BaseModel):
    name: Optional[str]
    id: Optional[int]
    metadata: dict
    
class VendorDeactivate(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None