import os
from pathlib import Path

os.environ["AGENT_LOOM_DATABASE_URL"] = f"sqlite:///{Path(__file__).parent / 'test_agent_loom.db'}"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

