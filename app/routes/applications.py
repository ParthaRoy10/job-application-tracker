from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import get_db
from app.model import User,Application,Company
from app.auth import get_current_user
from app.schemas import ApplicationCreate,ApplicationResponse,ApplicationUpdate


router = APIRouter(
    prefix="/applications",
    tags=["applications"]
)

@router.post(
    "/",
    response_model=ApplicationResponse
)
def application_create(
    application : ApplicationCreate,
    db: Session=Depends(get_db),
    current_user : User = Depends(get_current_user)
):

    company = db.query(Company).filter(Company.id==application.company_id).first()

    if company is None:
        raise HTTPException(
            status_code=404,
            detail="Company not found"
        )

    db_application = Application(
        user_id = current_user.id,
        company_id = company.id,
        status = application.status,
        date_applied = application.date_applied
    )

    try:
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="You have already applied to this company"
        )

    return db_application



@router.get(
        "/",
        response_model=list[ApplicationResponse]
    )


def get_applications(
    db : Session= Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()


    return applications


@router.get(
    '/{application_id}',
    response_model=ApplicationResponse
)
def get_application_by_id(
    application_id : int,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if application is None:
        raise HTTPException(
            status_code= 404,
            detail= "Application not found"
        )

    return application


@router.patch(
    "/{application_id}",
    response_model=ApplicationResponse
)
def update_application(
    application_id : int,
    application_status : ApplicationUpdate,
    db : Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    db_application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if db_application is None:
        raise HTTPException(
            status_code=404,
            detail= "Application not found "
        )

    db_application.status = application_status.status

    try:
        db.commit()
        db.refresh(db_application)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="database Error"
        )

    return db_application


@router.delete(
    "/{application_id}"
)
def delete_application(
    application_id : int,
    db: Session = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    db_application = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == current_user.id
    ).first()

    if db_application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )
    try:
        db.delete(db_application)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code= 500,
            detail= "Database Error"
        )
    return {
        "message" : "Successfully deleted the Application"
    }