"""
NAC deployment script
Guillem Martínez-Illescas Ruíz

Script Steps: 
Inputs:
check: (SiteID, vlan List)

2 options:

(1) Execute NAC_discovery alone

(2) Execute Nac configuration, that checks the config and aplies the configuration to make sure all the interfaces has been configured.

"""


import json
import time
from NAC_discovery import NAC_discovery
from NAC_config import NAC_configuration
from datetime import datetime
import os


now = datetime.now()
date_time = "_" + str(now.day) + "_" + str(now.month) + "_" + str(now.year) + "_" + str(now.hour) + "_" + str(now.minute) + "_" + str(now.second)

with open('input.json') as json_file:
    data = json.load(json_file)

def Stard_Discovery():

    inicio = time.time()
    print("Starting NAC Discovery","\n")
    print(" ... ","\n")

    siteID = 'Prueba'
    folder = "output_data/" + siteID + date_time
    os.makedirs(folder)

    NAC_discovery(date_time,data["ip_list"],data["vlan_list"],siteID)

    fin = time.time()
    ex_time = fin-inicio
    print("Execution Time: ",ex_time)

def Stard_Configuration():
    inicio = time.time()
    print("Starting NAC Configuration","\n")
    print(" ... ","\n")
    siteID = 'Prueba'
    nombre = siteID + date_time
    folder = "output_data/" + nombre
    os.makedirs(folder)


    d_data = {"Devices": {}}
    print("nac_discovery on ",date_time)
    print("nac_config on ",nombre)
    print("\n")
    time.sleep(1)
    NAC_discovery(date_time,data["ip_list"],data["vlan_list"],siteID)
    time.sleep(0.5)
    NAC_configuration(nombre)
    time.sleep(1)


    fin = time.time()
    ex_time = fin-inicio
    print("Execution Time: ",ex_time)


        
def menu():
    print("\n")
    print("Instructions NAC DEPLOYMENT ","\n")
    print(" On the stard_input.json file you have to initialize the sites you want to configure, also adding the NAC Vlans ","\n")
    print("Options to do: ","\n")
    print(" - To start NAC discovery only press 1 and enter ","\n")
    print(" - To start full NAC process (discovery + configuration) press 2 and enter ","\n")
    ToDo = input()
    if(ToDo == "1"):
        print("Executing NAC Discovery","\n")
        print(" ... ","\n")
        Stard_Discovery()


    elif(ToDo == "2"):
        print("Executing full NAC process (discovery + configuration)","\n")
        print(" ... ","\n")
        Stard_Configuration()



menu()
