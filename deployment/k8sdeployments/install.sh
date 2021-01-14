#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Usage: ./install.sh ip"
	exit 1
fi

ip_address=$1

echo "Installing pip..."
yum install -y  python-pip
curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
python get-pip.py

pip install pathlib
pip install ruamel.yaml

echo "$ip_address $(hostname).test.com $(hostname)" >> /etc/hosts

python update_k8s_cluster-config.py $ip_address
python update_keycloak_service_ip.py $ip_address

pwd=pwd

cp -r conf /home/ 
mkdir -p /home/keycloak-db
chmod 777 -R /home/keycloak-db

sudo cp /home/conf/certs/server.crt /home/conf/certs/tls.crt
sudo cp /home/conf/certs/tls.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust

modprobe br_netfilter
echo '1' > /proc/sys/net/bridge/bridge-nf-call-iptables
echo '1' > /proc/sys/net/ipv4/ip_forward
echo '1' > /proc/sys/net/bridge/bridge-nf-call-ip6tables
echo '1' > /proc/sys/net/ipv6/ip_forward

kubeadm init --config k8s_cluster_config.yaml

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


pip install ruamel.yaml
#git clone https://github.com/Gallore/yaml_cli
#cd yaml_cli
#pip install .
ipaddr=$(hostname -I|awk '{print $1}')
#yaml_cli -s spec:externalIPs [$ip_address]

echo "$ip_address keycloak" >> /etc/hosts

echo "installing elastic search, porcelain..."
kubectl create namespace ucp
./install-es.sh
./deployer.sh 

kubectl taint nodes $(hostname) node-role.kubernetes.io/master:NoSchedule-
kubectl taint nodes master node-role.kubernetes.io/master:NoSchedule-
echo $ip_address
kubectl patch svc kong-proxy  -p '{"spec": {"type": "LoadBalancer", "externalIPs":["'"$ip_address"'"]}}' -n kong

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

