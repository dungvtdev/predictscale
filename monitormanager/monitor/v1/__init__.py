from . import dbresource as res

catalog = [
    res.routes
]

endpoint = []

for tr in catalog:
    for r in tr:
        endpoint.append(r)