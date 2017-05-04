from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, String, \
    Integer, Boolean
from sqlalchemy.orm import relationship

Base = declarative_base()


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    desc = Column(String(250), nullable=True)
    image_id = Column(String(250))
    instances = relationship(Instance, backref='group', lazy='dynamic')
    rules = relationship(Rule, backref='group', lazy='dynamic')
    # script_file

    def __repr__(self):
        return "<User(name='%s', desc='%s', image_id='%s')>" \
            % (self.name, self.desc, self.image_id)


class Instance(Base):
    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    instance_id = Column(String(250), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship(Group)

    def __repr__(self):
        return "<Instance(user_id='%s', instance_id='%s', group_id='%s')>" \
            % (self.user_id, self.instance_id, self.group_id)


class Rule(Base):
    __tablename__ = 'rule'

    id = Column(Integer, primary_key=True)
    metric = Column(String(50), nullable=False)
    threshold_upper = Column(Integer, nullable=False)
    threshold_lower = Column(Integer, nullable=False)
    node_change = Column(Integer)
    status = Column(Boolean)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship(Group)

    def __repr__(self):
        return "<Rule(metric='%s', group_id='%s', status='%s')>" \
            % (self.metric, self.group_id, self.status)
