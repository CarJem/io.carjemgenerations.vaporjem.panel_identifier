#!/usr/bin/env python3
import subprocess
import json
import copy
import argparse
from configparser import (ConfigParser, MissingSectionHeaderError,
                          ParsingError, DEFAULTSECT)
import difflib
import os
import ini2json

used_ids = []
screen_ids = []
systemtray_ids = []

panelsToKeep = {}
panelsToRemove = {}

SystrayPairs = {}

def collect_appletsrc():
    global appletsrc
    global plasmashellrc

    global used_ids
    global screen_ids
    global systemtray_ids

    global panelsToKeep
    global panelsToRemove

    global SystrayPairs

    for screen_id in plasmashellrc["ScreenConnectors"]:
        screen_ids.append(screen_id)

    for containment_id in appletsrc["Containments"]:
        used_ids.append(containment_id)
        containment = appletsrc["Containments"][containment_id]

        if "plugin" in containment and containment["plugin"] == "org.kde.plasma.private.systemtray":
            systemtray_ids.append(containment_id)

        elif "Applets" in containment:
            for applet_id in containment["Applets"]:
                applet = containment["Applets"][applet_id]
                used_ids.append(applet_id)

                if "plugin" in applet and applet["plugin"] == "org.kde.plasma.systemtray" and "Configuration" in applet and "SystrayContainmentId" in applet["Configuration"]:
                        tray_id = applet["Configuration"]["SystrayContainmentId"]
                        SystrayPairs[tray_id] = containment_id

                if "plugin" in containment and containment["plugin"] == "org.kde.panel" and "plugin" in applet and applet["plugin"] == "io.carjemgenerations.vaporjem.panel_identifier":
                    if "Configuration" in applet and "General" in applet["Configuration"] and "allDisplays" in applet["Configuration"]["General"] and applet["Configuration"]["General"]["allDisplays"] == "true":
                        panelsToKeep[containment_id] = containment
                    else:
                        panelsToRemove[containment_id] = containment
    
def get_new_applet_container_ids():
    global used_ids

    i = 100
    while (i in used_ids):
        i += 1

    used_ids.append(i)
    return i

def create_new_panel_from_clone(containment, screen_id):
    global appletsrc

    if "Applets" in containment:
        applets = containment["Applets"]
        for old_applet_id in list(applets):
            applet = applets[old_applet_id]
            applet_id = get_new_applet_container_ids()

            #Clone System Tray
            if "plugin" in applet and applet["plugin"] == "org.kde.plasma.systemtray" and "Configuration" in applet and "SystrayContainmentId" in applet["Configuration"]:
                    old_tray_id = applet["Configuration"]["SystrayContainmentId"]
                    if old_tray_id in systemtray_ids:
                        old_system_tray = copy.deepcopy(appletsrc["Containments"][old_tray_id])
                        system_tray = create_new_panel_from_clone(old_system_tray, screen_id)
                        tray_id = get_new_applet_container_ids()
                        appletsrc["Containments"][tray_id] = system_tray
                        applet["Configuration"]["SystrayContainmentId"] = str(tray_id)
            
            #Indentifier for Panel
            if "plugin" in containment and containment["plugin"] == "org.kde.panel" and "plugin" in applet and applet["plugin"] == "io.carjemgenerations.vaporjem.panel_identifier":
                if "Configuration" in applet and "General" in applet["Configuration"]:
                    applet["Configuration"]["General"]["allDisplays"] = "false"
                    applet["Configuration"]["General"]["identifier"] = screen_id

            #Fixing Order on Contaiment
            if "General" in containment and "AppletOrder" in containment["General"]:
                applet_order = containment["General"]["AppletOrder"]
                applet_order = applet_order.replace(old_applet_id, str(applet_id))
                containment["General"]["AppletOrder"] = applet_order
            
            applets.pop(old_applet_id)
            containment["Applets"][applet_id] = applet
    return containment

def copy_panel_settings(old_panel_number, new_panel_number):
    global plasmashellrc

    panel_number = str(new_panel_number)

    for plasmaview_name in list(plasmashellrc["PlasmaViews"]):
        if plasmaview_name.startswith("Panel ") and plasmaview_name.endswith(old_panel_number):
            new_plasmaview = copy.deepcopy(plasmashellrc["PlasmaViews"][plasmaview_name])
            plasmashellrc["PlasmaViews"]["Panel " + panel_number] = new_plasmaview
    
def set_appletsrc_screen():
    global appletsrc
    global plasmashellrc
    
    global used_ids
    global screen_ids
    global systemtray_ids

    global panelsToKeep
    global panelsToRemove

    global SystrayPairs

    applet_cfg_path = os.path.expanduser('~/.config/plasma-org.kde.plasma.desktop-appletsrc')
    plasmashellrc_cfg_path = os.path.expanduser('~/.config/plasmashellrc')

    appletsrc = ini2json.read(applet_cfg_path)
    plasmashellrc = ini2json.read(plasmashellrc_cfg_path)

    collect_appletsrc()

    #Get Rid of Panels that aren't rooted or specific to screens
    for containment_id in panelsToRemove:
        for tray_id in list(systemtray_ids):
            if tray_id in SystrayPairs and SystrayPairs[tray_id] == containment_id:
                SystrayPairs.pop(tray_id)
                systemtray_ids.remove(tray_id)
        appletsrc["Containments"].pop(containment_id)
        used_ids.remove(containment_id)
        

    #Remove Orphaned SystemTrays
    for tray_id in list(systemtray_ids):
        if tray_id not in SystrayPairs:
            appletsrc["Containments"].pop(tray_id)
            systemtray_ids.remove(tray_id)

    #create new panels
    for screen_id in screen_ids:
        for old_contaiment_id in panelsToKeep:
            containment = panelsToKeep[old_contaiment_id]

            if "lastScreen" in containment and not containment["lastScreen"] == screen_id:
                new_containment = copy.deepcopy(containment)
                new_containment["lastScreen"] = screen_id
                containment_id = get_new_applet_container_ids()
                appletsrc["Containments"][containment_id] = create_new_panel_from_clone(new_containment, screen_id)
                copy_panel_settings(old_contaiment_id, containment_id)


    ini2json.write(appletsrc, applet_cfg_path)
    ini2json.write(plasmashellrc, plasmashellrc_cfg_path)

def main():
    subprocess.Popen(['/usr/bin/kquitapp5', 'plasmashell']).wait()
    set_appletsrc_screen()
    subprocess.Popen(['/usr/bin/kstart5', 'plasmashell'],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    #qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.showInteractiveConsole

if __name__ == '__main__':
    main()