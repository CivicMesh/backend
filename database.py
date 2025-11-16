from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#URL_DATABASE = "postgresql://postgres:Sunkurdi%402050@localhost:5433/CivicMesh" #might cause a issue
URL_DATABASE = "postgresql://civicmesh_user:jS6E76q5U04CJKOEKfLMGDu16SWuIKDd@dpg-d4ctrrali9vc73c7hfgg-a/civicmesh"

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()