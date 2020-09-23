# vcsa-api-monitoring
VCSA api monitoring via python

## Usage
```
  Usage: check_vcsa.py </br>
    [-u    <--host_username> ]   # api user name </br>
    [-p    <--host_password> ]   # pasword </br>
    [-H    <--host>          ]   # vcsa host adress </br>
    [-t    <--type>          ]   # Select "load,mem,storage" </br>
    [-d    <--datastore>     ]   # Select specific datastore or ALL </br>
    [-f    <--filter>        ]   # Filter datastore name</br>
    [-w    <--warning>       ]   # Warning point</br>
    [-c    <--ciritical>     ]   # Critical point</br>
  ```
  ## Examples
  ```bash 
    --> #check_vcsa.py -H vcsa -u administrator@vsphere.local -p 1234567 -t load
    --> #check_vcsa.py -H vcsa -u administrator@vsphere.local -p 1234567 -d vcsa_datastore
    --> #check_vcsa.py -H vcsa -u administrator@vsphere.local -p 1234567 -d ALL -f INFRA
    --> #check_vcsa.py -t load    --> host and auth. reads on cfg file.
  ```
