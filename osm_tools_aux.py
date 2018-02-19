# -*- coding: utf-8 -*-
"""
Created on Thu May 04 09:38:00 2017

@author: nnolde
"""
import os.path
import yaml
import requests

from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt

import qgis.gui
import qgis.utils
from qgis.core import QgsVectorLayer, Qgis, QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsProject
from qgis.gui import *

script_dir = os.path.dirname(os.path.abspath(__file__))

#TODO: Reproject instead of warning
def transformToWGS(old_layer, old_crs):
    new_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", old_layer.name(), "memory")
    new_crs = QgsCoordinateReferenceSystem(4326)
    old_crs = QgsCoordinateReferenceSystem(old_crs)
    xform = QgsCoordinateTransform(old_crs, new_crs, QgsProject.instance())
    feats = []
    for f in old_layer.getFeatures():
        g = f.geometry()
        g.transform(xform)
        f.setGeometry(g)
        feats.append(f)
    
    new_layer.dataProvider().addFeatures(feats)
    attrs = old_layer.dataProvider().fields().toList()
    new_layer.dataProvider().addAttributes(attrs)
    new_layer.updateFields()    
    
    return new_layer


#TODO: More error checking, e.g. print start/end X & Y in message bar
def CheckStatus(code, req):
    code_text = requests.status_codes._codes[code]
    msg = "HTTP status {}: {}\nGet request: {}".format(code, code_text, req)
    qgis.utils.iface.messageBar().pushMessage(msg, level=Qgis.Critical, duration=20)
    return

def readConfig():
    with open(os.path.join(script_dir, "config.yml")) as f:
        doc = yaml.safe_load(f)
        
    return doc

def writeConfig(key, value):
    
    doc = readConfig()
    doc[key] = value
    with open(os.path.join(script_dir, "config.yml"), 'w') as f:
        yaml.safe_dump(doc, f)
        
        
def pushProgressBar(iface):
    progressMessageBar = iface.messageBar().createMessage("Requesting analysis from ORS...")
    progress = QProgressBar(progressMessageBar)
    progress.setMaximum(100)
    progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    progressMessageBar.layout().addWidget(progress)
    iface.messageBar().pushWidget(progressMessageBar, level=Qgis.Info)
    
    return progress