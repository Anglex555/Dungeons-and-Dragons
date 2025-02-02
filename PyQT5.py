import sys
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, \
    QGraphicsDropShadowEffect, QPushButton, QProgressBar, QSpacerItem, \
    QSizePolicy, QApplication
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QAction, QMenu, QMenuBar, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt
from datetime import datetime
from PyQt5.QtGui import QIcon
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import QTimer, Qt, pyqtProperty
import sqlite3

dice_result = 0
Stylesheet = """
#Custom_Widget {
    background-color: #896648;
    border-radius: 10px;
}
#Custom_Dialog {
    background-color: #ac8b68;
    border-radius: 10px;
}

#closeButton {
    min-width: 36px;
    min-height: 36px;
    font-family: "Webdings";
    qproperty-text: "r";
    border-radius: 10px;
}
#modeButton {
    min-width: 36px;
    min-height: 36px;
    font-family: "Webdings";
    border-radius: 10px;
}
#modeButton:hover {
    color: white;
    background: #201c4d;
}
#closeButton:hover {
    color: white;
    background: red;
}
#VerticalRectangle {
    background-color: #800080; /* Цвет вертикального прямоугольника */
}
"""

class Dialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.setObjectName('Custom_Dialog')
        self.setStyleSheet('QDialog#Custom_Dialog { border-radius: 10px; }')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setStyleSheet(Stylesheet)
        self.initUi()
        # Добавляем анимацию открытия окна
        self.animate_open()
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(12)
        effect.setOffset(0, 0)
        effect.setColor(Qt.gray)
        self.setGraphicsEffect(effect)

    def initUi(self):
        layout = QVBoxLayout(self)

        # 重点: Этот виджет используется как фон с закругленными углами
        self.widget = QWidget(self)
        self.widget.setObjectName('Custom_Widget')
        self.widget.setStyleSheet("background-color: white;")

        layout.addWidget(self.widget)

        # Создаем кнопку закрытия и добавляем ее в правый верхний угол окна
        self.close_button = QPushButton('r', self)
        self.close_button.clicked.connect(self.accept)
        self.close_button.setObjectName('closeButton')
        self.close_button.setMaximumSize(36, 36)
        layout.addWidget(self.close_button, alignment=Qt.AlignTop | Qt.AlignRight)

        # Переместите кнопку закрытия на 40 пикселей ниже
        layout.addSpacing(-40)

        # Создаем кнопку для переключения режимов
        self.mode_button = QPushButton(self)
        self.mode_button.setObjectName('modeButton')
        self.mode_button.setIcon(QIcon("mod.png"))  # Укажите путь к изображению
        self.mode_button.setIconSize(QSize(44, 36))
        self.mode_button.clicked.connect(self.toggle_mode)
        layout.addWidget(self.mode_button, alignment=Qt.AlignLeft)
        # Создаем горизонтальный макет для размещения chat_window и dice_window
        horizontal_layout = QHBoxLayout()

        # Добавляем chat_window в левый столбец горизонтального макета
        self.hero = Hero()
        self.stats_window = StatsWindow(self.hero)
        self.chat_window = ChatWindow(self.hero, self.stats_window)
        self.dice_window = DiceApp(self.chat_window)

        # Добавляем dice_window в правый столбец горизонтального макета
        horizontal_layout.addWidget(self.stats_window)
        horizontal_layout.addWidget(self.chat_window)
        horizontal_layout.addWidget(self.dice_window)

        # Добавляем горизонтальный макет в вертикальный макет
        layout.addLayout(horizontal_layout)

        # Добавляем код чата сюда
        # self.chat_window = ChatWindow()
        # self.dice_window = DiceApp()
        # layout.addWidget(self.chat_window)
        # layout.addWidget(self.dice_window)

    def toggle_mode(self):
        # Добавьте ваш код для переключения режима (дневной/ночной) здесь
        if self.chat_window.is_night_mode:
            self.set_day_mode()
            self.chat_window.set_day_mode()
            self.stats_window.set_day_mode()
        else:
            self.set_night_mode()
            self.chat_window.set_night_mode()
            self.stats_window.set_night_mode()

    def set_day_mode(self):
        self.setStyleSheet(Stylesheet + """
            #Custom_Dialog {
                background-color: #ac8b68;
                border-radius: 10px;
            }
        """)
        self.chat_window.set_day_mode()
        self.is_night_mode = False

    def set_night_mode(self):
        self.setStyleSheet(Stylesheet + """
            #Custom_Dialog {
                background-color: #1b1b1f; /* Ночной режим */
                border-radius: 10px;
            }
        """)
        self.chat_window.set_night_mode()
        self.is_night_mode = True

    def animate_open(self):
        # Создаем анимацию для окна чата (плавное появление)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000)  # Длительность анимации в миллисекундах
        self.animation.setStartValue(0.0)  # Начальная прозрачность (окно невидимо)
        self.animation.setEndValue(1.0)  # Конечная прозрачность (полностью видимо)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)  # Устанавливаем кривую изменения прозрачности
        self.animation.start()

    def sizeHint(self):
        return QSize(1300, 600)
    
class ChatWindow(QMainWindow):
    def __init__(self, hero, stats_window):
        super().__init__()

        self.setWindowTitle("DnD")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.is_night_mode = False

        layout = QVBoxLayout()

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)
        
        self.stats_window = stats_window
        self.stats_window.update_stats()

        self.hero = hero
        self.enemy = Goblin()
        
        self.game_state = 1
        self.create_progress = 0
        self.game_progress = 0
        self.fight_progress = 0
        self.story_progress = 0
        self.select_techniques = 0
        self.locations_state = {
            "current_location": "фонтан",
            "visited_locations": set()
        }
        self.locations = {
            "фонтан": {
                "usage": "Вы находитесь у фонтана. Куда вы хотите пойти?",
                "options": {
                    "1": {
                        "text": "Деревня",
                        "location": "Деревня"
                    },
                    "2": {
                        "text": "Лес",
                        "location": "Лес"
                    }
                }
            },
            "Деревня": {
                "usage": "Вы пришли в деревню. Что вы хотите сделать?",
                "options": {
                    "1": {
                        "text": "Гильдия приключений",
                        "location": "Гильдия приключений"
                    },
                    "2": {
                        "text": "Магазин",
                        "location": "Магазин"
                    },
                    "3": {
                        "text": "Гостиница",
                        "location": "Гостиница"
                    },
                    "4": {
                        "text": "Вернуться к фонтану",
                        "location": "фонтан"
                    }
                }
            },
            "Лес": {
                "usage": "Вы в лесу. Что вы хотите сделать?",
                "options": {
                    "1": {
                        "text": "Идти в глубь леса",
                        "location": "тёмный лес"
                    },
                    "2": {
                        "text": "Вернуться к фонтану",
                        "location": "фонтан"
                    }
                }
            },
            "Гильдия приключений": {
                "usage": "Вы находитесь в гильдии приключений. Что вы хотите сделать?",
                "options": {
                    "1": {
                        "text": "Принять задание",
                        "location": "Принять задание"
                    },
                    "2": {
                        "text": "Поговорить с гильдмейстером",
                        "location": "Поговорить с гильдмейстером"
                    },
                    "3": {
                        "text": "Вернуться в деревню",
                        "location": "Деревня"
                    }
                }
            },
            "Магазин": {
                "usage": "Вы в магазине. Что вы хотите купить?",
                "options": {
                    "1": {
                        "text": "Оружие",
                        "location": "Магазин оружия"
                    },
                    "2": {
                        "text": "Броня",
                        "location": "Магазин брони"
                    },
                    "3": {
                        "text": "Зелья лечения",
                        "location": "Магазин зелий"
                    },
                    "4": {
                        "text": "Вернуться в деревню",
                        "location": "Деревня"
                    }
                }
            },
            "Гостиница": {
                "usage": "Вы в гостинице. Где вы хотите остановиться?",
                "options": {
                    "1": {
                        "text": "Обычная комната",
                        "location": "Обычная комната"
                    },
                    "2": {
                        "text": "Роскошная комната",
                        "location": "Роскошная комната"
                    },
                    "3": {
                        "text": "Вернуться в деревню",
                        "location": "Деревня"
                    }
                }
            },
            # Продолжайте добавлять другие локации по вашей необходимости

            # Добавьте остальные локации аналогичным образом
        }
        
        self.print_text("Создание персонажа")
        self.create_hero("0")
        self.is_roll = False

        input_layout = QHBoxLayout()

        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(35) 
        self.text_input.setPlaceholderText("Введите ваше сообщение...")
        self.text_input.keyPressEvent = self.custom_keyPressEvent
        self.text_input.keyPressEvent = self.process_enter_key
        input_layout.addWidget(self.text_input)

        self.send_button = QPushButton(self)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setObjectName("SendButton")
        self.send_button.setIcon(QIcon("send.png"))
        self.send_button.setIconSize(QSize(28, 24))
        self.send_button.setFixedSize(40, 36) 
        self.set_button_style(self.send_button)  
        input_layout.addWidget(self.send_button)


        layout.addLayout(input_layout)
        central_widget.setLayout(layout)

        self.set_day_mode()
        self.animate_open()
        
        self.opacity_effect = QGraphicsOpacityEffect(self.send_button)
        self.send_button.setGraphicsEffect(self.opacity_effect)
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setEasingCurve(QEasingCurve.OutQuad)
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setStartValue(0)
        self.opacity_animation.setEndValue(1)
        self.opacity_animation.finished.connect(self.reset_button_opacity)

        self.set_button_style(self.send_button)

    def animate_open(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000) 
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0) 
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.start()

    def reset_button_opacity(self):
        self.opacity_effect.setOpacity(1)

    def custom_keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            if event.modifiers() == Qt.ControlModifier:
                # Если нажаты одновременно Ctrl+Enter, то вставляем перенос строки
                cursor = self.text_input.textCursor()
                cursor.insertBlock()
                self.text_input.setTextCursor(cursor)
            else:
                # В противном случае отправляем сообщение
                self.send_message()
        else:
            super(QTextEdit, self.text_input).keyPressEvent(event)

    def process_enter_key(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.send_message()
        else:
            QTextEdit.keyPressEvent(self.text_input, event)
    
    def set_day_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #c3ab92; /* Немного темнее старой бумаги */
                border-radius: 10px;
            }
            QTextEdit {
                background-color: #d2c0ad; /* Немного темнее цвет пергамента */
                border: 1px solid #B9877B;
                padding: 5px;
                color: black;
            }
            QPushButton#SendButton {
                background-color: #800080; /* Фиолетовый цвет */
                color: white;
                border: none;
                padding: 5px 10px;
                margin-left: 5px;
                border-radius: 10px; /* Закругленные углы */
            }
        """)
        self.is_night_mode = False

    def set_night_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #222;
                border-radius: 10px;
            }
            QTextEdit {
                background-color: #333;
                border: 1px solid #444;
                padding: 5px;
                color: white;
            }
            QPushButton#SendButton {
                background-color: #800080; /* Фиолетовый цвет */
                color: white;
                border: none;
                padding: 5px 10px;
                margin-left: 5px;
                border-radius: 10px; /* Закругленные углы */
            }
        """)
        self.is_night_mode = True
        
    def send_message(self):
        text = self.text_input.toPlainText()
        if text and self.is_roll == False:
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] Вы: {text}"
            self.print_text(message)

            if(self.game_state == 1):
                self.create_hero(text)
            if(self.game_state == 2):
                self.game_process(text)
            if(self.game_state == 3):
                self.story(text)

            self.text_input.clear()
            self.text_input.setFocus()

            self.opacity_animation.start()

    def game_process(self, input):
        if self.game_progress == 1:
            current_location = self.locations_state["current_location"]
            options = self.locations.get(current_location, {}).get("options", {})

            if input in options:
                selected_option = options[input]
                self.locations_state["visited_locations"].add(current_location)
                self.locations_state["current_location"] = selected_option["location"]
                self.display_location(selected_option["location"])
            else:
                self.print_text("Неверный выбор. Пожалуйста, выберите опцию из списка.")
        elif self.game_progress == 2:
            self.fight(input)
        else:
            current_location = self.locations_state["current_location"]
            self.display_location(current_location)
            self.game_progress = 1 

    def fight(self, input):
        self.stats_window.update_stats()
        if self.fight_progress == 0:
            if input == '1':
                self.print_text('Выберите заклинание')
                
                self.print_text('\n\t\tЗаклинания:')
                for spell in self.hero.techniques:
                    self.print_text(f"\t{spell['index']}. {spell['name']}")
                self.fight_progress = 1
            elif input == '2':
                self.print_text('Бросьте кубик')
                self.is_roll = True
                self.fight_progress = -1
            else:
                self.print_text("Неверный выбор. Пожалуйста, выберите опцию из списка.")
        elif self.fight_progress == 1:
            if int(input) <= len(self.hero.techniques):
                self.select_techniques = int(input)
                self.print_text('Бросьте кубик')
                self.is_roll = True
                self.fight_progress = 2
            else:
                self.print_text("Неверный выбор. Пожалуйста, выберите опцию из списка.")
        elif self.fight_progress == 2:
            if self.hero.hero_class == 'Fighter':
                original_power = random.randint(self.hero.weapon.damage[0], self.hero.weapon.damage[1]) + self.hero.strength / 2
                damage = int(original_power * (float(self.hero.lvl) / 10 + 1) * (float(input) / 10))
            if self.hero.hero_class == 'Wizard':
                original_power = random.randint(self.hero.weapon.damage[0], self.hero.weapon.damage[1]) + self.hero.intelligence / 2
                damage = int(original_power * (float(self.hero.lvl) / 10 + 1) * (float(input) / 10))
            self.enemy.take_damage(damage)
            self.print_text(self.hero.get_spell_usage(self.select_techniques) + f' Враг получил {damage} урона.')
            if self.enemy.health > 0:
                self.print_text('Враг разозлился и готов атаковать. Защищайтесь!')
                self.print_text('Бросьте кубик')
                self.is_roll = True
                self.fight_progress = 3
            else:
                self.print_text('Враг повержен')
                self.hero.exp += 200
                self.locations_state["current_location"] = 'Лес'
                self.display_location(self.locations_state["current_location"])
                self.is_roll = False
                self.fight_progress = 0
                self.game_progress = 1 
        elif self.fight_progress == 3:
            print(self.hero.hp)
            self.print_text(self.enemy.attack(self.hero, input))
            self.print_text('Ваша очередь атаковать, выберите заклинание')
            self.print_text('\n\t\tЗаклинания:')
            for spell in self.hero.techniques:
                self.print_text(f"\t{spell['index']}. {spell['name']}")
            self.is_roll = False
            self.fight_progress = 1
        elif self.fight_progress == -1:
            self.print_text(self.enemy.escape_attack(self.hero, input))
            self.locations_state["current_location"] = 'Лес'
            self.display_location(self.locations_state["current_location"])
            self.fight_progress = 0
            self.game_progress = 1
        self.stats_window.update_stats()
        

    def display_location(self, location):
        if location == "тёмный лес":
            self.print_text("В тёмном лесу, где кроны деревьев не пропускали свет из за кустов выскочил гоблин. Его зеленая кожа пылала яростью, и острый клинок был готов к битве. Что вы делаете? \n 1.Напасть на гоблина \n 2.Попытаться убежать из леса")
            self.enemy = Goblin()
            self.game_progress = 2
        else:
            location_data = self.locations.get(location)

            usage = location_data["usage"]
            options = location_data.get("options")

            message = f"{usage}\n"
            if options:
                for option, option_data in options.items():
                    message += f"{option}. {option_data['text']}\n"

            self.print_text(message)


    def story(self, input):
        pass

    def create_hero(self, input):
        if self.create_progress == 0:
            # self.hero.name = "Хиро"
            # self.hero.hero_class = "Fighter"
            # self.hero.race = "Human"
            self.hero.name = "Эльфи"
            self.hero.hero_class = "Wizard"
            self.hero.race = "Elf"
            self.hero.weapon = Staff('обычный посох', 19)
            self.print_text(self.hero.add_random_spells(3, self.hero.hero_class))
            self.hero.strength = 10
            self.hero.dexterity = 10
            self.hero.constitution = 10
            self.hero.intelligence = 10
            self.hero.wisdom = 10
            self.hero.charisma = 10
            self.hero.max_hp = 10 * self.hero.constitution
            self.hero.hp = 100
            self.create_progress = 9
        if self.create_progress == 0:
            self.print_text("Введите имя вашего персонажа")
            self.create_progress = 1
        elif self.create_progress == 1:
            self.hero.name = input
            self.print_text("Выберите класс вашего персонажа: \n 1.Воин \n 2.Волшебник")
            self.create_progress = 2
        elif self.create_progress == 2:
            if '1' in input:
                self.hero.hero_class = 'Fighter'
            elif '2' in input:
                self.hero.hero_class = 'Wizard'
                self.hero.weapon = Staff('обычный посох', 19)
            self.print_text("Выберите расу вашего персонажа: \n 1.Человек \n 2.Эльф \n 3.Дварф")
            self.create_progress = 3
        elif self.create_progress == 3:
            if '1' in input:
                self.hero.race = 'Human'
            elif '2' in input:
                self.hero.race = 'Elf'
            elif '3' in input:
                self.hero.race = 'Dwarf'
            self.hero.add_random_spells(3, self.hero.hero_class)
            self.print_text("Бросьте кубик, чтобы определить силу вашего персонажа")
            self.is_roll = True
            self.create_progress = 4
        elif self.create_progress == 4:
            if self.hero.race == 'Human':
                self.hero.strength = input
            elif self.hero.race == 'Elf':
                self.hero.strength = int(input * 0.8)
            elif self.hero.race == 'Dwarf':
                self.hero.strength = int(input * 1.2)
            self.is_roll = True
            self.print_text("Бросьте кубик, чтобы определить ловкость вашего персонажа")
            self.create_progress = 5
        elif self.create_progress == 5:
            if self.hero.race == 'Human':
                self.hero.dexterity = input
            elif self.hero.race == 'Elf':
                self.hero.dexterity = int(input * 1.2)
            elif self.hero.race == 'Dwarf':
                self.hero.dexterity = int(input * 0.8)
            self.print_text("Бросьте кубик, чтобы определить телосложение вашего персонажа")
            self.is_roll = True
            self.create_progress = 6
        elif self.create_progress == 6:
            if self.hero.race == 'Human':
                self.hero.constitution = input
            elif self.hero.race == 'Elf':
                self.hero.constitution = int(input * 0.8)
            elif self.hero.race == 'Dwarf':
                self.hero.constitution = int(input * 1.2)
            self.hero.hp = 10 * self.hero.constitution
            self.hero.max_hp = 10 * self.hero.constitution
            self.print_text("Бросьте кубик, чтобы определить интеллект вашего персонажа")
            self.is_roll = True
            self.create_progress = 7
        elif self.create_progress == 7:
            if self.hero.race == 'Human':
                self.hero.intelligence = input
            elif self.hero.race == 'Elf':
                self.hero.intelligence = int(input * 1.2)
            elif self.hero.race == 'Dwarf':
                self.hero.intelligence = int(input * 0.8)
            self.print_text("Бросьте кубик, чтобы определить мудрость вашего персонажа")
            self.is_roll = True
            self.create_progress = 8
        elif self.create_progress == 8:
            if self.hero.race == 'Human':
                self.hero.wisdom = input
            elif self.hero.race == 'Elf':
                self.hero.wisdom = int(input * 1.2)
            elif self.hero.race == 'Dwarf':
                self.hero.wisdom = input
            self.print_text("Бросьте кубик, чтобы определить харизму вашего персонажа")
            self.is_roll = True
            self.create_progress = 9
        elif self.create_progress == 9:
            if self.hero.race == 'Human':
                self.hero.charisma = input
            elif self.hero.race == 'Elf':
                self.hero.charisma = input
            elif self.hero.race == 'Dwarf':
                self.hero.charisma = input
            self.print_text("Ваш персонаж успешно создан")
            self.is_roll = False
            self.game_state = 2
            self.print_text(self.hero.info())
            self.stats_window.update_stats()
            self.print_text('\n\t\tЗаклинания:')
            for spell in self.hero.techniques:
                self.print_text(f"\n  {spell['index']}.  {spell['name']}: {spell['description']}")
            self.print_text("\n")
            self.game_process('')

    def roll(self):
        global dice_result
        if self.game_state == 1:
            if self.create_progress > 2:
                self.create_hero(dice_result)
        if self.game_state == 2:
            if self.fight_progress != 0:
                self.fight(dice_result)


    def print_text(self, message):
        text_format = QTextCharFormat()
        text_format.setFontWeight(QFont.Bold)
        text_format.setFontPointSize(12)

        cursor = self.message_display.textCursor()
        cursor.setCharFormat(text_format)
        cursor.insertText(message + '\n')  # Используйте append() для автопрокрутки

        # Прокручиваем QTextEdit вниз
        scroll_bar = self.message_display.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def set_button_style(self, button):
        button.setStyleSheet("""
            background-color: #800080; /* Фиолетовый цвет */
            color: white;
            border: none;
            padding: 5px 10px;
            margin-left: 5px;
            border-radius: 10px; /* Закругленные углы */
        """)

    def sizeHint(self):
            return QSize(600, 400)

class Sword:
    def __init__(self, name, damage):
        self.name = name
        self.damage = (damage - 5, damage + 5)  # Диапазон урона
        self.weight = 40  # Вес
        self.type = "Меч"

class Hammer:
    def __init__(self, name, damage):
        self.name = name  # Название оружия
        self.damage = (damage - 8, damage + 8)  # Диапазон урона
        self.weight = 50  # Вес
        self.type = "Молот"

class Staff:
    def __init__(self, name, damage):
        self.name = name  # Название оружия
        self.damage = (damage - 10, damage + 10)  # Диапазон урона
        self.weight = 30  # Вес
        self.type = "Посох"


class Hero :
    name = 'Hero'
    hero_class = 'Wizard'
    race = 'Elf'
    hp = 100
    max_hp = 100
    mana = 100
    max_mana = 100
    strength = 10
    dexterity = 10
    constitution = 10
    intelligence = 10
    wisdom = 10
    charisma = 10
    techniques = []
    spells_quantity = 0
    spell_count = 0

    def __init__(self):
        self.name = "default"
        self.hero_class = 'default'
        self.race = 'default'
        self.hp = 100
        self.mana = 100
        self.weapon = Sword('обычный меч', 15)
        self.money = 10
        self.exp = 0
        self.exp_to_next_level = 1000
        self.lvl = 1

    def load_spells_from_database(self, table_name):
        connection = sqlite3.connect('hero_db.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name, description, usage, level, complexity FROM {table_name}")
        spells_data = cursor.fetchall()
        connection.close()
        return spells_data

    def add_random_spells(self, num_spells, hero_class):
        if hero_class == 'Wizard':
            spells_data = self.load_spells_from_database('spell_book')
        elif hero_class == 'Fighter':
            spells_data = self.load_spells_from_database('sword_book')
        else:
            return "Неверный класс героя."

        if len(spells_data) < num_spells:
            return "Недостаточно доступных заклинаний."

        for spell in spells_data:
            print(spell[3])
        level_1_spells = [spell for spell in spells_data if spell[3] == 1]
        print(level_1_spells)
        selected_spells = random.sample(level_1_spells, num_spells)

        out = ''
        for spell in selected_spells:
            self.spells_quantity += 1
            self.spell_count += 1
            spell_dict = {
                'index': self.spell_count,
                'name': spell[0],
                'description': spell[1],
                'usage': spell[2],
                'level': spell[3],
                'complexity': spell[4]
            }
            self.techniques.append(spell_dict)
            out += f"Вы освоили {hero_class} {spell_dict['level']} уровня '{spell_dict['name']}': {spell_dict['description']}\n"
        return out

    def get_spell_usage(self, index):
        for spell in self.techniques:
            if spell['index'] == index:
                return spell['usage']
        return "Заклинание не найдено."
    
    def info(self) :
        info = "\n\t Имя: " + self.name
        curr_out = 'default'
        if self.hero_class == "Wizard": curr_out = 'Волшебник'
        if self.hero_class == "Fighter": curr_out = 'Воин'
        info += "\n Класс: " + curr_out
        curr_out = 'default'
        if self.race == "Human": curr_out = 'Человек'
        if self.race == "Elf": curr_out = 'Эльф'
        if self.race == "Dwarf": curr_out = 'Дварф'
        info += "\n Раса: " + curr_out
        info += "\n Здоровье: " + str(self.hp)
        info += "\n Сила: " + str(self.strength)
        info += "\n Ловкость: " + str(self.dexterity)
        info += "\n Телосложение: " + str(self.constitution)
        info += "\n Интеллект: " + str(self.intelligence)
        info += "\n Мудрость: " + str(self.wisdom)
        info += "\n Харизма: " + str(self.charisma)
        info += "\n Оружие: " + self.weapon.name
        info += "\n Деньги:\n " + self.format_Money(self.money)
        info += "\n Уровень: " + str(self.lvl)
        info += "\n Опыт: " + str(self.exp)
        # info = "\n\t\t name: " + self.name
        # info += "\n\t Hero class: " + self.hero_class
        # info += "\n\t Hero race: " + self.race
        # info += "\n\t Hero hp: " + str(self.hp)
        # info += "\n\t Hero strength: " + str(self.strength)
        # info += "\n\t Hero dexterity: " + str(self.dexterity)
        # info += "\n\t Hero constitution: " + str(self.constitution)
        # info += "\n\t Hero intelligence: " + str(self.intelligence)
        # info += "\n\t Hero wisdom: " + str(self.wisdom)
        # info += "\n\t Hero charisma: " + str(self.charisma)
        # info += "\n\t Hero weapon: " + self.weapon.name
        # info += "\n\t Hero money: " + str(self.money)
        # info += "\n\t Hero level: " + str(self.lvl)
        # info += "\n\t Hero exp: " + str(self.exp)
        return info
    
    def stats(self) :
        # info = "\n       Имя: " + self.name
        curr_out = 'default'
        if self.hero_class == "Wizard": curr_out = 'Волшебник'
        if self.hero_class == "Fighter": curr_out = 'Воин'
        info = "\n  Класс: " + curr_out
        curr_out = 'default'
        if self.race == "Human": curr_out = 'Человек'
        if self.race == "Elf": curr_out = 'Эльф'
        if self.race == "Dwarf": curr_out = 'Дварф'
        info += "\n  Раса: " + curr_out
        info += "\n  Уровень: " + str(self.lvl)
        info += "\n\n  Сила: " + str(self.strength)
        info += "\n  Ловкость: " + str(self.dexterity)
        info += "\n  Телосложение: " + str(self.constitution)
        info += "\n  Интеллект: " + str(self.intelligence)
        info += "\n  Мудрость: " + str(self.wisdom)
        info += "\n  Харизма: " + str(self.charisma)
        info += "\n\n  Деньги:\n " + self.format_Money(self.money)
        return info
    
    def stats_weapon(self) :
        info = "  Название: " + self.weapon.name
        info += "\n  Тип: " + self.weapon.type
        info += "\n  Урон: " + f" от {self.weapon.damage[0]} до {self.weapon.damage[1]}"
        info += "\n  Вес: " + str(self.weapon.weight)
        return info

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def format_Money(self, coins):
        platinum = coins // 10000
        gold = (coins % 10000) // 1000
        silver = (coins % 1000) // 100
        bronze = coins % 100

        def pluralize(value, unit):
            if value == 0:
                return ""
            elif value % 10 == 1:
                return f"  {value} {unit}ая монета\n"
            elif 1 < value % 10 < 5:
                return f"  {value} {unit}ые монеты\n"
            else:
                return f"  {value} {unit}ых монет\n"

        result = ""
        if platinum > 0:
            result += pluralize(platinum, "платинов")
        if gold > 0:
            result += " " if result else ""
            result += pluralize(gold, "золот")
        if silver > 0:
            result += " " if result else ""
            result += pluralize(silver, "серебрян")
        if bronze > 0:
            result += " " if result else ""
            result += pluralize(bronze, "бронзов")

        if not result:
            return "0 бронзовых"

        return result

class Enemy:
    def __init__(self, name, health=50, damage=5, armor=5):
        self.name = name
        self.health = health
        self.damage = damage
        self.armor = armor

    def take_damage(self, damage):
        self.health -= damage + self.armor
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

class Goblin(Enemy):
    def __init__(self, name="Гоблин", health=40, damage=7, armor=0):
        super().__init__(name, health, damage, armor)

    def attack(self, hero, dice):
        choose_attack = random.randint(1, 3)
        if choose_attack == 1:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Гоблин делает уверенный мах коротким кинжалом, но вы ловко отклоняетесь, и его атака промахивается. Вы своими волосами чувствуете ветер кинжала, пронесшийся мимо вашего лица."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage)
                hero.take_damage(attack_damage)
                return f"Резким движением руки гоблин атакует вас, его кинжал вонзается в ваши доспехи. Острое лезвие буквально взрывает боль, когда проникает в вашу плоть, нанося вам {attack_damage} урона."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 2
                hero.take_damage(attack_damage)
                return f"Гоблин, будто испытывая внезапный порыв ярости, атакует с такой силой, что его кинжал пронзает вашу броню и глубоко проникает в ваше тело. Острая боль охватывает вас. Это был исключительно мощный удар, наносящий вам {attack_damage} урона."
        elif choose_attack == 2:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Гоблин резко метает дротик, но его бросок не слишком точен. Дротик проходит мимо вас, мчась в сторону, не представляя угрозы."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage)
                hero.take_damage(attack_damage)
                return f"Резким движением, гоблин метает смазанный ядом дротик, который точно попадает в вас. Острый кончик дротика задевает вашу кожу, нанося вам {attack_damage} урона."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 3
                hero.take_damage(attack_damage)
                return f"Гоблин резко бросает дротик с невероятной меткостью. Дротик точно попадает в вас и пронзает вашу плоть. Острая боль охватывает вас, и вы чувствуете, что дротик был покрыт ядом, нанося вам {attack_damage} урона."
        elif choose_attack == 3:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Гоблин начинает атаковать вас быстрыми ударами, но ваше умение и проворство позволяют вам избежать его ударов. Его мечи и мечеты промахиваются, оставляя вас невредимым."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage) 
                hero.take_damage(attack_damage)
                return f"Гоблин атакует вас быстрыми ударами, каждый из которых находит свою цель. Вы чувствуете, как лезвия короткого меча царапают вас, нанося вам {attack_damage} урона."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 4
                hero.take_damage(attack_damage)
                return f"Гоблин нападает с нескончаемой агрессией и скоростью вихря. Его мечи находят уязвимые места на вашем теле, и каждый удар проникает глубоко в ваши ткани. Это были удары смерти, наносящие вам {attack_damage} урона."
        
    def escape_attack(self, hero, dice):
        attack_damage = random.randint(1, self.damage) * 2
        hero.take_damage(attack_damage)
        if dice >= 10:
            return "Стремительно развернувшись, вы начали бежать со всех ног. Вскоре вы выбролись из темного леса, оставив за собой грозную атмосферу и опасность, что скрывалась в его чащах."
        else:
            return f"Вы ринулись вперед, стремясь выбраться из леса, однако внезапно гоблин запрыгнул на вас и вонзил свой нож вам в спину нанеся {attack_damage} урона."
        

class StatsWindow(QWidget):
    def __init__(self, hero):
        super().__init__()
        self.hero = hero
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Информация о герое')
        self.setGeometry(100, 100, 400, 600)
        self.setObjectName('Stats_Dialog')

        layout = QVBoxLayout()

        self.is_night_mode = False
        self.name = QLabel(self.hero.name)

        # Установите выравнивание по центру
        self.name.setAlignment(Qt.AlignCenter)

        # Добавьте QLabel в QVBoxLayout
        layout.addWidget(self.name)
        layout_stats = QHBoxLayout()
        self.image_label = QLabel(self)
        self.pixmap = QPixmap(f'c:/Ультилиты/2/Mai/DnD/Images/{self.hero.hero_class}{self.hero.race}.jpg')
        self.pixmap = self.pixmap.scaled(200, 300, Qt.KeepAspectRatio)
        self.image_label.setAlignment(Qt.AlignCenter)  # Выравниваем по центру
        self.image_label.setPixmap(self.pixmap)
        layout_stats.addWidget(self.image_label)
        
        info = self.hero.stats()
        self.stats_label = QLabel(info)
        layout_stats.addWidget(self.stats_label)
        layout.addLayout(layout_stats)
        
        self.info_label = QLabel("\t Оружие: \n" + self.hero.stats_weapon())
        layout.addWidget(self.info_label)
        
        self.hp_bar = QProgressBar(self)
        self.hp_bar.setValue(int(self.hero.hp / (self.hero.max_hp / 100)))
        self.hp_bar.setMaximum(int(self.hero.max_hp / (self.hero.max_hp / 100)))
        print(f"{self.hero.hp} из {self.hero.max_hp}")
        self.hp_bar.setAlignment(Qt.AlignCenter)
        self.hp_bar.setTextVisible(False)  # Отключение текстового значения
        self.hp_state = QLabel(f'Здоровье ({self.hero.hp}/{self.hero.max_hp}):')
        layout.addWidget(self.hp_state)
        layout.addWidget(self.hp_bar)

        self.mana_bar = QProgressBar(self)
        self.mana_bar.setValue(int(self.hero.mana / (self.hero.max_mana / 100)))
        self.mana_bar.setMaximum(int(self.hero.max_mana / (self.hero.max_mana / 100)))
        print(f"{self.hero.mana} из {self.hero.max_mana}")
        self.mana_bar.setAlignment(Qt.AlignCenter)
        self.mana_bar.setTextVisible(False)  # Отключение текстового значения
        self.mana_state = QLabel(f'Мана ({self.hero.mana}/{self.hero.max_mana}):')
        layout.addWidget(self.mana_state)
        layout.addWidget(self.mana_bar)

        self.exp_bar = QProgressBar(self)
        self.exp_bar.setValue(int(self.hero.exp / (self.hero.exp_to_next_level / 100)))
        self.exp_bar.setMaximum(int(self.hero.exp_to_next_level / (self.hero.exp_to_next_level / 100)))
        print(f"{self.hero.exp} из {self.hero.exp_to_next_level}")
        self.exp_bar.setAlignment(Qt.AlignCenter)
        self.exp_bar.setTextVisible(False)  # Отключение текстового значения
        self.exp_state = QLabel(f'Опыт ({self.hero.exp}/{self.hero.exp_to_next_level}):')
        layout.addWidget(self.exp_state)
        layout.addWidget(self.exp_bar)

        self.set_day_mode()
        
        self.setLayout(layout)

    def update_stats(self):
        # Обновим информацию о герое, включая hp_bar
        print("update")
        print(self.hero.hp)
        self.hp_bar.setValue(int(self.hero.hp / (self.hero.max_hp / 100)))
        self.mana_bar.setValue(int(self.hero.mana / (self.hero.max_mana / 100)))
        self.exp_bar.setValue(int(self.hero.exp / (self.hero.exp_to_next_level / 100)))

        self.pixmap = QPixmap(f'c:/Ультилиты/2/Mai/DnD/Images/{self.hero.hero_class}{self.hero.race}.jpg')
        self.pixmap = self.pixmap.scaled(200, 300, Qt.KeepAspectRatio)
        self.image_label.setAlignment(Qt.AlignCenter)  # Выравниваем по центру
        self.image_label.setPixmap(self.pixmap)
        self.image_label.repaint()
        # Другие обновления данных, если необходимо
        
        self.hp_state.setText(f'Здоровье ({self.hero.hp}/{self.hero.max_hp}):')
        self.mana_state.setText(f'Мана ({self.hero.mana}/{self.hero.max_mana}):')
        self.exp_state.setText(f'Опыт ({self.hero.exp}/{self.hero.exp_to_next_level}):')

        self.hp_state.update()
        self.mana_state.update()
        self.exp_state.update()

        # Обновим текстовые метки, если они тоже должны измениться
        self.name.setText(self.hero.name)
        self.name.repaint()  # Перерисовать метку

        self.info_label.setText("\t Оружие: \n" + self.hero.stats_weapon())
        self.info_label.repaint()  # Перерисовать метку

        self.stats_label.setText(self.hero.stats())
        self.stats_label.repaint()  # Перерисовать метку

    def set_day_mode(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
                color: white; 
                font-weight: bold;
            }
        """)
        self.stats_label.setStyleSheet("""
            background-color: #d2c0ad; /* Немного темнее цвет пергамента */
            color: #241c14;
            border-radius: 10px;
        """)
        self.info_label.setStyleSheet("""
            background-color: #d2c0ad; /* Немного темнее цвет пергамента */
            color: #241c14;
            border-radius: 10px;
        """)
        self.image_label.setStyleSheet("""
            background-color: #443525; /* Немного темнее старой бумаги */
            border-radius: 10px;
        """)
        self.name.setStyleSheet("""
            font-size: 22px;
            background-color: #d2c0ad; /* Немного темнее цвет пергамента */
            color: #241c14;
            border-radius: 10px;
        """)
        self.exp_bar.setStyleSheet('QProgressBar {border: 2px solid #695239; border-radius: 6px; background: #d5c4b2; height: 20px;}'
                             'QProgressBar::chunk {background: #c9ab47; border-radius: 5px; margin: 1px;}')
        self.hp_bar.setStyleSheet('QProgressBar {border: 2px solid #644d36; border-radius: 6px; background: #d5c4b2; height: 20px;}'
                             'QProgressBar::chunk {background: #FF0000; border-radius: 5px; margin: 1px;}')
        self.mana_bar.setStyleSheet('QProgressBar {border: 2px solid #644d36; border-radius: 6px; background: #d5c4b2; height: 20px;}'
                             'QProgressBar::chunk {background: #347deb; border-radius: 5px; margin: 1px;}')
        self.is_night_mode = False

    def set_night_mode(self):
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
                color: white; 
                font-weight: bold;
            }
        """)
        self.stats_label.setStyleSheet("""
            background-color: #333; /* Немного темнее цвет пергамента */
            color: white;
            border-radius: 10px;
        """)
        self.info_label.setStyleSheet("""
            background-color: #333; /* Немного темнее цвет пергамента */
            color: white;
            border-radius: 10px;
        """)
        self.image_label.setStyleSheet("""
            background-color: #333; /* Немного темнее старой бумаги */
            border-radius: 10px;
        """)
        self.name.setStyleSheet("""
            font-size: 22px;
            background-color: #333; /* Немного темнее цвет пергамента */
            color: white;
            border-radius: 10px;
        """)
        self.exp_bar.setStyleSheet('QProgressBar {border: 2px solid grey; border-radius: 6px; background: #333; height: 20px;}'
                             'QProgressBar::chunk {background: #c9ab47; border-radius: 5px; margin: 1px;}')
        self.hp_bar.setStyleSheet('QProgressBar {border: 2px solid grey; border-radius: 6px; background: #333; height: 20px;}'
                             'QProgressBar::chunk {background: #FF0000; border-radius: 5px; margin: 1px;}')
        self.mana_bar.setStyleSheet('QProgressBar {border: 2px solid grey; border-radius: 6px; background: #333; height: 20px;}'
                             'QProgressBar::chunk {background: #347deb; border-radius: 5px; margin: 1px;}')
        self.is_night_mode = True


class DiceApp(QWidget):
    def __init__(self, chat_window):
        super().__init__()
        self.chat_window = chat_window
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 300, 600)
        self.setWindowTitle('20-гранный кубик')

        layout = QVBoxLayout()

        self.dice_label = RotatableLabel(self)
        self.dice_label.setAlignment(Qt.AlignCenter)
        self.dice_label.setFixedSize(250, 250)
        layout.addWidget(self.dice_label)

        self.roll_button = QPushButton('Бросить кубик', self)
        self.roll_button.clicked.connect(self.start_animation)
        self.roll_button.setStyleSheet("""
            background-color: #912c81; /* Фиолетовый цвет */
            color: white;
            border: none;
            padding: 15px 10px;
            margin-left: 5px;
            border-radius: 10px; /* Закругленные углы */
            font-size: 16px; /* Увеличенный размер текста */
            font-weight: bold; /* Жирное начертание текста */
        """)
        layout.addWidget(self.roll_button)

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
        self.roll_button.setEnabled(False)
        self.roll_button.setStyleSheet(self.roll_button.styleSheet() + "background-color: #600060;")
        self.current_step = 0
        self.current_interval = 0  # Начальный интервал таймера
        self.animation_timer.start(self.current_interval)

    def update_animation(self):
        global dice_result
        if self.current_step < self.animation_steps:
            # Выбираем случайное изображение и отображаем его
            if self.current_step % 10 > self.current_step // 100 or self.current_step % 10 == 0:
                random_image = random.choice(self.dice_images)
                self.dice_label.setPixmap(random_image)
                self.dice_label.angle += 30  # Увеличиваем угол на 30 градусов на каждом шаге

            # Увеличиваем интервал таймера для замедления анимации
            self.current_interval += 1 + self.current_step // 3
            if self.current_step == 4:
                self.roll_button.setStyleSheet(self.roll_button.styleSheet() + "background-color: #944a88;")
            if self.current_step > 32:
                self.current_interval += 5
            self.animation_timer.setInterval(self.current_interval)

            self.current_step += 1
        else:
            # Анимация завершена, выбираем окончательное изображение
            self.roll_button.setStyleSheet(self.roll_button.styleSheet() + "background-color: #912c81;")
            self.roll_button.setEnabled(True)
            final_image = random.choice(self.dice_images)
            dice_result = self.dice_images.index(final_image) + 1
            self.chat_window.roll()
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
    import sys

    app = QApplication(sys.argv)
    w = Dialog()
    w.exec_()
    QTimer.singleShot(200, app.quit)
    sys.exit(app.exec_())