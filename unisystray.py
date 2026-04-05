from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class TrayMenu(QMenu):
	def __init__(self, title: str, checkable: bool):
		super().__init__(title)
		
		self.checkable = checkable
		self.actions = []

	def createAction(self, name: str, func: object, bChecked: bool = False):
		action = QAction(name)
		action.triggered.connect(func)
		action.triggered.connect(lambda: self.checkedStatus(action))
		action.setCheckable(self.checkable)
		action.setChecked(bChecked)
		self.addAction(action)

		self.actions.append(action)

	def checkedStatus(self, selectedAction: QAction):
		if not self.checkable:
			return

		for action in self.actions:
			if action == selectedAction:
				action.setChecked(True)
			else:
				action.setChecked(False)

class Tray(QSystemTrayIcon):
	def __init__(self, path: str, exit: object = None):
		self._app = QApplication([])
		self._app.setQuitOnLastWindowClosed(False)

		super().__init__()
		self.setIcon(QIcon(path))
		self.setVisible(True)

		if (exit == None):
			exit = self._app.quit
		self._exit = exit

	def createMenu(self, title:str, checkable: bool) -> TrayMenu:
		return TrayMenu(title, checkable)
	
	def addMenu(self, object, menu: TrayMenu):
		if isinstance(object, Tray):
			menu.addSeparator()
			menu.createAction("Quit", self._exit)

			object.setContextMenu(menu)
		else:
			object.addMenu(menu)

	def display(self):
		self._app.exec()

	def quit(self):
		self._app.quit()