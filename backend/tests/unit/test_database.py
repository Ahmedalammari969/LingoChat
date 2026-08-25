"""
LinguaChat — Database Schema & Models Unit Tests
Tests for TASK-01-YOUSEF
Schema Source of Truth: docs/database-schema.md
"""

import uuid
import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, inspect

from app.database.base import Base, utcnow
from app.database.session import get_db, AsyncSessionLocal
from app.database.models import User, Room, RoomMember, Message, Translation


def test_models_metadata_registered():
    """Verify all 5 tables are registered in Base.metadata with exact schema names."""
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {"users", "rooms", "room_members", "messages", "translations"}
    assert expected_tables.issubset(table_names), f"Missing tables: {expected_tables - table_names}"


def test_users_table_columns_and_constraints():
    """Verify 'users' table structure strictly matches docs/database-schema.md § 1."""
    table = Base.metadata.tables["users"]
    col_names = {c.name for c in table.columns}
    expected_cols = {
        "id",
        "username",
        "hashed_password",
        "preferred_language",
        "created_at",
        "updated_at",
        "is_active",
    }
    assert expected_cols == col_names

    # Check Primary Key
    assert table.columns["id"].primary_key is True

    # Check Username unique constraint
    username_col = table.columns["username"]
    assert username_col.unique is True or any(
        uc.name == "uq_users_username" or "username" in [c.name for c in uc.columns]
        for uc in table.constraints
    )


def test_rooms_table_columns_and_foreign_keys():
    """Verify 'rooms' table structure strictly matches docs/database-schema.md § 2."""
    table = Base.metadata.tables["rooms"]
    col_names = {c.name for c in table.columns}
    expected_cols = {"id", "name", "created_by", "created_at"}
    assert expected_cols == col_names

    # Check Foreign Key on created_by -> users.id with SET NULL
    created_by_col = table.columns["created_by"]
    fk = list(created_by_col.foreign_keys)[0]
    assert fk.target_fullname == "users.id"
    assert fk.ondelete == "SET NULL"


def test_room_members_table_composite_unique_and_cascades():
    """Verify 'room_members' table structure and compound uniqueness."""
    table = Base.metadata.tables["room_members"]
    col_names = {c.name for c in table.columns}
    expected_cols = {"id", "room_id", "user_id", "joined_at"}
    assert expected_cols == col_names

    # Foreign Keys with CASCADE
    assert list(table.columns["room_id"].foreign_keys)[0].ondelete == "CASCADE"
    assert list(table.columns["user_id"].foreign_keys)[0].ondelete == "CASCADE"

    # Unique constraint on (room_id, user_id)
    uq_names = {uc.name for uc in table.constraints if hasattr(uc, "columns")}
    assert "uq_room_members_room_user" in uq_names


def test_messages_table_columns_and_cascades():
    """Verify 'messages' table structure and FK cascades."""
    table = Base.metadata.tables["messages"]
    col_names = {c.name for c in table.columns}
    expected_cols = {
        "id",
        "room_id",
        "sender_id",
        "original_text",
        "original_language",
        "sent_at",
    }
    assert expected_cols == col_names

    assert list(table.columns["room_id"].foreign_keys)[0].ondelete == "CASCADE"
    assert list(table.columns["sender_id"].foreign_keys)[0].ondelete == "SET NULL"


def test_translations_table_composite_unique_and_cascades():
    """Verify 'translations' table structure and compound uniqueness."""
    table = Base.metadata.tables["translations"]
    col_names = {c.name for c in table.columns}
    expected_cols = {
        "id",
        "message_id",
        "target_language",
        "translated_text",
        "provider_used",
        "confidence",
        "created_at",
    }
    assert expected_cols == col_names

    assert list(table.columns["message_id"].foreign_keys)[0].ondelete == "CASCADE"

    # Unique constraint on (message_id, target_language)
    uq_names = {uc.name for uc in table.constraints if hasattr(uc, "columns")}
    assert "uq_translations_message_lang" in uq_names


@pytest.mark.asyncio
async def test_get_db_generator():
    """Test get_db dependency yields an active AsyncSession."""
    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    try:
        await gen.aclose()
    except Exception:
        pass


def test_models_orm_instantiation_and_defaults():
    """Test instantiate all 5 ORM models and verify schema column defaults."""
    # Verify column defaults on table schema
    users_table = Base.metadata.tables["users"]
    assert users_table.columns["is_active"].default.arg is True
    assert users_table.columns["preferred_language"].default.arg == "en"

    # User
    u_id = uuid.uuid4()
    user = User(
        id=u_id,
        username="yousef_orm_test",
        hashed_password="hashed_pwd_example",
        preferred_language="ar",
        is_active=True,
    )
    assert user.id == u_id
    assert user.username == "yousef_orm_test"
    assert user.preferred_language == "ar"
    assert user.is_active is True

    # Room
    r_id = uuid.uuid4()
    room = Room(id=r_id, name="General", created_by=user.id)
    assert room.id == r_id
    assert room.name == "General"
    assert room.created_by == user.id

    # RoomMember
    rm_id = uuid.uuid4()
    member = RoomMember(id=rm_id, room_id=room.id, user_id=user.id)
    assert member.id == rm_id
    assert member.room_id == room.id
    assert member.user_id == user.id

    # Message
    m_id = uuid.uuid4()
    msg = Message(
        id=m_id,
        room_id=room.id,
        sender_id=user.id,
        original_text="مرحبا",
        original_language="ar",
    )
    assert msg.id == m_id
    assert msg.original_text == "مرحبا"
    assert msg.original_language == "ar"

    # Translation
    t_id = uuid.uuid4()
    trans = Translation(
        id=t_id,
        message_id=msg.id,
        target_language="en",
        translated_text="Hello",
        provider_used="libretranslate",
        confidence=0.98,
    )
    assert trans.id == t_id
    assert trans.message_id == msg.id
    assert trans.target_language == "en"
    assert trans.translated_text == "Hello"
    assert trans.provider_used == "libretranslate"
    assert trans.confidence == 0.98
