#namespace that is used for deployment
NAMESPACE=ucp

#elasticsearch deployment resources directory
ES_DEPLOYMENT_DIR=./elasticsearch

#delete elasticsearch resources
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/es-statefulset.yml
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/es-service.yml
kubectl -n $NAMESPACE delete pvc -l service=elasticsearch
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/es-persistentvolume.yml
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/es-storageclass.yml
