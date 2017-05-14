from . import dbresource as res
from . import pingresource as ping
from . import actionresource as actionres

catalog = [
    res.routes,
    ping.routes,
    actionres.routes,
]

endpoint = []

for tr in catalog:
    for r in tr:
        endpoint.append(r)
