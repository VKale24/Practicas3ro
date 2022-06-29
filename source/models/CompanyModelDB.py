from sqlalchemy import Column, DateTime, Integer, Sequence, String
from entities.CompanyDB import Base

class CompanyBase(Base):
    __tablename__ = 'company'
 
    id = id = Column(Integer, Sequence('user_id_seq'), primary_key=True),                       
    name = Column(String(50)),
    register_date = Column(DateTime(timezone=True)),
    ip = Column(String(20)),
    token = Column(String(200))
 

    def __init__(self, name=None, register_date=None, ip=None, token=None):
        self.name = name
        self.register_date = register_date
        self.ip = ip
        self.token = token

    def __repr__(self):
        return f'<User {self.name!r}>'