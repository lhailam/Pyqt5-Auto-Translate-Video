import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, QUrl, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from gui import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, subtitles):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)

        self.uic.btn_input.clicked.connect(self.open_video_file)
        self.uic.btn_start_stop.clicked.connect(self.toggle_video_play)

        #Sub
        self.subtitles = subtitles
        self.current_subtitle_index = 0
        self.subtitle_timer  = QTimer(self)
        self.subtitle_timer.timeout.connect(self.update_subtitle)

        #Video
        self.video_capture = None
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.update_video_frame)
        self.is_playing = False

        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        self.layout = QVBoxLayout(self.uic.video)
        self.layout.addWidget(self.video_widget)

        self.uic.btn_start_stop.setEnabled(False)
        self.uic.lbl_thongbao.setText('')

        self.uic.txtSub.setText('')
        self.paused = True
        self.current_time = 0

    def update_subtitle(self):
        if self.paused:
            return

        # Update current time
        self.current_time += 1
        while self.current_subtitle_index < len(self.subtitles):
            index, time, text = self.subtitles[self.current_subtitle_index]
            start_time_seconds, end_time_seconds = self.time_to_seconds(time)

            if start_time_seconds <= self.current_time <= end_time_seconds:
                self.uic.txtSub.setText(text)
                break
            elif self.current_time > end_time_seconds:
                self.current_subtitle_index += 1
            else:
                self.uic.txtSub.clear()
                break

    def time_to_seconds(self, time_str):
        parts = time_str.split(' --> ')
        if len(parts) == 2:
            start_time_str, end_time_str = parts
            start_time_parts_delete_mili = start_time_str.split(',')[0]
            end_time_parts_delete_mili = end_time_str.split(',')[0]
            start_time_parts =start_time_parts_delete_mili.split(':')
            end_time_parts =end_time_parts_delete_mili.split(':')
            h, m = map(int, start_time_parts[:2])
            

            if '.' in start_time_parts[2]:
                start_seconds, start_milliseconds = map(int, start_time_parts[2].split('.'))
            else:
                start_seconds, start_milliseconds = int(start_time_parts[2]), 0
            
            if '.' in end_time_parts[2]:
                end_seconds, end_milliseconds = map(int, end_time_parts[2].split('.'))
            else:
                end_seconds, end_milliseconds = int(end_time_parts[2]), 0

            start_total_seconds = h * 3600 + m * 60 + start_seconds + start_milliseconds / 1000.0
            end_total_seconds = h * 3600 + m * 60 + end_seconds + end_milliseconds / 1000.0
            
            return start_total_seconds, end_total_seconds
        else:
            return 0, 0  

    def toggle_video_play(self):
        if not self.is_playing:
            if self.video_capture is not None and not self.video_capture.isOpened():
                self.video_capture.release()
            self.video_timer.start(30)
            self.is_playing = True
            self.uic.btn_start_stop.setText("Stop")
            self.play_video()
        else:
            self.video_timer.stop()
            if self.video_capture is not None and self.video_capture.isOpened():
                self.video_capture.release()
            self.is_playing = False
            self.uic.btn_start_stop.setText("Start")
            self.stop_video()

    def open_video_file(self):
        self.uic.lbl_thongbao.setText('')
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv);;All Files (*)", options=options)
        if file_name:
            self.is_playing = True
            self.uic.lbl_thongbao.setText('Import success!!!')
            self.toggle_video_play()
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_name)))
            self.uic.btn_start_stop.setEnabled(True)


    def play_video(self):
        self.media_player.play()
        self.paused = False
        self.subtitle_timer.start(1000)  # Update every 1 second

    def stop_video(self):
        self.media_player.pause()
        self.paused = True
        self.subtitle_timer .stop()
        self.current_time = 0  # Reset current time when stopped

    def update_video_frame(self):
        pass

# Đọc file srt
def read_srt_file(file_path):
    subtitles = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.read().split('\n\n') 
        for block in lines:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                subtitle_num = lines[0]
                time_info = lines[1]
                text = ' '.join(lines[2:])
                subtitles.append((subtitle_num, time_info, text))
    return subtitles


if __name__ == "__main__":

    file_path = "data/subtitle.srt"
    subtitles = read_srt_file(file_path)

    app = QApplication(sys.argv)
    main_win = MainWindow(subtitles)
    main_win.show()
    sys.exit(app.exec_())
