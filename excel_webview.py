#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import PyQt5
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
# from PyQt5.QtWebKitWidgets import QWebView , QWebPage
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
from PyQt5.QtWebEngineCore import *
# from PyQt5.QtWebKit import QWebSettings
from PyQt5.QtNetwork import *
import sys
from optparse import OptionParser
import os
from read_excel import ExcelReader
import algo
import json
 
 
class MyBrowser(QWebEnginePage):
	''' Settings for the browser.'''
 
	def userAgentForUrl(self, url):
		''' Returns a User Agent that will be seen by the website. '''
		return "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
 
class Browser(QWebEngineView):
	def __init__(self):
		# QWebView
		self.view = QWebEngineView.__init__(self)
		#self.view.setPage(MyBrowser())
		self.setWindowTitle('Loading...')
		self.titleChanged.connect(self.adjustTitle)
		#super(Browser).connect(self.ui.webView,QtCore.SIGNAL("titleChanged (const QString&)"), self.adjustTitle)
 
	def load(self,url):  
		self.setUrl(QUrl(url)) 
 
	def adjustTitle(self):
		self.setWindowTitle(self.title())
 
	def disableJS(self):
		settings = QWebEngineSettings.globalSettings()
		settings.setAttribute(QWebEngineSettings.JavascriptEnabled, False)

class CallHandler(QObject):
	@pyqtSlot()
	def test(self):
		print('call received')

"""
python call js
def js_callback(result):
	print(result)

def complete_name():
	view.page().runJavaScript('completeAndReturnName();', js_callback)

js call python
https://stackoverflow.com/questions/39544089/how-can-i-access-python-code-from-javascript-in-pyqt-5-7
"""

class CompExcel(QWidget):
	def __init__(self):
		super(CompExcel,self).__init__()

		self.cwd = os.getcwd()
		self.f1name = None
		self.f2name = None

		mainLayout = QVBoxLayout()
		hboxLayout = QHBoxLayout()		
		self.creatChooseFileBox()
		hboxLayout.addWidget(self.chooseFileBox)
		self.createCompView()
		hboxLayout.addWidget(self.compView)
		mainLayout.addLayout(hboxLayout)
		self.setLayout(mainLayout)

	def createCompView(self):
		self.compView = Browser()
		channel = QWebChannel()
		handler = CallHandler()
		channel.registerObject('handler', handler)
		self.compView.page().setWebChannel(channel)
		self.compView.load("file://" + self.cwd + "/view_excel.html")
		self.compView.showMaximized()

	def creatChooseFileBox(self):
		self.chooseFileBox = QGroupBox("Vbox layout")
		layout = QVBoxLayout() 
		# nameLabel = QLabel("tile")
		# bigEditor = QTextEdit()
		# bigEditor.setPlainText("this is the text")
		self.file1_btn = QPushButton("file1")
		self.file1_btn.clicked.connect(self.getfile1)
		self.file2_btn = QPushButton("file2")
		self.file2_btn.clicked.connect(self.getfile2)
		self.start_btn = QPushButton("start")
		self.start_btn.clicked.connect(self.start)
		self.reset_btn = QPushButton("reset")
		self.reset_btn.clicked.connect(self.reset)
		layout.addWidget(self.file1_btn)
		layout.addWidget(self.file2_btn)
		layout.addWidget(self.start_btn)
		layout.addWidget(self.reset_btn)
		self.chooseFileBox.setLayout(layout)

	def test_start(self):
		self.f1name = '/Users/david/Downloads/excel1.xlsx'
		self.f2name = '/Users/david/Downloads/excel2.xlsx'


	def start(self):
		self.test_start()
		if self.f1name is None or self.f2name is None:
			self.hint("Message", "Please set file1 and file2 first")
			return

		self.file1er = ExcelReader(self.f1name)
		self.file2er = ExcelReader(self.f2name)

		a = self.file1er.get_sheet_matrix('Sheet1')
		b = self.file2er.get_sheet_matrix('Sheet1')
		data = {}
		data["table1"] = {}
		data["table1"]["name"] = self.f1name + '[Sheet1]'
		data["table1"]["data"] = algo.get_diff_matrix(a, b)
		data["table2"] = {}
		data["table2"]["name"] = self.f2name + '[Sheet1]'
		data["table2"]["data"] = algo.get_diff_matrix(b, a)
		data = json.dumps(data)
		print data
		def js_callback(result):
			print(result)
		self.compView.page().runJavaScript('applyData(' + data + ');', js_callback)

		self.start_btn.setEnabled(False)
		pass

	def reset(self):
		self.f1name = None
		self.f2name = None
		self.start_btn.setEnabled(True)
		self.file1_btn.setText('file1')
		self.file1_btn.setEnabled(True)
		self.file2_btn.setText('file2')
		self.file2_btn.setEnabled(True)
		pass

	def getfile1(self):
		self.f1name = QFileDialog.getOpenFileName(self, 'Open file', '/Users/david/Downloads', "Excel files (*.xlsx *.xls)")[0]
		if os.path.isfile(self.f1name) is False:
			self.hint("Message", "The input file1 is not a file")
			self.f1name = None
			self.file1_btn.setEnabled(True)
			return
		name = os.path.basename(self.f1name)
		self.file1_btn.setText(name[0:5] + "..." if len(name) > 5 else name)
		self.file1_btn.setEnabled(False)

	def getfile2(self):
		self.f2name = QFileDialog.getOpenFileName(self, 'Open file', '/Users/david/Downloads', "Excel files (*.xlsx *.xls)")[0]
		if os.path.isfile(self.f2name) is False:
			self.hint("Message", "The input file2 is not a file")
			self.f2name = None
			self.file2_btn.setEnabled(True)
			return
		name = os.path.basename(self.f2name)
		self.file2_btn.setText(name[0:5] + "..." if len(name) > 5 else name)
		self.file2_btn.setEnabled(False)

	def hint(self, title, msg):
		msgBox = QMessageBox( self )
		msgBox.setIcon(QMessageBox.Information)
		msgBox.setText(title)

		msgBox.setInformativeText(msg)
		msgBox.addButton(QMessageBox.Yes)
		msgBox.addButton(QMessageBox.No)

		msgBox.setDefaultButton(QMessageBox.Yes) 
		ret = msgBox.exec_()

		if ret == QMessageBox.Yes:
			print( "Yes" )
			return
		else:
			print( "No" )
			return


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = CompExcel()
	ex.showMaximized()
	ex.show()
	sys.exit(app.exec_())


# wd = os.getcwd()
# app = QApplication(sys.argv) 
# view = Browser()
# channel = QWebChannel()
# handler = CallHandler()
# channel.registerObject('handler', handler)
# view.page().setWebChannel(channel)

# view.showMaximized()
# view.load("file://" + wd + "/view_excel.html")
# # view.page().runJavaScript("alert('hehe')")

# app.exec_()