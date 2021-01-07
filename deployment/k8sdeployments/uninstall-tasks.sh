#namespace that is used for deployment
NAMESPACE=ucp

#tasks deployment resources directory
ES_DEPLOYMENT_DIR=./tasks

#un-deploy tasks resources
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/tasks-deployment.yaml
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/tasks-service.yaml
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/tasks-pvc.yaml
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/tasks-persistentvolume.yml
kubectl -n $NAMESPACE delete -f $ES_DEPLOYMENT_DIR/tasks-storageclass.yml
