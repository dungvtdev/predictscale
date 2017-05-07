# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from horizon import tables
from horizon import forms
from horizon import workflows
from openstack_dashboard.dashboards.monitoring.scalepanel \
    import tables as scale_tables
from openstack_dashboard.dashboards.monitoring.scalepanel \
    import workflows as scale_workflows

from openstack_dashboard.dashboards.monitoring.backend.monitorclient \
    import MonitorClient


class GroupData:
    def __init__(self, id=None, name=None, desc=None, instances=None,
                 image=None, flavor=None, enable=None):
        self.id = id
        self.group_name = name or ''
        self.group_desc = desc or ''
        self.instances = instances or ''
        self.image = image or ''
        self.flavor = flavor or ''
        self.enable = 'True'

    @classmethod
    def create(cls, group_dict):
        g = group_dict
        instances = g['instances']
        instances_str = '\n'.join(instances)

        return GroupData(id=g['id'],
                         name=g['name'],
                         desc=g['desc'],
                         instances=instances_str,
                         image=g['image'],
                         flavor=g['flavor'])


class AddView(workflows.WorkflowView):
    workflow_class = scale_workflows.AddGroup
    # dung lai template mac dinh
    template_name = 'admin/flavors/create.html'
    page_title = _("Add Group")


class UpdateView(workflows.WorkflowView):
    workflow_class = scale_workflows.UpdateGroup
    template_name = 'admin/flavors/create.html'
    page_title = _("Update Group")


class IndexView(tables.DataTableView):
    table_class = scale_tables.ScaleGroupTable
    template_name = 'monitoring/scalepanel/index.html'
    page_title = _('Scale')

    def get_data(self):
        group_dicts = MonitorClient.default().get_groups(self.request)
        return [GroupData.create(g) for g in group_dicts]

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context
