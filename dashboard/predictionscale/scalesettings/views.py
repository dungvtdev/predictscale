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
from openstack_dashboard.dashboards.predictionscale.scalesettings \
    import tables as settings_tables
from openstack_dashboard.dashboards.predictionscale.scalesettings \
    import workflows as settings_workflows

from openstack_dashboard.dashboards.predictionscale.backend \
    import client
from openstack_dashboard.dashboards.predictionscale.backend.models import GroupData
from horizon import views
from horizon import exceptions


class AddView(workflows.WorkflowView):
    workflow_class = settings_workflows.AddGroup
    # dung lai template mac dinh
    template_name = 'admin/flavors/create.html'
    page_title = _("Add Group")


class UpdateView(workflows.WorkflowView):
    workflow_class = settings_workflows.UpdateGroup
    template_name = 'admin/flavors/create.html'
    page_title = _("Update Group")


class IndexView(tables.DataTableView):
    table_class = settings_tables.ScaleGroupTable
    template_name = 'predictionscale/scalesettings/index.html'
    page_title = _('Settings')

    def get_data(self):
        try:
            groups = []
            # groups = client(self.request).get_groups()
            return groups
        except Exception:
            err_msg = _('Can\'t retrieve group list')
            exceptions.handle(self.request, err_msg)

    # def get_context_data(self, **kwargs):
    #     context = super(IndexView, self).get_context_data(**kwargs)
    #     return context
