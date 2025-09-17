import kopf
import lightkube
from App import App
from lightkube.resources.apps_v1 import Deployment
import os
import logging
import redis

client = lightkube.Client()
logger = logging.getLogger(__name__)
r = redis.Redis(host="redis", port=6379, db=0)

def get_image_details(image):
    if not image:
        return None

    name, tag = image.rsplit(":", 1)
    return os.path.basename(name), tag


apps = []


@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, name, body, **kwargs):
    namespaces = spec.get("namespaces")
    r.set("elo", "zul")

    for namespace in namespaces:
        for event, deployment in client.watch(Deployment, namespace=namespace):
            if event == "DELETED":
                continue
            else:
                app_name = namespace.split('-')[0]
                for container in deployment.spec.template.spec.containers:
                    # name, tag = get_image_details(container.image)
                    apps.append(container.image)

    logger.info(r.get("elo"))
    return {'namespaces': namespaces}