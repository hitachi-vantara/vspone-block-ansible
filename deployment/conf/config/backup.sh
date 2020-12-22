cd /opt/jboss/keycloak/bin
./kcadm.sh config truststore --trustpass password /home/keycloak.jks
./kcadm.sh config credentials --server https://keycloak:8081/auth --realm master --user admin --password admin
./kcadm.sh create realms -s realm=ucpsystem -s id="ucpsystem" -s enabled=true -o
./kcadm.sh create clients -r ucpsystem -s clientId=ucpadvisor  -s id="ucpadvisor" -s enabled=true -s directAccessGrantsEnabled=true -s publicClient=true
./kcadm.sh create users -s username=ucpadmin -s enabled=true -r ucpsystem
./kcadm.sh set-password -r ucpsystem --username ucpadmin --new-password ucpadmin
./kcadm.sh create roles -r ucpsystem -s name=ucpAdminRole -s 'description=Admin user with all permissions'

./kcadm.sh create roles -r ucpsystem -s name=UcpAdvisorStorageAdmin -s 'description=Admin user with only Storage resources permissions'
./kcadm.sh create roles -r ucpsystem -s name=UcpAdvisorNetworkAdmin -s 'description=Admin user with only Network resources permissions'
./kcadm.sh create roles -r ucpsystem -s name=UcpAdvisorFibreChannelAdmin -s 'description=Admin user with only Fibre Channel resources permissions'
./kcadm.sh create roles -r ucpsystem -s name=UcpAdvisorComputeAdmin -s 'description=Admin user with only Compute resources permissions'
./kcadm.sh create roles -r ucpsystem -s name=UcpAdvisorReadOnly -s 'description=User with Read Only permissions to all resources'

# Create read only group and assign read only role to it
./kcadm.sh create groups -r ucpsystem -s name=UcpAdvisorReadOnlyGroup
./kcadm.sh add-roles -r ucpsystem --gname UcpAdvisorReadOnlyGroup --rolename UcpAdvisorReadOnly

./kcadm.sh create -r ucpsystem clients/ucpadvisor/protocol-mappers/models -b '{
"protocol":"openid-connect",
"config":{
"full.path":"false",
"id.token.claim":"true",
"access.token.claim":"true",
"userinfo.token.claim":"true",
"claim.name":"groups"
},
"name":"groups",
"protocolMapper":"oidc-group-membership-mapper"
}'

./kcadm.sh create clients/ucpadvisor/roles -r ucpsystem -s name=ucpAdvisorClientRole
./kcadm.sh add-roles --uusername ucpadmin  --rolename ucpAdminRole -r ucpsystem
./kcadm.sh add-roles -r ucpsystem --uusername ucpadmin --cclientid ucpadvisor --rolename ucpAdvisorClientRole
./kcadm.sh add-roles -r ucpsystem --uusername ucpadmin --cclientid realm-management --rolename manage-realm --rolename manage-users
./kcadm.sh update realms/ucpsystem -s ssoSessionIdleTimeout=3600
./kcadm.sh update realms/ucpsystem -s accessTokenLifespan=3600
./kcadm.sh update realms/ucpsystem -s defaultRoles=[] #set the default role list empty

./kcadm.sh delete roles/offline_access -r ucpsystem  #deleting role
./kcadm.sh delete roles/uma_authorization -r ucpsystem 

#Adding UcpAdvisorReadOnly to default roles
./kcadm.sh update realms/ucpsystem/ -f - << EOF
{ "defaultRoles" : [ "UcpAdvisorReadOnly"] }
EOF

#Assigning view-users role in Default client role
clientId=$(./kcadm.sh get clients -r ucpsystem --fields  id,clientId | grep -B 1 realm-management | grep id | cut -d":" -f2 | tr --d , | sed 's/"//g' | sed 's/ //g')
./kcadm.sh update realms/ucpsystem/clients/$clientId -f - << EOF
{ "defaultRoles" : [ "view-users", "view-realm"] }
EOF


# Move read only group to default group
groupId=$(./kcadm.sh get realms/ucpsystem/groups?search=UcpAdvisorReadOnlyGroup | grep id | cut -d ":" -f2 | tr --d , | sed 's/"//g' | sed 's/ //g' )
./kcadm.sh update realms/ucpsystem/default-groups/groupId -f - << EOF
{"realm":"ucpsystem","groupId": " + $groupId + " }
EOF


