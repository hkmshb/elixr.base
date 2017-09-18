import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gridix.data.models.base import Model



@pytest.fixture(scope='module')
def db():
    # setup
    engine = create_engine('sqlite:///:memory:')
    Model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session

    # teardown
    Model.metadata.drop_all(engine)
