"""
Extrct device information script
2022
Guillem Martínez-Illescas Ruíz
guille2299@gmail.com
Network and Software Engineer

"""

import re
import json
import os

from datetime import datetime

from ciscoconfparse import CiscoConfParse

from conection import ping_device,conect


user = X
passw = X

int_dic= {}


d_data = {}


d_data["Devices"] = {}






def get_version(version):

    num = ""
    for i in range(len(version)):
        if(version[i] == "("):
            break
        else:
            num = num + version[i]
    return float(num)


def logics(supported_model,supported_version_Legacy,supported_version_New,typ_correcto,ping,con,is_model,is_version,not_supported_version):
    ret = True
    IOS = "-"
    

    if(not ping):
        ret = False
        reason = "Device not reachable"
    else:
        if(not con):
            ret = False
            reason = "Device reachable by ping but authentication fails"
        else:
            if(not is_model):
                ret = False
                reason = "Switch is an access switch but it is not in catalog, please add it in supported or not supported"
            if(not is_version):
                ret = False
                reason = "Switch is an access switch but the ios is not in catalog, please add it in supported or not supported"
                IOS = "Not in catalog"
            if(not_supported_version):
                ret = False
                reason = "Switch is an access switch but the ios is not supported, please upgrade to support NAC"
                IOS = "Not Supported"
            else:
                if(typ_correcto):
                    if(supported_model):
                        if(supported_version_Legacy or supported_version_New):
                            ret = True
                            reason = "Switch qualifies for NAC"
                            if(supported_version_New):
                                IOS = "New Generation"
                            if(supported_version_Legacy):
                                IOS = "Old Generation"
                            
                        else:
                            ret = False
                            reason =  "Please upgrade to support NAC"
                            IOS = "Not supported IOS"
                    else:
                        ret = False
                        reason = "Not supported NAC"


    return ret,reason,IOS

def is_available(model,version,typ,ping,con):
    supported_model = False
    supported_version_New = False
    supported_version_Legacy = False
    is_model = True
    is_version = True

    

    with open('supported.json') as json_file:
        data = json.load(json_file)

    if(typ == "Switch - Access"):
        typ_correcto = True
    else:
        typ_correcto = False

    
    if(model in data["Supported Model"]):
        supported_model = True
    elif(model in data["Not Supported Model"]):
        supported_model = False
    else:
        is_model = False

    if(version in data["Supported IOS Newgen"]):
        supported_version_New = True
    else:
        supported_version_New = False
    if(version in data["Supported IOS Legacy"]):
        supported_version_Legacy = True
    else:
        supported_version_Legacy = False

    if(version in data["Not Supported IOS"]):
        not_supported_version = True
    else:
        not_supported_version = False

    if(not supported_version_Legacy):
        if(not supported_version_New):
            is_version = False

    
    ret,reason,IOS = logics(supported_model,supported_version_Legacy,supported_version_New,typ_correcto,ping,con,is_model,is_version,not_supported_version)

    

    return ret,reason,IOS

def up_to_json(date_time,siteID,charge):
    folder = "output_data/" + siteID + date_time 
    file_name = folder + "/" + siteID + date_time + ".json"
    with open(file_name , 'w') as file:
        json.dump(charge, file, indent=4)


def to_json(date_time,ip,version,model,interface,vlan,dot1x,auto,country,typ,os,ping,con,siteID,bcc):

    available,reason,IOS = is_available(model,version,typ,ping,con)

    try:
        d_data["Devices"][ip]["Device Type"] = typ
    except: 
        d_data["Devices"][ip] = {}
        d_data["Devices"][ip]["Device Type"] = typ
    d_data["Devices"][ip]["Model"] = model
    d_data["Devices"][ip]["Version"] = version
    d_data["Devices"][ip]["OS"] = IOS
    d_data["Devices"][ip]["Is Available"] = available
    d_data["Devices"][ip]["Reason"] = reason

    d_data["Devices"][ip]["Global"] = []
    d_data["Devices"][ip]["Global"].append({})
    d_data["Devices"][ip]["Global"][0]["Dot1x Authentication"] = dot1x
    
    try:
        d_data["Devices"][ip]["Interface"].append({interface: {"Vlan ID": vlan,"Interface dot1x": auto,"Base config checker": bcc} })
    except:
        d_data["Devices"][ip]["Interface"] = []
        d_data["Devices"][ip]["Interface"].append({interface: {"Vlan ID": vlan,"Interface dot1x": auto,"Base config checker": bcc} })

        
    
    up_to_json(date_time,siteID,d_data)





def read_data(date_time,ip,version,model,interface,vlan,dot1x,aut,country,typ,os,ping,con,siteID,bcc):
    
    to_json(date_time,ip,version,model,interface,vlan,dot1x,aut,country,typ,os,ping,con,siteID,bcc)

 
def get_interfaces_config(config,interface):
    splited = config.split("\n")
    for i in range(len(splited)):
        if(splited[i] == "interface "+ interface):
            result = []
            for a in range (i+1,len(splited)):
                if(splited[a] == "!"):
                    break
                else:
                    result.append(splited[a])

            return result

def get_model_and_version(net_connect):

    config = net_connect.send_command('show version')

    cisco_cfg = CiscoConfParse(config.splitlines())

    for intf_obj in cisco_cfg.find_objects('Model number'):
        
        s_a = intf_obj.text

    for intf_obj in cisco_cfg.find_objects('Model Number'):
        
        s_a = intf_obj.text

    index = s_a.find(":")

    fin = ""
    for i in range(index+2,len(s_a)):
        fin = fin + s_a[i]
    
    print("Model: " + fin)

    regex_version = re.compile(r'Cisco\sIOS\sSoftware.+Version\s([^,]+)')
    version = regex_version.findall(config)
    print("Switch Version: " + version[0]) 

    return version[0],fin

def interface_logic(acces_vlan,mode):
    if(acces_vlan):
        if(mode):
            return "Ready to apply"
        else:
            return " Interface qualifies, but doesn't have switchport mode access, apply manually"
    else:
        return "Interface not applicable for NAC"



def run(date_time,vlan_list,ip,net_connect,country,typ,ping,con,siteID):
    for o in range(len(vlan_list)):
        int_dic[vlan_list[o]] = []

    version,model = get_model_and_version(net_connect)

    net_connect.send_command("term len 0")
    run_config = net_connect.send_command("show run")
    cisco_cfg = CiscoConfParse(run_config.splitlines())


    
    try:
        for intf_obj in cisco_cfg.find_objects('^dot1x system-auth-control'):
        
            s_a = intf_obj.text

        if (s_a == "dot1x system-auth-control"):
            print("authentication auto: " + "True") 
            auth_control = True
        else:
            auth_control = False
    except:
        auth_control = False

    
    
    pattern = r'^\sswitchport\saccess\svlan\s' 
    inter = [obj.text for obj in cisco_cfg.find_objects(r"^interf") if obj.re_search_children(pattern)]
    

    for i in range(len(inter)):
        
        current = inter[i].split(' ')
        #print(current)
        if(current[0]== "interface"):
            interface_config_list = get_interfaces_config(run_config,current[1])
            #print(interface_config_list)
            mode = False
            for a in range(len(interface_config_list)):
                
                autentication = False
                

                for c in range(len(interface_config_list)):
                    if(interface_config_list[c] == " switchport mode access"):
                        mode = True
                
                #print(interface_config_list[a])

                for b in range(len(vlan_list)):
                    acces_vlan = False
                    if(interface_config_list[a] == " switchport access vlan " + vlan_list[b]):
                        acces_vlan = True
                        try: 
                            com = '^interface ' + current[1]
                            for intf_obj in cisco_cfg.find_objects_w_child(com, '^\s+authentication open'):
                                print("Autentication auto on: " + intf_obj.text) 
                                ac = intf_obj.text
                                if(current[1] == ac.split()[1]):
                                    is_in = intf_obj.text
                            access_var = is_in 
                            if(access_var.split()[1] == current[1]):
                                autentication = True
                        except: 
                            autentication = False  
                        bcc = interface_logic(acces_vlan,mode)
                       
                        if(autentication == True):
                            bcc = "Nac Applied"

                        int_dic[vlan_list[b]].append([current[1],autentication])
                        read_data(date_time,ip,version,model,current[1],vlan_list[b],auth_control,autentication,country,typ,"IOS",ping,con,siteID,bcc)
                        print("match")
                    


    
def catch_device_info(date_time,vlan_list,current_ip_address,country,typ,siteID):

    ping = False
    con = True
    
    ping_result = ping_device(current_ip_address)
    print(ping_result)

    if not ping_result:
        read_data(date_time,current_ip_address,"-","-","-","-","-","-","-","-","-",ping,False,siteID,"-")
    else:
        ping = True
        
        try:

            net_connect = conect(current_ip_address,user,passw,1)
            run(date_time,vlan_list,current_ip_address,net_connect,country,typ,ping,con,siteID)

        except:
            print("La ip " + current_ip_address + " no se pudo conectar")
            con = False
            read_data(date_time,current_ip_address,"-","-","-","-","-","-","-","-","-",ping,con,siteID,"-")




def NAC_discovery(date_time,ip_list,vlan_list,siteID):

    for ip in ip_list:
        catch_device_info(date_time,vlan_list,ip,"Barcelona", "Switch - Access", siteID)




