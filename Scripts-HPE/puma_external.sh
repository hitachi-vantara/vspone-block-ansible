#!/bin/bash

ip_address=$1
echo "IP address = $ip_address"
# generate puma.pem cert
echo quit | openssl s_client -showcerts -servername $ip_address -connect $ip_address:8444 > puma_$ip_address.pem

update-ca-trust force-enable

#echo "copy the certificate to ca-trust.."
mv -f puma_$ip_address.pem /etc/pki/ca-trust/source/anchors/

update-ca-trust extract

