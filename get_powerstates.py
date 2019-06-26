"""Gets the current powerstates of all VMS on vSphere"""
import atexit
import csv
import getpass
import time
import ssl

from pathlib import Path
from pyVim import connect
from pyVmomi import vim


def csv_writer(save_path, data):
    """Write 2D array to .csv file by row"""
    with open(save_path, 'w') as file:
        writer = csv.writer(file)
        for line in data:
            writer.writerow(line)


def organize_vms(name):
    switch = {"prt3": "Tier3",
              "tst3": "Tier3",
              "dvt3": "Tier3",
              "prt2": "Tier2",
              "tst2": "Tier2",
              "dvt2": "Tier2",
              "prt1": "Tier1",
              "tst1": "Tier1",
              "dvt1": "Tier1",
              "DOTDB": "DOT_Database",
              "DOTAS": "DOT_App",
              "DOTWS": "DOT_Web"}
    return switch.get(name, "Other_Servers")


def main():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    root = Path('.')

    tier1 = []
    tier2 = []
    tier3 = []
    dotdb = []
    dotas = []
    dotws = []
    other = []

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.verify_mode = ssl.CERT_NONE

    vsphere = connect.SmartConnect(
        host="vSphere.server",
        user=username,
        pwd=password)

    atexit.register(connect.Disconnect, vsphere)

    vm = None
    entity_stack = vsphere.content.rootFolder.childEntity
    while entity_stack:
        vm = entity_stack.pop()
        try:
            collect = []
            if vm.name[:3].upper() == "DOT":
                name = vm.name[:5]
            else:
                name = vm.name[:4]
            tier = organize_vms(name)
            collect = [vm.name, vm.runtime.powerState]
            if tier == "Tier1":
                tier1.append(collect)
            elif tier == "Tier2":
                tier2.append(collect)
            elif tier == "Tier3":
                tier3.append(collect)
            elif tier == "DOT_Database":
                dotdb.append(collect)
            elif tier == "DOT_App":
                dotas.append(collect)
            elif tier == "DOT_Web":
                dotws.append(collect)
            elif tier == "Other_Servers":
                other.append(collect)
            else:
                print(f"{vm.name} ain't right")
            print(f"{vm.name}")
        except AttributeError:
            pass
        if hasattr(vm, "childEntity"):
            entity_stack.extend(vm.childEntity)
        elif isinstance(vm, vim.Datacenter):
            entity_stack.append(vm.vmFolder)

    all = tier1 + tier2 + tier3 + dotdb + dotas + dotws + other
    timestr = time.strftime("%Y%m%d-%H%M")

    csv_writer(root / ("Tier1-" + timestr + ".csv"), tier1)
    csv_writer(root / ("Tier2-" + timestr + ".csv"), tier2)
    csv_writer(root / ("Tier3-" + timestr + ".csv"), tier3)
    csv_writer(root / ("DOT_Database-" + timestr + ".csv"), dotdb)
    csv_writer(root / ("DOT_App-" + timestr + ".csv"), dotas)
    csv_writer(root / ("DOT_Web-" + timestr + ".csv"), dotws)
    csv_writer(root / ("Other-" + timestr + ".csv"), other)
    csv_writer(root / ("All-" + timestr + ".csv"), all)


if __name__ == '__main__':
    main()
