from horizon import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from horizon import messages


class AddUserForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255,
                           label=_("Name"),
                           required=True,)
    email = forms.EmailField(max_length=255,
                             label=_("Email"),
                             required=True,)
    enable = forms.BooleanField(required=False,
                                label="Enable Notify")

    def handle(self, request, data):
        name = data['name']
        email = data['email']
        enable = data['enable']

        message = (_('Successfully updated aggregate: "%s."')
                   % name)
        messages.success(request, message)
        return True

    def get_success_url(self):
        return reverse("horizon:monitoring:userpanel:index")

    def get_failure_url(self):
        return reverse("horizon:monitoring:userpanel:index")
