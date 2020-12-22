#namespace which will be used for deployment
NAMESPACE=ucp

#deployment files folder
DEPLOYMENT_FILE_FOLDER=../k8sdeployments

#delete all deployments present in k8sdeployment folder for porcelain microservices
kubectl -n $NAMESPACE delete -f $DEPLOYMENT_FILE_FOLDER

sh ./uninstall-porcelain.sh
sh ./uninstall-tasks.sh
sh ./uninstall-idm.sh
