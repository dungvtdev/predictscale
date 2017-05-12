from django.http import JsonResponse
from .utils import get_data_state
from horizon import exceptions


def get_data_state(request, id):
    data_length = request.GET.get('data-length')
    try:
        data, ok = get_data_state(request, data_length)
    except Exception:
        exceptions.handle(request,
                          _('Unable to retrieve data state list.'))
    return JsonResponse(data)
