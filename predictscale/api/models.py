from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, String, \
    Integer, Boolean
from sqlalchemy.orm import relationship

Base = declarative_base()


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
        return {
            'id': self.id,
            'group_id': self.group_id,
            'name': self.name,
            'desc': self.desc,
            'image': self.image,
            'flavor': self.flavor,
            'instances': [i.instance_id for i in self.instances],
            'enable': self.enable,
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

    group_id = Column(Integer, ForeignKey('group.id'))

    def __repr__(self):
        return "<Instance(user_id='%s', instance_id='%s', group_id='%s')>" \
            % (self.user_id, self.instance_id, self.group_id)
