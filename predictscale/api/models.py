from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, String, \
    Integer, Boolean, DateTime
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()


instance_meta_pattern = {
    'instance_id': 1,
    'period': 10,
    'data_length': 100,
    'predict_length': 3,
    'update_in_time': 10,
    'endpoint': '192.168.122.124',
    'db_name': 'cadvisor',
    'neural_size': 15,
    'recent_point': 4,
    'periodic_number': 1,
    'metric': 'cpu_usage_total',
    'epoch': 'm'
}

group_pattern = {
    'db_name': 'cadvisor',
    'neural_size': 15,
    'recent_point': 4,
    'periodic_number': 1,
    'period': 1,
    'update_in_time': 1,
    'data_length': 7,
    'predict_length': 3,
}

for k in group_pattern:
    group_pattern[k] = instance_meta_pattern[k]


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    group_id = Column(String(250), nullable=False, unique=True)
    user_id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    desc = Column(String(250), nullable=True)
    image = Column(String(250))
    flavor = Column(String(250))
    enable = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    period = Column(Integer)
    data_length = Column(Integer)
    recent_point = Column(Integer)
    periodic_number = Column(Integer)
    predict_length = Column(Integer)
    update_in_time = Column(Integer)
    neural_size = Column(Integer)

    instances = relationship("Instance", backref='group')

    def __repr__(self):
        return "<User(name='%s')>" \
            % (self.name)

    def to_dict(self):
        created = self.created.isoformat()
        return {
            'id': self.id,
            'group_id': self.group_id,
            'name': self.name,
            'desc': self.desc,
            'image': self.image,
            'flavor': self.flavor,
            'instances': [i.instance_id for i in self.instances],
            'enable': self.enable,
            'created': created,
            'period': self.period,
            'data_length': self.data_length,
            'recent_point': self.recent_point,
            'periodic_number': self.periodic_number,
            'predict_length': self.predict_length,
            'update_in_time': self.update_in_time,
            'neural_size': self.neural_size}


class Instance(Base):
    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    instance_id = Column(String(250), nullable=False, unique=True)
    endpoint = Column(String(20))
    db_name = Column(String(20))

    group_id = Column(Integer, ForeignKey('group.group_id'))

    def __repr__(self):
        return "<Instance(user_id='%s', instance_id='%s', group_id='%s')>" \
            % (self.user_id, self.instance_id, self.group_id)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'instance_id': self.instance_id,
            'endpoint': self.endpoint,
            'db_name': self.db_name,
            'group_id': self.group_id,
        }
