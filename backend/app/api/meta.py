from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database.session import get_db
from ..models import Sector, Category, Department, User
from ..schemas import (SectorCreate, SectorOut, CategoryCreate, CategoryOut,
                       DepartmentCreate, DepartmentOut)
from .deps import require_admin

router = APIRouter(prefix="/api/meta", tags=["catalog"])


@router.get("/bootstrap")
def bootstrap(db: Session = Depends(get_db)):
    """Everything a form needs: sectors with their categories, and departments."""
    sectors = db.query(Sector).order_by(Sector.name).all()
    categories = db.query(Category).order_by(Category.name).all()
    departments = db.query(Department).order_by(Department.name).all()
    return {
        "sectors": [SectorOut.model_validate(s) for s in sectors],
        "categories": [CategoryOut.model_validate(c) for c in categories],
        "departments": [DepartmentOut.model_validate(d) for d in departments],
    }


@router.post("/sectors", response_model=SectorOut, status_code=201)
def create_sector(body: SectorCreate, db: Session = Depends(get_db),
                  admin: User = Depends(require_admin)):
    sector = Sector(name=body.name.strip(), description=body.description)
    db.add(sector)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "A sector with this name already exists.")
    db.refresh(sector)
    return sector


@router.delete("/sectors/{sector_id}", status_code=204)
def delete_sector(sector_id: int, db: Session = Depends(get_db),
                  admin: User = Depends(require_admin)):
    sector = db.get(Sector, sector_id)
    if sector is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sector not found.")
    if sector.issues:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "Sector is used by existing issues and cannot be deleted.")
    db.delete(sector)
    db.commit()
    return None


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(body: CategoryCreate, db: Session = Depends(get_db),
                    admin: User = Depends(require_admin)):
    if db.get(Sector, body.sector_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sector not found.")
    category = Category(sector_id=body.sector_id, name=body.name.strip(),
                        description=body.description)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "This category already exists in that sector.")
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db),
                    admin: User = Depends(require_admin)):
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found.")
    if category.issues:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "Category is used by existing issues and cannot be deleted.")
    db.delete(category)
    db.commit()
    return None


@router.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(body: DepartmentCreate, db: Session = Depends(get_db),
                      admin: User = Depends(require_admin)):
    if body.sector_id is not None and db.get(Sector, body.sector_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sector not found.")
    dept = Department(name=body.name.strip(), sector_id=body.sector_id,
                      contact_email=body.contact_email)
    db.add(dept)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "A department with this name already exists.")
    db.refresh(dept)
    return dept


@router.delete("/departments/{department_id}", status_code=204)
def delete_department(department_id: int, db: Session = Depends(get_db),
                      admin: User = Depends(require_admin)):
    dept = db.get(Department, department_id)
    if dept is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Department not found.")
    if dept.assignments or dept.staff_members:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "Department has staff or assignments and cannot be deleted.")
    db.delete(dept)
    db.commit()
    return None
