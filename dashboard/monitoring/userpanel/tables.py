from horizon import tables
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy


class DeleteUser(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete User",
            u"Delete Users",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted User",
            u"Deleted Users",
            count
        )

    def delete(self, request, obj_id):
        pass


class AddUser(tables.LinkAction):
    name = 'add_user'
    verbose_name = _('Add User')
    url = 'horizon:monitoring:userpanel:add_user'
    classes = ('ajax-modal', )
    icon = 'plus'

    def allowed(self, request, datum=None):
        return True


class UsersTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('User name'))
    email = tables.Column('email', verbose_name=_('Email'))

    class Meta(object):
        name = 'users'
        verbose_name = _('Users')
        table_actions = (AddUser, DeleteUser, )
