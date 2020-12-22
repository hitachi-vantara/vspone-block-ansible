#namespace which will be used for deployment
NAMESPACE=ucp

#deployment files folder
DEPLOYMENT_FILE_FOLDER=/k8sdeployments

#kong setup files
KONG_SETUP_FOLDER=/kong/setup

#kong custome changes
KONG_CUSTOMIZATION_FILE_FOLDER=/kong/customization

#create namespace if not present
kubectl create namespace $NAMESPACE

#apply all deployments present in k8sdeployment folder for porcelain microservices
kubectl -n $NAMESPACE apply -f $DEPLOYMENT_FILE_FOLDER

sh ./install-idm.sh
sh ./install-tasks.sh
sh ./install-porcelain.sh

#admin cluster role binding creation
kubectl apply -f /clusterrolebindingfiles

#rbac cluster role binding creation
kubectl apply -f /rbac

#create secret for kong gateway
kubectl create secret tls porcelain-secret --cert=/home/conf/certs/server.crt --key=/home/conf/certs/server.key

#create kong setup
kubectl apply -f $DEPLOYMENT_FILE_FOLDER$KONG_SETUP_FOLDER

#create kong customization
kubectl apply -f $DEPLOYMENT_FILE_FOLDER$KONG_CUSTOMIZATION_FILE_FOLDER -n $NAMESPACE

#wait till keycloak pod is up
echo wait till keycloak setup is up..Please Ignore follwing connection refused messages

# Day 0 script for keycloak initialization
COUNT=1
while [ $COUNT != 0 ] && [ $COUNT != 20 ]
do
   curl --connect-timeout 60 --max-time 60 https://keycloak:8081/auth/realms/master -k
   if [ 0 == $? ]; then
        kubectl exec $(kubectl get pod -l "app=keycloak" -o jsonpath='{.items[0].metadata.name}' -n $NAMESPACE) /bin/bash /home/keycloakSetup.sh -n $NAMESPACE
        COUNT=0
   else
      COUNT=$(( COUNT+1 ))
      sleep 10
   fi;
done;
if [ $COUNT == 20 ]; then
  echo; echo deployment unsuccessful
  exit 1
else 
  echo; echo deployment successful
  exit 0
fi;
