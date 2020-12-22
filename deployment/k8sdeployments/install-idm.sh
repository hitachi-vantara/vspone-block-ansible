#namespace that is used for deployment
NAMESPACE=ucp

#idm deployment resources directory
ES_DEPLOYMENT_DIR=./idm

#deploy idm resources
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/idm-storageclass.yml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/idm-persistentvolume.yml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/idm-pvc.yaml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/idm-service.yaml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/idm-deployment.yaml
