DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for file in $DIR/*.yaml
do
    if [[ "$file" == *"ucp.hitachivantara.com_storagesystems_crd"* ]]; then
        echo "skip" $file
        continue
    elif [[ "$file" == *"ucp.hitachivantara.com_ucpsystems_crd"* ]]; then
        echo "skip" $file
        continue
    fi
    echo "clean up cr" $file
    kubectl delete -f $file
done