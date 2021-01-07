# Current Operator version
VERSION ?= 1.0.0
# Default bundle image tag
BUNDLE_IMG ?= controller-bundle:$(VERSION)
# Options for 'bundle-build'
ifneq ($(origin CHANNELS), undefined)
BUNDLE_CHANNELS := --channels=$(CHANNELS)
endif
ifneq ($(origin DEFAULT_CHANNEL), undefined)
BUNDLE_DEFAULT_CHANNEL := --default-channel=$(DEFAULT_CHANNEL)
endif
BUNDLE_METADATA_OPTS ?= $(BUNDLE_CHANNELS) $(BUNDLE_DEFAULT_CHANNEL)

# Image URL to use all building/pushing image targets
IMG ?= controller:latest
# Produce CRDs that work back to Kubernetes 1.11 (no version conversion)
CRD_OPTIONS ?= "crd:trivialVersions=true"

OS=$(go env GOOS)
ARCH=$(go env GOARCH)

# Get the currently used golang install path (in GOPATH/bin, unless GOBIN is set)
ifeq (,$(shell go env GOBIN))
GOBIN=$(shell go env GOPATH)/bin
else
GOBIN=$(shell go env GOBIN)
endif

PACKAGES=./pkg/...
PROJECT=infrastructure-operator
GO_DOWNLOAD_URL=https://golang.org/dl/go1.14.4.linux-amd64.tar.gz
OPERATOR_SDK_VERSION=v1.0.0
OPERATOR_SDK_DOWNLOAD_URL=curl -LO https://github.com/operator-framework/operator-sdk/releases/download/${OPERATOR_SDK_VERSION}/operator-sdk-${OPERATOR_SDK_VERSION}-x86_64-linux-gnu
MINIKUBE_DOWNLOAD_URL=https://github.com/kubernetes/minikube/releases/download/v1.9.2/minikube-linux-amd64
KUBECTL_DOWNLOAD_URL=https://storage.googleapis.com/kubernetes-release/release/v1.18.2/bin/linux/amd64/kubectl
OLM_DEPLOYMENT_VERSION=1.0.0

all: manager

ENVTEST_ASSETS_DIR=$(shell pwd)/testbin

# Run tests
test: $GOPATH/bin/gotestsum $GOPATH/bin/cover generate fmt vet manifests 
	mkdir -p ${ENVTEST_ASSETS_DIR}
	test -f ${ENVTEST_ASSETS_DIR}/setup-envtest.sh || curl -sSLo ${ENVTEST_ASSETS_DIR}/setup-envtest.sh https://raw.githubusercontent.com/kubernetes-sigs/controller-runtime/master/hack/setup-envtest.sh
	source ${ENVTEST_ASSETS_DIR}/setup-envtest.sh; fetch_envtest_tools $(ENVTEST_ASSETS_DIR); setup_envtest_env $(ENVTEST_ASSETS_DIR); 
	gotestsum --format testname --rerun-fails --junitfile operator_unittest_report.xml --packages="./..." -- -p 1 -timeout 200s -tags=integration -coverpkg ./... -coverprofile=cover-unit.coverprofile -covermode count
	go tool cover -func cover-unit.coverprofile 

# Build manager binary
manager: generate fmt vet
	go build -o bin/manager main.go

# Run against the configured Kubernetes cluster in ~/.kube/config
run: generate fmt vet manifests
	@mkdir -p /tmp/k8s-webhook-server/serving-certs
	@cp -rf config/examples/certificate/tls.key /tmp/k8s-webhook-server/serving-certs 
	@cp -rf config/examples/certificate/tls.crt /tmp/k8s-webhook-server/serving-certs 
	go run ./main.go 

# Run against the configured Kubernetes cluster in ~/.kube/config
testrun: generate fmt vet manifests
	@mkdir -p /tmp/k8s-webhook-server/serving-certs
	@cp -rf config/examples/certificate/tls.key /tmp/k8s-webhook-server/serving-certs 
	@cp -rf config/examples/certificate/tls.crt /tmp/k8s-webhook-server/serving-certs 
	go run ./main.go --testmode

# Install CRDs into a cluster
install: manifests kustomize
	$(KUSTOMIZE) build config/crd | kubectl apply -f -

# Uninstall CRDs from a cluster
uninstall: manifests kustomize
	$(KUSTOMIZE) build config/crd | kubectl delete -f -

# Deploy controller in the configured Kubernetes cluster in ~/.kube/config
deploy: manifests kustomize
	cd config/manager && $(KUSTOMIZE) edit set image controller=${IMG}
	$(KUSTOMIZE) build config/default | kubectl apply -f -

# Generate manifests e.g. CRD, RBAC etc.
manifests: controller-gen
	$(CONTROLLER_GEN) $(CRD_OPTIONS) rbac:roleName=manager-role webhook paths="./..." output:crd:artifacts:config=config/crd/bases

# Run go fmt against code
fmt:
	go fmt ./...

# Run go vet against code
vet:
	go vet ./...

# Generate code
generate: controller-gen
	$(CONTROLLER_GEN) object:headerFile="hack/boilerplate.go.txt" paths="./..."

# Build the docker image and run test before
docker-build: test
	#git rev-parse --short HEAD | tee buildtag
	docker build . -t ${IMG}

# Deploy controller in the configured Kubernetes cluster in ~/.kube/config
deploy-puma: 
	$(KUSTOMIZE) build config/puma/default | kubectl apply -f -
	#docker-registry.sie.hds.com:443/sdi_gateway/8.6.0/sdi_gateway_block:8.6.0
	#cd config/puma/manager && $(KUSTOMIZE) edit set image controller=${IMG}

# Push the docker image
docker-push:
	docker push ${IMG}

# find or download controller-gen
# download controller-gen if necessary
controller-gen:
ifeq (, $(shell which controller-gen))
	@{ \
	set -e ;\
	CONTROLLER_GEN_TMP_DIR=$$(mktemp -d) ;\
	cd $$CONTROLLER_GEN_TMP_DIR ;\
	go mod init tmp ;\
	go get sigs.k8s.io/controller-tools/cmd/controller-gen@v0.3.0 ;\
	rm -rf $$CONTROLLER_GEN_TMP_DIR ;\
	}
CONTROLLER_GEN=$(GOBIN)/controller-gen
else
CONTROLLER_GEN=$(shell which controller-gen)
endif

kustomize:
ifeq (, $(shell which kustomize))
	@{ \
	set -e ;\
	KUSTOMIZE_GEN_TMP_DIR=$$(mktemp -d) ;\
	cd $$KUSTOMIZE_GEN_TMP_DIR ;\
	go mod init tmp ;\
	go get sigs.k8s.io/kustomize/kustomize/v3@v3.5.4 ;\
	rm -rf $$KUSTOMIZE_GEN_TMP_DIR ;\
	}
KUSTOMIZE=$(GOBIN)/kustomize
else
KUSTOMIZE=$(shell which kustomize)
endif

.PHONY: code/sec
code/sec: $GOPATH/bin/gosec ## Run gosec
	gosec -severity medium --confidence medium -quiet $(PACKAGES)

$GOPATH/bin/gosec:
	go get -u github.com/securego/gosec/cmd/gosec

$GOPATH/bin/gotestsum:
	go get gotest.tools/gotestsum	

$GOPATH/bin/cover:
	go get golang.org/x/tools/cmd/cover	

# Generate bundle manifests and metadata, then validate generated files.
.PHONY: bundle
bundle: manifests
	operator-sdk generate kustomize manifests -q
	cd config/manager && $(KUSTOMIZE) edit set image controller=$(IMG)
	$(KUSTOMIZE) build config/manifests | operator-sdk generate bundle -q --overwrite --version $(VERSION) $(BUNDLE_METADATA_OPTS)
	operator-sdk bundle validate ./bundle

# Build the bundle image.
.PHONY: bundle-build
bundle-build:
	docker build -f bundle.Dockerfile -t $(BUNDLE_IMG) .

##############################
.PHONY: setup/travis
setup/travis:
	@echo Installing go
	@curl -Lo go.tar.gz ${GO_DOWNLOAD_URL} && tar -C /usr/local -xvzf  go.tar.gz
	@curl -Lo kubectl ${KUBECTL_DOWNLOAD_URL} && chmod +x kubectl && sudo mv kubectl /usr/local/bin/
	@echo Installing Kubectl
	@curl -Lo kubectl ${KUBECTL_DOWNLOAD_URL} && chmod +x kubectl && sudo mv kubectl /usr/local/bin/
	@echo Installing Minikube
	@curl -Lo minikube ${MINIKUBE_DOWNLOAD_URL} && chmod +x minikube && sudo mv minikube /usr/local/bin/
	@echo Booting Minikube up, see Travis env. variables for more information
	@mkdir -p $HOME/.kube $HOME/.minikube
	@echo Installing operator-sdk
	@curl -Lo operator-sdk ${OPERATOR_SDK_DOWNLOAD_URL} && chmod +x operator-sdk-${OPERATOR_SDK_VERSION}-x86_64-linux-gnu && sudo mkdir -p /usr/local/bin/ && sudo cp operator-sdk-${OPERATOR_SDK_VERSION}-x86_64-linux-gnu /usr/local/bin/operator-sdk && rm operator-sdk-${OPERATOR_SDK_VERSION}-x86_64-linux-gnu
	@touch $KUBECONFIG
	@minikube start --kubernetes-version=v1.18.1  --bootstrapper=kubeadm --extra-config=kubelet.authentication-token-webhook=true --extra-config=kubelet.authorization-mode=Webhook --extra-config=scheduler.address=0.0.0.0 --extra-config=controller-manager.address=0.0.0.0 --vm-driver=none
	@chown -R ${USER}: /home/${USER}/.minikube/
	sudo ./hack/modify_etc_hosts.sh "ucp.local"
	@minikube addons enable ingress

.PHONY: setup/kubebuilder
setup/kubebuilder: 
	# download kubebuilder and extract it to tmp
	curl -L https://go.kubebuilder.io/dl/2.3.1/${OS}/${ARCH} | tar -xz -C /tmp/
	# move to a long-term location and put it on your path
	# (you'll need to set the KUBEBUILDER_ASSETS env var if you put it somewhere else)
	sudo mv /tmp/kubebuilder_2.3.1_${OS}_${ARCH} /usr/local/kubebuilder
	export PATH=$PATH:/usr/local/kubebuilder/bin

#############################
.PHONY: setup/thirdparty
setup/thirdparty: 
	@echo "create namespace ucp"
	kubectl create namespace ucp
	#kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing.io_jaegers_crd.yaml
	#kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/service_account.yaml
	#kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role.yaml
	#kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/role_binding.yaml
	#kubectl apply -n ucp -f third-party/jaeger/operator.yaml
	#kubectl apply -n ucp -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/cluster_role.yaml
	#kubectl apply -n ucp -f third-party/jaeger/cluster_role_binding.yaml
	#kubectl apply -n ucp -f third-party/jaeger/jaeger.yaml
	#sleep 120
	#kubectl get -n ucp ingress
	@echo "install kube-prometheus"
	cd third-party/kube-prometheus && kubectl create -f manifests/setup; until kubectl get servicemonitors --all-namespaces; do date; sleep 1; done && kubectl create -f manifests/
	@echo "install cert-manager"
	kubectl apply -f third-party/cert-manager/cert-manager.yaml
	@echo "wait unitl all the third party containers are installed, up and running ..."
	until [[ $$count -gt 2 ]]; do count=$$(kubectl get pods -n cert-manager| grep Running | wc -l); sleep 1; done
	@sleep 10

.PHONY: setup/clusterdeploy
setup/clusterdeploy: setup/thirdparty deploy
	@echo "sleeping for 60 seconds to make sure operator containers are installed, up and running ..."
	@sleep 300

.PHONY: setup/uninstall
setup/uninstall:
	./uninstall.sh
	
