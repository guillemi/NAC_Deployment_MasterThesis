"""
NAC deployment script - Configuration
Guillem Martínez-Illescas Ruíz
"""


import os
import json
from pathlib import Path
from dotenv import load_dotenv
import threading
import time

from conection import ping_device, conect

inicio = time.time()


env_path = Path('') / 'dwddw'

env_path = os.path.join(env_path)

if os.path.exists(env_path):
    load_dotenv(env_path)

load_dotenv(env_path)


user = X
passw = X

print("User: ",user,pawws)


def try_conect(current_ip_address):
    ping_result = ping_device(current_ip_address)
    print(ping_result)

    if ping_result:

        try:
            try:
                net_connect = conect(current_ip_address, user, passw, 1)
                print("connected on :" + current_ip_address)
                return net_connect
            except:
                net_connect = conect(current_ip_address, user, passw, 0)
                print("connected on :" + current_ip_address)
                return net_connect
        except:
            print("It is not possible to connect to device: " + current_ip_address)


def send_command_lines(txtname, net, interface):
    fil = "configs/" + txtname
    with open(fil) as f:
        commands_lines = f.read()
    config_lines = commands_lines.split('\n')

    if (interface == "0"):
        net.send_config_set(config_lines, cmd_verify=False, delay_factor=2)

    else:
        config_lines.insert(0, 'interface ' + interface)
        net.send_config_set(config_lines, cmd_verify=False, delay_factor=2)


    del config_lines[0]



def apply_dot1x_config(net, ip, apply, logica):
    if (not apply):
        if (logica == 1):

            send_command_lines('Global config IOS Newgen.txt', net, "0")
            print("To the Switch with IP " + ip + " applying config: Global config IOS - APAC-Primary-Newgen.txt")

        elif (logica == 2):
            send_command_lines('Global config IOS Legacy.txt', net, "0")
            print("To the Switch with IP " + ip + " applying config: Global config IOS - APAC-Primary-Legacy.txt")


def apply_aut_config(ip, net, interface, apply, check, logica):
    if (not apply):
        if (check == "Ready to apply"):
            if (logica == 1):
                send_command_lines('Interface config IOS-Newgen.txt', net, interface)
                print(
                    "To the switch with IP: " + ip + " at Interface: " + interface + " Applying Interface config IOS-Newgen.txt")
            if (logica == 2):
                send_command_lines('Interface config IOS-Legacy.txt', net, interface)
                print(
                    "To the switch with IP: " + ip + " at Interface: " + interface + " Applying Interface config IOS-Legacy.txt")





def run(i, ip_list, data):
    ip = ip_list[i]

    net = try_conect(ip)
    reason = data["Devices"][ip]["Reason"]
    os = data["Devices"][ip]["OS"]
    logica = 0
    if (reason == "Switch qualifies for NAC"):
        if (os == "New Generation"):
            logica = 1
        elif (os == "Old Generation"):
            logica = 2


    apply_dot1x_config(net, ip, data["Devices"][ip]["Global"][0]["Dot1x Authentication"], logica)
    print("apply_dot1x_config")

    if (logica != 0):
        for a in range(len(data["Devices"][ip]["Interface"])):
            interface = list(data["Devices"][ip]["Interface"][a].keys())[0]
            auto = data["Devices"][ip]["Interface"][a][interface]["Interface dot1x"]
            check = data["Devices"][ip]["Interface"][a][interface]["Base config checker"]

            apply_aut_config(ip, net, interface, auto, check, logica)
            print("apply_aut_config")
    send_command_lines('write_config.txt',net, '0')


def NAC_configuration(fichero):

    nombre = "output_data/" + fichero + "/" + fichero + ".json"
    with open(nombre) as json_file:
        data = json.load(json_file)

    ip_list = list(data["Devices"].keys())
    ips = []
    iterations = 3
    end = False
    cont = 0
    for i in ip_list:
        ip = i
        ips.append(ip)
        if cont == len(ip_list) - 1:
            end = True
        if (len(ips) > iterations or end):

            threads = list()
            print("Configuring this ip: ", ips)
            for ip in range(len(ips)):
                t = threading.Thread(target=run, args=(ip, ips, data))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()
            ips = []
        cont = cont + 1
