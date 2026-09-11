from datetime import UTC, datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

class Base(DeclarativeBase):
    pass

class BookModel(Base):
    __tablename__ = 'books'

    # Вариант создания столбцов таблицы БД с использованием Mapped[type] приоритетнее
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, default=None)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    posts: Mapped[list[Post]] = relationship(back_populates='author')

    image_file: Mapped[str| None] = mapped_column(
        String(200), 
        nullable=True,
        default=None
    )

    reset_tokens: Mapped[list[PasswordResetToken]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan'
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f'/media/profile_pics/{self.image_file}'
        return '/static/profile_pics/default.png'
     

class Post(Base):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    author: Mapped[User] = relationship(back_populates='posts')



class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    ) 

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

    user: Mapped[User] = relationship(back_populates='reset_tokens')