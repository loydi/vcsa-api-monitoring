#!/usr/bin/python3

import requests
from requests.auth import HTTPBasicAuth
import json
import argparse
import sys
import os
import urllib3
import datetime
date1 = datetime.datetime.utcnow() + datetime.timedelta(minutes=-15)
date2 = datetime.datetime.utcnow()
start_date = date1.strftime('%Y-%m-%dT%H:%M:%S.000Z')
end_date = date2.strftime('%Y-%m-%dT%H:%M:%S.000Z')


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--host_username", action="store", type=str)
    parser.add_argument("-p", "--host_password", action="store", type=str)
    parser.add_argument("-H", "--host", action="store", type=str)
    parser.add_argument("-t", "--type", action="store", type=str)
    parser.add_argument("-d", "--datastore", action="store", type=str)
    parser.add_argument("-f", "--filter", action="store", type=str)
    parser.add_argument("-w", "--warning", action="store", type=str)
    parser.add_argument("-c", "--ciritical", action="store", type=str)

    return parser.parse_args(sys.argv[1:])

def get_vcenter_health_status(api_url,args):
    resp = get_api_data(api_url,args)
    j = resp.json()
    return j

def get_vcenter_datastore_output(args,json):
    if not args.filter:
        c = False
        w = False
        for dst in json['value']: 
            percent = (float(dst['free_space'])/float(dst['capacity'])*100)
            print("Datastore name : {} / Datastore Free Space : {}  / Datastore Used : {:.2f}% | '{} Free Space'={};;;;".format(dst['name'],pretty_size(float(dst['free_space'])),percent,dst['name'],dst['free_space']))
            if args.warning and args.ciritical:
                if (percent >= int(args.warning)) and (percent < int(args.ciritical)):
                    sys.exit(1)
                elif percent >= float(args.ciritical):
                    sys.exit(2)
    else:
        for dst in json['value']: 
            if args.filter in dst['name']:
                percent = (float(dst['free_space'])/float(dst['capacity'])*100)
                print("Datastore name : {} / Datastore Free Space : {}  / Datastore Used : {:.2f}% | '{} Free Space'={};;;;".format(dst['name'],pretty_size(float(dst['free_space'])),percent,dst['name'],dst['free_space']))         
                
def pretty_size(bytes):
    """
        calculation file size
    """
    units = [
    (1<<50, ' PB'),
    (1<<40, ' TB'),
    (1<<30, ' GB'),
    (1<<20, ' MB'),
    (1<<10, ' KB'),
    (1, (' byte', ' bytes')),
]
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix

def auth_vcenter(host,username,password):
    #print('Authenticating to vCenter, user: {}'.format(username))
    resp = requests.post('https://{}/rest/com/vmware/cis/session'.format(host),auth=(username,password),verify=False)
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp.json()['value']

def get_api_data(req_url,args):
    sid = auth_vcenter(args.host,args.host_username,args.host_password)
    #print('Requesting Page: {}'.format(req_url))
    resp = requests.get(req_url,verify=False,headers={'vmware-api-session-id':sid})
    if resp.status_code != 200:
        print('Error! API responded with: {}'.format(resp.status_code))
        return
    return resp


def main():
    conf_file = "/usr/lib/nagios/plugins/cfg/conf.json"
    args = get_arguments()
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
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if args.type:
        if args.type == "storage":
            api_url ="https://{}/rest/appliance/health/{}".format(args.host,args.type)
            response = get_vcenter_health_status(api_url,args)
            if response['value'] == "green":
                print("OK : vCenter {} health : {}".format(args.type,response['value']))
                sys.exit(0)
            elif ((response['value'] == "orange") and (response['value'] == "yellow")):
                print("WARNING : vCenter {} health : {}".format(args.type,response['value']))
                sys.exit(1)
            elif response['value'] == "red":
                print("CRITICAL : vCenter {} health : {}".format(args.type,response['value']))
                sys.exit(2)
            else:
                print("UNKOWN : vCenter {} health : {}".format(args.type,response['value']))
                sys.exit(3)
        api_url ="https://{}/rest/appliance/monitoring/query?item.names={}&item.interval=MINUTES30&item.function=AVG&item.start_time={}&item.end_time={}".format(args.host,args.type,start_date,end_date)
        response = get_vcenter_health_status(api_url,args)
        percent_data = response['value'][0]['data'][0]
        if percent_data > args.ciritical:
            print("CRITICAL : vCenter {} is : {} | '{}'={};;;; ".format(args.type,percent_data,args.type,percent_data))
            sys.exit(2)
        elif percent_data > args.warning:
            print("WARNING : vCenter {} is : {} | '{}'={};;;; ".format(args.type,percent_data,args.type,percent_data))
            sys.exit(1)
        elif percent_data < args.warning:
            print("OK : vCenter {} is : {} | '{}'={};;;; ".format(args.type,percent_data,args.type,percent_data))
            sys.exit(0)
        else:
            print("UNKOWN : vCenter {} ".format(args.type))
            sys.exit(3)
    if args.datastore:
        if args.datastore == "ALL":
            api_url ="https://{}/rest/vcenter/datastore?filter.types=VMFS".format(args.host,args.type)
            response = get_vcenter_health_status(api_url,args)
            get_vcenter_datastore_output(args,response)
        else:
            api_url ="https://{}/rest/vcenter/datastore?filter.names={}&filter.types=VMFS".format(args.host,args.datastore)
            response = get_vcenter_health_status(api_url,args)
            get_vcenter_datastore_output(args,response)



if __name__ == "__main__":
    main()