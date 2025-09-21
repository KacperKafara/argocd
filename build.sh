#!/usr/bin/env bash

kubectl delete deployment kopf-operator -n operator
kubectl delete nginx istio-nginx -n operator

kubectl wait --for=delete deployment/kopf-operator -n operator --timeout=60s
kubectl wait --for=delete nginx/istio-nginx -n operator --timeout=60s

docker build -t "kopf-test:1.0.0" ./kopf/.
minikube image load "kopf-test:1.0.0" --overwrite
echo "image loaded"