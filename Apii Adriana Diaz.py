from netmiko import ConnectHandler
from getpass import getpass
import netmiko as nm
import json


def ospf_table_f(device):

    net_connect = ConnectHandler(**device)

    output = net_connect.send_command('show cdp neighbors')

    lines = output.split('\n')

    print('Device ID | Local Interface | Neighbor Device ID | Neighbor Interface')
    print('----------+----------------+-------------------+--------------------')

    for line in lines:
        parts = line.split()

        if len(parts) >= 4 and parts[0] != 'Device' and parts[0] != 'Total':
            print('{:10} | {:14} | {:18} | {:20}'.format(parts[0], parts[1], parts[2], parts[3]))


def mac_table_f(device):

    net_connect = ConnectHandler(**device)

    output = net_connect.send_command('show mac address-table')

    lines = output.split('\n')

    print('VLAN | MAC Address | Port')
    print('-----+-------------+-----')

    for line in lines:
        parts = line.split()

        if len(parts) >= 3 and parts[0].isdigit() and parts[1] != '*':
            print('{:4} | {:11} | {:4}'.format(parts[0], parts[1], parts[3]))


def vlan_c(device):

    vlan_name = input('Enter the VLAN name: ')
    net_connect = ConnectHandler(**device)
    net_connect.config_mode()
    net_connect.send_command('vlan ' + vlan_name)
    net_connect.send_command('write memory')
    net_connect.exit_config_mode()

    output = net_connect.send_command('show vlan')

    lines = output.split('\n')

    print('VLAN | Name')
    print('-----+-----')

    for line in lines:
        parts = line.split()

        if len(parts) >= 2 and parts[0].isdigit() and parts[0] != 'VLAN':

            print('{:4} | {}'.format(parts[0], parts[1]))


def ftp_run(device):

    ftp_server_ip = input("Enter the IP address of the FTP server: ")
    username = input("Enter your username: ")
    password = getpass("Enter your password: ")

    net_connect = ConnectHandler(**device)
    net_connect.send_command(f"copy ftp://{ftp_server_ip}/startup-config startup-config")


def mac_find(device):
    x = input("\nINGRESE LA MAC: ")

    x = x.lower()
    x = x.replace("-","")

    x = list(x)
    x.insert(4,".")
    x.insert(9,".")

    x = "".join(x)
    print("")

    #conexion ssh
    ssh = nm.ConnectHandler(**device)             
    ssh.enable()
    nombre=""

    while not nombre:

        output = ssh.send_command("show mac address-table",use_textfsm = True)
        output= (json.dumps(output, indent = 2))
        output= json.loads(output)

        for mac in range(len(output)):
            if x == (output[mac]['destination_address']):
                puerto_mac = (output[mac]['destination_port'])[0]
            else: pass

        output2 = ssh.send_command("show cdp neighbors detail",use_textfsm = True)
        output2= (json.dumps(output2, indent = 2))
        output2= json.loads(output2)
        print(output2)

        for mac in range(len(output2)):
            puertov = (output2[mac]["remote_port"])

            a=(puertov[0:2])
            b=(puertov[12:])

            puerto=a+b

        (output2[mac]["local_port"])=puerto

        for ve in range(len(output2)):
            puertov = (output2[ve]["local_port"])
            try:
                if puertov == puerto_mac:
                    ip_v=(output2[ve]["management_ip"])

                    device["host"]=ip_v
                    ssh = nm.ConnectHandler(**device)
                    ssh.enable()
                else:
                    nombre = ssh.send_command("show run | include hostname")
                    print('La direcicon mac ',x,' se encuentra conectada al puerto ',puerto_mac,'en el Switch',nombre)
            except:
                print("Error")
                break


def menu(device):
    print("\nOPCION 1 - TABLA VECINOS OSPF")
    print("OPCION 2 - TABLA DE MACS DE DISPOSITIVOS CONECTADOS")
    print("OPCION 3 - CREAR VLAN DENTRO DE UN SWITCH")
    print("OPCION 4 - COPIA DE CONFIGURACIONES EN FTP")
    print("OPCION 5 - BUSQUEDA DE MAC DENTRO DE LA RED")

    try:
        seleccion=int(input("\nSeleccione que accion quiere hacer (solo numeros): "))
    except:
        print("\ningrese valores validos")

    if seleccion == 1:
        ospf_table_f(device)

    elif seleccion == 2:
        mac_table_f(device)

    elif seleccion == 3:
        vlan_c(device)

    elif seleccion == 4:
        ftp_run(device)

    elif seleccion == 5:
        mac_find(device)


Switch=input("IP primer switch: ")
User = input("Usuario: ")
Pass= input("Contraseña: ")
E_Pass = "cisco"

device = {
    "host": Switch,
    "username": User,
    "password": Pass,
    "device_type": "cisco_ios",
    "secret": E_Pass,}


menu(device)