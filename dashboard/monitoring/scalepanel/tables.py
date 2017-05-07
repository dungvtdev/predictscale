from horizon import tables
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy


class DeleteGroup(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Group",
            u"Delete Groups",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Group",
            u"Deleted Groups",
            count
        )

    def delete(self, request, obj_id):
        pass


class AddGroup(tables.LinkAction):
    name = 'add_group'
    verbose_name = _('Add Group')
    url = 'horizon:monitoring:scalepanel:add_group'
    classes = ('ajax-modal', )
    icon = 'plus'

    def allowed(self, request, datum=None):
        return True


class UpdateGroup(tables.LinkAction):
    name = "update"
    verbose_name = _("Edit Group")
    url = "horizon:monitoring:scalepanel:update"
    classes = ("ajax-modal",)
    icon = "pencil"


class ScaleGroupTable(tables.DataTable):
    group_name = tables.Column("group_name",
                               verbose_name=_("Groupname"))

    desc = tables.Column("group_desc",
                         verbose_name=_("Descriptions"))

    instances = tables.Column("instances",
                              verbose_name=_("Instances"))

    image = tables.Column("image",
                          verbose_name=_("Image"))
    flavor = tables.Column("flavor",
                           verbose_name=_("Flavor"))
    enable = tables.Column("enable",
                           verbose_name=_("Enable"))

    class Meta(object):
        name = 'scalegroups'
        verbose_name = _("ScaleGroups")
        table_actions = (AddGroup, DeleteGroup, )
        row_actions = (UpdateGroup, )
