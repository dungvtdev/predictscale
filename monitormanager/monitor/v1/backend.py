from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from monitor import configtool
from monitor import models


class DBBackend(object):
    def __init__(self):
        config = configtool.get_config('DB')
        engine_path = config['engine']
        is_debug = config['debug']

        self._engine = create_engine(engine_path, echo=False)
        self._session = scoped_session(sessionmaker(bind=self._engine))

        models.Base.metadata.create_all(self._engine)

    def _get_localsession(self):
        self._session()
        return self._session

    def _close_localsession(self):
        self._session.remove()

    def add_group(self, **kwargs):
        ss = self._get_localsession()

        name = kwargs.get('name', None)
        desc = kwargs.get('desc', None)
        image_id = kwargs.get('image_id', None)

        id = kwargs.get('id', None)
        group = None
        if id is not None:
            group = ss.query(models.Group).filter(
                models.Group.id == id).first()
        if not group:
            group = models.Group(name=name, desc=desc, image_id=image_id)
        else:
            group.name = name
            group.desc = desc
            group.image_id = image_id

        ss.add(group)
        ss.commit()

        self._close_localsession()

    def drop_group(self, id=None):
        if id is None:
            raise ValueError('group id must is not None')
        ss = self._get_localsession()
        group = ss.query(models.Group).filter(models.Group.id == id).first()
        if group is not None:
            ss.delete(group)
            ss.commit()

        self._close_localsession()