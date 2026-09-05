from fastapi import APIRouter,Depends,HTTPException
from app.database import get_db
from app.model import Application,User,Company
from app.auth import  get_current_user,get_priv
from app.schemas   import CompanyResponse,CompanyCreate,ApplicationStatus
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)

@router.post(
    '/',
    response_model=CompanyResponse
)
def get_companies(
    company : CompanyCreate,
    db:Session = Depends(get_db),
    user : User = Depends(get_current_user)
):
    db_company = Company(
        company_name = company.company_name,
        position = company.position,
        ctc = company.ctc,
        location = company.location,
        date_visiting =  company.date_visiting
    )

    try :
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )
    return db_company


@router.get(
    '/',
    response_model=list[CompanyResponse]
)
def get_companies_list(
    db : Session = Depends(get_db),
):
    return db.query(Company).all()


@router.get(
    '/{company_id}',
    response_model=CompanyResponse
)
def get_company_details(
    company_id : int,
    db:Session=Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company Not found"
        )
    return company


@router.delete(
    '/{company_id}'
)
def delete_company(
    company_id : int,
    db: Session= Depends(get_db),
    priv : str=Depends(get_priv)
):
    if(priv != 'admin'):
        raise HTTPException(
            status_code=403,
            detail='forbidden'
        )

    # NOTE: this query used to happen *after* the null-check below, which
    # referenced `company` before it was ever assigned (NameError on every
    # call). Query first, then check.
    company = db.query(Company).filter(
        Company.id==company_id
    ).first()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Not Found"
        )

    application = db.query(Application).filter(
        Application.company_id == company_id,
        Application.status == ApplicationStatus.APPLIED
    ).first()

    if application is not None:
        raise HTTPException(
            status_code=409,
            detail= "Active application exists"
        )


    db.delete(company)
    db.commit()
    return {
        "Message" : "Deleted successfully"
    }
