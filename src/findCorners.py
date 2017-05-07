import sys
import os
from PyQt5 import QtGui, QtWidgets
from mainui import Ui_Dialog
import cv2
import numpy as np
import scipy.io
from sizeSetter import sizeSetter
import hammer
from mocinput import Input

boardWidth = 0.04  # the width of the board in m
boardHeight = 0.04  # the height of the board in m


class FindCornerGui(QtWidgets.QDialog):
    ''' the is the corner finder which works similar with matlab calib
        toolbox corner extractor
    '''

    def __init__(self, parent=None):
        super(FindCornerGui, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.path_pushButton.clicked.connect(self.setDirPath)
        self.ui.find_pushButton.clicked.connect(self.begin_find)
        self.ui.next_pushButton.clicked.connect(self.findNextImage)
        self.ui.refind_pushButton.clicked.connect(self.findTempImage)
        self.ui.save_pushButton.clicked.connect(self.ChangeMatName)

    def keysUpdateAfterFind(self):
        if self.count == len(self.imageLists):
            self.ui.save_pushButton.setEnabled(True)

    def showImageName(self, name):
        self.ui.name_label.setText(name)

    def setDirPath(self):
        self.dirPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Data", Input.dockerdatavolumn_local)
        self.ui.path_lineEdit.setText(self.dirPath)
        self.matName = str(self.dirPath + os.sep + "tmp.mat")

    def begin_find(self):
        self.imageLists = []
        for i in os.listdir(self.dirPath):
            name, extension = os.path.splitext(i)
            if hammer.isImage(i):
                self.imageLists.append(i)
        self.winName = 'findCorners'
        self.window_init()

        self.count = 0

        scipy.io.savemat(self.matName, {}, oned_as='row')
        self.find(0)

    def find(self, count):
        self.ptsCount = 0
        self.corners = []
        self.imageName, _ = os.path.splitext(self.imageLists[self.count])
        image = cv2.imread(str(self.dirPath + os.sep + self.imageLists[count]))

        if self.count == 0:
            self.saveNxNy(image)
        temp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        show = image.copy()
        self.image = show
        self.window_init()
        cv2.imshow(self.winName, self.image)
        cv2.waitKey(0)
        row = self.row + 1
        col = self.col + 1
        rightPts = []
        index = []
        for i in range(0, col):
            for j in range(0, row):
                rightPts.append(
                    [(col - i - 1) * boardWidth, (row - j - 1) * boardHeight])
        self.findCorners(temp, self.corners, rightPts, row, col)
        self.corners = self.corners.tolist()

        for i in range(0, len(self.corners[0])):
            cv2.circle(image,
                       (int(self.corners[0][i][0]), int(self.corners[0][i][1])), 10, (255, 0, 0), 4)

        cv2.imshow(self.winName, image)
        resizeImage = cv2.resize(image, (731, 486))
        rgbImage = cv2.cvtColor(resizeImage, cv2.COLOR_BGR2RGB)
        qimg = QtGui.QImage(rgbImage.data, rgbImage.shape[1],
                            rgbImage.shape[0], rgbImage.strides[0], QtGui.QImage.Format_RGB888)

        self.showImageName(self.imageName)
        self.ui.image_label.setPixmap(QtGui.QPixmap.fromImage(qimg))
        self.keysUpdateAfterFind()
        self.saveMat(self.imageName, self.corners, rightPts)

    def findNextImage(self):
        if self.count < len(self.imageLists) - 1:
            self.count = self.count + 1
            self.find(self.count)
        else:
            QtWidgets.QMessageBox.information(
                self, "In this dir", 'No images reminded')

    def findTempImage(self):
        self.find(self.count)

    def saveNxNy(self, image):
        mat = scipy.io.loadmat(self.matName)
        shape = image.shape
        mat['nx'] = shape[1]
        mat['ny'] = shape[0]
        mat['dX'] = boardWidth
        mat['dY'] = boardHeight
        scipy.io.savemat(self.matName, mat, oned_as='row')

    def ChangeMatName(self):
        if os.path.exists(self.dirPath + os.sep + "Calib_Results.mat"):
            os.remove(str(self.dirPath + os.sep + "Calib_Results.mat"))
        os.rename(self.dirPath + os.sep + "tmp.mat",
                  self.dirPath + os.sep + "Calib_Results.mat")

    def saveMat(self, imageName, corners, rightPts):
        corners = corners[0]
        rightPts_inM = []
        for i in rightPts:
            rightPts_inM.append([self.row * boardHeight - i[1], i[0], 0])
        rightPts = rightPts_inM
        corners = zip(*corners)
        rightPts = zip(*rightPts)
        mat = scipy.io.loadmat(self.matName)
        mat['x_' + imageName] = corners
        mat['X_' + imageName] = rightPts
        mat['dX_' + imageName] = boardWidth
        mat['dY_' + imageName] = boardHeight
        scipy.io.savemat(self.matName, mat, oned_as='row')

    def window_init(self):
        cv2.namedWindow(self.winName,
                        cv2.WINDOW_NORMAL)
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        cv2.resizeWindow(
            self.winName, screen.width() * 3 / 4, screen.height() * 3 / 4)
        cv2.moveWindow(self.winName, screen.width() / 8, screen.height() / 8)
        cv2.setMouseCallback(self.winName, self.on_mouse)

    def findCorners(self, image, corners, rightPts, row, col):
        self.corners = np.asarray(corners, dtype='float32')
        cv2.cornerSubPix(image, self.corners, (10, 10), (-1, -1),
                         (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS,
                          30, 0.1))
        right4 = np.array(
            [[0, (
                row - 1) * boardHeight], [(
                col - 1) * boardWidth, (row - 1) * boardHeight],
             [(col - 1) * boardWidth, 0], [0, 0]], np.float32)
        trans = cv2.getPerspectiveTransform(right4, self.corners)

        rightPts = np.asarray(rightPts, dtype='float32')
        rightPts = np.array([rightPts])
        self.corners = cv2.perspectiveTransform(rightPts, trans)
        cv2.cornerSubPix(image, self.corners, (20, 20), (-1, -1),
                         (cv2.TERM_CRITERIA_MAX_ITER | cv2.TERM_CRITERIA_EPS,
                          30, 0.1))

    def setSize(self):
        setter = sizeSetter()
        if setter.exec_() == QtWidgets.QDialog.Accepted:
            self.row, self.col = setter.getSize()

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.ptsCount < 4:
                self.ptsCount = self.ptsCount + 1
                if self.ptsCount > 1:
                    if self.ptsCount == 1 or self.ptsCount == 3:
                        color = (255, 0, 0)
                    else:
                        color = (0, 255, 0)
                    cv2.line(
                        self.image, (int(self.corners[self.ptsCount - 2][0]),
                                     int(self.corners[
                                         self.ptsCount - 2][1])),
                        (x, y), color, 4)
                if self.ptsCount == 4:
                    cv2.line(self.image, (x, y), (int(self.corners[0][0]),
                                                  int(self.corners[0][1])), (255, 0, 0), 4)
                self.corners.append((float(x), float(y)))
                cv2.circle(self.image, (x, y), 15, (0, 0, 255), 4)
                cv2.imshow(self.winName, self.image)
            if self.ptsCount == 4:
                self.setSize()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = FindCornerGui()
    myapp.show()
    sys.exit(app.exec_())
