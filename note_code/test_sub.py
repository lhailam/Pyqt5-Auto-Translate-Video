import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt

class SubtitlePlayer(QMainWindow):
    def __init__(self, subtitles):
        super().__init__()
        self.setWindowTitle("Subtitle Player")
        self.setGeometry(100, 100, 800, 200)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.subtitle_label = QLabel(self)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("font-size: 20px;")
        self.central_layout = QVBoxLayout()
        self.central_layout.addWidget(self.subtitle_label)
        self.central_widget.setLayout(self.central_layout)

        self.subtitles = subtitles
        self.current_subtitle_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_subtitle)
        
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_subtitle)
        
        self.stop_button = QPushButton("Stop", self)
        self.stop_button.clicked.connect(self.stop_subtitle)
        
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.stop_button)
        self.central_layout.addLayout(self.button_layout)
        
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
                self.subtitle_label.setText(text)
                break
            elif self.current_time > end_time_seconds:
                self.current_subtitle_index += 1
            else:
                self.subtitle_label.clear()
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



    def start_subtitle(self):
        self.paused = False
        self.timer.start(1000)  

    def stop_subtitle(self):
        self.paused = True
        self.timer.stop()
        self.current_time = 0 

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
    app = QApplication(sys.argv)

    file_path = "mau.srt"
    subtitles = read_srt_file(file_path)
    player = SubtitlePlayer(subtitles)
    player.show()

    sys.exit(app.exec_())
