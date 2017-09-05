import json
from threading import Thread
import os
import logging
import sys
import shutil

from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QLabel, QMainWindow, QSizePolicy, QGraphicsDropShadowEffect, QProgressBar
from PyQt5.QtCore import QCoreApplication, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QFontDatabase

from spring_downloader import Downloader
from spring_launcher import Launcher
from chobby_config import ChobbyConfig

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.config = ChobbyConfig()
        self.initUI()

    def initUI(self):
        fontPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font/Audiowide-Regular.ttf')
        font_id = QFontDatabase.addApplicationFont(fontPath)
        families = QFontDatabase.applicationFontFamilies(font_id)
        font = QFont("Audiowide")
        self.setFont(font)

        self.btnAction = QPushButton('Download Engine', self)
        self.btnAction.clicked.connect(self.OnBtnClick)
        self.btnAction.resize(self.btnAction.sizeHint())
        self.btnAction.move(20, 145)
        self.btnAction.setFont(font)

        self.lblStatus = QLabel('Status label', self)
        self.lblStatus.resize(self.btnAction.sizeHint())
        self.lblStatus.setText("")
        self.lblStatus.setContentsMargins(0,0,0,0);
        self.lblStatus.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.lblStatus.move(190, 150)
        self.lblStatus.setFont(font)
        #self.lblStatus.setStyleSheet("border: 1px solid black;");
        dse = QGraphicsDropShadowEffect(self)
        dse.setBlurRadius(10)
        dse.setColor(QColor("#FFEEEE"))
        dse.setOffset(4,4)
        self.lblStatus.setGraphicsEffect(dse)

        self.pbDownload = QProgressBar(self)
        self.pbDownload.setGeometry(30, 40, 400, 25)
        self.step = 0

        self.setGeometry(300, 300, 550, 250)
        self.setStyleSheet("QMainWindow {border-image: url(data/background.jpg) 0 0 0 0 stretch stretch;}")
        self.setObjectName("Window")
        self.setWindowTitle(self.config.game_title)
        self.show()

        self.dl = Downloader()
        self.dl.downloadStarted.connect(self.OnDownloadStarted)
        self.dl.downloadFinished.connect(self.OnDownloadFinished)
        self.dl.downloadFailed.connect(self.OnDownloadFailed)
        self.dl.downloadProgress.connect(self.OnDownloadProgress)
        self.launcher = Launcher()
        self.launcher.lobbyClosed.connect(self.OnLobbyClosed)

        self.actions = ["autoupdate", "game", "engine", "lobby", "extra", "start"]
        self.DisplayNextAction()
        if self.config.auto_download:
            self.btnAction.setEnabled(False)
            self.MaybeNextStep()

    def DisplayNextAction(self):
        if len(self.actions) == 0:
            return

        nextAction = self.actions[0]
        if nextAction in ["game", "engine", "lobby", "extra"]:
            self.btnAction.setText("Download")
            self.btnAction.resize(self.btnAction.sizeHint())
        elif nextAction == "autoupdate":
            self.btnAction.setText("Self-update")
        elif nextAction == "start":
            self.btnAction.setText("Launch")

    def MaybeNextStep(self):
        self.currentAction = None
        if len(self.actions) == 0:
            self.btnAction.setEnabled(True)
            return

        self.DisplayNextAction()
        self.currentAction = self.actions[0]
        self.actions = self.actions[1:]
        logging.info("Action: {}".format(self.currentAction))
        self.btnAction.setEnabled(False)

        if self.currentAction == "autoupdate":
            logging.warning("Implement autoupdate")
            self.MaybeNextStep()
        elif self.currentAction == "game":
            thread = Thread(target = self.dl.DownloadGame, args = (self.config.game_rapid,))
            thread.start()
        elif self.currentAction == "engine":
            thread = Thread(target = self.dl.DownloadEngine, args = (self.launcher.GetGameEngineVersion(),))
            thread.start()
        elif self.currentAction == "lobby":
            thread = Thread(target = self.dl.DownloadGame, args = (self.config.lobby_rapid,))
            thread.start()
        elif self.currentAction == "extra":
            logging.warning("Implement downloading other stuff (maps/games)")
            if self.actions[0] == "start" and not self.config.auto_start:
                self.currentAction = None
                self.btnAction.setEnabled(True)
                self.DisplayNextAction()
            else:
                self.MaybeNextStep()
        elif self.currentAction == "start":
            if not os.path.exists(os.path.join(self.dl.FOLDER, "chobby_config.json")):
                shutil.copy("config.json", os.path.join(self.dl.FOLDER, "chobby_config.json"))
            thread = Thread(target = self.launcher.StartChobby, args = (self.launcher.GetGameEngineVersion(),))
            thread.start()
            self.hide()
            # NOTE: This **might** be needed for Windows; test!
            # if platform.name.is_windows():
            #     self.hidden = True
            #     self.setWindowFlags(Qt.ToolTip)
            self.MaybeNextStep()

    @pyqtSlot(str, str)
    def OnDownloadStarted(self, name, type):
        self.lblStatus.setText("Downloading: " + name)
        self.lblStatus.adjustSize()

    @pyqtSlot()
    def OnDownloadFinished(self):
        self.lblStatus.setText("Download finished.")
        self.lblStatus.adjustSize()
        self.MaybeNextStep()

    @pyqtSlot()
    def OnDownloadFailed(self):
        self.lblStatus.setText("Failed to download: " + name)
        self.lblStatus.adjustSize()

    @pyqtSlot(int, int)
    def OnDownloadProgress(self, current, total):
        self.pbDownload.setValue(current / total * 100)

    @pyqtSlot()
    def OnLobbyClosed(self):
        sys.exit(0)

    def OnBtnClick(self):
        self.MaybeNextStep()