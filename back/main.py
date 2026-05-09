from database import engine
from back.models import Base

Base.metadata.create_all(bind=engine)