#namespace that is used for deployment
NAMESPACE=ucp

#porcelain deployment resources directory
ES_DEPLOYMENT_DIR=./porcelain

#deploy porcelain resources
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/porcelain-storageclass.yml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/porcelain-persistentvolume.yml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/porcelain-pvc.yaml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/porcelain-service.yaml
kubectl -n $NAMESPACE apply -f $ES_DEPLOYMENT_DIR/porcelain-deployment.yaml
