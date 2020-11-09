ansible-playbook -i hosts.ini get_storage_information_ps.yaml
ansible-playbook -i hosts.ini get_lun_info_ps.yaml -e "lun_id=5"


ansible-playbook -i hosts.ini create_present_lun.yaml -e "dynamic_pool_id=5 lun_size_GB=1 lun_name=test_Dra_004 hostgroup_name=ESX_37_106_Sanjeev storage_port=CL1-F"
ansible-playbook -i hosts.ini unpresent_delete_lun.yaml -e "lun_id=702 hostgroup_name=ESX_37_106_Sanjeev storage_port=CL1-F"

