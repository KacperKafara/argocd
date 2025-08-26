import kopf
import pykube


@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, **kwargs):
    host = spec.get("host")

    if host is None:
        raise kopf.PermanentError("Host cannot be null!")

    print('New CR created witch host argument: ' + host)
    return {'host': host}
