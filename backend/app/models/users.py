from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import DateTime


from app.core.database import Base

class User(Base):
    
    __tablename__ = "users"
    
    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    username : Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email : Mapped[str | None] = mapped_column(String(255), unique=True)     
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    tasks = relationship(
        "Task",
        back_populates="owner",
        cascade = "all, delete-orphan"
    )