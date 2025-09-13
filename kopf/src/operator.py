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
def on_create(spec, name, namespace, logger, body, **kwargs):
    host, registry, tag = load_spec(spec)

    api = pykube.HTTPClient(pykube.KubeConfig.from_env())
    image = create_image_spec(registry, tag)
    deployment_model, deployment_name = resources_generator.create_deployment_model(image, host)

    kopf.append_owner_reference(deployment_model, body)
    pykube.Deployment(api, deployment_model).create()

    logger.info(f"Created deployment model {deployment_name}")
    return {'host': host, 'image': image}