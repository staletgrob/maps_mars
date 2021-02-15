import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QRadioButton
from PyQt5.QtGui import QPixmap
import requests
from PyQt5.QtCore import Qt


def get_map_image(lat_lon, l, z):
    params = {
        'll': f'{lat_lon[0]},{lat_lon[1]}',
        'l': l,
        'z': z
    }
    response = requests.get('http://static-maps.yandex.ru/1.x/', params=params)
    if not response:
        raise RuntimeError('Ошибка такой карты не находит!!!')
    result = QPixmap()
    if l.startswith('map') and not l.endswith('sat'):
        result.loadFromData(response.content, 'PNG')
    elif l.startswith('sat'):
        result.loadFromData(response.content, 'JPG')
    return result


def clamp(v, min_v, max_v):
    return max(min_v, min(v, max_v))


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.map_center = [37, 55]
        self.map_scale = 5
        self.l = 'map'
        self.init_ui()

    def update_map(self):
        self.map_label.setPixmap(get_map_image(self.map_center, self.l, self.map_scale))

    def init_ui(self):
        self.setGeometry(300, 300, 600, 450)
        self.map_label = QLabel('', self)
        self.update_map()
        self.map_switch = QRadioButton('Карта', self)
        self.map_switch.move(5, 390)
        self.map_switch.toggled.connect(self.l_switch)
        self.map_switch.toggle()

        self.sat_switch = QRadioButton('Спутник', self)
        self.sat_switch.move(5, 410)
        self.sat_switch.toggled.connect(self.l_switch)

        self.hyb_switch = QRadioButton('Гибрид', self)
        self.hyb_switch.move(5, 430)
        self.hyb_switch.toggled.connect(self.l_switch)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.map_scale += 1
        elif event.key() == Qt.Key_PageDown:
            self.map_scale -= 1
        elif event.key() == Qt.Key_W:
            self.map_center[1] += 180 / (2 ** self.map_scale * 2)
        elif event.key() == Qt.Key_S:
            self.map_center[1] -= 180 / (2 ** self.map_scale * 2)
        elif event.key() == Qt.Key_D:
            self.map_center[0] += 360 / (2 ** self.map_scale * 2)
        elif event.key() == Qt.Key_A:
            self.map_center[0] -= 360 / (2 ** self.map_scale * 2)
        self.map_scale = clamp(self.map_scale, 0, 17)
        self.map_center = [clamp(self.map_center[0], -180, 180),
                           clamp(self.map_center[1], -90, 90)]
        try:
            self.update_map()
        except RuntimeError:
            print(f'Так не пойдет!!!')

    def l_switch(self):
        if self.sender() == self.map_switch:
            self.l = 'map'
            self.update_map()
        elif self.sender() == self.sat_switch:
            self.l = 'sat'
            self.update_map()
        elif self.sender() == self.hyb_switch:
            self.l = 'sat,skl'
            self.update_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    exit(app.exec())