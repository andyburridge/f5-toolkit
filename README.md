# f5-toolkit

Tools written in Anisble and Python to assist with F5 BIG-IP deployment and operations.

**Ansible Tools**
* create_adc_service.yml  
*Use to deploy a load balanced application and set of services to a BIG-IP device.*  
`ansible-playbook create_adc_service.yml -i example-hosts -e "group=example-group partition=example-partition"`  
example-hosts: Ansible inventory containing hosts that will make up the load balanced application.  
example-group: Ansible group_var file containing the required parameters for deploying the load balanced application.  
example-partition: The user partition on the BIG-IP into which the load balanced application should be deployed.  

* delete_adc_service.yml  
*Use to remove a load balanced application and set of services from a BIG-IP device.*  
`ansible-playbook delete_adc_service.yml -i example-hosts -e "group=example-group partition=example-partition"`  
example-hosts: Ansible inventory containing hosts that will make up the load balanced application.  
example-group: Ansible group_var file containing the required parameters for deploying the load balanced application.  
example-partition: The user partition on the BIG-IP into which the load balanced application should be deployed.  

&nbsp;  
**Python Tools**
*  get_vs_inventory.py  
*Use to get a full inventory of all the virtual servers on the BIG-IP (Virtual Servers/Pools/Monitors/Nodes), in .csv format.*
