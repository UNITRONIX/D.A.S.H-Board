# Import modules

import random
import os
from fastapi import Request
from nicegui import ElementFilter, app, ui, native, events
from typing import List, Tuple
from pathlib import Path
from nicegui.elements import markdown
from datetime import date
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles
import shutil
from datetime import datetime, timedelta
#from device_detector import DeviceDetector #pip install device_detector
import time
import psutil
import socket
import json
import uuid
import subprocess
import platform
import glob
import threading
from fastapi import FastAPI
import importlib.util

api = FastAPI()

#Font add module for NiceGui
app.add_static_file(local_file='fonts/Comfortaa.ttf', url_path='/fonts/Comfortaa.ttf')

app.add_static_files('/images/background', '.')
app.add_static_files('/images/profile', '.')
app.add_static_files('/images/language_flags', '.')

ui.query('.nicegui-content').classes('w-full')
ui.query('.q-page').classes('flex')

# SQL Lite database configure

# Daily message list and function
daily_message_list = ["I'm up and running!","All systems are a go!","Ready to assist!","Percolating and pondering...","Percolating and pondering...","Just doing robot things.","Optimizing my processes.","Always learning, always growing.","Bleep bloop, I'm online!","I'm feeling a little rusty today.","Robot mode: activated!."]

aibo_daily_message = random.choice(daily_message_list) # Aibo daily message under his image

today = date.today()
# mobile layout enable/disable

ml_switch = ['grid grid-cols-1 w-full opacity-95', 'grid grid-cols-2 w-full opacity-95', 'grid grid-cols-3 w-full opacity-95']

def generate_unique_id():
    return str(uuid.uuid4())

# Plugin system
plugin_tabs = []

def load_plugins(ui, plugin_tabs):
    plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    active_plugins = []
    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
    print(f"[PLUGIN] Scanning folder: {plugins_dir}")
    for file in os.listdir(plugins_dir):
        if file.endswith('.py'):
            plugin_path = os.path.join(plugins_dir, file)
            spec = importlib.util.spec_from_file_location(file[:-3], plugin_path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, 'register'):
                    module.register(ui, plugin_tabs)
                    active_plugins.append(file)
                    print(f"[PLUGIN] Loaded: {file}")
                else:
                    print(f"[PLUGIN] Skipped (no register()): {file}")
            except Exception as e:
                print(f"[PLUGIN] Error loading {file}: {e}")
    print(f"[PLUGIN] Active plugins: {active_plugins}")

# Create config.json file with default values
def create_config(robot_name='Dash', coins=1500, os_version='1.0'):
    robot_id = generate_unique_id()
    config = {
        'robot-name': robot_name,
        'coins': coins,
        'os-version': os_version,
        'water': 1,
        'hunger': 1,
        'happiness': 1,
        'unique-id': robot_id,
        'level': 1,
        'experience': 0,
        'mood': 'Neutral',
        'power-mode': 'Normal',
        'wifi_ssid': 'Dash_WiFi',
        'wifi_password': 'Dash1234',
        'hotspot_mode': True,
        'dark_mode': True,
        'dash_image': 'images/profile/profile.png',
        'battery': '83%',
        'connection_type': 'WI-FI',
        'software_ver': '5.50',
        'background_image_set': 'images/background/119.png',
        'dash_coins': 1500,
        'dash_lvl': 1,
        'layout': 0,
        'global_primary_color': '#6E93D6',
        'connection': '1',
        'eye_outer_color': "#000000",
        'eye_inner_color': "#FFFFFF"
    }
    with open('config.json', 'w') as f:
        json.dump(config, f)

# Read config.json file and return its content
def read_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Config file not found. Creating a new one with default settings.")
        create_config()
        return read_config()
    
if not os.path.isfile('config.json'):
        create_config()
else:
    config = read_config()

LANG_DIR = os.path.join(os.path.dirname(__file__), 'lang')
current_lang = {'code': 'en', 'data': {}}

def load_language(lang_code):
    path = os.path.join(LANG_DIR, f'{lang_code}.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            current_lang['data'] = json.load(f)
            current_lang['code'] = lang_code
    except Exception:
        current_lang['data'] = {}
        current_lang['code'] = 'en'

def t(key):
    return current_lang['data'].get(key, key)

load_language(config['language'])

def load_language_selector():
    path = os.path.join(LANG_DIR, 'language_selector.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return [
            {"code": "en", "label": "English", "flag": "images/language_flags/us.png"}
        ]
    
def get_background_images():
    bg_dir = os.path.join(os.path.dirname(__file__), 'images', 'background')
    # Obsługa plików png, jpg, jpeg
    return sorted(glob.glob(os.path.join(bg_dir, '*.png')) + glob.glob(os.path.join(bg_dir, '*.jpg')) + glob.glob(os.path.join(bg_dir, '*.jpeg')))
        
#Global color apply
ui.colors(primary=config['global_primary_color'])

dark_mode = ui.dark_mode(True) # Dark mode variable

background_image_set = config['background_image_set'] # Background image

# Desktop and mmobile layout module

gui_layout = config['layout']

#gui_layout = 0 # 0 - desktop, 1 - mobile
if gui_layout == 0:
    print('Desktop layout enabled')
    home_page_layout = ml_switch[1]
    controls_layout = ''
    personalization_layout = ml_switch[1]
    service_layout = ml_switch[1]

elif gui_layout == 1:
    print('Mobile layout enabled')
    home_page_layout = ml_switch[0]
    controls_layout = ''
    personalization_layout = ml_switch[0]
    service_layout = ml_switch[0]
    
#Set new laout value and restart module
def layout_mod(layout_value):
    print('Change layout preset')
    #set new value to layout data
    update_config('layout', layout_value)
    #save all changes to pickle
    ui.notify('Changing interface...')
    
    os.utime('main.py')
    
#Save global primary color to pickle
def change_global_color(value):
    print('global_color_change')
    update_config('global_primary_color', value)
    
    os.utime('main.py')

#Upload image as profile (not working yet)

# get battery level function
def get_battery_level():
    try:
        battery = psutil.sensors_battery()
        if battery is not None and battery.percent is not None:
            return battery.percent
    except Exception as e:
        print(f"Error getting battery level: {e}")
    return "N/A"

# Get local IP address function
def get_ip():
    try:
        # Pobieranie adresu IP lokalnego
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania adresu IP: {e}")
        return None

# Check network type function
def check_network_type():
    ip = get_ip()
    if ip is not None:
        # Sprawdzanie, czy adres IP należy do sieci WiFi lub LAN
        if ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.16.'):
            return "LAN"
        elif ip.startswith('10.0.') or ip.startswith('172.17.') or ip.startswith('172.18.') or ip.startswith('172.19.') or ip.startswith('172.20.') or ip.startswith('172.21.') or ip.startswith('172.22.') or ip.startswith('172.23.') or ip.startswith('172.24.') or ip.startswith('172.25.') or ip.startswith('172.26.') or ip.startswith('172.27.') or ip.startswith('172.28.') or ip.startswith('172.29.') or ip.startswith('172.30.') or ip.startswith('172.31.'):
            return "LAN"
        elif ip.startswith('169.254.'):
            return "LAN"
        else:
            return "WiFi"
    else:
        return "none"

# Update config.json file with new values  
def update_config(key, value):
    config = read_config()
    config[key] = value
    with open('config.json', 'w') as f:
        json.dump(config, f)
config = read_config()
# Create a new config file with default settings
#create_config()

# Read the current configuration
print(read_config())

def set_power_mode(mode):
    """
    Ustawia tryb zasilania CPU na ARM/Linux.
    Dostępne tryby: 'powersave', 'ondemand', 'performance'
    """
    # Mapowanie trybów UI na tryby systemowe
    mode_map = {
        1: 'powersave',    # Power Saving
        2: 'ondemand',     # Normal
        3: 'performance',  # Performance
    }
    governor = mode_map.get(mode, 'ondemand')
    try:
        # Ustawienie governor dla wszystkich CPU
        cpu_count = os.cpu_count()
        for i in range(cpu_count):
            path = f'/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_governor'
            # Wymaga uprawnień root!
            subprocess.run(['sudo', 'sh', '-c', f'echo {governor} > {path}'], check=True)
        ui.notify(f'Power mode set to: {governor}')
    except Exception as e:
        ui.notify(f'Failed to set power mode: {e}', color='red')
    # Zawsze zapisuj wybrany tryb do config.json
    update_config('power-mode', governor)

# Get CPU information function
def get_cpu_info():
    try:
        with open("/proc/cpuinfo") as f:
            lines = f.readlines()
        model = [l for l in lines if "model name" in l]
        if model:
            cpu_name = model[0].split(":")[1].strip()
        else:
            cpu_name = platform.processor()
    except Exception:
        cpu_name = platform.processor()
    return cpu_name

# Get RAM type function
def get_ram_type():
    try:
        with open('/proc/meminfo') as f:
            for line in f:
                if 'MemTotal' in line:
                    return 'DDR (detected)'
    except Exception:
        pass
    return 'Unknown'

# Get RAM usage function
def get_ram_usage():
    mem = psutil.virtual_memory()
    return f"{mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB ({mem.percent}%)"

# Get disk type function
def get_disk_type():
    try:
        import subprocess
        result = subprocess.check_output("lsblk -d -o name,rota", shell=True).decode()
        # rota=1 -> HDD, rota=0 -> SSD/eMMC
        if " 0" in result:
            return "SSD/eMMC"
        elif " 1" in result:
            return "HDD"
    except Exception:
        pass
    return "Unknown"

# Get device specifications function
def get_device_specs():
    return [
        ("System", platform.system()),
        ("Node", platform.node()),
        ("Release", platform.release()),
        ("Version", platform.version()),
        ("Machine", platform.machine()),
        ("Processor", get_cpu_info()),
        ("Python", platform.python_version()),
    ]

# battery status function
def get_battery_status():
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return "No Battery"
        percent = battery.percent
        plugged = battery.power_plugged
        if plugged:
            return f"{percent}% (AC Power)"
        else:
            return f"{percent}% (Battery)"
    except Exception:
        return "Unknown"

#get temperature function
def get_cpu_temperature():
    try:
        temps = psutil.sensors_temperatures()
        # Najczęściej spotykane klucze: 'coretemp', 'cpu-thermal', 'soc_thermal'
        for key in temps:
            for entry in temps[key]:
                # Szukamy sensora CPU
                if ('cpu' in entry.label.lower() or 'core' in entry.label.lower() or key in ['coretemp', 'cpu-thermal', 'soc_thermal']):
                    return f"{entry.current:.1f}°C"
        # Jeśli nie znaleziono, spróbuj pierwszy dostępny sensor
        for key in temps:
            if temps[key]:
                return f"{temps[key][0].current:.1f}°C"
        return "No temperature data"
    except Exception:
        return "No temperature data"
    
config = read_config()

# Automatyczne ustawienie trybu zasilania z config.json po starcie
power_mode_map = {'powersave': 1, 'ondemand': 2, 'performance': 3}
saved_mode = config.get('power-mode', 'ondemand')
set_power_mode(power_mode_map.get(saved_mode, 2))

# WiFi and Hotspot functions for Linux
def scan_wifi_networks():
    """Zwraca listę wykrytych sieci WiFi (Linux, wymaga sudo)."""
    try:
        result = subprocess.check_output("nmcli -t -f SSID dev wifi", shell=True).decode()
        networks = list({ssid for ssid in result.strip().split('\n') if ssid})
        return networks
    except Exception as e:
        print(f"Błąd skanowania WiFi: {e}")
        return []

# try to connect to WiFi
def try_connect_wifi(ssid, password):
    """Próbuje połączyć z wybraną siecią WiFi (Linux, wymaga sudo)."""
    try:
        if password:
            cmd = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        else:
            cmd = f"nmcli dev wifi connect '{ssid}'"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Błąd połączenia WiFi: {e}")
        return False

# Start WiFi hotspot
def start_hotspot(ssid, password):
    """Tworzy hotspot WiFi (Linux, wymaga sudo)."""
    try:
        if password:
            cmd = f"nmcli dev wifi hotspot ssid '{ssid}' password '{password}'"
        else:
            cmd = f"nmcli dev wifi hotspot ssid '{ssid}'"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error starting hotspot: {e}")
        return False

def save_wifi_config(mode, ssid, password):
    update_config('hotspot_mode', mode == 'hotspot')
    update_config('wifi_ssid', ssid)
    update_config('wifi_password', password)

def load_wifi_config():
    mode = 'hotspot' if config.get('hotspot_mode', False) else 'wifi'
    ssid = config.get('wifi_ssid', '')
    password = config.get('wifi_password', '')
    return mode, ssid, password

def show_wifi_dialog():
    mode, ssid, password = load_wifi_config()
    with ui.dialog() as wifi_dialog, ui.card():
        ui.label('WiFi / Hotspot Configuration').style('font-size: 150%; font-weight: 1000')
        mode_select = ui.toggle({'wifi': 'WiFi', 'hotspot': 'Hotspot'}, value=mode)
        ssid_input = ui.input('SSID', value=ssid)
        password_input = ui.input('Password (leave empty for open)', password=True, value=password)
        status_label = ui.label().style('color: red')
        def apply():
            selected_mode = mode_select.value
            selected_ssid = ssid_input.value
            selected_password = password_input.value
            if selected_mode == 'wifi':
                if try_connect_wifi(selected_ssid, selected_password):
                    save_wifi_config('wifi', selected_ssid, selected_password)
                    status_label.set_text('Connected to WiFi!').style('color: green')
                    ui.notify('Connected to WiFi!')
                    wifi_dialog.close()
                else:
                    status_label.set_text('Error with connecting to WiFi. Try again.')
            else:
                if start_hotspot(selected_ssid, selected_password):
                    save_wifi_config('hotspot', selected_ssid, selected_password)
                    status_label.set_text('Hotspot is launched!').style('color: green')
                    ui.notify('Hotspot is launched!')
                    wifi_dialog.close()
                else:
                    status_label.set_text('Error with launching hotspot.')
        ui.button(t('apply'), on_click=apply)
        ui.button(t('cancel'), on_click=wifi_dialog.close)
    wifi_dialog.open()


#hotspot launch on start
if config.get('hotspot_mode', False):
    ssid = config.get('wifi_ssid', 'Dash_WiFi')
    password = config.get('wifi_password', 'Dash1234')
    start_hotspot(ssid, password)

# Get memory files function 
def get_memory_files():
    memory_dir = os.path.join(os.path.dirname(__file__), 'ai_memory')
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir)
    files = glob.glob(os.path.join(memory_dir, '*.md'))
    return [os.path.basename(f) for f in files]

selected_memory_file = ['memoryEN.md']  # default file

def change_background_image(image_path):
    """Change the application background."""
    config['background_image_set'] = image_path
    update_config('background_image_set', image_path)
    ui.notify('Background image changed!')
    os.utime('main.py')  # Reload the page to apply the new background

def change_name(new_name):
    """Change the robot name."""
    config['robot-name'] = new_name
    update_config('robot-name', new_name)
    ui.notify('Robot name changed!')
    os.utime('main.py')  # Reload the page to apply the new background

def eye_color_change_inner(inner_color):
    """Change the inner eye color."""
    config['eye_inner_color'] = inner_color
    update_config('eye_inner_color', inner_color)
    ui.notify('Eye inner color changed!')
    os.utime('main.py') 

def eye_color_change_outer(outer_color):
    """Change the outer eye color."""
    config['eye_outer_color'] = outer_color
    update_config('eye_outer_color', outer_color)
    ui.notify('Eye outer color changed!')
    os.utime('main.py')

def on_profile_upload(upload_event):
    file_name = upload_event.name
    dest_path = os.path.join('images/profile', file_name)
    # Odczytaj zawartość pliku i zapisz
    with open(dest_path, 'wb') as f:
        f.write(upload_event.content.read())
    update_config('dash_image', dest_path)
    ui.notify('Profile image updated!')
    os.utime('main.py')

@api.get("/coin_inject")
def coins_injector(coins_amount: int):
    """Inject coins into the user's account."""
    current_coins = config.get('coins', 0)
    config['coins'] = current_coins + coins_amount
    update_config('coins', config['coins'])
    ui.notify(f'You get {coins_amount} coins!')
    time.sleep(5)
    os.utime('main.py')

app.mount("/api", api)
# Top Menu Tabs
ui.add_head_html('''
<style>
@font-face {
    font-family: 'Comfortaa';
    src: url('fonts/Comfortaa.ttf') format('truetype');
}
</style>
''')

def refresh_coins_label(label):
    """Refreshes the coins label in the GUI without restarting the app."""
    config = read_config()
    label.set_text(config.get('coins', 0))

#Tab panel (nav-bar)
with ui.tabs().classes('w-full') as tabs:
    home = ui.tab(t('main_page'), icon='home').style('font-size: 200%; font-weight: 1000')
    specs = ui.tab(t('specifications'), icon='memory').style('font-size: 200%; font-weight: 1000')
    controls = ui.tab(t('controls'), icon='sports_esports').style('font-size: 200%; font-weight: 1000')
    personalization = ui.tab(t('personalization'), icon='brush').style('font-size: 200%; font-weight: 1000')
    playful_dash = ui.tab(t('playful'), icon='queue_music').style('font-size: 200%; font-weight: 1000')
    careful_dash = ui.tab(t('caring'), icon='hotel_class').style('font-size: 200%; font-weight: 1000')
    service = ui.tab(t('service'), icon='build').style('font-size: 200%; font-weight: 1000')
    load_plugins(ui, plugin_tabs)
    for tab, _ in plugin_tabs:
        ui.tab(tab, icon='extension').style('font-size: 200%; font-weight: 1000')
    settings = ui.tab(t('settings_panel'), icon='settings').style('font-size: 200%; font-weight: 1000')
    about = ui.tab(t('about'), icon='info').style('font-size: 200%; font-weight: 1000')

    # Load plugins and add their tabs
    

#Full app interface

# Tab Panels
with ui.tab_panels(tabs, value=home).classes('w-full'):
    # Home tab Module
    with ui.tab_panel(home):
        with ui.row().classes(home_page_layout):
            ui.image(background_image_set).classes('absolute inset-0')
            with ui.row().classes('grid grid-cols-1 w-full opacity-95') as home_row:
                    # Main Grid - Welcome grid with app name
                    with ui.card():
                        ui.label(t('dash_welcome')).style('font-size: 200%; font-weight: 1000')
                        ui.label(t('robot_desc')).style('font-size: 200%; font-weight: 500')
                    # Main Grid - Welcome grid with app name - Updates timeline


                    #dash coins and lvl
                    with ui.row().classes('grid grid-cols-2 w-full'):

                        #dash coins
                        with ui.card().classes('w-full h-full'):
                            ui.label(t('coins')).style('font-weight: 1000; font-size: 120%')
                            with ui.row():
                                #dash coins icon
                                ui.icon('paid', color='primary').classes('text-5xl')
                                #dash coins amount with variable
                                coins_label = ui.label(read_config().get('coins', 0)).style('font-weight: 1000; font-size: 230%;')

                        #dash lvl
                        with ui.card().classes('w-full h-full'):
                            ui.label(t('dash_lvl')).style('font-weight: 1000; font-size: 120%')
                            with ui.row().classes('grid grid-cols-1 w-full'):
                                #dash level icon
                                with ui.row():
                                    ui.label(t('level'))
                                    ui.label(config['level'])
                                #dash level progress
                                ui.linear_progress(value=config['level'] / 10)

                    #Update card
                    with ui.card().classes('w-full'):
                        ui.label(t('check_updates')).style('font-weight: 1000; font-size: 120%')
                        with ui.row():
                            ui.icon('task_alt', color='green').classes('text-5xl')

                        with ui.list().props('dense separator'):
                            ui.item(t('no_updates')).style('font-weight: 1000')
                            ui.item(t('firmware_ver') + ': ' + config['os-version']).style('font-weight: 1000')
                            ui.item(t('app_ver') + ': 0.8').style('font-weight: 1000')
                        ui.button(t('check_updates'), on_click=lambda: ui.notify(t('no_updates')))

                # dash Stats            
            with ui.row().classes('grid grid-cols-1 w-full opacity-95'):
                with ui.card():
                    with ui.row().classes('grid grid-cols-2 w-full opacity-95'):
                        with ui.row().classes('grid grid-cols-1 w-full opacity-95'):
                            ui.label(t('your_dash')).style('font-size: 150%; font-weight: 1000')
                            ui.label(config['robot-name']).style('font-size: 250%; font-weight: 1000').classes('text-center')
                            ui.chat_message(aibo_daily_message).style('font-size: 150%')
                            with ui.dialog() as profile_dialog, ui.card():
                                ui.label(t('dash_image')).style('font-size: 120%; font-weight: 1000')
                                ui.upload(
                                    on_upload=on_profile_upload,
                                    on_rejected=lambda: ui.notify('Rejected!'),
                                    max_file_size=10_000_000
                                ).classes('max-w-full').props('accept=".jpeg,.jpg,.png"')
                                ui.button(t('cancel'), on_click=profile_dialog.close)
                            ui.button(t('change_profile_image'), on_click=profile_dialog.open)
                            with ui.dialog() as name_change_dialog, ui.card():
                                name_input =ui.input(t('change_dash_name'), value=config['robot-name'])
                                ui.button(t('set_new_name'), on_click= lambda: change_name(name_input.value)).style('font-size: 120%; font-weight: 1000')
                            ui.button(t('change_name'), on_click=name_change_dialog.open)

                        #aibo image scaling
                        #with ui.card().classes('w-full justify-center').style('text-align: center'):
                        # with ui.row().classes('grid grid-cols-1 w-full'):
                        ui.image(config['dash_image']).props('fit=scale-down').classes('rounded-full ')

                        #with ui.dialog() as dialog, ui.card():
                            # Profile image upload and change 
                            #ui.upload(on_upload=on_upload,
                            #on_rejected=lambda: ui.notify('Rejected!'),
                            #max_file_size=10_000_000).classes('max-w-full').props('accept=".jpeg,.jpg,.png"')
                            #ui.button('Close', on_click=dialog.close)
                        #ui.button('Change image', on_click=dialog.open).style('font-weight: 1000')

                        #dash Vitals

                    with ui.expansion(t('vitals'), icon='bar_chart').classes('w-full text-2xl'):
                            with ui.row().classes('grid grid-cols-3 w-full'):
                                #Food
                                with ui.card().classes('w-full'):
                                    with ui.circular_progress(value=config['hunger'], show_value=False, color='orange').classes('w-full h-full items-center m-auto') as food_progress:
                                        ui.icon('local_dining', color='primary').classes('text-2xl').props('flat round').classes('w-full h-full')
                                #Water
                                with ui.card().classes('w-full'):
                                    with ui.circular_progress(value=config['water'], show_value=False, color='blue').classes('w-full h-full items-center m-auto') as water_progress:
                                        ui.icon('water_drop', color='primary').classes('text-2xl').props('flat round').classes('w-full h-full')
                                #Love
                                with ui.card().classes('w-full'):
                                    with ui.circular_progress(value=config['happiness'], show_value=False, color='red').classes('w-full h-full items-center m-auto') as love_progress:
                                        ui.icon('favorite', color='primary').classes('text-2xl').props('flat round').classes('w-full h-full')
                        
                        #dash stats card
                with ui.row().classes('grid grid-cols-1 w-full opacity-95'):
                            with ui.grid(columns=2):
                                #-
                                # Connection status checker - IF
                                #if connection == '1':
                                    #ui.label('Connected').style('font-weight: 1000; color: green')
                                    #ui.label('')
                                    
                                #elif connection == '0':
                                    #ui.label('Disconnected').style('font-weight: 1000; color: red')
                                    #ui.label('')
                                # Connection type box
                                with ui.card():
                                    with ui.row().classes('grid grid-cols-2 w-full opacity-95'):
                                        with ui.row().classes('grid grid-cols-1 w-full opacity-95'):
                                            ui.label(t('network')).style('font-weight: 1000')
                                            ui.label(check_network_type()).style('font-weight: 1000; font-size: 150%')
                                        ui.icon('wifi', color='primary').classes('text-6xl')
                                # -
                                # Battery box
                                with ui.card():
                                     with ui.row().classes('grid grid-cols-2 w-full opacity-95'):
                                        with ui.row().classes('grid grid-cols-1 w-full opacity-95'):
                                            ui.label(t('battery')).style('font-weight: 1000')
                                            ui.label(get_battery_level()).style('font-weight: 1000; font-size: 150%')
                                        ui.icon('battery_full', color='primary').classes('text-6xl')
                                # -
                                # dash software box
                                with ui.card():
                                    with ui.row().classes('grid grid-cols-2 w-full opacity-95'):
                                        with ui.row().classes('grid grid-cols-1 w-full opacity-95'):
                                            ui.label(t('software')).style('font-weight: 1000')
                                            ui.label(config['os-version']).style('font-weight: 1000; font-size: 150%')
                                        ui.icon('api', color='primary').classes('text-6xl')
                                # dash mood box
                                with ui.card():
                                    with ui.row().classes('grid grid-cols-2 w-full opacity-95'):
                                        with ui.row().classes('grid grid-cols-1 w-full opacity-95'):
                                            ui.label(t('mood')).style('font-weight: 1000')
                                            ui.label(config['mood']).style('font-weight: 1000; font-size: 150%')
                                        ui.icon('theater_comedy', color='primary').classes('text-6xl')

                                ui.chip(t('device_id'), icon='content_copy', on_click=lambda: ui.clipboard.write(config['unique-id'])).style('font-weight: 1000; font-size: 150%')

                                ui.chip(t('cloud_token'), icon='content_copy', on_click=lambda: ui.clipboard.write(config['cloud-token'])).style('font-weight: 1000; font-size: 150%')
                                async def read() -> None:
                                    ui.notify(await ui.clipboard.read())

                
        # Team loadout 
    # Specifications tab  
    with ui.tab_panel(specs):
        ui.image(background_image_set).classes('absolute inset-0')
        with ui.row().classes(home_page_layout):
                # Live stats
                with ui.card().classes('w-full'):

                    with ui.card().classes('w-full'):
                        ui.label(t('cpu_specs')).style('font-size: 130%; font-weight: 1000')
                        cpu_label = ui.label().style('font-size: 120%')
                        cpu_threads_label = ui.label().style('font-size: 120%')
                        # Dynamiczne paski progresu dla rdzeni
                        core_progress_bars = []
                        core_labels = []
                    
                    with ui.card().classes('w-full'):
                        ui.label(t('cpu_core_usage_table')).style('font-size: 130%; font-weight: 1000')
                        for i in range(psutil.cpu_count()):
                            with ui.row().classes('items-center').classes('w-full'):
                                bar = ui.linear_progress(value=0, show_value=False).classes('w-full')
                                label = ui.label(f'Core {i}: 0%').classes('w-full').style('margin-left: 1em; font-size: 90%')
                                core_progress_bars.append(bar)
                                core_labels.append(label)
                    with ui.card().classes('w-full'):
                        ram_label = ui.label().style('font-size: 120%')
                        ram_type_label = ui.label().style('font-size: 120%')
                        ram_progress = ui.linear_progress(value=0, show_value=False, color='green').classes('w-full')
                        ram_percent_label = ui.label('0%').style('font-size: 90%')
                    with ui.card().classes('w-full'):
                        disk_label = ui.label().style('font-size: 120%')
                        disk_type_label = ui.label().style('font-size: 120%')
                        disk_progress = ui.linear_progress(value=0, show_value=False, color='orange').classes('w-full')
                        disk_percent_label = ui.label('0%').style('font-size: 90%')

                # Device specs table
                with ui.card().classes('w-full opacity-95'):
                    ui.label(t('device_specification_table')).style('font-size: 130%; font-weight: 1000')
                    def get_full_device_specs():
                        specs = [
                            (t('sys'), platform.system()),
                            (t('node'), platform.node()),
                            (t('release'), platform.release()),
                            (t('version'), platform.version()),
                            (t('machine'), platform.machine()),
                            (t('processor'), get_cpu_info()),
                            (t('python'), platform.python_version()),
                            (t('battery'), get_battery_status()),
                            (t('cpu_temp'), get_cpu_temperature()),
                        ]
                        return specs
                    table = ui.table(
                        columns=[
                            {'name': 'param', 'label': 'Parameter', 'field': 'param'},
                            {'name': 'value', 'label': 'Value', 'field': 'value'},
                        ],
                        rows=[{'param': k, 'value': v} for k, v in get_full_device_specs()],
                        column_defaults={
                            'align': 'left',
                            'headerClasses': 'uppercase text-primary',
                        }
                    ).classes('w-full')

                    # Aktualizacja statystyk co 1s
                    def update_stats():
                        cpu_percent = psutil.cpu_percent(interval=None)
                        per_core = psutil.cpu_percent(interval=None, percpu=True)
                        cpu_label.set_text(f'CPU usage: {cpu_percent}%')
                        cpu_threads_label.set_text(f'{t("cores")}: {psutil.cpu_count(logical=False)}, {t("threads")}: {psutil.cpu_count()}')
                        # Aktualizacja pasków progresu dla rdzeni/wątków
                        for i, bar in enumerate(core_progress_bars):
                            if i < len(per_core):
                                bar.value = per_core[i] / 100
                                core_labels[i].set_text(f'{t("core")} {i}: {per_core[i]}%')
                        mem = psutil.virtual_memory()
                        ram_label.set_text(f'{t("ram")}: {mem.used / (1024**3):.2f}GB / {mem.total / (1024**3):.2f}GB ({mem.percent}%)')
                        ram_type_label.set_text(f'{t("ram_type")}: {get_ram_type()}')
                        ram_progress.value = mem.percent / 100
                        ram_percent_label.set_text(f'{mem.percent}%')
                        disk = psutil.disk_usage('/')
                        disk_label.set_text(f'{t("disk")}: {disk.used / (1024**3):.2f}GB / {disk.total / (1024**3):.2f}GB ({disk.percent}%)')
                        disk_type_label.set_text(f'{t("disk_type")}: {get_disk_type()}')
                        disk_progress.value = disk.percent / 100
                        disk_percent_label.set_text(f'{disk.percent}%')
                        # Aktualizacja tabeli specyfikacji
                        table.rows = [{'param': k, 'value': v} for k, v in get_full_device_specs()]

                    ui.timer(1.0, update_stats)
    # Controls
    with ui.tab_panel(controls):
        ui.label(t('control_panel')).style('font-size: 200%; font-weight: 1000')
    # Personalization
    with ui.tab_panel(personalization):

        ui.image(background_image_set).classes('absolute inset-0')
        with ui.card().classes("w-full text-center"):
            ui.label(t('personalize_your_dash')).style('font-size: 200%; font-weight: 1000')
        with ui.row().classes(personalization_layout):

            #Aibo eye color picker
            with ui.card():
                ui.label(t('eye_color')).style('font-size: 150%; font-weight: 1000')
                with ui.row().classes('grid grid-cols-2 w-full'):
                    # color settings
                    with ui.card():
                        ui.label(t('outer_color'))
                        with ui.button(icon='colorize') as outer_color:
                            eye_outer_color = ui.color_picker(on_pick=lambda e: outer_color.classes(f'!bg-[{e.color}]', eye_color_change_outer(outer_color=e.color)))
                            eye_outer_color.q_color.props('default-view=palette no-header no-footer')
                        ui.separator()
                        ui.label("inner Color:")
                        with ui.button(icon='colorize') as inner_color:
                            eye_inner_color = ui.color_picker(on_pick=lambda e: inner_color.classes(f'!bg-[{e.color}]', eye_color_change_inner(inner_color=e.color)))
                            eye_inner_color.q_color.props('default-view=palette no-header no-footer')
                    # eye overview
                    with ui.image("images/gui/eye.png").classes("w-25 h-25 rounded-full"):
                        with ui.card().classes("w-full h-full !bg-[#eeeee4] rounded-full") as outer_color:
                            with ui.card().classes("w-full h-full !bg-[#000000] rounded-full") as inner_color:
                                ui.label()
            #language change
            with ui.card():
                ui.label(t('language_change')).style('font-size: 150%; font-weight: 1000')
                languages = load_language_selector()
                lang_options = {lang['code']: lang['label'] for lang in languages}
                selected_lang = [config.get('language', 'en')]

                # Funkcja pomocnicza do pobierania ścieżki flagi dla wybranego języka
                def get_flag_path(lang_code):
                    for lang in languages:
                        if lang['code'] == lang_code:
                            return lang['flag']
                    return "images/language_flags/default.png"

                flag_image = ui.image(get_flag_path(selected_lang[0])).classes('rounded-full w-24 h-24 m-auto mb-2')

                def on_language_change(e):
                    selected_lang[0] = e.value
                    flag_image.set_source(get_flag_path(e.value))

                def apply_language():
                    update_config('language', selected_lang[0])
                    load_language(selected_lang[0])
                    ui.notify(f"Language set to: {selected_lang[0]}")
                    os.utime('main.py')

                ui.radio(options=lang_options, value=selected_lang[0], on_change=on_language_change)
                ui.button(t('apply'), on_click=apply_language)
    # New playful dash tab
    with ui.tab_panel(playful_dash):
        ui.image(background_image_set).classes('absolute inset-0')
        with ui.row().classes('grid grid-cols-2 w-full'):
            with ui.card():
                ui.label('Default dance #1').style('font-size: 150%; font-weight: 1000')
                ui.separator()
                with ui.expansion('More info', icon='music_note').classes('w-full'):
                    ui.label('Rich desc..').style('font-size: 110%; font-weight: 500')
    # Caring DASH Tab
    with ui.tab_panel(careful_dash):
        ui.image(background_image_set).classes('absolute inset-0')
        with ui.row().classes('grid grid-cols-1 w-full') as home_row:          
            # ERS 1000 Stats            
            with ui.card().classes('opacity-95'):

                    #dash image scaling
                    with ui.card().classes('w-full'):
                        ui.image(config['dash_image']).props('fit=scale-down').classes('rounded-full').style('height: 400px')

                    with ui.dialog() as dialog, ui.card():
                        # Profile image upload and change 
                        ui.upload(on_upload=lambda e: ui.notify(f'Uploaded {e.name}'),
                        on_rejected=lambda: ui.notify('Rejected!'),
                        max_file_size=10_000_000).classes('max-w-full').props("accept=.png")
                        ui.button('Close', on_click=dialog.close)

                    #aibo Vitals
                    with ui.row().classes('grid grid-cols-2 w-full'):
                            with ui.card().classes('w-full'):
                                ui.label(t('vitals')).style('font-size: 150%; font-weight: 1000')
                                with ui.row().classes('grid grid-cols-3 w-full'):
                                
                                    #Food
                                    with ui.card().classes('w-full'):
                                        with ui.circular_progress(value=0.3, show_value=False, color='orange').classes('w-full h-full items-center m-auto') as food_progress:
                                            ui.icon('local_dining', color='primary').classes('text-2xl').props('flat round').classes('w-full h-full')
                                    
                                    #Water
                                    with ui.card().classes('w-full'):
                                        with ui.circular_progress(value=0.5, show_value=False, color='blue').classes('w-full h-full items-center m-auto') as water_progress:
                                            ui.icon('water_drop', color='primary').classes('text-2xl').props('flat round').classes('w-full h-full')
                                    
                                    #Love
                                    with ui.card().classes('w-full'):
                                        with ui.circular_progress(value=0.8, show_value=False, color='red').classes('w-full h-full items-center m_auto') as love_progress:
                                            ui.icon('favorite', color='primary').classes('text-2xl').props('flat round').classes('w-full h-full')

                            with ui.card().classes('w-full h-full'):
                                ui.label(t('coins')).style('font-weight: 1000; font-size: 120%')
                            
                                with ui.row():
                                    #aibo coins icon
                                    ui.icon('paid', color='primary').classes('text-5xl')
                                    #aibo coins amount with variable
                                    coins_label = ui.label(config['dash_coins']).style('font-weight: 1000; font-size: 230%')
                    #left card
            with ui.card().classes('opacity-95 h-full'):
                #dash coins
                ui.label(t('coins')).style('font-weight: 1000; font-size: 120%')
                ui.label(config['dash_coins']).style('font-weight: 1000; font-size: 230%')

                #playful tab menu with shops        
                with ui.tabs().classes('w-full') as playful_tabs:
                    ui.tab('restaurant', label=t('restaurant'), icon='restaurant')
                    ui.tab('toy_shop', label=t('toy_store'), icon='toys')

                with ui.tab_panels(playful_tabs, value='restaurant').classes('w-full'):

                    with ui.tab_panel(t('restaurant')).classes('h-full'):

                        with ui.row().classes('grid grid-cols-1 w-full'):

                                #Big Meal
                                with ui.card().classes('w-full'):
                                    with ui.row().classes('grid grid-cols-2 w-full'):
                                        ui.icon('fastfood', color='primary').classes('w-full h-full text-8xl')
                                        with ui.card():
                                            #Describe
                                            ui.label(t('large_meal')).style('font-weight: 1000; font-size: 120%')
                                            with ui.list().props('dense separator'):
                                                ui.item(t('food') + ': 100%')
                                                ui.item(t('water') + ': 100%')
                                                ui.item(t('level') + ': +10 points')
                                            ui.separator()
                                            ui.button(t('buy')).classes('w-full')

                                #Medium Meal
                                with ui.card().classes('w-full'):
                                    with ui.row().classes('grid grid-cols-2 w-full'):
                                        ui.icon('dinner_dining', color='primary').classes('w-full h-full text-8xl')
                                        with ui.card():
                                            #Describe
                                            ui.label(t('medium_meal')).style('font-weight: 1000; font-size: 120%')
                                            with ui.list().props('dense separator'):
                                                ui.item(t('food') + ': 50%')
                                                ui.item(t('water') + ': 50%')
                                                ui.item(t('level') + ': +5 points')
                                            ui.separator()
                                            ui.button(t('buy')).classes('w-full')

                    with ui.tab_panel(t('toy_store')).classes('h-full'):
                        ui.label('Second tab')    
    # Service   
    with ui.tab_panel(service):
        ui.image(background_image_set).classes('absolute inset-0')
        with ui.card().classes("w-full text-center"):
            ui.label(t('find_dash_repair_service')).style('font-size: 200%; font-weight: 1000')
        
    # Settings
    with ui.tab_panel(settings):
                ui.label(t('settings_panel')).style('font-size: 200%; font-weight: 1000')
                with ui.tabs().classes('w-full') as settings_tabs:
                    ui_sett = ui.tab(t('ui_settings'))
                    pwr_sett = ui.tab(t('power_settings'))
                    network = ui.tab(t('network_settings'))
                with ui.tab_panels(settings_tabs, value=ui_sett).classes('w-full'):
                    with ui.tab_panel(ui_sett):
                        #Dark mode switch
                        with ui.switch(t('dark_mode')).bind_value(dark_mode) as dark_mode_switch:
                            ui.label(t('dark_mode_enabled')).bind_visibility_from(dark_mode_switch, 'value').style('color: green')
                            ui.tooltip(t('enable_dark_mode')).classes('bg-green')

                        ui.separator() # separator ui

                        #Mobile layout switch
                        ui.label(t('gui_mode_switch')).style('font-size: 130%; font-weight: 500')
                        with ui.toggle({0: t('desktop'), 1: t('mobile')}, value=gui_layout, on_change=lambda e: layout_mod(layout_value=e.value)) as layout_switch:
                            ui.tooltip(t('enable_mobile_layout')).classes('bg-green')
                            
                        ui.separator() # separator ui

                        #GUI Primary color changer
                        ui.label(t('global_primary_color')).style('font-size: 130%; font-weight: 500')
                        with ui.button(icon='colorize'):
                            picker = ui.color_picker(on_pick=lambda e: (ui.colors(primary =f'{e.color}'), change_global_color(value=e.color)))
                            picker.q_color.props('default-view=palette no-header no-footer')

                        ui.separator() # separator ui

                        #background image changer
                        with ui.dialog().classes('w-columns-2xs') as bg_changer, ui.card().classes('p-6 shadow-lg'):
                            with ui.row().classes('grid grid-cols-3 gap-4 w-full'):
                                for img_path in get_background_images():
                                    rel_path = os.path.relpath(img_path, os.path.dirname(__file__))
                                    with ui.card().classes('w-full flex flex-col items-center'):
                                        ui.image(rel_path).props('fit=scale-down').classes('rounded-full w-32 h-32 shadow-md mb-2')
                                        ui.button(t('select'), on_click=lambda p=rel_path: change_background_image(p)).classes('w-full')
                        ui.button(t('background_image_change'), on_click=bg_changer.open)

                        ui.separator() # separator ui


                    with ui.tab_panel(pwr_sett):
                        #power buttons
                        # --- Restart & Shutdown buttons ---
                        with ui.row().classes('grid grid-cols-2 gap-4 w-full'):
                            # Restart button
                            def show_restart_dialog():
                                with ui.dialog() as restart_dialog, ui.card():
                                    ui.label('Czy na pewno chcesz uruchomić ponownie system?').style('font-size: 120%; font-weight: 1000; color: red')
                                    ui.button('Anuluj', on_click=restart_dialog.close)
                                    def do_restart():
                                        ui.notify('Restartowanie systemu...')
                                        import subprocess
                                        subprocess.Popen(['sudo', 'reboot'])
                                    ui.button('Uruchom ponownie', on_click=do_restart)
                                restart_dialog.open()
                            ui.button('Uruchom ponownie', on_click=show_restart_dialog, icon='restart_alt').classes('w-full')
                            # Shutdown button
                            def show_shutdown_dialog():
                                with ui.dialog() as shutdown_dialog, ui.card():
                                    ui.label('Czy na pewno chcesz wyłączyć system?').style('font-size: 120%; font-weight: 1000; color: red')
                                    ui.button('Anuluj', on_click=shutdown_dialog.close)
                                    def do_shutdown():
                                        ui.notify('Wyłączanie systemu...')
                                        import subprocess
                                        subprocess.Popen(['sudo', 'poweroff'])
                                    ui.button('Wyłącz', on_click=do_shutdown)
                                shutdown_dialog.open()
                            ui.button('Wyłącz', on_click=show_shutdown_dialog, icon='power_settings_new').classes('w-full')

                        #Power management settings
                        ui.label(t('power_mgmt')).style('font-size: 130%; font-weight: 500')

                        power_mode_value = {'powersave': 1, 'ondemand': 2, 'performance': 3}.get(config.get('power-mode', 'ondemand'), 2)

                        power_mode_select = ui.toggle(
                            {1: t('power_save'), 2: t('normal'), 3: t('high_performance')},
                            value=power_mode_value,
                            on_change=lambda e: set_power_mode(e.value)
                        )

                    with ui.tab_panel(network):

                        ui.label(t('wifi_settings')).style('font-size: 130%; font-weight: 500')
                        ui.button(t('wifi/hotspot_settings'), on_click=show_wifi_dialog)

                        ui.separator() # separator ui
                
    # About
    with ui.tab_panel(about):
        ui.image(background_image_set).classes('absolute inset-0')
        with ui.row().classes('grid grid-cols-2 w-full'):
            with ui.card():
                ui.label('Made by UNITRONIX').style('font-size: 150%')
                ui.label('D.A.S.H Toolkit').style('font-size: 200%; font-weight: 1000')
                ui.separator()
                ui.label('Github')
                ui.chip('ERS Labolatories Github', icon='ads_click', on_click=lambda: ui.navigate.to("https://github.com/ers-laboratories/Aibo-Toolkit/tree/main", new_tab=True)).style('font-size: 150%')

            with ui.card():
                ui.label('Resources:').style('font-size: 150%')
                ui.separator()
                ui.label('Github')
                ui.chip('Gifs Page', icon='ads_click', on_click=lambda: ui.navigate.to("https://www.flaticon.com/", new_tab=True)).style('font-size: 150%')
                ui.chip('Icons and fonts', icon='ads_click', on_click=lambda: ui.navigate.to("https://fonts.google.com/icons", new_tab=True)).style('font-size: 150%')
            
        with ui.card().classes("w-full opacity-95"):
            
            ui.label('Our Team:').style('font-weight: 1000; font-size: 130%')

            with ui.row().classes('grid grid-cols-1 gap-4 w-full'):
                with ui.card():
                    with ui.image('images/unitronix.png').props('fit=scale-down'):
                        ui.tooltip('UNITRONIX').classes('bg-green').style('font-weight: 1000; font-size: 130%;')

    for tab, content_func in plugin_tabs:
        with ui.tab_panel(tab):
            content_func()

ui.timer(2.0, lambda: refresh_coins_label(coins_label))


#Interface runing command
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='D.A.S.H Toolkit')


