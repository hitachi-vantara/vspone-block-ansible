#!/usr/bin/bash

minikube start --addons=ingress
kubectl create namespace ucp
kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing.io_jaegers_crd.yaml
kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/service_account.yaml
kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role.yaml
kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role_binding.yaml
kubectl apply -n ucp -f ./operator.yaml
kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/cluster_role.yaml
kubectl apply -n ucp -f ./cluster_role_binding.yaml
sleep 30
kubectl apply -n ucp -f jaeger.yaml
kubectl get -n ucp ingress
