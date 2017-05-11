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
    n_period_to_train = Column(Integer)
    n_predict = Column(Integer)
    period_train_again = Column(Integer)

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
            'enable': self.enable
        }


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

