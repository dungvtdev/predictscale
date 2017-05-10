from . import dbresource as res
from . import pingresource as ping

catalog = [
    res.routes,
    ping.routes
]

endpoint = []

for tr in catalog:
    for r in tr:
        endpoint.append(r)
