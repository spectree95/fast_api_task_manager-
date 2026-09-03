import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import Base,get_db
from backend.app.models.users import User
from backend.app.models.tasks import Task


TEST_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autoflush = False,
    autocommit = False,
    bind = engine,
)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    
    yield
    
    Base.metadata.drop_all(bind=engine)
    
    
@pytest.fixture
def db():
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        

@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()