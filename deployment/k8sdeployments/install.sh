#!/bin/bash

pwd=pwd

cp -r conf /home/ 
mkdir -p /home/keycloak-db
chmod 777 -R /home/keycloak-db

sudo cp /home/conf/certs/server.crt /home/conf/certs/tls.crt
sudo cp /home/conf/certs/tls.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust

kubeadm init --config k8s_cluster_config.yaml

modprobe br_netfilter
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables
echo '1' > /proc/sys/net/ipv4/ip_forward
echo '1' > /proc/sys/net/bridge/bridge-nf-call-ip6tables
echo '1' > /proc/sys/net/ipv6/ip_forward

mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
export kubever=$(kubectl version | base64 | tr -d '\n')

kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$kubever"
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
echo "applying roles ..."
kubectl apply -f kubeconfig/apiroles.yaml
kubectl apply -f kubeconfig/auth.yaml
kubectl apply -f kubeconfig/roles.yaml

#git clone https://github.com/Gallore/yaml_cli
#cd yaml_cli
#pip install .
ip_address=`ip addr | grep "^ *inet " | grep -v "vi" | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' `
#yaml_cli -s spec:externalIPs [$ip_address]

echo "installing elastic search, porcelain..."
./install-es.sh
./deployer.sh 

kubectl taint nodes $(hostname) node-role.kubernetes.io/master:NoSchedule-
echo $ip_address
kubectl patch svc kong-proxy  -p '{"spec": {"type": "LoadBalancer", "externalIPs":[$ip_address]}}' -n kong

curl -s "https://raw.githubusercontent.com/\
kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
mv kustomize /usr/local/bin

yum -y install gcc
yum -y install gcc-c++

yum install wget -y

wget https://dl.google.com/go/go1.15.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.15.linux-amd64.tar.gz
# vi ~/.bashrc
echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
. ~/.bashrc
go version

#kubectl create namespace ucp
kubectl apply --validate=false -f third-party/cert-manager/cert-manager.yaml
kubectl create -f third-party/kube-prometheus/manifests/setup
until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done
kubectl create -f third-party/kube-prometheus/manifests/
cd config/default/ && kustomize edit set namespace "ucp" && cd ../..
make deploy IMG=triangulum-docker-dev-sc.repo.sc.eng.hitachivantara.com/infrastructure-operator:latest

