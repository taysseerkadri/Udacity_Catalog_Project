from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()


class Brand(Base):
    __tablename__ = 'brand'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    picture = Column(String)
    description = Column(String)
    creator = Column(String)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'descritpion': self.description,
            'creator': self.creator
        }


class BrandAddress(Base):
    __tablename__ = 'brandaddress'
    id = Column(Integer, primary_key=True)
    streetaddress = Column(String(250))
    city = Column(String(150))
    state = Column(String(150))
    postalcode = Column(String(150))
    country = Column(String(150))
    brand_id = Column(Integer, ForeignKey('brand.id'))
    brand = relationship(Brand)


class ClothingItem(Base):
    __tablename__ = 'clothingitem'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    picture = Column(String)
    description = Column(String)
    price = Column(Float)
    stockamount = Column(Integer)
    brand_id = Column(Integer, ForeignKey('brand.id'))
    brand = relationship(Brand)
    creator = Column(String)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
            'descritpion': self.description,
            'price': self.price,
            'stockamount': self.stockamount,
            'creator': self.creator
        }


engine = create_engine('sqlite:///clothing.db')

Base.metadata.create_all(engine)
