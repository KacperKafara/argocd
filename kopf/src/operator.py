import kopf
import lightkube
from lightkube.resources.core_v1 import Pod

from App import App
from lightkube.resources.apps_v1 import Deployment
import os
import redis

client = lightkube.Client()
r = redis.Redis(host="redis", port=6379, db=0)


def get_image_details(image):
    if not image:
        return None

    name, tag = image.rsplit(":", 1)
    return os.path.basename(name), tag


def resolve_containers(deployment, namespace, logger):
    containers = []
    for container in deployment.spec.template.spec.containers:
        try:
            if container.image == "auto":
                logger.warning("Image is 'auto', resolving from Pod status...")

                labels = deployment.spec.selector.matchLabels

                pod_list = client.list(Pod, namespace=namespace, labels=labels)

                for pod in pod_list:
                    if pod.status and pod.status.containerStatuses:
                        for cs in pod.status.containerStatuses:
                            logger.info(f"Processing for container: {cs.image}")
                            name, tag = get_image_details(cs.image)
                            containers.append({name: tag})

            else:
                logger.info(f"Processing for container: {container.image}")
                name, tag = get_image_details(container.image)
                containers.append({name: tag})
        except ValueError:
            logger.error(f"Error during processing container: {container.image}")

    return containers


@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, name, logger, body, **kwargs):
    namespaces = spec.get("namespaces")

    for namespace in namespaces:
        for event, deployment in client.watch(Deployment, namespace=namespace):
            if event == "DELETED":
                continue
            else:
                app_name = namespace.split('-')[0]
                app = App(app_name, resolve_containers(deployment, namespace, logger))
                logger.info(app)

    return {'namespaces': namespaces}
