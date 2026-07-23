from __future__ import annotations

from collections.abc import Generator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool


def build_engine(database_url: str) -> Engine:
    connect_args: dict[str, object] = {}
    extra_kwargs: dict[str, object] = {}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    else:
        extra_kwargs = {
            "poolclass": QueuePool,
            "pool_size": 3,
            "max_overflow": 2,
            "pool_timeout": 30,
            "pool_pre_ping": True,
            "pool_recycle": 1800,
        }

    return create_engine(database_url, future=True, connect_args=connect_args, **extra_kwargs)


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def get_db(request: Request) -> Generator[Session, None, None]:
    session_factory: sessionmaker[Session] = request.app.state.session_factory
    db = session_factory()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()