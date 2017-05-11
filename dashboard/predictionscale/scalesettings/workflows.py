from django.utils.translation import ugettext_lazy as _
from horizon import workflows
from horizon import forms
from openstack_dashboard import api
from horizon import exceptions

from .utils import create_group
from openstack_dashboard.dashboards.predictionscale.backend.models \
    import GroupData


class AddGroupInfoAction(workflows.Action):
    _group_id_regex = (r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
                       r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12}|[0-9]+|auto$')
    _group_id_help_text = _("Group ID should be UUID4 or integer. "
                            "Leave this field blank or use 'auto' to set "
                            "a random UUID4.")

    name = forms.RegexField(
        label=_("Name"),
        max_length=255,
        regex=r'^[\w\.\- ]+$',
        error_messages={'invalid': _('Name may only contain letters, numbers, '
                                     'underscores, periods and hyphens.')})
    group_id = forms.RegexField(label=_("ID"),
                                regex=_group_id_regex,
                                required=False,
                                initial='auto',
                                help_text=_group_id_help_text)
    desc = forms.CharField(max_length=512,
                           label=_("Desc"),
                           required=False)

    image = forms.ChoiceField(label='Image')
    flavor = forms.ChoiceField(label='Flavor')

    def populate_image_choices(self, request, context):
        try:
            images, _, _ = \
                api.glance.image_list_detailed(self.request)
        except Exception:
            images = []
            exceptions.handle(self.request, _("Unable to retrieve images."))
        return [(img.id, '%s {%s}' % (img.name, img.id)) for img in images]

    def populate_flavor_choices(self, request, context):
        try:
            flavors, _, _ = api.nova.flavor_list_paged(request)
            print(flavors)
        except Exception:
            flavors = []
            exceptions.handle(request,
                              _('Unable to retrieve flavor list.'))
        return [(f.id, '%s{%s}' % (f.name, f.id))for f in flavors]

    class Meta(object):
        name = _("Group Information")
        help_text = _("Group define name, description, image, flavor")

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        if not name:
            msg = _('Group name cannot be empty.')
            self._errors['name'] = self.error_class([msg])
        return name

    def clean(self):
        pass


class AddGroupInfo(workflows.Step):
    action_class = AddGroupInfoAction
    contributes = ("group_id",
                   "name",
                   "desc",
                   "image",
                   "flavor")


class UpdateGroupInstancesAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(UpdateGroupInstancesAction, self).__init__(request,
                                                         *args,
                                                         **kwargs)
        err_msg = _('Unable to retrieve instances list. '
                    'Please try again later.')
        context = args[0]

        default_role_field_name = self.get_default_role_field_name()
        self.fields[default_role_field_name] = forms.CharField(required=False)
        self.fields[default_role_field_name].initial = 'member'

        field_name = self.get_member_field_name('member')
        self.fields[field_name] = forms.MultipleChoiceField(required=False)

        # Get list of available projects.
        all_instances = []
        try:
            all_instances, hasmore = api.nova.server_list(self.request)
        except Exception:
            exceptions.handle(request, err_msg)

        instances_list = [(inst.id, inst.name)
                          for inst in all_instances]

        self.fields[field_name].choices = instances_list

        # If we have a POST from the CreateFlavor workflow, the flavor id
        # isn't an existing flavor. For the UpdateFlavor case, we don't care
        # about the access list for the current flavor anymore as we're about
        # to replace it.
        if request.method == 'POST':
            return

        # Get list of flavor projects if the flavor is not public.
        # group_id = context.get('group_id')
        # group_instance = []
        # try:
        #     if group_id:
        #         flavor = api.nova.flavor_get(request, flavor_id)
        #         if not flavor.is_public:
        #             flavor_access = [project.tenant_id for project in
        #                              api.nova.flavor_access_list(request,
        #                                                          flavor_id)]
        # except Exception:
        #     exceptions.handle(request, err_msg)

        # self.fields[field_name].initial = flavor_access
        # self.fields[field_name].initial = [(1, 2)]

    class Meta(object):
        name = _("Group Instances")
        slug = "update_group_instance"


class UpdateGroupInstances(workflows.UpdateMembersStep):
    action_class = UpdateGroupInstancesAction
    help_text = _("Select instances where group will apply and monitoring")
    available_list_title = _("All Instances")
    members_list_title = _("Selected Instances")
    no_available_text = _("No instances found.")
    no_members_text = _("No instances selected. ")
    show_roles = False
    depends_on = ("group_id",)
    contributes = ("instances",)

    def contribute(self, data, context):
        if data:
            member_field_name = self.get_member_field_name('member')
            context['instances'] = data.get(member_field_name, [])
        return context


class AddGroup(workflows.Workflow):
    slug = "add_group"
    name = _("Add Group")
    finalize_button_name = _("Add Group")
    success_message = _('Created new group "%s".')
    failure_message = _('Unable to create group "%s".')
    success_url = "horizon:predictionscale:scalesettings:index"
    default_steps = (AddGroupInfo, UpdateGroupInstances, )

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, data):
        print('****************************************')
        print(data)
        if '__dict__' in data:
            print(data.__dict__)

        '''
        {'name': None, 'image': u'07b28db9-feae-4ea2-9ac2-024c4daae486', 
        'instances': [u'a7e600e2-6e7f-4460-a1b1-6e8dcd12baee'], 'flavor': u'1', 
        'group_id': u'auto', 'desc': u'tesst'}
        '''

        group = GroupData.create(data)
        try:
            ok = create_group(request, group)
            return ok
        except:
            # msg = _('Can\'t create group. Try again later')
            # exceptions.handle(request, msg)
            raise
            return False


class UpdateGroup(workflows.Workflow):
    pass
