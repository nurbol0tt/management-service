from typing import Optional
from txpostgres import txpostgres
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from app.settings import settings

_pool: Optional[txpostgres.ConnectionPool] = None

def get_pool() -> txpostgres.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = txpostgres.ConnectionPool(None, dsn=settings.db_dsn, min=1, max=5, reactor=reactor)
    return _pool

@inlineCallbacks
def start_pool():
    pool = get_pool()
    yield pool.start()

@inlineCallbacks
def stop_pool(_=None):
    global _pool
    if _pool is not None:
        yield _pool.close()
        _pool = None
