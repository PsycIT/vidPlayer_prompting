from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton, QDesktopWidget, QRadioButton, \
    QLabel, QButtonGroup


class Prompt(QDialog):
    def __init__(self, master, save_path, videoname):
        super().__init__()
        self.master = master
        self.save_path = save_path
        self.current_video = videoname

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Post Annotation Prompt')
        monitor = QDesktopWidget().screenGeometry(1)
        self.move(monitor.left(), monitor.top())
        self.setGeometry(100, 100, 700, 150)

        # label + radio button layout
        layout = QVBoxLayout()
        label = QLabel('해당 지점에서 몰입도 점수는?')
        radio_layout = QHBoxLayout()
        self.rbtn_list = [QRadioButton('1', self), QRadioButton('2', self), QRadioButton('3', self),
                     QRadioButton('4', self), QRadioButton('5', self), QRadioButton('6', self),
                     QRadioButton('7', self)]
        self.mood_button_group = QButtonGroup()
        for i, rbtn in enumerate(self.rbtn_list, 1):
            radio_layout.addWidget(rbtn)
            self.mood_button_group.addButton(rbtn, i)

        # OK button layout
        button_layout = QHBoxLayout()
        btnOK = QPushButton("확인")
        btnOK.clicked.connect(self.onOKButtonClicked)

        # arrange layouts
        button_layout.addStretch(1)
        button_layout.addWidget(btnOK)
        button_layout.addStretch(1)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addLayout(radio_layout)
        layout.addStretch(1)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def radio_button_clicked(self):
        return self.mood_button_group.checkedId()

    def onOKButtonClicked(self):

        radio_value = self.radio_button_clicked()
        if radio_value < 0:
            print("점수 매기지 않고 확인 누름.")
        else:
            self.writeLog(radio_value)
            # self.master.mp.player.play()
            self.master.clickPlay()

            self.accept()
            self.resetRadioButtons(radio_value)

    def resetRadioButtons(self, radio_value):
        self.mood_button_group.setExclusive(False)

        self.rbtn_list[radio_value-1].setChecked(False)
        self.mood_button_group.setExclusive(True)

    def onCancelButtonClicked(self):
        # Not use here
        self.reject()

    def showModal(self, playtime):
        self.playtime = playtime
        return super().exec_()

    def writeLog(self, value):
        with open(self.save_path, 'a') as f:
            log = str(self.playtime) + ',' + str(value) + '\n'
            f.write(log)  # [playtime_position] [user_answer]
            print("[WRITE] ", log)