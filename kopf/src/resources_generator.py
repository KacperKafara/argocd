def create_deployment_model(image, host, config_name):
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
                            ],
                            "volumeMounts": [
                                {
                                    "mountPath": "/etc/nginx/",
                                    "name": f"{config_name}-volume",
                                    "readOnly": True,
                                }
                            ]
                        }
                    ],
                    "volumes": [
                        {
                            "name": f"{config_name}-volume",
                            "configMap": {
                                "name": f"{config_name}"
                            }
                        }
                    ]
                }
            }
        }
    }
    return obj, name


def create_config_map(content, name):
    configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": f"{name}",
        },
        "data": {
            "nginx.conf": content['nginx.conf'],
            "mime.types": content['mime.types']
        }
    }
    return configmap

def create_service(ports):
    generated_ports = []
    for port in ports:
        generated_ports.append(
            {
                "name": f"port-{port}",
                "port": port,
                "protocol": "TCP",
                "targetPort": port,
            }
        )
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": "nginx-service",
        },
        "spec": {
            "type": "ClusterIP",
            "ports": generated_ports,
            "selector": {
                "app": "nginx",
            }
        }
    }

    return service