sudo yum remove docker                   docker-client                   docker-client-latest                   docker-common                   docker-latest                   docker-latest-logrotate                   docker-logrotate                   docker-engine
sudo yum install -y yum-utils
sudo yum-config-manager     --add-repo     https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io --skip-broken
sudo systemctl start docker
sudo yum -y update
sudo yum -y install docker-distribution
cat > /etc/docker-distribution/registry/config.yml << EOF
version: 0.1
log:
  fields:
	service: registry
storage:
	cache:
		layerinfo: inmemory
	filesystem:
		rootdirectory: /var/lib/registry
http:
	addr: :5000
EOF
firewall-cmd --add-port=5000/tcp --permanent
firewall-cmd --reload
systemctl start docker-distribution
systemctl enable docker-distribution
cat > /etc/docker/daemon.json << EOF
{
"insecure-registries" : ["myregistry.local:5000"]
}
EOF
systemctl restart docker


cp -r conf /home/ 

mkdir -p /home/keycloak-db
chmod 777 -R /home/keycloak-db

git clone https://github.com/Gallore/yaml_cli
cd yaml_cli
pip install .

yaml_cli -s spec:externalIPs ["172.25.20.109"]

/k8sdeployments/install-es.sh
/k8sdeployments/deployer.sh

curl -s "https://raw.githubusercontent.com/\
kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
mv kustomize /usr/local/bin

yum -y install gcc
yum -y install gcc-c++



kubectl create namespace ucp
kubectl apply --validate=false -f third-party/cert-manager/cert-manager.yaml
kubectl create -f third-party/kube-prometheus/manifests/setup
until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done
kubectl create -f third-party/kube-prometheus/manifests/
cd config/default/ && kustomize edit set namespace "ucp" && cd ../..
make deploy IMG=triangulum-docker-dev-sc.repo.sc.eng.hitachivantara.com/infrastructure-operator:latest

