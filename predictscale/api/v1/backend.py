import falcon
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from share import configtool
from api import models
import uuid


db = None


class DBBackend(object):
    def __init__(self):
        config = configtool.get_config('DB')
        engine_path = config['engine']
        is_debug = config['debug']

        self._engine = create_engine(engine_path, echo=False)
        self._session = scoped_session(sessionmaker(bind=self._engine))

        models.Base.metadata.create_all(self._engine)

    @classmethod
    def default(cls):
        global db
        if db is None:
            db = DBBackend()
        return db

    def _get_localsession(self):
        self._session()
        return self._session

    def _close_localsession(self):
        self._session.remove()

    def _update_group_object(self, group, group_dict, session):
        desc = group_dict.get('desc', None)
        image = group_dict.get('image', None)
        flavor = group_dict.get('flavor', None)

        group.desc = desc or group.desc
        group.image = image or group.image
        group.flavor = flavor or group.flavor

    def _update_group_instance(self, user_id, group, group_dict, session):
        instances = group_dict.get('instances', None)
        if instances:
            # remove all old
            old_instances = None
            if group.group_id is not None:
                old_instances = session.query(models.Instance) \
                    .filter(models.Instance.user_id == user_id)\
                    .filter(models.Instance.group_id == group.id).all()
                if old_instances is not None:
                    for oi in old_instances:
                        oi.group_id = None
            # create new
            for inst_id in instances:
                instance = session.query(models.Instance)\
                    .filter(models.Instance.user_id == user_id)\
                    .filter(models.Instance.instance_id == inst_id)\
                    .one_or_none()
                if instance:
                    instance.group_id = group.group_id
                else:
                    instance = models.Instance(user_id=user_id,
                                               group_id=group.id,
                                               instance_id=inst_id)
                    session.add(instance)

            # remove all old_instance not link group
            if old_instances is not None:
                for oi in old_instances:
                    if oi.group_id is None:
                        session.delete(oi)

    def add_group(self, user_id, groups):
        ss = self._get_localsession()
        # try:
        for group_dict in groups:
            name = group_dict.get('name', None)
            group_id = group_dict.get('group_id', None)
            if group_id is None or group_id == 'auto':
                group_id = str(uuid.uuid4())

            group = models.Group()
            if not(user_id and name):
                raise ValueError('Group init must have user id and name')
            group.user_id = user_id
            group.name = name
            group.group_id = group_id
            group.enable = False

            self._update_group_object(group, group_dict, ss)
            ss.add(group)
            ss.commit()
            self._update_group_instance(user_id, group, group_dict, ss)
            ss.commit()

        # except:
        #     # ss.rollback()
        #     raise falcon.HTTPBadRequest('Group DB error')
        # finally:
        self._close_localsession()

    def drop_group(self, user_id, id):
        # try:
        if user_id is None or id is None:
            raise ValueError('Delete group get invalid value')
        ss = self._get_localsession()
        group = ss.query(models.Group).filter(
            models.Group.id == id).first()
        if group is not None:
            ss.delete(group)
            ss.commit()
        # except:
        #     ss.rollback()
        #     raise falcon.HTTPBadRequest('Group DB error')
        # finally:
        self._close_localsession()

    def get_groups(self, user_id):
        ss = self._get_localsession()
        try:
            groups = ss.query(models.Group).filter(
                models.Group.user_id == user_id).all()
            group_dicts = [g.to_dict() for g in groups]
            return group_dicts
        except:
            raise falcon.HTTPBadRequest('Group DB error')
        finally:
            self._close_localsession()

    def update_groups(self, user_id, id, group_dict):
        ss = self._get_localsession()
        try:
            group = ss.query(models.Group).filter(
                models.Group.user_id == user_id).filter(models.Group.id == id).one()

            group.enable = group_dict.get('enable', group.enable)
            self._update_group_object(group, group_dict, ss)
            self._update_group_instance(user_id, group, group_dict, ss)

            ss.commit()
        except:
            ss.rollback()
            raise falcon.HTTPBadRequest('Group DB error')
        finally:
            self._close_localsession()

    def get_group(self, user_id, id):
        # print('user_id %s, id %s' % (user_id, id))
        ss = self._get_localsession()
        # try:
        group = ss.query(models.Group)\
            .filter(models.Group.user_id == user_id)\
            .filter(models.Group.id == id).one()
        return group
        # except Exception:
        #     raise falcon.HTTPBadRequest('Group DB error')
        # finally:
        self._close_localsession()
