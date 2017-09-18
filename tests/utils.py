import os



def _get_settings():
    db_name = 'pylons.test.sqlite'
    db_path = os.path.join(os.path.dirname(__file__), '..')
    sqlalchemy_url = 'sqlite:///%s/%s' % (db_path, db_name)
    return {
        'jwt.private_key': 'op3n',
        'sqlalchemy.url': sqlalchemy_url,
        'db': os.path.join(db_path, db_name)
    }

def _init_db(settings):
    from gridix.data.models.base import BASE
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from elixr.sax.auth import User

    ## mk engine & Session
    engine = create_engine(settings['sqlalchemy.url'])
    Session = sessionmaker(bind=engine)

    # create tables
    BASE.metadata.create_all(engine)
    session = Session()

    # create user
    user = User(username='usr', is_active=True)
    user.set_password('open')
    session.add(user)
    session.commit()

    return session


def _clear_db(db, *table_names):
    from gridix.data.models.base import BASE
    tables = reversed(BASE.metadata.sorted_tables)
    if table_names:
        tables = [t for t in tables if t.name in table_names]
    
    for table in tables:
        db.execute(table.delete())
    db.commit()
