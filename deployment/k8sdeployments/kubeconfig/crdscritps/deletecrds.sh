

#getall crds

#allcrds="`kubectl get crds | grep ucp | awk -F ' ' '{print $1}' | grep -v 'infrastructuresparepools.ucp.hitachivantara.com' | grep -v 'ucpsystems.ucp.hitachivantara.com'` "
allcrds="`kubectl get crds | grep ucp.hitachivantara.com | awk -F ' ' '{print $1}' `"
echo $allcrds
for cr in $allcrds
do 
	echo $cr
        kubectl get $cr -o yaml --namespace=ucp > delme.yaml
        kubectl patch -f ./delme.yaml -p '{"metadata":{"finalizers":[]}}' --type=merge
	kubectl delete $cr -n ucp --all 
        kubectl delete crd $cr -n ucp 
done
leftover="`kubectl get crds | grep ucp | awk -F ' ' '{print $1}'`"
echo $leftover
