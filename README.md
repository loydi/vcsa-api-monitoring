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

## Read Config 

It reads json file in "conf_file".  
```python
  conf_file = "/usr/lib/nagios/plugins/cfg/conf.json"
    try:
        with open(conf_file) as json_data_file:
            try:
                data = json.load(json_data_file)
                args.host = data['host']
                args.host_username = data['user']
                args.host_password = data['passwd']
            except ValueError:
                print("Config file is corrupt")    
    except OSError:
        print("Can't open Config file")
        if (not args.host) and (not args.host_username) and (not args.host_password):
            print("You must add credentials")
            sys.exit(2)
```
