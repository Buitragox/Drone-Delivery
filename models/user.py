from sqlalchemy.types import Text, Integer, UUID
from uuid import uuid4
from sqlalchemy import Table, Column, MetaData

user_account = Table("user_account", MetaData("admin_account"),
                     Column("user_id", UUID(as_uuid=True), default=uuid4, primary_key=True),
                     Column("user_name", Text, nullable=False),
                     Column("user_password", Text, nullable=False),
                     Column("user_state", Integer, nullable=False),
                     Column("user_email", Text, nullable=False))
