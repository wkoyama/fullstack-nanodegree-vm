import random
import string

from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)
                     for x in range(32))


class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    password_hash = Column(String(64))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'id': self.id
        }

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=10000):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id


class Categoria(Base):
    __tablename__ = 'categoria'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('usuario.id'))
    user = relationship(Usuario)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    date = Column(DateTime, nullable=False)
    category_id = Column(Integer, ForeignKey('categoria.id'))
    categoria = relationship(Categoria,
                             backref=backref("item", cascade="all,delete"))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id
        }


engine = create_engine('sqlite:///catalogitems.db')

Base.metadata.create_all(engine)
