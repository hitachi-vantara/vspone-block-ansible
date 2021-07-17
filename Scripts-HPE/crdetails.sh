#!/usr/bin/env bash

# get all CR details

FACTSLIST="
datacenterfacts.ucp.hitachivantara.com
esxidatastorefacts.ucp.hitachivantara.com
esxihostfacts.ucp.hitachivantara.com
ethernetswitchfacts.ucp.hitachivantara.com
fcswitchfacts.ucp.hitachivantara.com
firmwarebundlefacts.ucp.hitachivantara.com
freelunfacts.ucp.hitachivantara.com
hostgroupfacts.ucp.hitachivantara.com
lunfacts.ucp.hitachivantara.com
lunperformancefacts.ucp.hitachivantara.com
paritygroupfacts.ucp.hitachivantara.com
poolperformancefacts.ucp.hitachivantara.com
portperformancefacts.ucp.hitachivantara.com
quorumdiskfacts.ucp.hitachivantara.com
remotereplicationfacts.ucp.hitachivantara.com
resourcegroupfacts.ucp.hitachivantara.com
serverfacts.ucp.hitachivantara.com
storageharddrivefacts.ucp.hitachivantara.com
storagepoolfacts.ucp.hitachivantara.com
storageportfacts.ucp.hitachivantara.com
storagesystemfacts.ucp.hitachivantara.com
vsanfacts.ucp.hitachivantara.com
generatelogbundles.ucp.hitachivantara.com
getalllogbundleinfoes.ucp.hitachivantara.com
"

getCRs() {
	NAMESPACE=$1
	DOMAIN=$2
	echo "Getting CRDs and CRs in namespace $NAMESPACE domain $DOMAIN"

	CRDS=$(kubectl api-resources --verbs=list --namespaced -o name | grep "$DOMAIN")
	echo "$CRDS" > k8s_info/CRDs.list

	echo "Skipping CRDs that don't have CR running"

	for i in $CRDS "configmaps"
	do
		CRS=$(kubectl get -n $NAMESPACE $i 2>/dev/null | tail -n +2 | sed 's/\s.*//g')
		if [ "$CRS" == "" ]
		then
			# echo "No CR for $i"
			continue
		fi

		echo "Getting CR list of $i"
		mkdir k8s_info/$i >/dev/null 2>&1
		kubectl get -n $NAMESPACE $i > k8s_info/$i/$i.crs.list

		# skip facts on kubectl describe
		if echo $FACTSLIST | grep "$i"  >/dev/null 2>&1
		then
			continue
		fi

		for j in $CRS
		do
			echo "kubectl describe on CR: $i $j"
			kubectl describe -n $NAMESPACE $i $j > k8s_info/$i/$j.yaml
			# kubectl get -n $NAMESPACE $i $j -o json > $i/$j.json
		done
	done

	echo "Done getting CRDs and CRs"
	echo
}

mkdir k8s_info
NSP=${1:-"ucp"}
DIR=${2:-"."}

# rm -rf cr_details >/dev/null 2>&1
# mkdir cr_details >/dev/null 2>&1
# cd cr_details
cd $DIR

getCRs $NSP "ucp.hitachivantara.com"

mkdir k8s_info/pods
cd k8s_info/pods

echo "kubectl get pods -n ucp"
kubectl get pods -n ucp > pods.txt

for n in $(kubectl get pods -n ucp | awk -F 'NAME' '{print $1}' | awk '{ print $1 }')
do
    echo "kubectl describe pod $n -n ucp"
	kubectl describe pod $n -n ucp > $n.txt
    # do something on $n below, say count line numbers
    # wc -l "$n"
done

cd ..

echo "collecting memory info"
cat /proc/meminfo > memory_info.txt

free -h > memory_info_1.txt

df -h > disk_info.txt

echo "collecting cpu usage"
top -n 1 > cpu_usage.txt

sdi=$(kubectl get pods -n ucp | awk -F 'NAME' '{print $1}' | awk '{ print $1 }' | grep sdi-gateway-block)
kubectl -n ucp  exec -it $sdi -- /usr/sbin/fdisk -l > gateway_dev.txt

kubectl exec -it $sdi -n ucp -- bash -c "ls /dev/sd* | /HORCM/usr/bin/inqraid -CLI -fx" > gateway_cmd_dev.txt

cd ..

tar -czvf k8s_info.tar.gz k8s_info
rm -rf k8s_info
echo
echo "Done collecting info"
