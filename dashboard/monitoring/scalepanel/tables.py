from django.utils.translation import ugettext_lazy as _

from horizon import tables


class ScaleGroupTable(tables.DataTable):
    group_name = tables.Column("group_name",
                               verbose_name=_("Groupname"))

    desc = tables.Column("group_desc",
                         verbose_name=_("Descriptions"))

    instances = tables.Column("instances",
                              verbose_name=_("Instances"))

    rules_appling = tables.Column("rules_appling",
                                  verbose_name=_("Rules (Appling)"))

    rules_queueing = tables.Column("rules_queueing",
                                   verbose_name=_('Rules (Queueing)'))

    class Meta(object):
        name = 'scalegroups'
        verbose_name = _("ScaleGroups")
