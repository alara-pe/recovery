import sys
import argparse
import winreg
import datetime
from datetime import datetime as datetimev
import os
import psutil
import win32evtlog
import tempfile
import wmi

from browser_history import get_history 

def registro_cambio(initime, fintime):
    #Extraemos los cambios en el registro en el tiempo señalado
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    key = winreg.HKEY_LOCAL_MACHINE
    
    try:
        registry_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_READ)
        last_write_time = winreg.QueryInfoKey(registry_key)[2]
        if last_write_time/10000000 - 11644473600 > initime.timestamp() and last_write_time/10000000 - 11644473600 < fintime.timestamp():
            winreg.CloseKey(registry_key)

            print(f"$$$$$$$__Los Registros Modificados son los Siguientes______$$$$$$$$: {datetimev.fromtimestamp(last_write_time/10000000 - 11644473600)}")
    except WindowsError:
        print("\nError en el acceso a los registros")

def archivos_recientes(initime, fintime):
    #Extraemos los archivos recientes
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"
    key = winreg.HKEY_CURRENT_USER

    try:
        registry_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_READ)
        num_entries = winreg.QueryInfoKey(registry_key)[1]

        
        print("\n$$$$$$$$$_____ARCHIVOS RECIENTES_____$$$$$$$$$:")
        for i in range(num_entries):
            value_name = winreg.EnumValue(registry_key, i)[0]

            try:
                timestamp = int(value_name)
                file_datetime = datetimev.fromtimestamp(timestamp)

                if initime <= file_datetime <= fintime:
                    print(f"- {file_datetime}: {value_name}")
            except ValueError:
                # Ignore non-numeric value_names
                pass

        winreg.CloseKey(registry_key)
    except WindowsError:
        print("\nError AL ACCEDER A LOS ARCHIVOS RECIENTES.")

def ft_extract_recent_files(initime, fintime):
    '''Extract the recent files within the given time lapse'''
    recent_folder_path = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Recent")
  
    try:
        print("\n$$$$$$$$$$$$$___________ARCHIVOS RECIENTES______________$$$$$$$$$$$$$$$$$$$$$$$:")
        for filename in os.listdir(recent_folder_path):
            file_path = os.path.join(recent_folder_path, filename)
            modified_time = datetimev.fromtimestamp(os.path.getmtime(file_path))

            if initime <= modified_time <= fintime:
                print(f"- {modified_time}: {filename}")
    except OSError:
        print("\nError accessing the Recent folder.\n")


def archivos_temporales(initime, fintime):
    #extraemos los archivos temporales

    temporal_files = []
    try:
        # Get the system's temporary directory
        temp_dir = tempfile.gettempdir()

        # Iterate through all files in the temporary directory
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_create_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))

                # Check if the file creation time is within the given time lapse
                if initime <= file_create_time <= fintime:
                    temporal_files.append(file_path)

    except Exception as e:
        print(f"\nError al accerder al archivo temporal: {e}")

    return temporal_files

def programas_instalados(initime, fintime):
    #extraemos los programas instalados

    # Define the registry key path for installed programs
    registry_key_path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"

    
    print("\n\n$$$$$$$$$$$_______PROGRAMAS INSTALADOS__________$$$$$$$$$$$$:\n")
    try:
        # Open the registry key for reading
        registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_key_path, 0, winreg.KEY_READ)

        # Get the number of subkeys under the registry branch
        num_subkeys = winreg.QueryInfoKey(registry_key)[0]

        # Iterate through the subkeys and extract the installed programs within the given time lapse
        for i in range(num_subkeys):
            subkey_name = winreg.EnumKey(registry_key, i)
            subkey_path = registry_key_path + "\\" + subkey_name

            # Open the subkey for reading
            subkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path, 0, winreg.KEY_READ)

            # Check if the subkey has an "InstallDate" value
            try:
                install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]

                # Convert the install date to a datetime object
                install_date = datetime.datetime.strptime(install_date, "%Y%m%d")

                # Check if the install date is within the given time lapse
                if initime <= install_date <= fintime:
                    program_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    print(f"Program Name: {program_name}")
                    print()

            except FileNotFoundError:
                pass  # Ignore subkeys without an "InstallDate" value

            # Close the subkey
            winreg.CloseKey(subkey)

        # Close the registry key
        winreg.CloseKey(registry_key)

    except OSError as e:
        print(f"ERROR AL ACCEDER AL REGISTRO: {e}")

def programas_abiertos(initime, fintime):
    #sabemos que programas hay abiertos en ese periodo porque accedemos a los procesos abiertos

    running_processes = []

    print("\n\n$$$$$$$$$$$$$_________ESTAN ABIERTOS LOS SIGUIENTES PROGRAMAS__________:$$$$$$$$$$$$$:\n")
    try:
        # Iterate through all running processes
        for process in psutil.process_iter(['pid', 'name', 'create_time']):
            # Get the process creation time
            create_time = datetime.datetime.fromtimestamp(process.info['create_time'])
            

            # Check if the creation time is within the given time lapse
            if initime <= create_time <= fintime:
                running_processes.append({
                    'pid': process.info['pid'],
                    'name': process.info['name'],
                    'create_time': create_time
                })

    except psutil.Error as e:
        print(f"ERROR EN EL PROCESO {e}")

    return running_processes


def histo_navegador(initime, fintime):
    '''Extract the browser history within the given time lapse'''

    try:
        print("\n\n$$$$$$$$$$$$$$$$$$$$$$____________HISTORIAL DE NAVEGACIÓN _________________$$$$$$$$$$$$$$$$$$$$:")
        # Get the browser history for all browsers
        output = get_history().histories
        for visit,url in output:
                print(visit, url)

    except Exception as e:
        print(f"Error accessing browser history: {e}")

def ft_extract_connected_devices():
    '''Extract the connected devices info'''
    c = wmi.WMI()

    
    print("\n$$$$$$$$$$$$$$$$$$_______________Connected Devices________________$$$$$$$$$$$$$$$$:")
    for device in c.Win32_PnPEntity():
        if device.ConfigManagerErrorCode == 0:
            print(f"Device Name: {device.Name}")
            print(f"Description: {device.Description}")
            print(f"Manufacturer: {device.Manufacturer}")
            print()

def ft_extract_event_logs(initime, fintime):
    '''Extract the event logs within the given time lapse'''

    event_logs = []

    try:
        print("\n\n$$$$$$$$$$$$$$$$$$$$$$____________EVENTOS LOGS _________________$$$$$$$$$$$$$$$$$$$$:")
        # Open the Application event log
        hand = win32evtlog.OpenEventLog(None, "Application")

        # Iterate through the events in the log
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        total_records = win32evtlog.GetNumberOfEventLogRecords(hand)
        print(f"\nTotal Records: {total_records}")
        events = win32evtlog.ReadEventLog(hand, flags, 0)

        while events:
            for event in events:
                # print(f"Event ID: {event.EventID}")
                event_time = event.TimeGenerated.Format()  # Get the event log timestamp as string

                # Parse the event time using a custom format
                event_datetime = datetime.datetime.strptime(event_time, "%a %b %d %H:%M:%S %Y")

                # Check if the event time is within the given time lapse
                if initime <= event_datetime <= fintime:
                    event_logs.append({
                        'TimeGenerated': event_time,
                        'SourceName': event.SourceName,
                        'EventID': event.EventID,
                        'EventType': event.EventType,
                        'EventCategory': event.EventCategory,
                        'Strings': event.StringInserts
                    })

            events = win32evtlog.ReadEventLog(hand, flags, 0)

        # Close the event log
        win32evtlog.CloseEventLog(hand)

    except Exception as e:
        print(f"Error accessing event logs: {e}")

    return event_logs

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Recovery system info within a given time lapse')
    parser.add_argument('-i', '--initime', type=str, help='Start date in YYYY-MM-DD format')
    parser.add_argument('-f', '--fintime', type=str, help='End date in YYYY-MM-DD format')
    args = parser.parse_args()

    # Convert input dates to datetime objects
    try:
        if args.initime and args.fintime:
            initime = datetime.datetime.strptime(args.initime, '%Y-%m-%d')
            fintime = datetime.datetime.strptime(args.fintime, '%Y-%m-%d')
        elif args.fintime:
           
            fintime = datetime.datetime.strptime(args.fintime, '%Y-%m-%d')
            initime =  fintime - datetime.timedelta(hours=24)
        elif args.initime:
            initime = datetime.datetime.strptime(args.initime, '%Y-%m-%d')
            fintime = datetime.datetime.now()
        else:
            initime = datetime.datetime.now() - datetime.timedelta(hours=4)
            fintime = datetime.datetime.now()
    except ValueError:
        print("\nInvalid date format. Please use YYYY-MM-DD format.")
        sys.exit()

    print("\nShow recovery info from: " + str(initime) + " to " + str(fintime))

    # Extract the registry changes within the given time lapse
    registro_cambio(initime, fintime)

    # Extract the recent files within the given time lapse in registry 
    # ft_ft_extract_recent_files_reg(initime, fintime)

    # Extract the recent files within the given time lapse
    ft_extract_recent_files(initime, fintime)

    # Extract the temporal files within the given time lapse
    temporal_files = archivos_temporales(initime, fintime)

    # Print the temporal files
    
    print("\n_$$$$$$$$$$$$$$$$$$____________ARCHIVOS TEMPORALES___________$$$$$$$$$$$$$$$$$$:")
    for file in temporal_files:
        print(file)

    # Extract the installed programs within the given time lapse
    programas_instalados(initime, fintime)

    # Extract the running processes within the given time lapse
    running_processes = programas_abiertos(initime, fintime)

    # Print the list of running processes
    for process in running_processes:
        print(f"Process: {process['name']}, PID: {process['pid']}, Creation Time: {process['create_time']}")

    # Extract the web browser history within the given time lapse
    histo_navegador(initime, fintime)

    # Extract the connected devices    
    ft_extract_connected_devices()

    # Extract the event logs within the given time lapse
    event_logs = ft_extract_event_logs(initime, fintime)
    # Print the event logs
    for log in event_logs:
        print(f"Time Generated: {log['TimeGenerated']}")
        print(f"Source Name: {log['SourceName']}")
        print(f"Event ID: {log['EventID']}")
        print(f"Event Type: {log['EventType']}")
        print(f"Event Category: {log['EventCategory']}")
        # Check if 'Strings' is iterable before using 'join'
        if isinstance(log['Strings'], list):
            print(f"Strings: {', '.join(log['Strings'])}")
        else:
            print(f"Strings: {log['Strings']}")
        print()