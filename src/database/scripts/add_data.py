import pandas as pd
import datetime
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, DateTime, Date, Float


engine = create_engine('sqlite:///quicktimerbot.db', echo=True)


meta = MetaData()

trackeds = Table(
    'trackeds',
    meta,
    Column('id', Integer, primary_key=True),
    Column('start_time', DateTime, default=None),
    Column('stop_time', DateTime, default=None),
    Column('time_worked', Float, default=None),
    Column('task_id', String(255), default=None),
    Column('task_name', String(255)),
    Column('date', Date, default=datetime.datetime.utcnow),
    Column('user_id', ForeignKey('users.id')),
)


df = pd.read_csv('trackeds.csv')
values = df.values.tolist()

conn = engine.connect()

for value in values:

    def format(date):
        date = date.replace('-', ',').replace(':', ',').replace('.', ',').replace(' ', ',').split(',')
        date = [int(i) for i in date]
        return datetime.datetime(*date)


    tracked_db = trackeds.insert().values(
        id=value[0],
        start_time=format(value[1]),
        stop_time=format(value[2]),
        time_worked=value[3],
        task_id=None,
        task_name=value[4],
        date= datetime.datetime.strptime(value[5], '%Y-%m-%d'),
        user_id=value[6]
    )
    conn.execute(tracked_db)
    conn.commit()

conn.close()
