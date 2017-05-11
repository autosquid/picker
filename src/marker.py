__author__ = 'rainawu'

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os


class ImageMarker(QMainWindow):
    def __init__(self, imageList, parent=None):
        super(ImageMarker, self).__init__(parent)
        self.imageWidget = QWidget(self)
        self.crtImageId = 0
        self.crtMarkerCnt = 0
        self.recordDict = {}
        self.imageList = []
        self.setImageList(imageList)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Marker')
        self.imageLabel = QLabel(self)
        self.updateImage(self.crtImageId)
        print len(self.imageList), self.imageList

    def setImageList(self, imageList):
        self.imageList = imageList
        self.recordDict.clear()
        for image in imageList:
            self.recordDict[image] = [None, None, None]

    def mouseReleaseEvent(self, event):
        print event.pos()
        self.recordDict[self.imageList[self.crtImageId]][self.crtMarkerCnt] = event.pos()
        self.crtMarkerCnt = self.crtMarkerCnt + 1 if self.crtMarkerCnt < 2 else 0
        if self.crtMarkerCnt == 0:
            if self.crtImageId != len(self.imageList)-1:
                self.crtImageId += 1
                self.updateImage(self.crtImageId)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_N:
            self.nextImage()
        elif event.key() == Qt.Key_P:
            self.previousImage()
        elif event.key() == Qt.Key_S:
            self.saveRecord()
        elif event.key() == Qt.Key_R:
            print "reset marker count"
            self.crtMarkerCnt = 0

    def saveRecord(self):
        recordPath = os.getcwd()+"\\triplets.txt"
        recordFile = open(recordPath, 'w')
        for imageFilePath, markers in self.recordDict.iteritems():
            try:
                recordFile.write("{0} {1} {2} {3} {4} {5} {6}\n".format(
                    imageFilePath,
                    markers[0].x(),
                    markers[0].y(),
                    markers[1].x(),
                    markers[1].y(),
                    markers[2].x(),
                    markers[2].y()))
            except:
                recordFile.write("{0} not marked successfully.\n".format(imageFilePath))
                continue
        recordFile.close()
        QMessageBox.information(self, "Save Record", "record saved to {0}".format(recordPath))
        print "record saved to {0}".format(recordPath)

    def updateImage(self, imageId):
        crtImage = QPixmap(self.imageList[imageId])
        self.imageLabel.setPixmap(crtImage)
        self.imageLabel.resize(crtImage.size())
        self.resize(crtImage.size())
        self.crtMarkerCnt = 0

    def nextImage(self):
        print "image {0}/{1}".format(self.crtImageId+1, len(self.imageList))
        if self.crtImageId != len(self.imageList)-1:
            self.crtImageId += 1
            self.updateImage(self.crtImageId)

    def previousImage(self):
        print "image {0}/{1}".format(self.crtImageId+1, len(self.imageList))
        if self.crtImageId != 0:
            self.crtImageId -= 1
            self.updateImage(self.crtImageId)


class Marker(QMainWindow):
    def __init__(self, parent=None):
        super(Marker, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Marker')
        loadImageBtn = QPushButton('Load Images', self)
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        hbox = QGridLayout(centralWidget)
        hbox.addWidget(loadImageBtn)
        loadImageBtn.clicked.connect(self.loadImageSeq)

    def loadImageSeq(self):
        dirPath = QFileDialog.getExistingDirectory(self,
                                        "Open Image Directory",
                                        "/home",
                                        QFileDialog.ShowDirsOnly|
                                        QFileDialog.DontResolveSymlinks)
        filePaths = []
        for root, dirs, files in os.walk(str(dirPath)):
            for name in files:
                if os.path.splitext(name)[1] in [".jpg", ".png", ".tif"]:
                    filePaths.append(os.path.join(root, name))
        if len(filePaths)>0:
            self.imageWidget = ImageMarker(filePaths, self)
            self.imageWidget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    marker = Marker()
    marker.show()
    sys.exit(app.exec_())