#namespace that is used for deployment
NAMESPACE=ucp

#elasticsearch deployment resources directory
ES_DEPLOYMENT_DIR=./elasticsearch

#deploy elasticsearch resources
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/es-storageclass.yml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/es-persistentvolume.yml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/es-service.yml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/es-statefulset.yml
