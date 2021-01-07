function install_docker(){
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
sudo yum install -y yum-utils
sudo yum-config-manager     --add-repo     https://download.docker.com/linux/centos/docker-ce.repo
sudo yum -y install docker-ce docker-ce-cli containerd.io --skip-broken
sudo systemctl start docker
sudo systemctl enable  docker

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
ip_address=`ip addr | grep "^ *inet " | grep -v "vi" | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p' `
ip_address+=' myregistry.local'
echo $ip_address >> /etc/hosts
systemctl restart docker
export DOCKER_OPTS+=" --insecure-registry myregistry.local:5000"
}

function load_images(){
docker load < ../Images/hv-idm.tar.gz
docker load < ../Images/hv-infrastructure-operator.tar.gz
docker load < ../Images/hv-tasks.tar.gz
#docker load < ../Images/sdi_gateway_block:8.6.0.tar.gz
docker load < ../Images/hv-porcelain.tar.gz
}


install_docker
load_images
