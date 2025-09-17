import kopf
import lightkube
from App import App
from lightkube.resources.apps_v1 import Deployment
import os
import logging

client = lightkube.Client()
logger = logging.getLogger(__name__)

def get_image_details(image):
    logger.info(image)
    name, tag = image.rsplit(":", 1)
    return os.path.basename(name), tag


apps = []


@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, name, logger, body, **kwargs):
    namespaces = spec.get("namespaces")

    for namespace in namespaces:
        for event, deployment in client.watch(Deployment, namespace=namespace):
            if event == "DELETED":
                continue
            else:
                app_name = namespace.split('-')[0]
                for container in deployment.spec.template.spec.containers:
                    name, tag = get_image_details(container.image)
                    apps.append(App(app_name, {name: tag}))

    return {'namespaces': namespaces}