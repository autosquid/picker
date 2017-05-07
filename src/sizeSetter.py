import inputDlg
from PyQt5 import QtGui, QtWidgets
import sys

class sizeSetter(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(sizeSetter, self).__init__(parent)
        self.ui = inputDlg.Ui_Dialog()
        self.ui.setupUi(self)

    def getSize(self):
        self.row = int(self.ui.lineEdit.text())
        self.col = int(self.ui.lineEdit_2.text())
        return self.row,self.col


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = sizeSetter()
    myapp.show()
    sys.exit(app.exec_())
