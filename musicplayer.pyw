from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolTip, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPixmap, QCursor, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtCore import QUrl, Qt, QTimer
from player_ui import Player
import sys,eyed3,os,json,ctypes

# for the eyed3 errors i didnt know what errors eyed3 could give so i used all exceptions.

class PlayerWindow(QMainWindow, Player):
    def __init__(self, start_minimized=False):
        super().__init__()
        self.u = Player()
        self.u.setupUi(self)
        self.setWindowIcon(QIcon("icon.ico"))
        self.dark()
        if sys.platform == "win32":
            myappid = "com.emir.musicplayer"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        self.u.label_4.hide()
        self.currentmediaload = None
        self.SETTINGSFILE = "player_settings.json"
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        
        self.setupui()
        self.loadsettings()
        
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QIcon("icon.ico"))
        self.tray.setToolTip("Music Player")

        tray_menu = QMenu(self)

        show_action = QAction("Show Player", self)
        quit_action = QAction("Quit", self)

        show_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(QApplication.quit)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        
        self.tray.setVisible(True)
        self.tray.show()

        if start_minimized:
            QTimer.singleShot(5, self.showMinimized)
    
    def setupui(self):
        self.player.setVolume(100)
        self.u.checkBox_2.setTristate(True)
        self.u.actionOpen_File.triggered.connect(self.openfile)
        self.u.actionOpen_Folder.triggered.connect(self.openfolder)
        self.u.pushButton.clicked.connect(self.playbutton)
        self.u.actionDark.triggered.connect(self.dark)
        self.u.actionLight.triggered.connect(self.light)
        self.u.actionShow_Photo.changed.connect(self.showphoto)
        self.u.pushButton_5.pressed.connect(self.playlist.next)
        self.u.pushButton_4.pressed.connect(self.playlist.previous)
        self.player.currentMediaChanged.connect(self.updatemedia)
        self.u.checkBox_2.stateChanged.connect(self.repeatcheck)
        self.u.checkBox.stateChanged.connect(self.shuffle)
        self.u.action0_5x.triggered.connect(self.r0_5x)
        self.u.action1x.triggered.connect(self.r1x)
        self.u.action1_5x.triggered.connect(self.r1_5x)
        self.u.action2x.triggered.connect(self.r2x)
        self.player.durationChanged.connect(self.setduration)
        self.player.positionChanged.connect(self.updatetime)
        self.u.horizontalSlider.sliderMoved.connect(self.settime)
        self.u.verticalSlider.valueChanged.connect(self.volume)
        self.player.error.connect(self.handleplayererror)

    def openfile(self):
        if hasattr(self, "folder"):
            del self.folder  
        path, _ = QFileDialog.getOpenFileName(self, "Select a Music File", "", "Media Files(*.mp3)")
        self.filepath = path
        self.playlist.clear()
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.playmedia()
    
    def loadfile(self, path=None):
        if hasattr(self, "folder"):
            del self.folder  
        if path is None:
            path, _ = QFileDialog.getOpenFileName(self, "Select a Music File", "", "Media Files(*.mp3)")
        if not path:
            return
        self.filepath = path
        self.playlist.clear()
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.playmedia()

    def playmedia(self):
        self.u.verticalSlider.setValue(self.player.volume())
        self.vol = self.u.verticalSlider.value()
        self.player.setVolume(0)
        if self.u.checkBox.isChecked():
            self.playlist.shuffle()
            self.playlist.setCurrentIndex(0)
        self.player.stop()
        self.player.play()
        self.player.setVolume(self.vol)
        self.setWindowTitle(os.path.basename(self.player.currentMedia().canonicalUrl().toLocalFile()).split(os.extsep, 1)[0])
        self.u.pushButton.setText("| |")

    def openfolder(self):
        self.folder = QFileDialog.getExistingDirectory(self, "Select Music Folder")
        if self.folder:
            self.playlist.clear()
            for filename in os.listdir(self.folder):
                if filename.endswith(".mp3"):
                    path = os.path.join(self.folder, filename)
                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.playlist.setCurrentIndex(0)
        self.playmedia()
    
    def playbutton(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.u.pushButton.setText("|>")
        elif self.player.state() == QMediaPlayer.PausedState:
            self.player.play()
            self.u.pushButton.setText("| |")
        else:
            if self.playlist.mediaCount() > 0:
                self.player.play()
                self.u.pushButton.setText("| |")
    def volume(self):
        value = self.u.verticalSlider.value()
        self.player.setVolume(value)

        pos = self.u.verticalSlider.mapFromGlobal(QCursor.pos())
        QToolTip.showText(self.u.verticalSlider.mapToGlobal(pos), f"{value}%", self.u.verticalSlider)

    def mstotime(self, ms):
        self.seconds = ms // 1000
        self.minutes = self.seconds // 60
        self.seconds = self.seconds % 60
        return f"{self.minutes:02d}:{self.seconds:02d}"
    
    def updatetime(self, position):
        self.u.horizontalSlider.setValue(position)
        self.u.label_2.setText(self.mstotime(position))
    
    def setduration(self, duration):
        self.u.horizontalSlider.setMaximum(duration)
        self.u.label_3.setText(self.mstotime(duration))
    
    def settime(self):
        self.player.setPosition(self.u.horizontalSlider.sliderPosition())

    def showphoto(self):
        self.u.label_4.hide()
        if self.u.actionShow_Photo.isChecked():
            self.currentmedia = self.player.currentMedia().canonicalUrl().toLocalFile()
            if not self.currentmedia or not os.path.isfile(self.currentmedia):
                return
            try:    
                self.currentmediaload = eyed3.load(self.currentmedia)
                if self.currentmediaload and self.currentmediaload.tag and self.currentmediaload.tag.images:
                    img_data = self.currentmediaload.tag.images[0].image_data
                    pixmap = QPixmap()
                    if pixmap.loadFromData(img_data):
                        scaled_pixmap = pixmap.scaled(self.u.label_4.size(),aspectRatioMode=1,transformMode=1)
                        self.u.label_4.setPixmap(scaled_pixmap)
                        self.u.label_4.show()
            except Exception as e: #Line 8
                print(f"Loading album art error: {e}")
            else:
                self.u.label_4.hide()
        else:
            self.u.label_4.hide()
    
    def updatemedia(self):
        self.u.label_4.hide()
        self.currentmedia = self.player.currentMedia().canonicalUrl().toLocalFile()
        self.setWindowTitle(os.path.basename(self.player.currentMedia().canonicalUrl().toLocalFile()).split(os.extsep, 1)[0])
        if self.u.actionShow_Photo.isChecked():
            if not self.currentmedia or not os.path.isfile(self.currentmedia):
                return
            try:    
                self.currentmediaload = eyed3.load(self.currentmedia)
                if self.currentmediaload and self.currentmediaload.tag and self.currentmediaload.tag.images:
                    img_data = self.currentmediaload.tag.images[0].image_data
                    pixmap = QPixmap()
                    if pixmap.loadFromData(img_data):
                        scaled_pixmap = pixmap.scaled(self.u.label_4.size(),aspectRatioMode=1,transformMode=1)
                        self.u.label_4.setPixmap(scaled_pixmap)
                        self.u.label_4.show()
            except Exception as e: #Line 8
                print(f"Loading album art error: {e}")
            else:
                self.u.label_4.hide()
    
    def repeatcheck(self):
        if self.u.checkBox_2.checkState() == Qt.Unchecked:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
            if self.u.actionLight.isChecked():
                self.u.checkBox_2.setStyleSheet("QCheckBox::indicator { background-color: #ffffff; border: 1px solid #888888; }")
            else:
                self.u.checkBox_2.setStyleSheet("QCheckBox::indicator { border: 1px solid #888; }")
        elif self.u.checkBox_2.checkState() == Qt.PartiallyChecked:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
            if self.u.actionLight.isChecked():
                self.u.checkBox_2.setStyleSheet("QCheckBox::indicator { background-color: #bbbbbb; border: 1px solid #888888; }")
            else:
                self.u.checkBox_2.setStyleSheet("QCheckBox::indicator { background-color: #525050; border: 1px solid #525050; }")
        elif self.u.checkBox_2.checkState() == Qt.Checked:
            self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            if self.u.actionLight.isChecked():

                self.u.checkBox_2.setStyleSheet("QCheckBox::indicator { background-color: #888888; border: 1px solid #888888; }")
            else:
                self.u.checkBox_2.setStyleSheet("QCheckBox::indicator { background-color: #2b2b2b; border: 1px solid #2b2b2b; }")

    def shuffle(self):
        if self.u.checkBox.isChecked():
            self.playlist.shuffle()

    def r0_5x(self):
        self.player.setPlaybackRate(0.5)
        for option in [self.u.action1x, self.u.action1_5x, self.u.action2x]:
            if option.isChecked():
                option.setChecked(False)
    
    def r1x(self):
        self.player.setPlaybackRate(1.0)
        for option in [self.u.action0_5x, self.u.action1_5x, self.u.action2x]:
            if option.isChecked():
                option.setChecked(False)

    def r1_5x(self):
        self.player.setPlaybackRate(1.5)
        for option in [self.u.action1x, self.u.action0_5x, self.u.action2x]:
            if option.isChecked():
                option.setChecked(False)

    def r2x(self):
        self.player.setPlaybackRate(2.0)
        for option in [self.u.action1x, self.u.action1_5x, self.u.action0_5x]:
            if option.isChecked():
                option.setChecked(False)
    
    def savesettings(self):
        if self.playlist.mediaCount() > 1:
            last_path = os.path.dirname(self.playlist.media(0).canonicalUrl().toLocalFile())
        elif self.playlist.mediaCount() == 1:
            last_path = self.playlist.media(0).canonicalUrl().toLocalFile()
        else:
            last_path = ""

        settings = {
            "last_playlist_path": last_path,
            "last_track": self.player.currentMedia().canonicalUrl().toLocalFile() if self.player.currentMedia() else "",
            "volume": self.player.volume(),
            "repeat_mode": self.u.checkBox_2.checkState(),
            "shuffle": self.u.checkBox.isChecked(),
            "theme": "dark" if self.u.actionDark.isChecked() else "light",
            "show_photo": self.u.actionShow_Photo.isChecked(),
            "playback_rate": self.player.playbackRate(),
        }
        try:    
            with open(self.SETTINGSFILE, "w") as f:
                json.dump(settings, f, indent=4)
        except(PermissionError, OSError) as e:
            print(f"Failed to save settings: {e}")

    def loadsettings(self):
        if not os.path.exists(self.SETTINGSFILE):
            return
        try:    
            with open(self.SETTINGSFILE, "r") as f:
                settings = json.load(f)
        except(FileNotFoundError, json.JSONDecodeError, PermissionError, OSError) as e:
            print(f"Failed to load settings: {e}")
            return

        self.player.setVolume(settings.get("volume", 100))
        self.u.verticalSlider.setValue(self.player.volume())


        if settings.get("theme") == "dark":
            self.u.actionDark.setChecked(True)
            self.dark()
        else:
            self.u.actionLight.setChecked(True)
            self.light()


        self.u.checkBox_2.setCheckState(settings.get("repeat_mode", Qt.Unchecked))
        self.u.checkBox.setChecked(settings.get("shuffle", False))
        self.repeatcheck()
        self.shuffle()


        last_path = settings.get("last_playlist_path", "")
        if last_path:
            if os.path.isdir(last_path):
                self.loadfolder(last_path)
            elif os.path.isfile(last_path):
                self.loadfile(last_path)

        last_track = settings.get("last_track", "")
        if last_track:
            for i in range(self.playlist.mediaCount()):
                if self.playlist.media(i).canonicalUrl().toLocalFile() == last_track:
                    self.playlist.setCurrentIndex(i)
                    break
            self.player.setPosition(0)
            self.u.pushButton.setText("|>")

        rate = settings.get("playback_rate", 1.0)
        self.player.setPlaybackRate(rate)

    def loadfolder(self, folder_path):
        self.playlist.clear()
        for filename in os.listdir(folder_path):
            if filename.endswith(".mp3"):
                path = os.path.join(folder_path, filename)
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
        if self.playlist.mediaCount() > 0:
            self.playlist.setCurrentIndex(0)

    def handleplayererror(self, error):
        errors = {
            QMediaPlayer.NoError: "No error",
            QMediaPlayer.ResourceError: "File missing or corrupt",
            QMediaPlayer.FormatError: "File format not supported",
            QMediaPlayer.AccessDeniedError: "Access denied",
            QMediaPlayer.ServiceMissingError: "Audio system missing",
        }
        msg = errors.get(error)
        print(f"Player error: {msg}")
        self.u.pushButton.setText("|>")

    def closeEvent(self, event):
        self.savesettings()
        super().closeEvent(event)
    
    def dark(self):
        if self.u.actionDark.isChecked():    
            QApplication.instance().setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
                color: #eeeeee;
            }

            QMenuBar {
                background-color: #181818;
                color: #ffffff;
                border-bottom: 1px solid #2a2a2a;
            }
            QMenuBar::item:selected { background-color: #252525; }
            QMenu { background-color: #1c1c1c; color: #ffffff; border: 1px solid #2a2a2a; }
            QStatusBar { background-color: #181818; color: #aaaaaa; border-top: 1px solid #2a2a2a; }

            QPushButton {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #2b2b2b; }

            QLabel { color: #cccccc; }

            QSlider::groove:horizontal { background: #333; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #888; width: 12px; border-radius: 6px; }
            QSlider::groove:vertical { background: #333; width: 6px; border-radius: 3px; }
            QSlider::handle:vertical { background: #888; height: 12px; border-radius: 6px; }

            QCheckBox { color: #cccccc; }
            QCheckBox {
                color: #cccccc;
            }

            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border: 1px solid #888888;
            }
                                                  
            QCheckBox::indicator:checked {
                border: 1px solid #888888;
                background-color: #888888;
            }
            """)
            self.u.label.setStyleSheet("background-color: black;")
            if self.u.actionLight.isChecked():
                self.u.actionLight.setChecked(False)
                self.repeatcheck()

    def light(self):
        if self.u.actionLight.isChecked():
            QApplication.instance().setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f3f3f3;
                color: #2a2a2a;
            }

            QMenuBar {
                background-color: #e6e6e6;
                color: #202020;
                border-bottom: 1px solid #cccccc;
            }
            QMenuBar::item:selected { background-color: #d9d9d9; }
            QMenu { background-color: #f9f9f9; color: #202020; border: 1px solid #c0c0c0; }
            QStatusBar { background-color: #e6e6e6; color: #505050; border-top: 1px solid #cccccc; }

            QPushButton {
                background-color: #ffffff;
                color: #1a1a1a;
                border: 1px solid #cccccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #eaeaea; }
            QPushButton:pressed { background-color: #dcdcdc; }

            QLabel { color: #1e1e1e; }

            QSlider::groove:horizontal { background: #cccccc; height: 6px; border-radius: 3px; }
            QSlider::handle:horizontal { background: #888888; width: 12px; border-radius: 6px; }
            QSlider::groove:vertical { background: #cccccc; width: 6px; border-radius: 3px; }
            QSlider::handle:vertical { background: #888888; height: 12px; border-radius: 6px; }

            QCheckBox { color: #1e1e1e; }

            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border: 1px solid #888888;
                background-color: #ffffff;
                border-radius: 3px;
            }       

            QCheckBox::indicator:checked {
                background-color: #888888;
                border: 1px solid #888888;
            }
            """)
            self.u.label.setStyleSheet("background-color: #7e7e7e;")
            if self.u.actionDark.isChecked():
                self.u.actionDark.setChecked(False)
                self.repeatcheck()

app = QApplication(sys.argv)
app.setWindowIcon(QIcon("icon.ico"))
start_minimized = "--minimized" in sys.argv
window = PlayerWindow(start_minimized=start_minimized)
window.show() if not start_minimized else None
sys.exit(app.exec_())
