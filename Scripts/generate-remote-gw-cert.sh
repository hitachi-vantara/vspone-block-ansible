#!/bin/bash
 
#Required: ip address of the external gateway server
domain=$1
ip_address=$domain
 
if [ -z "$domain" ]
then
    echo "Argument not present."
    echo "Usage $0 [gateway server ip address]"
 
    exit 1
fi
 
#echo "Generating key request for $domain"
openssl s_client -showcerts -servername $ip_address -connect $ip_address:8444 > puma.$ip_address.pem 
cp -f puma.$ip_address.pem /etc/pki/ca-trust/source/anchors
update-ca-trust extract
