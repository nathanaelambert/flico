from sqlalchemy.orm import DeclarativeBase, Session, mapped_column, Mapped, relationship
from sqlalchemy import Boolean, Column, ForeignKey, String, Double
from pgvector.sqlalchemy import VECTOR
from typing import Optional
 
class Base(DeclarativeBase):
    pass
 
class MachineLearningPhoto(Base):
    __tablename__ = 'machine_learning_photo'
    owner_nsid: Mapped[str] = mapped_column(primary_key=True)
    id : Mapped[int] = mapped_column(primary_key=True)
    is_date_test_set  : Mapped[bool] = mapped_column(default=False)
    is_date_train_set : Mapped[bool] = mapped_column(default=False)
    geo_cluster_id : Mapped[Optional[int]] = mapped_column(ForeignKey("geo_cluster.id"))
    embedding : Mapped[Optional[VECTOR(768)]]

class GeoCluster(Base):
    __tablename__ = 'geo_cluster'
    id : Mapped[int] = mapped_column(primary_key=True)
    min_latitude : Mapped[float] = mapped_column(Double)
    max_latitude : Mapped[float] = mapped_column(Double)

class Photo(Base):
    __tablename__ = 'photo'
    owner_nsid: Mapped[str] = mapped_column(primary_key=True)
    id : Mapped[int] = mapped_column(primary_key=True)
    url_n : Mapped[str] = mapped_column(Text)



Base.metadata.create_all(engine)

with Session(engine) as session:
    pics = session.query(MachineLearningPhoto).all()

    stmt = select(Photo)
    photos = session.scalars(stmt).all()

    stmt = select(Photo).where(Photo.url_n == "")
    empty = session.scalars(stmt).first()

    