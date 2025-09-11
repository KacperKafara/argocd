import kopf
import pykube
import resources_generator


def create_image_spec(registry, tag):
    registry = f"{registry}/" if registry else ""
    tag = tag or "latest"
    return f"{registry}nginx:{tag}"

def load_spec(spec):
    host = spec.get("host")
    registry = spec.get("registry")
    tag = spec.get("tag")

    return host, registry, tag

@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, **kwargs):
    host, registry, tag = load_spec(spec)

    api = pykube.HTTPClient(pykube.KubeConfig.from_env())
    image = create_image_spec(registry, tag)
    deployment_model, deployment_name = resources_generator.create_deployment_model(image, host)

    pykube.Deployment(api, deployment_model).create()

    print('New CR created witch host argument: ' + host)
    return {'host': host, 'image': image}
