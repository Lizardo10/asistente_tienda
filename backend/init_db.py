from app.db import Base, engine
from app import models

if __name__ == "__main__":
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("OK")
