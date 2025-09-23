import kopf
import lightkube
from lightkube.resources.core_v1 import Pod

from App import App
from lightkube.resources.apps_v1 import Deployment
import os
import redis
import pickle

client = lightkube.Client()
r = redis.Redis(host="redis", port=6379, db=0)


def get_image_details(image):
    if not image:
        return None

    name, tag = image.rsplit(":", 1)
    return os.path.basename(name), tag


def resolve_containers(deployment, namespace, logger):
    containers = {}
    for container in deployment.spec.template.spec.containers:
        try:
            if container.image == "auto":
                logger.warning("Image is 'auto', resolving from Pod status...")

                labels = deployment.spec.selector.matchLabels

                pod_list = client.list(Pod, namespace=namespace, labels=labels)

                for pod in pod_list:
                    if pod.status and pod.status.containerStatuses:
                        for cs in pod.status.containerStatuses:
                            logger.debug(f"Processing for container: {cs.image}")
                            name, tag = get_image_details(cs.image)
                            containers[name] = tag

            else:
                logger.debug(f"Processing for container: {container.image}")
                name, tag = get_image_details(container.image)
                containers[name] = tag
        except ValueError:
            logger.error(f"Error during processing container: {container.image}")

    return containers


def notify(containers: dict, logger):
    if not containers or len(containers) == 0:
        return

    logger.info("----------NOTIFICATION----------")
    for name, tag in containers.items():
        logger.info(f"{name}:{tag}")
    logger.info("----------NOTIFICATION-END----------")


def compare_containers(readed_app: App, app: App):
    containers = {}
    for name, tag in app.containers.items():
        readed_tag = readed_app.containers.get(name)
        if readed_tag != tag:
            containers[name] = tag

    return containers



def save_images_and_notify(app: App, logger):
    app_data = r.get(app.name)
    readed_app = pickle.loads(app_data) if app_data is not None else None

    logger.debug(f"Readed app: {readed_app}")
    if not readed_app:
        r.set(app.name, pickle.dumps(app))
        notify(app.containers, logger)
        return

    containers = compare_containers(readed_app, app)
    r.set(app.name, pickle.dumps(App(app.name, readed_app.containers | containers)))
    notify(containers, logger)


@kopf.on.create("istio.com", "v1", "nginx")
def on_create(spec, name, logger, body, **kwargs):
    namespaces = spec.get("namespaces")

    for namespace in namespaces:
        app_name = namespace.split('-')[0]
        for event, deployment in client.watch(Deployment, namespace=namespace):
            if event == "DELETED":
                continue
            else:
                app = App(app_name, resolve_containers(deployment, namespace, logger))
                save_images_and_notify(app, logger)

    return {'namespaces': namespaces}
