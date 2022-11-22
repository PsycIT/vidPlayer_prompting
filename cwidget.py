import os
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPalette
from PyQt5.uic import loadUi
from media import CMultiMedia

from prompt_qt import Prompt
import datetime
import time
from utils import formatting_filename
import numpy as np


event_dict = {
    "video1" : [3000, 5000],
    "video2" : [1000, 5000],
    "video3" : [1000, 2000],
}

class CWidget(QWidget):
    def __init__(self, pname):
        super().__init__()
        loadUi('main.ui', self)

        # Multimedia Object
        self.mp = CMultiMedia(self, self.view)

        # video background color
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.black)
        self.view.setAutoFillBackground(True);
        self.view.setPalette(pal)

        # volume, slider
        self.vol.setRange(0, 100)
        self.vol.setValue(50)

        # play time
        self.duration = ''

        # signal
        self.btn_add.clicked.connect(self.clickAdd)
        self.btn_del.clicked.connect(self.clickDel)
        self.btn_play.clicked.connect(self.clickPlay)
        self.btn_stop.clicked.connect(self.clickStop)
        self.btn_pause.clicked.connect(self.clickPause)
        self.btn_forward.clicked.connect(self.clickForward)
        self.btn_prev.clicked.connect(self.clickPrev)

        self.list.itemDoubleClicked.connect(self.dbClickList)
        self.vol.valueChanged.connect(self.volumeChanged)
        self.bar.sliderMoved.connect(self.barChanged)


        self.p_folder = "./participant/" + pname +'/'
        if not os.path.exists(self.p_folder):
            os.makedirs(self.p_folder)

        
        

    def clickAdd(self):
        files, ext = QFileDialog.getOpenFileNames(self
                                                  , 'Select one or more files to open'
                                                  , ''
                                                  , 'Video (*.mp4 *.mpg *.mpeg *.avi *.wma)')
        print(files, ext)
        if files:
            cnt = len(files)
            row = self.list.count()
            for i in range(row, row + cnt):
                self.list.addItem(files[i - row])
            self.list.setCurrentRow(0)

            self.mp.addMedia(files)

        # 우선은 파일 하나만 add했을 때만 돌아감.
        video_name = files[0].split('/')[-1].split('.')[0]     # video name만 추출
        self.makePromptWindow(video_name)
    
    def clickDel(self):
        row = self.list.currentRow()
        self.list.takeItem(row)
        self.mp.delMedia(row)

    def clickPlay(self):
        # 비디오가 변경된 경우 prompt 다시 생성
        video_name = self.list.currentItem().text().split('/')[-1].split('.')[0]     # video name만 추출
        if video_name != self.prompt_win.current_video:
            self.makePromptWindow(video_name)

        index = self.list.currentRow()
        self.mp.playMedia(index)
        self.monitor_on = True

    def clickStop(self):
        self.mp.stopMedia()
        self.monitor_on = False


    def clickPause(self):
        self.mp.pauseMedia()
        self.monitor_on = False

    def clickForward(self):
        print('in clickForward')

        cnt = self.list.count()
        curr = self.list.currentRow()
        print(cnt, curr)
        if curr < cnt - 1:
            self.list.setCurrentRow(curr + 1)
            self.mp.forwardMedia()
        else:
            self.list.setCurrentRow(0)
            self.mp.forwardMedia(end=True)

    def clickPrev(self):
        cnt = self.list.count()
        curr = self.list.currentRow()
        if curr == 0:
            self.list.setCurrentRow(cnt - 1)
            self.mp.prevMedia(begin=True)
        else:
            self.list.setCurrentRow(curr - 1)
            self.mp.prevMedia()

    def dbClickList(self, item):
        # 비디오가 변경된 경우 prompt 다시 생성
        video_name = self.list.currentItem().text().split('/')[-1].split('.')[0]     # video name만 추출
        if video_name != self.prompt_win.current_video:
            self.makePromptWindow(video_name)


        row = self.list.row(item)
        self.mp.playMedia(row)
        self.monitor_on = True

    def volumeChanged(self, vol):
        self.mp.volumeMedia(vol)

    def barChanged(self, pos):
        print(pos)
        self.mp.posMoveMedia(pos)

    def updateState(self, msg):
        self.state.setText(msg)

    def updateBar(self, duration):
        self.bar.setRange(0, duration)
        self.bar.setSingleStep(int(duration / 10))
        self.bar.setPageStep(int(duration / 10))
        self.bar.setTickInterval(int(duration / 10))
        td = datetime.timedelta(milliseconds=duration)
        stime = str(td)
        idx = stime.rfind('.')
        self.duration = stime[:idx]

    def updatePos(self, pos):
        self.bar.setValue(pos)
        td = datetime.timedelta(milliseconds=pos)
        stime = str(td)
        idx = stime.rfind('.')
        stime = f'{stime[:idx]} / {self.duration}'
        self.playtime.setText(stime)

    def makePromptWindow(self, video_name):
        # 프롬프트 서베이 결과를 저장할 파일 경로 지정 및 인스턴스 생성
        self.save_path = os.path.join(self.p_folder, video_name) + ' score.txt'
        self.prompt_win = Prompt(self, self.save_path, video_name)
        self.event_list = event_dict[video_name]
        print("make prompt")
        
        self.monitor_on = True
        self.play_monitor = threading.Thread(target=self.playMonitor)
        self.play_monitor.setDaemon(True)
        self.play_monitor.start()
        print("start monitoring")
        #---


    def playMonitor(self):
        event_count = 0

        while self.monitor_on:
            if self.mp.player.position() in self.event_list:
                print("[SHOW PROMPT] count - %d" % event_count)

                # remove event time at the list
                target = self.event_list.index(self.mp.player.position())
                self.event_list[target] = 0

                # show prompt
                self.clickPause()
                r = self.prompt_win.showModal(self.mp.player.position())

                # move to next event
                event_count += 1
            
            if np.array(self.event_list).sum() ==0 :
                # 모든 prompt event가 끝나면 break
                print("There is no event. thread break")
                break