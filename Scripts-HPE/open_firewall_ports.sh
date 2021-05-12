
# check if appsettings.json file exists
file="/opt/hpe/ansible/storage_management_services/hpeAnsibleAppsettings.json"
if [ ! -f "$file" ]
then
    echo "$0: File '${file}' not found."
fi

http_url=$(cat $file | grep HttpUrl | awk -F HttpUrl '{print $2 }' | awk -F , '{print $1 }')
https_url=$(cat $file | grep HttpsUrl | awk -F HttpsUrl '{print $2 }' | awk -F , '{print $1 }')

http_temp=`echo "$http_url" |  sed 's/"//g'`
https_temp=`echo "$https_url" |  sed 's/"//g'`

http_port=${http_temp: -4}
echo $http_port

https_port=${https_temp: -4}
echo $https_port

echo "Opening the ports $http_port and $https_port"

if [ -z "$(sudo netstat -tupln | grep $http_port)" ]; then
	/usr/bin/firewall-cmd --zone=public --add-port=$http_port/tcp --permanent 2> /dev/null
fi

if [ -z "$(sudo netstat -tupln | grep $https_port)" ]; then
	/usr/bin/firewall-cmd --zone=public --add-port=$https_port/tcp --permanent 2> /dev/null
fi

if [ -z "$(sudo netstat -tupln | grep 8444)" ]; then
	/usr/bin/firewall-cmd --zone=public --add-port=8444/tcp --permanent 2> /dev/null
fi

if [ -z "$(sudo netstat -tupln | grep 2030)" ]; then
	/usr/bin/firewall-cmd --zone=public --add-port=2030/tcp --permanent 2> /dev/null
fi

if [ -z "$(sudo netstat -tupln | grep 2031)" ]; then
  	/usr/bin/firewall-cmd --zone=public --add-port=2031/tcp --permanent 2> /dev/null
fi

/usr/bin/firewall-cmd --reload  2> /dev/null

