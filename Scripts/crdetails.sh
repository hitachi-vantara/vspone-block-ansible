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
"

getCRs() {
	NAMESPACE=$1
	DOMAIN=$2
	echo "Getting CRDs and CRs in namespace $NAMESPACE domain $DOMAIN"

	CRDS=$(kubectl api-resources --verbs=list --namespaced -o name | grep "$DOMAIN")
	echo "$CRDS" > CRDs.list

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
		mkdir $i >/dev/null 2>&1
		kubectl get -n $NAMESPACE $i > $i/$i.crs.list

		# skip facts on kubectl describe
		if echo $FACTSLIST | grep "$i"  >/dev/null 2>&1
		then
			continue
		fi

		for j in $CRS
		do
			echo "kubectl describe on CR: $i $j"
			kubectl describe -n $NAMESPACE $i $j > $i/$j.yaml
			# kubectl get -n $NAMESPACE $i $j -o json > $i/$j.json
		done
	done

	echo "Done getting CRDs and CRs"
	echo
}

NSP=${1:-"ucp"}
DIR=${2:-"."}

# rm -rf cr_details >/dev/null 2>&1
# mkdir cr_details >/dev/null 2>&1
# cd cr_details
cd $DIR

getCRs $NSP "ucp.hitachivantara.com"
