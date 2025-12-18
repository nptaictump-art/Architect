from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any
from enum import Enum

class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    STAFF = 'STAFF'
    STUDENT = 'STUDENT'

class EquipmentStatus(str, Enum):
    AVAILABLE = 'AVAILABLE'
    IN_USE = 'IN_USE'
    BOOKED = 'BOOKED'
    BROKEN = 'BROKEN'
    MAINTENANCE = 'MAINTENANCE'
    LIQUIDATED = 'LIQUIDATED'

class User(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    department: str
    violationCount: int = 0
    isLocked: bool = False
    avatar: Optional[str] = None
    password: Optional[str] = None

class SOP(BaseModel):
    id: str
    title: str
    type: str
    url: str
    required: bool

class Equipment(BaseModel):
    id: str
    name: str
    code: str
    unit: Optional[str] = None
    origin: Optional[str] = None
    quantity: Optional[int] = 1
    yearOfUse: Optional[int] = None
    depreciation: Optional[str] = None
    receiver: Optional[str] = None
    usingDepartment: Optional[str] = None
    fundingSource: Optional[str] = None
    technicalSpecs: Optional[str] = None
    introduction: Optional[str] = None
    application: Optional[str] = None
    model: str = ""
    serial: str = ""
    provider: str = ""
    receiveDate: str
    price: float = 0
    managerId: str
    location: str
    status: EquipmentStatus
    images: List[str] = []
    notes: str = ""
    sops: List[SOP] = []
    isRestricted: Optional[bool] = False

class Booking(BaseModel):
    id: str
    equipmentId: str
    userId: str
    guestName: Optional[str] = None
    userCode: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    startTime: str
    endTime: str
    purpose: str
    status: Literal['PENDING', 'APPROVED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'REJECTED']
    sopConfirmed: bool = False
    approverName: Optional[str] = None
    rejectionReason: Optional[str] = None
    createdAt: str
    updatedAt: Optional[str] = None

class UsageLog(BaseModel):
    id: str
    bookingId: Optional[str] = None
    equipmentId: str
    userId: str
    guestName: Optional[str] = None
    userCode: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    startTime: str
    endTime: Optional[str] = None
    purpose: str
    preStatus: str = 'GOOD'
    postStatus: Optional[str] = 'GOOD'
    preImages: List[str] = []
    postImages: List[str] = []
    notes: Optional[str] = None
    isCompleted: bool = False

class HomePageConfig(BaseModel):
    appName: str
    logo: Optional[str] = None
    layoutOrder: List[str] = ['HERO', 'INTRO', 'FEATURED', 'LABS']
    heroTitle: str
    heroSubtitle: str
    heroImage: Optional[str] = None
    introTitle: str
    introContent: str
    featuredTitle: str
    featuredEquipmentIds: List[str] = []
    labsTitle: Optional[str] = None
    contactAddress: Optional[str] = None
    contactEmail: Optional[str] = None
    contactHotline: Optional[str] = None
    visitorCount: int = 0

class Lab(BaseModel):
    id: str
    name: str
    description: str
    detailContent: str
    images: List[str]
    locationCode: str