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
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import tables

from horizon import forms
from openstack_dashboard.dashboards.monitoring.userpanel \
    import tables as user_tables
from openstack_dashboard.dashboards.monitoring.userpanel \
    import forms as user_forms


class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email


id = 1
users = [
    User(1, 'test1', 'email1')
]


def add_user(name, email):
    global users
    global id
    id = id + 1
    users.append(User(id, name, email))


class AddUserView(forms.ModalFormView):
    form_class = user_forms.AddUserForm
    form_id = "add_user_form"
    modal_header = _("Add User For Notify")
    submit_label = _("Add User")
    submit_url = reverse_lazy('horizon:monitoring:userpanel:add_user')
    template_name = 'monitoring/userpanel/add_user.html'
    success_url = reverse_lazy('horizon:monitoring:userpanel:index')
    page_title = _("Add User For Notify")

    def get_initial(self):
        initial = {}
        return initial


class IndexView(tables.DataTableView):
    table_class = user_tables.UsersTable
    template_name = 'monitoring/userpanel/index.html'
    page_title = _('Users')

    # def has_prev_data(self, table):
    #     return self._prev

    # def has_more_data(self, table):
    #     return self._more

    def get_data(self):
        global users
        return users

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        return context
