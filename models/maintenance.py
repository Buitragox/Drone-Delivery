from sqlalchemy.types import Text, Integer
from sqlalchemy import Table, Column, MetaData, Date

maintenance = Table("maintenance", MetaData("robots"),
                     Column("maintenance_id", Integer, autoincrement=True, primary_key=True),
                     Column("robot_id", Integer),
                     Column("maintenance_date", Date, nullable=False),
                     Column("technician_id", Text, nullable=False),
                     Column("description", Text, nullable=False))
