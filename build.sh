#!/usr/bin/env bash

docker build -t "kopf-test:1.0.0" ./kopf/.
kubectl delete deployment kopf-operator -n operator
kubectl delete nginx istio-nginx -n operator

sleep 5

minikube image rm "kopf-test:1.0.0"
echo "Image deleted"
minikube image load "kopf-test:1.0.0"
echo "image loaded"