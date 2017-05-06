from django.utils.translation import ugettext_lazy as _
from horizon import tabs
from openstack_dashboard.dashboards.monitoring.scalepanel \
    import tables as scalegroup_tables

from openstack_dashboard.api import nova


class ScaleGroupTab(tabs.TableTab):
    table_classes = (scalegroup_tables.ScaleGroupTable, )
    name = _('Scale Group')
    slug = 'scalegroup'
    template_name = "horizon/common/_detail_table.html"

    def get_scalegroups_data(self):
        pass


class ScaleRuleTab(tabs.TableTab):
    table_classes = ()
    name = _('Scale Rule')
    slug = 'scalerule'
    template_name = "horizon/common/_detail_table.html"

    def get_scale_rule_data(self):
        pass


class ScaleRulesSettingTabs(tabs.TabGroup):
    slug = 'scalerule_setting'
    tabs = (ScaleGroupTab, )
    sticky = True
