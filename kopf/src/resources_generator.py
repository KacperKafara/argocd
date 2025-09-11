def create_deployment_model(image, host):
    name = f"{host.split('.')[0]}-nginx"
    obj = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{name}",
        },
        "spec": {
            "replicas": 1,
            "selector": {
                "matchLabels": {
                    "app": "nginx"
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": "nginx"
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": f"{name}",
                            "image": f"{image}",
                            "ports": [
                                {"containerPort": 80}
                            ]
                        }
                    ]
                }
            }
        }
    }
    return obj, name
