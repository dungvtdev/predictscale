from django.utils.translation import ugettext_lazy as _
from horizon import workflows
from horizon import forms


class AddGroupInfoAction(workflows.Action):
    name = forms.RegexField(
        label=_("Name"),
        max_length=255,
        regex=r'^[\w\.\- ]+$',
        error_messages={'invalid': _('Name may only contain letters, numbers, '
                                     'underscores, periods and hyphens.')})
    desc = forms.CharField(max_length=512,
                           label=_("Desc"))

    image = forms.ChoiceField(label='Image')
    flavor = forms.ChoiceField(label='Flavor')

    def populate_image_choices(self, request, context):
        return [(1, 'test')]

    def populate_flavor_choices(self, request, context):
        return [(1, 'test')]

    class Meta(object):
        name = _("Group Information")
        help_text = _("Group define name, description, image, flavor")

    def clean(self):
        pass


class AddGroupInfo(workflows.Step):
    action_class = AddGroupInfoAction
    contributes = ("name",
                   "desc",
                   "image",
                   "flavor")


class UpdateGroupInstancesAction(workflows.MembershipAction):
    def __init__(self, request, *args, **kwargs):
        super(UpdateGroupInstances, self).__init__(request,
                                                   *args, **kwargs)
        context = args[0]

    class Meta(object):
        name = _("Group Instances")
        slug = "update_group_instances"


class UpdateGroupInstances(workflows.UpdateMembersStep):
    action_class = UpdateGroupInstancesAction
    help_text = _("Select instances where group will apply and monitoring")
    available_list_title = _("All Instances")
    members_list_title = _("Selected Instances")
    no_available_text = _("No instances found.")
    no_members_text = _("No instances selected. ")
    show_roles = False
    # depends_on = ("flavor_id",)
    # contributes = ("flavor_access",)


class AddGroup(workflows.Workflow):
    slug = "add_group"
    name = _("Add Group")
    finalize_button_name = _("Add Group")
    success_message = _('Created new group "%s".')
    failure_message = _('Unable to create group "%s".')
    success_url = "horizon:monitoring:scalepanel:index"
    default_steps = (AddGroupInfo, UpdateGroupInstances, )

    def format_status_message(self, message):
        return message % self.context['name']

    def handle(self, request, data):
        pass


class UpdateGroup(workflows.Workflow):
    pass
