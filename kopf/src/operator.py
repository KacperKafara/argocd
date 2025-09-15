import kopf
import pykube


@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, name, namespace, logger, body, **kwargs):
    namespaces = spec.get("namespaces")

    api = pykube.HTTPClient(pykube.KubeConfig.from_env())

    return {'namespaces': namespaces}
