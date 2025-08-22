#!/usr/bin/env bash

# delete minikube
minikube delete

# run minikube
minikube start --cpus=4 --memory=8192

# install argocd
kubectl create namespace argocd
helm install argocd argo/argo-cd --namespace argocd \
  --set server.extraArgs={--insecure}

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.0/cert-manager.yaml
kubectl rollout status deployment/argocd-server -n argocd

#bcrypt(password)=$2a$10$rRyBsGSHK6.uc8fntPwVIuLVHgsAhAX7TcdrqW/RADU0uh7CaChLa
kubectl -n argocd patch secret argocd-secret \
  -p '{"stringData": {
    "admin.password": "$2a$10$rRyBsGSHK6.uc8fntPwVIuLVHgsAhAX7TcdrqW/RADU0uh7CaChLa",
    "admin.passwordMtime": "'$(date +%FT%T%Z)'"
  }}'

kubectl patch svc -n argocd argocd-server \
  -p '{"spec": {"type": "NodePort"}}'

echo "ArgoCD is ready!"
echo "URL: http://$(minikube ip):$(kubectl get svc -n argocd argocd-server -o=jsonpath='{.spec.ports[0].nodePort}')"
echo "Login: admin"
echo "Password: password"

kubectl apply -f argocd-secret.yaml
kubectl apply -f app_root.yaml