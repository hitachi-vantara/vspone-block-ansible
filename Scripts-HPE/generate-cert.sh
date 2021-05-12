#!/bin/bash
 
#Required
domain=$1
commonname=$domain
 
#Change to your company details
country=US
state=CA
locality="Santa Clara"
organization="Hewlett-Packard"
organizationalunit=HPE
#email=lakshmi.sarma@hitachivantara.com
 
#Optional
password=e401f032-eb38-4694-b6d6-6a3932cf0a73
 
if [ -z "$domain" ]
then
    echo "Argument not present."
    echo "Useage $0 [common name]"
 
    exit 1
fi
 
#echo "Generating key request for $domain"
 
#Generate a key
openssl genrsa -des3 -passout pass:$password -out $domain.key 2048 -noout 
 
#Remove passphrase from the key. Comment the line out to keep the passphrase
#echo "Removing passphrase from key"
openssl rsa -in $domain.key -passin pass:$password -out $domain.key 
 
#Create the CSR request
openssl req -new -key $domain.key -out $domain.csr -passin pass:$password \
    -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname" 
    
#Generating a Self-Signed Certificate
openssl x509 -req -days 1095 -in $domain.csr -signkey $domain.key -out $domain.pem 

#Configure and restart PUMA with the new certs
/usr/bin/puma_adm --configure --key $domain.key --cert $domain.pem -s

#Configure and install pkcs12 cert for VI Service
vipath=/opt/hpe/ansible/vi_service/VIService-ApacheLicense
openssl pkcs12 -export -out keystore.p12 -in $domain.pem -inkey $domain.key -passin pass:$password -passout pass:$password -name ucp
/bin/cp keystore.p12 $vipath
service vi restart
