from sqlalchemy.types import Text, Integer
from sqlalchemy import Table, Column, MetaData

robot_drone = Table("robot_drone", MetaData("robots"),
                     Column("robot_id", Integer, autoincrement=True, primary_key=True),
                     Column("robot_type", Integer, nullable=False),
                     Column("robot_reference", Text, nullable=False),
                     Column("robot_state", Integer, nullable=False))
