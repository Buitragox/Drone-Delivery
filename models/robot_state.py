from sqlalchemy.types import Text, Integer
from sqlalchemy import Table, Column, MetaData

robot_states = Table("states", MetaData("robots"),
                     Column("robot_state", Integer, autoincrement=True, primary_key=True),
                     Column("state_name", Text, nullable=False))
