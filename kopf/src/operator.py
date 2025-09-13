import kopf
import pykube
import resources_generator
import os


def create_image_spec(registry, tag):
    registry = f"{registry}/" if registry else ""
    tag = tag or "latest"
    return f"{registry}nginx:{tag}"

def load_spec(spec):
    host = spec.get("host")
    registry = spec.get("registry")
    tag = spec.get("tag")
    config_name = spec.get("config_name") or "nginx-config"

    return host, registry, tag, config_name

BASE_DIR = os.path.dirname(__file__)

@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, name, namespace, logger, body, **kwargs):
    host, registry, tag, config_name = load_spec(spec)

    api = pykube.HTTPClient(pykube.KubeConfig.from_env())
    image = create_image_spec(registry, tag)

    with open(os.path.join(BASE_DIR, "config", "nginx.conf")) as f:
        nginx_config = f.read()

    with open(os.path.join(BASE_DIR, "config", "mime.types")) as f:
        mime_types = f.read()


    deployment_model, deployment_name = resources_generator.create_deployment_model(image, host, config_name)
    config_map = resources_generator.create_config_map({'nginx.conf': nginx_config, 'mime.types': mime_types}, config_name)

    kopf.append_owner_reference(deployment_model, body)
    kopf.append_owner_reference(config_map, body)
    pykube.Deployment(api, deployment_model).create()
    pykube.ConfigMap(api, config_map).create()

    logger.info(f"Created deployment model {deployment_name}")
    return {'host': host, 'image': image}