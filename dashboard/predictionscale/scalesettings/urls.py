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

from django.conf.urls import url

from openstack_dashboard.dashboards.predictionscale.scalesettings import views
from openstack_dashboard.dashboards.predictionscale.scalesettings \
    import ajaxviews


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^step1', views.Step1View.as_view(), name='step1'),
    url(r'^(?P<id>[^/]+)/step2', views.Step2View.as_view(), name='step2'),
    url(r'^step3', views.Step3View.as_view(), name='step3'),
    url(r'^add_group', views.AddView.as_view(), name='add_group'),
    url(r'^(?P<id>[^/]+)/update/$', views.UpdateView.as_view(), name='update'),
    url(r'^ajax/groups/(?P<id>[^/]+)/data/$',
        ajaxviews.get_data_state, name='get_data_state'),
    url(r'^ajax/groups/(?P<id>[^/]+)/run/$',
        ajaxviews.run_containers, name='run_containers')
]
