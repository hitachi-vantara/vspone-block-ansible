ka isp.yaml -n ucp
ka vcenter.yaml -n ucp
ka storage30078.yaml -n ucp
ka server11.64.yaml -n ucp
cd ../syncesxihostuplinkvlan/
ka configmap.yaml -n ucp
ka scp-credentials.yaml -n ucp
ka eth59.24.yaml -n ucp
cd ../fcswitch/
ka cr.59.34.yaml -n ucp
cd ../createdatastore/
sleep 10
ka ucp4.yaml -n ucp
sleep 120
cd ../lun
ka lunfree.yaml -n ucp
cd ../hostgroup
ka hg-120id.yaml -n ucp
sleep 60

kg service -n ucp
kg ssf -n ucp
kg lun -n ucp
kg hg -n ucp
