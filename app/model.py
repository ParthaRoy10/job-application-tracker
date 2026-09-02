from sqlalchemy import (Numeric, DateTime,String, Date ,ForeignKey,func,UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date,datetime
from decimal import Decimal

class Base(DeclarativeBase):
    pass



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now(), nullable=False)

    applications:Mapped[list["Application"]] = relationship(back_populates="user")




class Application(Base):
    __tablename__ = "applications"

    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    company_id:Mapped[int] = mapped_column(ForeignKey("companies.id"),nullable=False)
    status:Mapped[str] = mapped_column(String(50), nullable=False)
    date_applied:Mapped[date] = mapped_column(Date, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False,server_default=func.now())
    updated_at:Mapped[datetime] = mapped_column(DateTime, nullable=False,onupdate=datetime.now,server_default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "company_id",
            name="uq_application_user_company"
        ),
    )

    user:Mapped["User"] = relationship(back_populates="applications")
    company:Mapped["Company"] = relationship(back_populates="applications")


class Company(Base):
    __tablename__ = "companies"

    id:Mapped[int] = mapped_column(primary_key=True)
    company_name:Mapped[str] = mapped_column(String(100), nullable=False)
    position:Mapped[str] = mapped_column(String(100), nullable=False)
    location:Mapped[str] = mapped_column(String(100), nullable=False)
    ctc:Mapped[Decimal] = mapped_column(Numeric(12,2), nullable=False)
    date_visiting:Mapped[date] = mapped_column(Date, nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, nullable=False,server_default=func.now())

    applications:Mapped[list["Application"]] = relationship(back_populates="company")





