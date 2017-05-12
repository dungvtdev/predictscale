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
from django.views.generic.base import RedirectView
from openstack_dashboard import api


# def get_group_view_data(request, groups):
#     # flavors = api.nova.flavor_list(request)
#     # images = api.glance.image_list_detailed(request)
#     # instances = api.nova.server_list(request)

#     for group in groups:
#         group = group.clone()

#         if group.flavor:
#             flavor_name = api.nova.flavor_get(request, group.flavor)
#             group.flavor = flavor_name or group.flavor

#         if group.image:
#             image_name = api.glance.image_get(request, group.image)

#         # inst_names = []
#         # if group.instances:
#         #     for inst_id in group.instances:
#         #         name = api.nova.server_get(request, inst_id)
#         #         inst_names.append(name or inst_id)

#         # group.instances = '\n'.join(inst_names)

#     return groups
class InstanceTmpl:
    name = None
    id = None

    def __init__(self, name, id):
        self.name = name
        self.id = id


class AddView(workflows.WorkflowView):
    workflow_class = settings_workflows.AddGroup
    # dung lai template mac dinh
    template_name = 'admin/flavors/create.html'
    page_title = _("Add Group")


class UpdateView(workflows.WorkflowView):
    workflow_class = settings_workflows.UpdateGroup
    template_name = 'admin/flavors/create.html'
    page_title = _("Update Group")


class IndexView(RedirectView):
    url = reverse_lazy('horizon:predictionscale:scalesettings:step1')


class Step1View(tables.DataTableView):
    table_class = settings_tables.ScaleGroupTable
    template_name = 'predictionscale/scalesettings/group_table.html'
    page_title = _('Settings')
    step_title = _('Group Settings')
    step_index = 1

    def get_data(self):
        try:
            groups = client(self.request).get_groups()
            return groups
        except Exception:
            err_msg = _('Can\'t retrieve group list')
            exceptions.handle(self.request, err_msg)

    def get_context_data(self, **kwargs):
        context = super(Step1View, self).get_context_data(**kwargs)
        context['step_title'] = self.step_title
        context['step_index'] = self.step_index
        return context


class Step2View(views.APIView):
    template_name = 'predictionscale/scalesettings/service_setting.html'
    step_title = _('Service Settings')
    step_index = 2

    def get_data(self, request, context, *args, **kwargs):
        context = super(Step2View, self).get_context_data(**kwargs)
        id = kwargs['id']
        context['step_title'] = self.step_title
        context['step_index'] = self.step_index

        try:
            group = client(request).get_group(id)
            if group is None:
                raise
        except:
            err_msg = _('Can\'t retrieve group')
            exceptions.handle(self.request, err_msg)
            return context

        instances = group.instances
        context['instances'] = [InstanceTmpl(inst, inst) for inst in instances]
        context['group'] = group
        return context


class Step3View(views.APIView):
    template_name = 'predictionscale/scalesettings/apply_confirm.html'
    step_title = _('Apply Confirm')
    step_index = 3

    def get_data(self, request, context, *args, **kwargs):
        context = super(Step3View, self).get_context_data(**kwargs)
        context['step_title'] = self.step_title
        context['step_index'] = self.step_index
        return context


# class IndexView(views.APIView):
#     # A very simple class-based view...
#     template_name = 'predictionscale/scalesettings/index.html'

#     def get_data(self, request, context, *args, **kwargs):
#         # Add data to the context here...
#         return context
