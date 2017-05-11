class GroupData:

    def __init__(self, id=None, name=None, group_id=None, desc=None, instances=None,
                 image=None, flavor=None, enable=False, process=None):
        self.id = id
        self.group_id = group_id
        self.name = name or ''
        self.desc = desc or ''
        self.instances = instances or ''
        self.image = image or ''
        self.flavor = flavor or ''
        self.process = process
        enable = enable if enable is not None else False
        self.enable = enable

        if self.process is None:
            self.process = 'Unknown' if self.enable else 'NotActive'

    def to_dict(self):
        inst_str = '\n'.join(self.instances)
        return {
            'id': self.id,
            'group_id': self.id,
            'name': self.name,
            'desc': self.desc,
            'instances': inst_str,
            'image': self.image,
            'flavor': self.flavor,
            'enable': self.enable,
            'process': self.process,
        }

    @classmethod
    def create(cls, group_dict):
        g = group_dict
        return GroupData(id=g.get('id', None),
                         group_id=g['group_id'],
                         name=g['name'],
                         desc=g['desc'],
                         instances=g['instances'],
                         image=g['image'],
                         flavor=g['flavor'],
                         enable=g.get('enable', False),
                         process=g.get('process', None))
