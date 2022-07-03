from flask import jsonify
from sqlalchemy import Column, DateTime, Integer, Sequence, String
from database.db import Base


class CompanyBase(Base):
    __tablename__ = 'company'

    idCompany = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    crypt = Column(String(200))
    password = Column(String(200))
    register_date = Column(DateTime(timezone=True))
    ip = Column(String(20))
    token = Column(String(200))

    def __init__(self, name=None, password=None, crypt=None, register_date=None, ip=None, token=None):
        self.name = name
        self.crypt = crypt
        self.password = password
        self.register_date = register_date
        self.ip = ip
        self.token = token