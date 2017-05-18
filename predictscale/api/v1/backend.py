import falcon
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from share import configtool
from api import models
import uuid
from .. import models

db = None


def _wrap_default_group_object(group, default_dict):
    for attr in group.__dict__:
        if attr in default_dict and getattr(group, attr) is None:
            setattr(group, attr, default_dict[attr])
    return group


def _wrap_default_instance_dict(instance, default_dict, group=None):
    d = {}
    group = group or {}
    for k in default_dict:
        d[k] = getattr(instance, k, None) \
            or getattr(group, k, None) or default_dict[k]
    return d


class DBBackend(object):
    def __init__(self):
        config = configtool.get_config('DB')
        engine_path = config['engine']
        is_debug = config['debug']

        self._engine = create_engine(engine_path, echo=False)
        self._session = scoped_session(sessionmaker(bind=self._engine))

        models.Base.metadata.create_all(self._engine)

        self.group_pattern = models.group_pattern
        self.instance_meta_pattern = models.instance_meta_pattern

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

    # def _wrap_default_group_values(self, groups):
    #     for g in groups:
    #         for attr in g.__dict__:
    #             if attr in self.default_vals and getattr(g, attr) is None:
    #                 setattr(g, attr, self.default_vals[attr])

    def _update_group_object(self, group, group_dict, session):
        desc = group_dict.get('desc', None)
        image = group_dict.get('image', None)
        flavor = group_dict.get('flavor', None)
        selfservice = group_dict.get('selfservice', None)
        provider = group_dict.get('provider', None)

        group.desc = desc or group.desc
        group.image = image or group.image
        group.flavor = flavor or group.flavor
        group.selfservice = selfservice or group.selfservice
        group.provider = provider or group.provider

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
            for inst_id, endpoint in instances:
                instance = session.query(models.Instance)\
                    .filter(models.Instance.user_id == user_id)\
                    .filter(models.Instance.instance_id == inst_id)\
                    .one_or_none()
                if instance:
                    instance.group_id = group.group_id
                else:
                    instance = models.Instance(user_id=user_id,
                                               group_id=group.group_id,
                                               instance_id=inst_id,
                                               endpoint=endpoint,
                                               monitor=True)
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

            exist_group = self.get_group(user_id=user_id, group_id=group_id)
            if exist_group is not None:
                group = exist_group
            else:
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
            try:
                self._update_group_instance(user_id, group, group_dict, ss)
            except:
                ss.delete(group)
                raise
            finally:
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
            # delete all instance associate with
            insts = group.instances
            if insts:
                for inst in insts:
                    ss.delete(inst)
            ss.delete(group)
        ss.commit()
        # except:
        #     ss.rollback()
        #     raise falcon.HTTPBadRequest('Group DB error')
        # finally:
        self._close_localsession()

    def get_groups(self, user_id, group_default=None):
        group_default = self.group_pattern or group_default

        ss = self._get_localsession()
        # try:
        groups = ss.query(models.Group).filter(
            models.Group.user_id == user_id).all()

        if group_default is not None:
            groups = [_wrap_default_group_object(
                group, group_default) for group in groups]

        group_dicts = [g.to_dict() for g in groups]
        # return group_dicts
        # except:
        #     raise falcon.HTTPBadRequest('Group DB error')
        # finally:
        self._close_localsession()
        return group_dicts

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

    def get_group(self, user_id, id, group_default=None):
        group_default = group_default or self.group_pattern
        # print('user_id %s, id %s' % (user_id, id))
        ss = self._get_localsession()
        # try:
        group = ss.query(models.Group)\
            .filter(models.Group.user_id == user_id)\
            .filter(models.Group.id == id).one()
        group = _wrap_default_group_object(group, group_default)
        return group.to_dict()
        # except Exception:
        #     raise falcon.HTTPBadRequest('Group DB error')
        # finally:
        self._close_localsession()

    def get_instance(self, user_id, instance_id):
        ss = self._get_localsession()

        inst = ss.query(models.Instance)\
            .filter(models.Instance.instance_id == instance_id) \
            .filter(models.Instance.user_id == user_id).one()
        return inst.to_dict()

        self._close_localsession()

    def get_instance_meta_from_db(self, user_id, instance_id,
                                  default_instance_dict=None):
        default_instance_dict = default_instance_dict \
            or self.instance_meta_pattern

        ss = self._get_localsession()

        inst = ss.query(models.Instance)\
            .filter(models.Instance.instance_id == instance_id) \
            .filter(models.Instance.user_id == user_id).one()

        group = inst.group

        if default_instance_dict is not None:
            inst_dict = _wrap_default_instance_dict(
                inst, default_instance_dict, group)
            return inst_dict
        else:
            return inst.to_dict()

    def get_instances_in_group(self, user_id, group_id):
        ss = self._get_localsession()
        try:
            group = ss.query(models.Group)\
                .filter(models.Group.user_id == user_id)\
                .filter(models.Group.id == group_id).one()
            instances = group.instances
            return instances
        except Exception as e:
            raise falcon.HTTPBadRequest('Group DB error')
        finally:
            self._close_localsession()
