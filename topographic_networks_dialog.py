# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TopographicNetworksDialog
                                 A QGIS plugin
 Creation and analysis of topographic (surface) networks.
                             -------------------
        begin                : 2014-10-26
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Zoran Čučković
        email                : /
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_topographic_networks.ui'))


class TopographicNetworksDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(TopographicNetworksDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        #connections
        self.cmdBrowse.clicked.connect(self.fileOutput)
##        self.cmdAbout.clicked.connect(self.OpenPDFfile)


    def returnDEMLayer(self):
        #ovo mu daje varant sa svim podaccima
        l=self.cmbDEM.itemData(self.cmbDEM.currentIndex())
        return str(l)
    
    def returnClassificationLayer(self):
        i=self.cmbClassification.currentIndex()
        if i>0: return str(self.cmbClassification.itemData(i))
        else : return 0
        
    def returnOutputFile(self):
        #ovo mu daje varant sa svim podaccima
        l=self.txtOutput.toPlainText() #inace text()..
        return str(l)
    
    def returnSearch (self):
        try: return int(self.txtSearch.text()) #inace text()..
        except: return 1

    def returnMerge (self):
        try: return int(self.txtMerge.text()) #inace text()..
        except: return 1
        
    def returnInverse(self):      
        if self.chkInverse.isChecked(): return True
        else: return False
                
    def returnLowest(self):
               
        #if self.chkLowest.isChecked(): return True
        #else: return False
		return False
		
    def returnOutput (self):
        if self.chkComplete.isChecked(): return "Complete"
        elif self.chkRidge.isChecked(): return "Ridge"
        elif self.chkID.isChecked(): return "ID"
      #  elif self.chkFlow.isChecked(): return "Flow"
     #   elif self.chkReeb.isChecked(): return "Reeb"
        else : return 0
        
    def fileOutput(self): #problem je ekstenzija!!!!
            homedir = os.path.expanduser('~') # ...works on at least windows and linux. 
            
            filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', homedir, '*')
            try :
                fname = open(filename, 'w')
                self.txtOutput.clear()
                self.txtOutput.insertPlainText(filename)
                #fname.write(txtOutput.toPlainText())
                fname.close()
            except: pass

            
