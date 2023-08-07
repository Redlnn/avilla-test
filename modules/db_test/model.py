from dataclasses import dataclass

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column as col
from sqlalchemy.types import BIGINT, INTEGER

from libs.database.model import Base


@dataclass
class Test(Base):
    __tablename__ = "test"

    qq: Mapped[int] = col(BIGINT(), nullable=False, index=True, unique=True, primary_key=True)
    sex: Mapped[int] = col(INTEGER(), nullable=False)
