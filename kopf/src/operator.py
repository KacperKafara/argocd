import kopf
import pykube

@kopf.on.create("istio.com", "v1", "nginx")
def on_create(host, **kwargs):
    if host is None:
        raise kopf.PermanentError("Host cannot be null!")
    return "New CR created."
