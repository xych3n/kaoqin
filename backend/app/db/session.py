from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./sql.db")
SessionLocal = sessionmaker(bind=engine)
