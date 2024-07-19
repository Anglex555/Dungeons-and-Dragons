import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import QTimer, Qt, pyqtProperty

class DiceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 300, 600)
        self.setWindowTitle('20-гранный кубик')

        layout = QVBoxLayout()

        self.dice_label = RotatableLabel(self)
        self.dice_label.setAlignment(Qt.AlignCenter)
        self.dice_label.setFixedSize(250, 250)
        layout.addWidget(self.dice_label)

        roll_button = QPushButton('Бросить кубик', self)
        roll_button.clicked.connect(self.start_animation)
        layout.addWidget(roll_button)

        self.setLayout(layout)

        self.dice_images = []
        for i in range(1, 21):
            image_path = f'c:/Ультилиты/2/Mai/DnD/Dice/d{i}.png'
            image = QPixmap(image_path)
            scaled_image = image.scaled(self.dice_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.dice_images.append(scaled_image)

        self.dice_label.setPixmap(self.dice_images[19])
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_duration = 500  # Продолжительность анимации в миллисекундах
        self.animation_steps = 35  # Количество шагов анимации
        self.current_step = 0
        self.current_image = None
        self.current_interval = 0  # Начальный интервал таймера

    def start_animation(self):
        self.current_step = 0
        self.current_interval = 0  # Начальный интервал таймера
        self.animation_timer.start(self.current_interval)

    def update_animation(self):
        if self.current_step < self.animation_steps:
            # Выбираем случайное изображение и отображаем его
            if self.current_step % 10 > self.current_step // 100 or self.current_step % 10 == 0:
                random_image = random.choice(self.dice_images)
                self.dice_label.setPixmap(random_image)
                self.dice_label.angle += 30  # Увеличиваем угол на 30 градусов на каждом шаге

            # Увеличиваем интервал таймера для замедления анимации
            self.current_interval += 3 + self.current_step // 3
            if self.current_step // 10 == 3:
                self.current_interval += 5
            self.animation_timer.setInterval(self.current_interval)

            self.current_step += 1
            if self.current_step % 10 == 0:
                print(self.current_step)
                print(self.animation_steps)
                print(self.current_step < self.animation_steps)
        else:
            # Анимация завершена, выбираем окончательное изображение
            final_image = random.choice(self.dice_images)
            self.dice_label.setPixmap(final_image)
            self.dice_label.angle += 30
            self.animation_timer.stop()

class RotatableLabel(QLabel):
    def __init__(self, parent=None):
        super(RotatableLabel, self).__init__(parent)
        self._angle = 0

    @pyqtProperty(float)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        transform = QTransform()
        transform.rotate(self._angle)
        self.setPixmap(self.pixmap().transformed(transform))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DiceApp()
    window.show()
    sys.exit(app.exec_())
