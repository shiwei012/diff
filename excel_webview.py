#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import PyQt5
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebChannel import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtNetwork import *
import sys
from optparse import OptionParser
import os
from read_excel import ExcelReader
import algo
import json
from functools import partial
import time
import hashlib

def md5(fname):
	hash_md5 = hashlib.md5()
	with open(fname, "rb") as f:
		for chunk in iter(lambda: f.read(4096), b""):
			hash_md5.update(chunk)
	return hash_md5.hexdigest()
 
 
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

def replaceFileStr(fileOld, fileNew, strOld, strNew):
	if os.path.exists(fileOld) is False:
		return
	try:
		os.remove(fileNew)
	except OSError:
		pass
	with open(fileOld, "rt", encoding='UTF-8') as fin:
		with open(fileNew, "w+", encoding='UTF-8') as fout:
			for line in fin:
				fout.write(line.replace(strOld, strNew))

class CompExcel(QWidget):
	def __init__(self):
		super(CompExcel,self).__init__()

		# modify html
		# {__cwd__}
		import platform
		if platform.system() == "Windows":
			self.cwd = "file:///" + os.getcwd()
		else:
			self.cwd = "file://" + os.getcwd()
		replaceFileStr(os.getcwd() + "/view_excel.template.html", os.getcwd() + "/view_excel.html", "{__cwd__}", self.cwd)

		self.f1name = None
		self.f2name = None
		self.loadPageList = ["index.html", "view_excel.html"]
		self.loadPageIndex = 0

		# self.xlsWD = self.cwd
		self.xlsWD = '/Users/david/Downloads/excel_cmp_data'
		rightLayout = QVBoxLayout()
		mainLayout = QVBoxLayout()
		hboxLayout = QHBoxLayout()		
		self.creatChooseFileBox()
		hboxLayout.addWidget(self.chooseFileBox)
		self.createCompView()
		self.createTab()
		rightLayout.addWidget(self.tabBox)
		rightLayout.addWidget(self.compView)
		hboxLayout.addLayout(rightLayout)
		mainLayout.addLayout(hboxLayout)
		self.createProgressBar()
		mainLayout.addWidget(self.progressBar)
		self.setLayout(mainLayout)

	def createProgressBar(self):
		self.progressBar = QProgressBar(self)
		self.progressBar.setMinimum(0)    
		self.progressBar.setMaximum(100)  

	def startProgress(self):
		self.progressBar.setValue(0)
		self.progressBar.setValue(30)

	def stopProgress(self):
		self.progressBar.setValue(100)

	def createTab(self):
		self.tabBox = QGroupBox("")
		self.tabBoxLayout = QHBoxLayout()
		self.tabBox.setLayout(self.tabBoxLayout)
		pass

	def onTabBtnSelected(self, name):
		self.changeLoadPageIndex(1)
		def js_callback(result):
			print(result)
		print (name)
		"""
		每 256 * 1024字节的传送
		"""
		size = 1024 * 1024
		# size = 98
		for i in range(int(len(self.cmpRet[name]) / size) + 1):
			self.compView.page().runJavaScript("delta('" + self.cmpRet[name][i * size : (i+1) * size] + "');", js_callback)
		self.compView.page().runJavaScript('applyData();', js_callback)
		# self.compView.page().runJavaScript('applyData(' + self.cmpRet[name] + ');', js_callback)

	def createTabBtns(self, names):
		for name in names:
			print ('createTabBtns', name)
			btn = QPushButton(name)
			# btn.clicked.connect(lambda: self.onTabBtnSelected(name))  用lambda两个的onclick绑定都在最后一个上
			btn.clicked.connect(partial(self.onTabBtnSelected, name))  
			self.tabBoxLayout.addWidget(btn)
		pass

	def delTabBtns(self):
		for i in reversed(range(self.tabBoxLayout.count())): 
			self.tabBoxLayout.itemAt(i).widget().deleteLater()
		pass

	def createCompView(self):
		self.compView = Browser()
		channel = QWebChannel()
		handler = CallHandler()
		channel.registerObject('handler', handler)
		self.compView.page().setWebChannel(channel)
		self.compView.load(self.cwd + "/" + self.loadPageList[self.loadPageIndex])
		self.compView.showMaximized()

	def creatChooseFileBox(self):
		self.chooseFileBox = QGroupBox("")
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

	def test1(self):
		self.f1name = '/Users/david/Downloads/excel_cmp_data/1/a.xlsx'
		self.f2name = '/Users/david/Downloads/excel_cmp_data/1/b.xlsx'

	def test2(self):
		self.f1name = '/Users/david/Downloads/excel_cmp_data/2/a.xlsx'
		self.f2name = '/Users/david/Downloads/excel_cmp_data/2/b.xlsx'

	def test3(self):
		self.f1name = '/Users/david/Downloads/excel_cmp_data/3/a.xlsx'
		self.f2name = '/Users/david/Downloads/excel_cmp_data/3/b.xlsx'

	def test4(self):
		self.f1name = '/Users/david/Downloads/excel_cmp_data/4/a.xlsx'
		self.f2name = '/Users/david/Downloads/excel_cmp_data/4/b.xlsx'

	def test5(self):
		self.f1name = '/Users/david/Downloads/excel_cmp_data/5/a.xlsx'
		self.f2name = '/Users/david/Downloads/excel_cmp_data/5/b.xlsx'

	def test6(self):
		self.f1name = '/Users/david/Downloads/excel_cmp_data/6/a.xlsx'
		self.f2name = '/Users/david/Downloads/excel_cmp_data/6/b.xlsx'

	def test_start(self):
		self.f1name = '/Users/david/Downloads/excel1.xlsx'
		self.f2name = '/Users/david/Downloads/excel2.xlsx'

	def changeLoadPageIndex(self, index):
		if self.loadPageIndex != index:
			self.loadPageIndex = index
			self.compView.load(self.cwd + "/" + self.loadPageList[self.loadPageIndex])
			self.compView.showMaximized()

	def start(self):
		
		# self.test_start()
		# self.test1()
		# self.test2()
		# self.test3()
		# self.test4()
		# self.test5()
		# self.test6()
		if self.f1name is None or self.f2name is None:
			self.hint("Message", "Please set file1 and file2 first")
			return

		# same file?
		if md5(self.f1name) == md5(self.f2name):
			self.hint("Message", "The two file are the same")
			self.reset()
			return

		self.changeLoadPageIndex(1)

		self.file1er = ExcelReader(self.f1name)
		self.file2er = ExcelReader(self.f2name)

		file1SheetNames = self.file1er.get_sheets_names()
		file2SheetNames = self.file2er.get_sheets_names()

		self.cmpRet = {}
		names = []
		for fn in file1SheetNames:
			if fn in file2SheetNames:
				start = time.clock()
				print (fn)
				names.append(fn)
				a = self.file1er.get_sheet_matrix(fn)
				print (a)
				b = self.file2er.get_sheet_matrix(fn)
				print (b)
				data = {}
				data["table1"] = {}
				data["table1"]["name"] = self.f1name + '[' + fn + ']'
				data["table1"]["data"], cell_diff_a2A, cell_diff_A2a, cell_diff_a2b, row_ins_A2b, row_ins_a2A, col_ins_A2b, col_ins_a2A, row_del_A, col_del_A = algo.get_diff_matrix(a, b)
				print (data["table1"]["data"])
				data["table2"] = {}
				data["table2"]["name"] = self.f2name + '[' + fn + ']'
				data["table2"]["data"], cell_diff_b2B, cell_diff_B2b, cell_diff_b2a, row_ins_B2a, row_ins_b2B, col_ins_B2a, col_ins_b2B, row_del_B, col_del_B = algo.get_diff_matrix(b, a)
				print (row_ins_B2a, row_ins_b2B, col_ins_B2a, col_ins_b2B)
				data["cell_diff_A2B"] = algo.get_cell_diff_A2B(cell_diff_a2A, cell_diff_A2a, cell_diff_a2b, cell_diff_b2B, cell_diff_B2b, cell_diff_b2a)
				data["table1"]["row_ins"] = algo.get_ins_A2B(row_ins_A2b, row_ins_a2A, row_ins_B2a, row_ins_b2B)
				print ('row_ins', data["table1"]["row_ins"])
				data["table1"]["col_ins"] = algo.get_ins_A2B(col_ins_A2b, col_ins_a2A, col_ins_B2a, col_ins_b2B)
				data["table1"]["row_del"] = row_del_A
				data["table1"]["col_del"] = col_del_A
				data["table2"]["row_ins"] = algo.get_ins_A2B(row_ins_B2a, row_ins_b2B, row_ins_A2b, row_ins_a2A)
				data["table2"]["col_ins"] = algo.get_ins_A2B(col_ins_B2a, col_ins_b2B, col_ins_A2b, col_ins_a2A)
				data["table2"]["row_del"] = row_del_B
				data["table2"]["col_del"] = col_del_B
				print (row_del_A)
				print (col_del_A)
				print (row_del_B)
				print (col_del_B)
				data = json.dumps(data)
				self.cmpRet[fn] = data
				elapsed = (time.clock() - start)
				print("Time used:",elapsed)
		self.stopProgress()
		if len(names) > 0:
			self.createTabBtns(names)
			self.start_btn.setEnabled(False)
		else:
			self.hint("Message", "There is no sheet to be compared in this two file")
			self.reset()
		pass

	def reset(self):
		self.f1name = None
		self.f2name = None
		self.start_btn.setEnabled(True)
		self.file1_btn.setText('file1')
		self.file1_btn.setEnabled(True)
		self.file2_btn.setText('file2')
		self.file2_btn.setEnabled(True)
		self.loadPageIndex = 0
		self.compView.load(self.cwd + "/" + self.loadPageList[self.loadPageIndex])
		self.delTabBtns()
		self.progressBar.setValue(0)
		pass

	def getfile1(self):
		self.f1name = QFileDialog.getOpenFileName(self, 'Open file', self.xlsWD, "Excel files (*.xlsx *.xls)")[0]
		if os.path.isfile(self.f1name) is False:
			self.hint("Message", "The input file1 is not a file")
			self.f1name = None
			self.file1_btn.setEnabled(True)
			return
		name = os.path.basename(self.f1name)
		self.file1_btn.setText(name[0:5] + "..." if len(name) > 5 else name)
		self.file1_btn.setEnabled(False)
		self.progressBar.setValue(10)

	def getfile2(self):
		self.f2name = QFileDialog.getOpenFileName(self, 'Open file', self.xlsWD, "Excel files (*.xlsx *.xls)")[0]
		if os.path.isfile(self.f2name) is False:
			self.hint("Message", "The input file2 is not a file")
			self.f2name = None
			self.file2_btn.setEnabled(True)
			return
		name = os.path.basename(self.f2name)
		self.file2_btn.setText(name[0:5] + "..." if len(name) > 5 else name)
		self.file2_btn.setEnabled(False)
		self.progressBar.setValue(20)

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
