sh ../deploy/crds/deploy_crds.sh
kubectl apply -f ../isp/infra_cr.yaml
kubectl apply -f ../storagesystems/storage-415056.cr.yaml
kubectl apply -f ../ucpsystems/ucp.hitachivantara.com_v1alpha1_ucpsystem_cr.yaml
