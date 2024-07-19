import sys
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, \
    QGraphicsDropShadowEffect, QPushButton, QProgressBar, QMessageBox, \
    QSizePolicy, QApplication
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt
from datetime import datetime
from PyQt5.QtGui import QIcon, QColor
import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout
from PyQt5.QtGui import QPixmap, QTransform
from PyQt5.QtCore import QTimer, Qt, pyqtProperty
import sqlite3
import json


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
        self.mode_button.setIcon(QIcon("Images/mod.png"))  # Укажите путь к изображению
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
        self.game_story = 'Начало игры\n'

        self.message_queue = []

        self.hero = hero
        self.enemy = Goblin()
        
        self.game_state = 1
        self.create_progress = 0
        self.game_progress = 0
        self.fight_progress = 0
        self.story_progress = 0
        self.select_techniques = 0
        self.store_progress = 0
        self.guild_progress = 0
        self.count_g = 10
        self.count_r = 10
        self.count_o = 10
        self.select_store = Store("default")
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
                "usage": "Вы пришли на главную площадь деревни. Что вы хотите сделать?",
                "options": {
                    "1": {
                        "text": "Пойти в гильдию приключений",
                        "location": "Гильдия приключений"
                    },
                    "2": {
                        "text": "Пойти на рынок",
                        "location": "Рынок"
                    },
                    "3": {
                        "text": "Пойти в таверну",
                        "location": "Таверна"
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
                        "text": "Вернуться на главную площадь",
                        "location": "Деревня"
                    }
                }
            },
            "Рынок": {
                "usage": "Вы пришли на рынок. В какой магазин вы пойдёте?",
                "options": {
                    "1": {
                        "text": "Оружейная лавка",
                        "location": "Лавка оружия"
                    },
                    # "2": {
                    #     "text": "Лавка с заклинаниями",
                    #     "location": "Лавка заклинаний"
                    # },
                    "2": {
                        "text": "Алхимическая лавка",
                        "location": "Лавка зелий"
                    },
                    "3": {
                        "text": "Вернуться на главную площадь",
                        "location": "Деревня"
                    }
                }
            },
            "Таверна": {
                "usage": "Как только вы зашли в таверну, в ваших глазах потемнело, а голова резко заболела, но вскоре вам стало легче. Вы заказали себе эль и жареного цыплёнка. На удивление никто даже не обратил на вас внимание.",
                "options": {
                    "1": {
                        "text": "Снять комнату комната",
                        "location": "Таверна"
                    },
                    "2": {
                        "text": "ПОпробовать с кем-то поговорить",
                        "location": "Таверна"
                    },
                    "3": {
                        "text": "Выйти из таверны",
                        "location": "Таверна"
                    }
                }
            },
            # Продолжайте добавлять другие локации по вашей необходимости

            # Добавьте остальные локации аналогичным образом
        }
        self.current_locality = 'Виллоудел'
        self.store_weapons_Willowdale = WeaponStore("Кузнеца Гримма Горновара")
        self.store_potions_Willowdale = PotionStore("Эликсиры и Экстракты")
        self.store_spells_Willowdale = SpellStore("Арканум Магии")
        self.stores_in_locations = {
            "Виллоудел": {
                "weapons": self.store_weapons_Willowdale,
                "potions": self.store_potions_Willowdale,
                "spells": self.store_spells_Willowdale,
            },
            # "Анакрон": {
            #     "weapons": store_weapons,
            #     "potions": store_potions,
            #     "spells": store_spells,
            # }
        }
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Стальной меч", 25, 10, 'Sword2.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Рыцарский меч", 35, 20, 'Sword3.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Одноручный тесак", 50, 30, 'Sword4.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Мифриловый меч", 100, 50, 'Sword5.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Адамантиевый меч", 150, 75, 'Sword6.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Меч Альбиона", 200, 100, 'Sword7.png'))
        
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Хороший посох", 25, 10, 'Staff2.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Продвинутый посох", 35, 20, 'Staff3.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Рыцарский посох", 50, 30, 'Staff4.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Мифриловый посох", 100, 50, 'Staff5.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Кристалический посох", 150, 75, 'Staff6.png'))
        self.stores_in_locations["Виллоудел"]["weapons"].add_item(Sword("Посох Альбиона", 200, 100, 'Staff7.png'))

        self.stores_in_locations["Виллоудел"]["potions"].add_item(HpPotion("Малое зелье здоровья", 50, 3, 'HpPotion1.png'))
        self.stores_in_locations["Виллоудел"]["potions"].add_item(HpPotion("Среднее зелье здоровья", 100, 5, 'HpPotion2.png'))
        self.stores_in_locations["Виллоудел"]["potions"].add_item(HpPotion("Большое зелье здоровья", 200, 8, 'HpPotion3.png'))
        self.stores_in_locations["Виллоудел"]["potions"].add_item(ManaPotion("Малое зелье маны", 50, 3, 'ManaPotion1.png'))
        self.stores_in_locations["Виллоудел"]["potions"].add_item(ManaPotion("Среднее зелье маны", 100, 5, 'ManaPotion2.png'))
        self.stores_in_locations["Виллоудел"]["potions"].add_item(ManaPotion("Большое зелье маны", 200, 8, 'ManaPotion3.png'))
        
        # self.stores_in_locations["Виллоудел"]["spells"].add_item(Sword("Железный меч", 30, 1))
        # self.stores_in_locations["Виллоудел"]["spells"].add_item(Sword("Бронзовый меч", 30, 1))
        # self.stores_in_locations["Виллоудел"]["spells"].add_item(Sword("Стальной меч", 30, 1))
                
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
        self.send_button.setIcon(QIcon("Images/send.png"))
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
        self.stats_window.print_text_signal.connect(self.print_queue)

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
                cursor = self.text_input.textCursor()
                cursor.insertBlock()
                self.text_input.setTextCursor(cursor)
            else:
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
            hero_color = 'ffffff'
            if self.hero.race == 'Human':
                hero_color = '#00237d'
            elif self.hero.race == 'Elf':
                hero_color = '#005905'
            elif self.hero.race == 'Dwarf':
                hero_color = '#611e0c'
            self.print_text(message, hero_color)

            if(self.game_state == 1):
                self.create_hero(text)
            if(self.game_state == 2):
                self.game_process(text)
            if(self.game_state == 3):
                self.story(text)

            if text == '/txt':
                with open("Stories/story.txt", "w") as file:
                    file.write(self.game_story)
                    self.print_text("История успешно создана в папку /Stories")

            self.text_input.clear()
            self.text_input.setFocus()

            # self.opacity_animation.start()

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
        elif self.game_progress == 3:
            self.store(input)
        elif self.game_progress == 4:
            self.guild(input)
        else:
            current_location = self.locations_state["current_location"]
            self.display_location(current_location)
            self.game_progress = 1 

    def fight(self, input):
        self.stats_window.update_stats()
        if self.fight_progress == 0:
            if input == '1':
                if self.hero.hero_class == 'Fighter': self.print_text('Выберите приём\n\t    Техники:')
                if self.hero.hero_class == 'Wizard': self.print_text('Выберите заклинание\n\t    Заклинания:')
                for spell in self.hero.techniques:
                    self.print_text(f"\t{spell['index']}. {spell['name']}")
                    self.print_text(self.hero.spell_complexity(spell))
                self.print_text("")
                self.fight_progress = 1
            elif input == '2':
                self.print_text('Бросьте кубик')
                self.is_roll = True
                self.fight_progress = -1
            elif input == '3':
                self.print_text('Вы решаете дать разбойнику часть своих денег.')
                self.print_text("Разбойник: 'Хороший выбор, теперь ты можешь идти своей дорогой. Но не забывай, это наша территория.'\n", "#940000")
                self.hero.money -= 5
                self.fight_progress = 0
                self.game_progress = 1 
                self.locations_state["current_location"] = 'Лес'
                self.display_location(self.locations_state["current_location"])
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
            self.print_text(self.hero.attack(input, self.select_techniques, self.enemy))
            self.print_text(f"У врага осталось {self.enemy.health} здоровья.")
            if self.enemy.health > 0:
                self.print_text('\nВраг разозлился и готов атаковать. Защищайтесь!')
                self.print_text('Бросьте кубик')
                self.is_roll = True
                self.fight_progress = 3
            else:
                self.print_text('\nВраг повержен')
                self.print_text(f'+{self.enemy.exp} exp')
                self.hero.exp += self.enemy.exp
                if self.hero.exp >= self.hero.exp_to_next_level:
                    self.print_text('Поздравляем с повышением уровня!')
                    self.print_text(self.hero.level_up())
                self.locations_state["current_location"] = 'Лес'
                self.display_location(self.locations_state["current_location"])
                self.is_roll = False
                self.fight_progress = 0
                self.game_progress = 1 
        elif self.fight_progress == 3:
            print(self.hero.hp)
            self.print_text(self.enemy.attack(self.hero, input))
            self.stats_window.update_stats()
            if self.hero.hp == 0:
                self.game_state = 0
                self.print_text("Не выдержав атаки, вы закрыли глаза. Вновь открыв их, вы уже лежали в луже крови, чувствуя, как жизненная энергия медленно покидает ваше тело. \n \n«Это была славная жизнь...» \n \nЭто конец.")
                return

            if self.hero.hero_class == 'Fighter': self.print_text('\nВаша очередь атаковать, выберите приём\n\t    Техники:')
            if self.hero.hero_class == 'Wizard': self.print_text('\nВаша очередь атаковать, выберите заклинание\n\t    Заклинания:')
            for spell in self.hero.techniques:
                self.print_text(f"\t{spell['index']}. {spell['name']}")
                self.print_text(self.hero.spell_complexity(spell))
            self.print_text("")
            self.is_roll = False
            self.fight_progress = 1
        elif self.fight_progress == -1:
            print(input)
            self.print_text(self.enemy.escape_attack(self.hero, input))
            self.stats_window.update_stats()
            if self.hero.hp == 0:
                self.game_state = 0
                self.print_text("Не выдержав атаки, вы закрыли глаза. Вновь открыв их, вы уже лежали в луже крови, чувствуя, как жизненная энергия медленно покидает ваше тело. \n \n«Всё таки как же обидно умереть от удара в спину...» \n \nЭто конец.")
                return
            self.locations_state["current_location"] = 'Лес'
            self.display_location(self.locations_state["current_location"])
            self.is_roll = False
            self.fight_progress = 0
            self.game_progress = 1
        self.stats_window.update_stats()
        
    # def fight(self, input):
    #     self.stats_window.update_stats()
    #     if self.fight_progress == 0:
    #         if input == '1':
    #             if self.hero.hero_class == 'Fighter': self.print_text('Выберите приём\n\t    Техники:')
    #             if self.hero.hero_class == 'Wizard': self.print_text('Выберите заклинание\n\t    Заклинания:')
    #             for spell in self.hero.techniques:
    #                 self.print_text(f"\t{spell['index']}. {spell['name']}")
    #                 self.print_text(self.hero.spell_complexity(spell))
    #             self.print_text("")
    #             self.fight_progress = 1
    #         elif input == '2':
    #             self.print_text('Бросьте кубик')
    #             self.is_roll = True
    #             self.fight_progress = -1

    def display_location(self, location):
        if location == "тёмный лес":
            choice = random.randint(1, 10)
            if choice < 5:
                self.print_text("В тёмном лесу, где кроны деревьев не пропускали свет из за кустов выскочил гоблин. Его зеленая кожа пылала яростью, и острый клинок был готов к битве. Что вы делаете? \n 1.Напасть на гоблина \n 2.Попытаться убежать из леса\n")
                self.enemy = Goblin()
                self.count_g += 1
            elif choice < 9:
                self.print_text("Идя по лесу и оставаясь настороже, вы наслаждаетесь спокойствием, когда вдруг появляется незваный гость. Разбойник с банданой на лице и кинжалом в руке выходит на тропу.")
                self.print_text("Разбойник: 'Эй, зря ты зашёл на нашу территорию, с тебя 5 бронзовых.'", "#940000")
                self.print_text("Разбойник: 'Ну что, дорогу платишь? '", "#940000")
                if self.hero.money >= 5: self.print_text("Что вы делаете? \n 1.Напасть на разбойника \n 2.Попытаться убежать из леса \n 3.Дать разбойнику 5 бронзовых монет\n")
                else: self.print_text("Что вы делаете? \n 1.Напасть на разбойника \n 2.Попытаться убежать из леса\n")
                self.enemy = Robber()
                self.count_r += 1
            else:
                self.print_text("Идя по лесу вы вдруг слышите громкий и ужасающий рык. Не успело пройти и пары секунд, как вы увидели, что из-за деревьев выходит огромный огр с дубиной в руке. Похоже, он настроен враждебно. Что вы делаете? \n 1.Напасть на Огра \n 2.Попытаться убежать из леса\n")
                self.enemy = Ogre()
                self.count_o += 1
            self.game_progress = 2
        elif "Лавка" in location:
            self.store_progress = 1
            self.game_progress = 3
            self.store(location)
        elif "Таверна" in location:
            self.print_text("Закрыто.")
            self.locations_state["current_location"] = 'Деревня'
            self.display_location(self.locations_state["current_location"])
        elif "Гильдия" in location:
            self.guild_progress = 1
            self.game_progress = 4
            self.guild(location)
        else:
            location_data = self.locations.get(location)

            usage = location_data["usage"]
            options = location_data.get("options")

            message = f"{usage}\n"
            if options:
                for option, option_data in options.items():
                    message += f"{option}. {option_data['text']}\n"

            self.print_text(message)

    def store(self, input):
        if self.store_progress == 1:
            if 'оружия' in input: 
                type = 'weapons'
                self.print_text('Вы пришли в оружейную лавку')
                self.print_text('Кузнец: Приветствую путник, у меня лучшее оружие во всей деревне!', '#691217')

                self.print_text(self.stores_in_locations[self.current_locality][type].list_items(self.hero.hero_class))
                self.print_text('\t7.Вернуться на рынок')
                self.print_text('\nКузнец: Что-то приглянулось?', '#691217')
                self.store_progress = 2
            if 'зелий' in input: 
                type = 'potions'
                self.print_text('Вы пришли в алхимическую лавку')
                self.print_text('Владелец лавки: Добро пожаловать, у меня очень большой ассортимент, какое зелье ты хочешь купить?', '#7e0091')
                
                self.print_text(self.stores_in_locations[self.current_locality][type].list_items())
                self.print_text('\t7.Вернуться на рынок')
                self.store_progress = 6
            self.select_store = self.stores_in_locations[self.current_locality][type]
            #     self.print_text('Вы пришли в лавку заклинаний')
            #     self.print_text('Торговец заклинаниеми: Добро пожаловать в ')
            # self.print_text(self.stores_in_locations[self.current_locality][type].list_items())
            # self.print_text('\t7.Вернуться на рынок')
        elif self.store_progress == 2:
            if input == '7':
                self.game_progress = 1 
                self.locations_state["current_location"] = 'Рынок'
                self.display_location(self.locations_state["current_location"])
            else:
                if self.hero.hero_class == "Fighter":
                    if self.hero.money >= self.select_store.items[int(input) - 1].price:
                        self.hero.money -= self.select_store.items[int(input) - 1].price
                        self.hero.weapon = self.select_store.items[int(input) - 1]
                        self.print_text('Кузнец: Спасибо за покупку, удачи в твоих приключениях!', '#691217')
                        self.stats_window.update_stats()
                        self.game_progress = 1 
                        self.locations_state["current_location"] = 'Рынок'
                        self.display_location(self.locations_state["current_location"])
                    else:
                        self.print_text('Недостаточно денег')
                if self.hero.hero_class == "Wizard":
                    if self.hero.money >= self.select_store.items[int(input) + 5].price:
                        self.hero.money -= self.select_store.items[int(input) + 5].price
                        self.hero.weapon = self.select_store.items[int(input) + 5]
                        self.print_text('Кузнец: Спасибо за покупку, удачи в твоих приключениях!', '#691217')
                        self.stats_window.update_stats()
                        self.game_progress = 1 
                        self.locations_state["current_location"] = 'Рынок'
                        self.display_location(self.locations_state["current_location"])
                    else:
                        self.print_text('Недостаточно денег')
        elif self.store_progress == 6:
            if input == '7':
                self.game_progress = 1 
                self.locations_state["current_location"] = 'Рынок'
                self.display_location(self.locations_state["current_location"])
            else:
                if self.hero.money >= self.select_store.items[int(input) - 1].price:
                    self.hero.money -= self.select_store.items[int(input) - 1].price
                    self.hero.inventory.append(self.select_store.items[int(input) - 1])
                    self.print_text('Владелец лавки: Спасибо за покупку, удачи в твоих приключениях!', '#7e0091')
                    self.stats_window.update_stats()
                    self.game_progress = 1 
                    self.locations_state["current_location"] = 'Рынок'
                    self.display_location(self.locations_state["current_location"])
                else:
                    self.print_text('Недостаточно денег')
            
    def guild(self, input):
        if self.guild_progress == 1:
            self.print_text('Добро пожаловать в гильдию авантюристов')
            self.print_text('Сейчас доступно 3 задания: \t\n 1.Истребить 10 гоблинов. \nНаграда: 50 Бронзовых монет\n \t\n 2.Победить 5 разбойников. \nНаграда: 100 Бронзовых монет\n \t\n 1.Убить 2 огра. \nНаграда: 300 Бронзовых монет\n ')
            if self.count_g >= 10:
                self.print_text(f'Спасибо за вашу помощь, вот ваша награда\n+{50 * (self.count_g // 10)} Бронзовых монет')
                self.hero.money += 50 * (self.count_g // 10)
                self.count_g -= 10
            if self.count_r >= 5:
                self.print_text(f'Спасибо за вашу помощь, вот ваша награда\n+{100 * (self.count_r // 5)} Бронзовых монет')
                self.hero.money += 100 * (self.count_r // 5)
                self.count_r -= 5
            if self.count_o >= 2:
                self.print_text(f'Спасибо за вашу помощь, вот ваша награда\n+{300 * (self.count_o // 2)} Бронзовых монет')
                self.hero.money += 300 * (self.count_o // 2)
                self.count_o -= 2
            self.print_text('1. Вернуться на площадь')
            self.guild_progress = 2
        if self.guild_progress == 2:
            if input == '1':
                self.game_progress = 1 
                self.locations_state["current_location"] = 'Деревня'
                self.display_location(self.locations_state["current_location"])
        self.stats_window.update_stats()

    def story(self, input):
        pass 

    def create_hero(self, input):
        if self.create_progress == 0:
            # self.hero.name = "Хиро"
            # self.hero.hero_class = "Fighter"
            # self.hero.race = "Human"
            self.hero.name = "e'Qwerty"
            self.hero.hero_class = "Wizard"
            self.hero.race = "Elf"
            self.hero.weapon = Staff('обычный посох', 19, 5, 'staff1.png')
            self.hero.add_random_spells(3, self.hero.hero_class)
            self.hero.strength = 10
            self.hero.dexterity = 10
            self.hero.constitution = 10
            self.hero.intelligence = 10
            self.hero.wisdom = 10
            self.hero.charisma = 10
            self.hero.max_hp = 10 * self.hero.constitution
            self.hero.hp = 100
            self.hero.max_mana = (self.hero.constitution + self.hero.intelligence + (self.hero.wisdom * 2) + self.hero.charisma) * 5 + 100
            self.hero.mana = self.hero.max_mana
            self.create_progress = 9
            self.hero.inventory.append(HpPotion("Малое зелье здоровья", 50, 3, 'HpPotion1.png'))
            self.hero.inventory.append(HpPotion("Среднее зелье здоровья", 100, 5, 'HpPotion2.png'))
            self.hero.inventory.append(HpPotion("Большое зелье здоровья", 200, 8, 'HpPotion3.png'))
            self.hero.inventory.append(ManaPotion("Малое зелье маны", 50, 3, 'ManaPotion1.png'))
            self.hero.inventory.append(ManaPotion("Среднее зелье маны", 100, 5, 'ManaPotion2.png'))
            self.hero.inventory.append(ManaPotion("Большое зелье маны", 200, 8, 'ManaPotion3.png'))
            print(self.hero.inventory)
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
                self.hero.weapon = Staff('обычный посох', 19, 10, 'staff1.png')
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
                self.hero.strength = int(input)
            elif self.hero.race == 'Elf':
                self.hero.strength = int(input * 0.8)
            elif self.hero.race == 'Dwarf':
                self.hero.strength = int(input * 1.2)
            self.is_roll = True
            self.print_text("Бросьте кубик, чтобы определить ловкость вашего персонажа")
            self.create_progress = 5
        elif self.create_progress == 5:
            if self.hero.race == 'Human':
                self.hero.dexterity = int(input)
            elif self.hero.race == 'Elf':
                self.hero.dexterity = int(input * 1.2)
            elif self.hero.race == 'Dwarf':
                self.hero.dexterity = int(input * 0.8)
            self.print_text("Бросьте кубик, чтобы определить телосложение вашего персонажа")
            self.is_roll = True
            self.create_progress = 6
        elif self.create_progress == 6:
            if self.hero.race == 'Human':
                self.hero.constitution = int(input)
            elif self.hero.race == 'Elf':
                self.hero.constitution = int(input * 0.8)
            elif self.hero.race == 'Dwarf':
                self.hero.constitution = int(input * 1.2)
            self.hero.max_hp = 10 * self.hero.constitution
            self.hero.hp = self.hero.max_hp
            self.print_text("Бросьте кубик, чтобы определить интеллект вашего персонажа")
            self.is_roll = True
            self.create_progress = 7
        elif self.create_progress == 7:
            if self.hero.race == 'Human':
                self.hero.intelligence = int(input)
            elif self.hero.race == 'Elf':
                self.hero.intelligence = int(input * 1.2)
            elif self.hero.race == 'Dwarf':
                self.hero.intelligence = int(input * 0.8)
            self.print_text("Бросьте кубик, чтобы определить мудрость вашего персонажа")
            self.is_roll = True
            self.create_progress = 8
        elif self.create_progress == 8:
            if self.hero.race == 'Human':
                self.hero.wisdom = int(input)
            elif self.hero.race == 'Elf':
                self.hero.wisdom = int(input * 1.2)
            elif self.hero.race == 'Dwarf':
                self.hero.wisdom = int(input)
            self.print_text("Бросьте кубик, чтобы определить харизму вашего персонажа")
            self.is_roll = True
            self.create_progress = 9
        elif self.create_progress == 9:
            if self.hero.race == 'Human':
                self.hero.charisma = int(input)
            elif self.hero.race == 'Elf':
                self.hero.charisma = int(input)
            elif self.hero.race == 'Dwarf':
                self.hero.charisma = int(input)
            self.hero.max_mana = (self.hero.constitution + self.hero.intelligence + (self.hero.wisdom * 2) + self.hero.charisma) * 5 + 100
            self.hero.mana = self.hero.max_mana
            self.print_text("Ваш персонаж успешно создан")
            self.is_roll = False
            self.game_state = 2
            # self.print_text(self.hero.info())
            self.stats_window.update_stats()
            # if self.hero.hero_class == 'Fighter': self.print_text('\n\t\t\tТехники:')
            # if self.hero.hero_class == 'Wizard': self.print_text('\n\t\t\tЗаклинания:')
            # for spell in self.hero.techniques:
            #     self.print_text(f"\n  {spell['index']}.  {spell['name']}: {spell['description']}")
            #     self.print_text(self.hero.spell_complexity(spell))
            # self.print_text("")
            self.hero.charisma = 10
            self.game_process('')

    def roll(self):
        global dice_result
        if self.game_state == 1:
            if self.create_progress > 2:
                self.create_hero(dice_result)
        if self.game_state == 2:
            if self.fight_progress != 0:
                self.fight(dice_result)


    # def print_text(self, message):
    #     text_format = QTextCharFormat()
    #     text_format.setFontWeight(QFont.Bold)
    #     text_format.setFontPointSize(12)

    #     cursor = self.message_display.textCursor()
    #     cursor.setCharFormat(text_format)
    #     cursor.insertText(message + '\n')  # Используйте append() для автопрокрутки

    #     # Прокручиваем QTextEdit вниз
    #     scroll_bar = self.message_display.verticalScrollBar()
    #     scroll_bar.setValue(scroll_bar.maximum())

    def print_queue(self):  # По умолчанию черный цвет
        while self.stats_window.text_queue != []:
            queue_list = self.stats_window.text_queue
            for queue in queue_list:
                self.print_text(queue)
                self.stats_window.text_queue.remove(queue)

    def print_text(self, message, color="black"):  # По умолчанию черный цвет
        self.game_story += message
        self.message_queue.append((message, QColor(color)))
        if len(self.message_queue) == 1:
            self.process_message_queue()

    def process_message_queue(self):
        if self.message_queue:
            message, color = self.message_queue[0]
            text_format = QTextCharFormat()
            text_format.setFontWeight(QFont.Bold)
            text_format.setFontPointSize(10)
            if color != QColor("black"): text_format.setForeground(color)  # Устанавливаем цвет текста

            cursor = self.message_display.textCursor()
            cursor.setCharFormat(text_format)

            def append_message(message, cursor, index=0):
                if index < len(message):
                    cursor.insertText(message[index])
                    self.scroll_to_bottom()
                    QTimer.singleShot(1, lambda: append_message(message, cursor, index + 1))
                else:
                    cursor.insertText('\n')
                    self.scroll_to_bottom()
                    self.message_queue.pop(0)
                    self.process_message_queue()

            append_message(message, cursor)

    def scroll_to_bottom(self):
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
    def __init__(self, name, damage, price, image):
        self.name = name
        self.damage = (damage - 5, damage + 5)  # Диапазон урона
        self.weight = 40  # Вес
        self.type = "Меч"
        self.price = price
        self.image = image


class Hammer:
    def __init__(self, name, damage, price, image):
        self.name = name  # Название оружия
        self.damage = (damage - 8, damage + 8)  # Диапазон урона
        self.weight = 50  # Вес
        self.type = "Молот"
        self.price = price
        self.image = image


class Staff:
    def __init__(self, name, damage, price, image):
        self.name = name  # Название оружия
        self.damage = (damage - 10, damage + 10)  # Диапазон урона
        self.weight = 30  # Вес
        self.type = "Посох"
        self.price = price
        self.image = image
    

class Potion:
    def __init__(self, name, price, image):
        self.name = name
        self.price = price
        self.image = image

    def use(self, character):
        pass


class HpPotion(Potion):
    def __init__(self, name, effect, price, image):
        super().__init__(name, price, image)
        self.effect = effect

    def use(self, character):
        character.hp += self.effect
        if character.hp > character.max_hp:
            character.hp = character.max_hp
        out = f"Вы выпили {self.name}. Внезапно, ваши раны начали заживать, а усталость в миг исчезла. \nВосстановлено {self.effect} здоровья."
        return out


class ManaPotion(Potion):
    def __init__(self, name, effect, price, image):
        super().__init__(name, price, image)
        self.effect = effect

    def use(self, character):
        character.mana += self.effect
        if character.mana > character.max_mana:
            character.mana = character.max_mana
        out = f"Вы выпили {self.name} и в миг почувствовали, как магическая энергия вновь наполнила вас. \nВосстановлено {self.effect} маны."
        return out


class Store:
    def __init__(self, name):
        self.name = name
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    
class WeaponStore(Store):
    def __init__(self, name):
        super().__init__(name)

    def list_items(self, hero_class):
        out = 'Ассортимент'
        i = 1
        for item in self.items:
            if "Staff" in item.image and hero_class == "Wizard":
                out += f"\n\t{i}. Название: {item.name}, \n\tТип: {item.type}, \n\tДиапазон урона: {item.damage[0]}-{item.damage[1]}, \n\tВес: {item.weight}\n\t    Цена: {item.price}\n"
                i += 1
            if "Sword" in item.image and hero_class == "Fighte":
                out += f"\n\t{i}. Название: {item.name}, \n\tТип: {item.type}, \n\tДиапазон урона: {item.damage[0]}-{item.damage[1]}, \n\tВес: {item.weight}\n\t    Цена: {item.price}\n"
                i += 1
        return out
    

class PotionStore(Store):
    def __init__(self, name):
        super().__init__(name)

    def list_items(self):
        out = 'Ассортимент зелий'
        i = 1
        for item in self.items:
            if 'здоровья' in item.name: out += f"\n\t{i}. Название: {item.name} \n\t    Эффект: +{item.effect} Hp \n\t    Цена: {item.price}\n"
            elif 'маны' in item.name: out += f"\n\t{i}. Название: {item.name} \n\t    Эффект: +{item.effect} Маны \n\t    Цена: {item.price}\n"
            i += 1
        return out
    

class SpellStore(Store):
    def __init__(self, name):
        super().__init__(name)

    def list_items(self):
        out = 'Свитки с заклинаниями'
        i = 1
        for item in self.items:
            out += f"\n\t{i}. Название: {item.name}, \n\tТип: {item.type}, \n\tДиапазон урона: {item.damage[0]}-{item.damage[1]}, \n\tВес: {item.weight}\n"
            i += 1
        return out
    

class WeaponEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Sword):
            return {
                'name': obj.name,
                'damage': obj.damage,
                'weight': obj.weight,
                'type': obj.type,
                'price': obj.price,
                'image': obj.image
            }
        elif isinstance(obj, Staff):
            return {
                'name': obj.name,
                'damage': obj.damage,
                'weight': obj.weight,
                'type': obj.type,
                'price': obj.price,
                'image': obj.image
            }
        return super().default(obj)


class PotionEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HpPotion):
            return {
                'name': obj.name,
                'effect': obj.effect,
                'price': obj.price,
                'image': obj.image
            }
        if isinstance(obj, ManaPotion):
            return {
                'name': obj.name,
                'effect': obj.effect,
                'price': obj.price,
                'image': obj.image
            }
        return super().default(obj)


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
    inventory = []

    def __init__(self):
        self.name = "default"
        self.hero_class = 'default'
        self.race = 'default'
        self.hp = 100
        self.mana = 100
        self.weapon = Sword('обычный меч', 15, 5, 'Sword1.png')
        self.money = 100
        self.exp = 0
        self.exp_to_next_level = 1000
        self.level = 1
        
    def attack(self, dice, select_index, enemy):
        for spell in self.techniques:
            if spell['index'] == select_index:
                select_techniques = spell
        if self.mana >= (select_techniques['complexity'] + select_techniques['damage'] - 1) * 10:
            if dice >= select_techniques['complexity'] * 2:
                self.mana -= (select_techniques['complexity'] + select_techniques['damage'] - 1) * 10
                if self.hero_class == 'Fighter':
                    weapon_power = random.randint(self.weapon.damage[0], self.weapon.damage[1])
                    hero_power = random.randint(int(self.strength / 2), self.strength) + self.intelligence // 10 * self.level
                    damage = int((weapon_power + hero_power) * (float(dice) / 10)) 
                if self.hero_class == 'Wizard':
                    weapon_power = random.randint(self.weapon.damage[0], self.weapon.damage[1])
                    hero_power = random.randint(int(self.intelligence / 2), self.intelligence) + self.strength // 10 * self.level
                    damage = int((weapon_power + hero_power) * (float(dice) / 10)) 
                damage = int((damage / 2) * (select_techniques['complexity'] + 1) * (select_techniques['damage'] / 10 * 1.5 + 1))
                if select_techniques['name'] == 'Небесное благословление':
                    danage += 200
                enemy.take_damage(damage)
                return select_techniques['usage'] + f' Враг теряет {damage} здоровья.'
            else:
                return 'Магическая сила не отозвалась и ваше заклинание сорвалось.'
        else:
            return 'Похоже, у вас закночилась мана, пришло время отдохнуть и восполнить запасы магической энергии, ну или просто выпить зелье.'

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
    
    def save(self):
        conn = sqlite3.connect('hero_database.db')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hero (
                id INTEGER,
                name TEXT,
                hero_class TEXT,
                race TEXT,
                hp INTEGER,
                max_hp INTEGER,
                mana INTEGER,
                max_mana INTEGER,
                strength INTEGER,
                dexterity INTEGER,
                constitution INTEGER,
                intelligence INTEGER,
                wisdom INTEGER,
                charisma INTEGER,
                spells_quantity INTEGER,
                spell_count INTEGER,
                money INTEGER,
                exp INTEGER,
                exp_to_next_level INTEGER,
                level INTEGER,
                inventory JSON,
                weapon JSON,
                techniques JSON
            )
        ''')

        inventory_json = json.dumps(self.inventory, cls=PotionEncoder)
        weapon_json = json.dumps(self.weapon, cls=WeaponEncoder)
        techniques_json = json.dumps(self.techniques)

        if self.is_table_empty():
            cursor.execute('''
                REPLACE INTO hero VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                1,
                self.name,
                self.hero_class,
                self.race,
                self.hp,
                self.max_hp,
                self.mana,
                self.max_mana,
                self.strength,
                self.dexterity,
                self.constitution,
                self.intelligence,
                self.wisdom,
                self.charisma,
                self.spells_quantity,
                self.spell_count,
                self.money,
                self.exp,
                self.exp_to_next_level,
                self.level,
                inventory_json,
                weapon_json,
                techniques_json
            ))
        else:
            cursor.execute('''
                UPDATE hero
                SET name = ?,
                    hero_class = ?,
                    race = ?,
                    hp = ?,
                    max_hp = ?,
                    mana = ?,
                    max_mana = ?,
                    strength = ?,
                    dexterity = ?,
                    constitution = ?,
                    intelligence = ?,
                    wisdom = ?,
                    charisma = ?,
                    spells_quantity = ?,
                    spell_count = ?,
                    money = ?,
                    exp = ?,
                    exp_to_next_level = ?,
                    level = ?,
                    inventory = ?,
                    weapon = ?,
                    techniques = ?
                WHERE id = "1"
            ''', (
                self.name,
                self.hero_class,
                self.race,
                self.hp,
                self.max_hp,
                self.mana,
                self.max_mana,
                self.strength,
                self.dexterity,
                self.constitution,
                self.intelligence,
                self.wisdom,
                self.charisma,
                self.spells_quantity,
                self.spell_count,
                self.money,
                self.exp,
                self.exp_to_next_level,
                self.level,
                inventory_json,
                weapon_json,
                techniques_json
            ))

        conn.commit()
        conn.close()

    def is_table_empty(self):
        conn = sqlite3.connect('hero_database.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM hero')
        count = cursor.fetchone()[0]

        conn.close()

        return count == 0

    def load(self):
        conn = sqlite3.connect('hero_database.db')
        cursor = conn.cursor()
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT name, hero_class, race, hp, max_hp, mana, max_mana, strength, dexterity, constitution, intelligence, wisdom, charisma, spells_quantity, spell_count, money, exp, exp_to_next_level, level, inventory, weapon, techniques FROM hero")
        row = cursor.fetchall()
        print(row)

        for hero in row:  
            if row is not None:
                self.name = hero[0]
                self.hero_class = hero[1]
                self.race = hero[2]
                self.hp = hero[3]
                self.max_hp = hero[4]
                self.mana = hero[5]
                self.max_mana = hero[6]
                self.strength = hero[7]
                self.dexterity = hero[8]
                self.constitution = hero[9]
                self.intelligence = hero[10]
                self.wisdom = hero[11]
                self.charisma = hero[12]
                self.spells_quantity = hero[13]
                self.spell_count = hero[14]
                self.money = hero[15]
                self.exp = hero[16]
                self.exp_to_next_level = hero[17]
                self.level = hero[18]
                inventory_json = hero[19]
                weapon_json = hero[20]
                techniques_json = hero[21]
                
                
                self.inventory = json.loads(inventory_json)  # Deserializing the JSON string into an array of objects
                self.weapon = json.loads(weapon_json)  # Deserializing the JSON string into an array of objects
                print(self.weapon)
                self.techniques = json.loads(techniques_json)  # Deserializing the JSON string into an array of objects
        
        conn.close()

    def load_spells_from_database(self, table_name):
        connection = sqlite3.connect('hero_database.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name, description, usage, level, complexity, damage FROM {table_name}")
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

        level_1_spells = [spell for spell in spells_data if spell[3] == 1]
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
                'complexity': spell[4],
                'damage': spell[5]
            }
            self.techniques.append(spell_dict)
            out += f"Вы освоили {hero_class} {spell_dict['level']} уровня '{spell_dict['name']}': {spell_dict['description']}\n"
        return out
    
    def add_spell(self):
        if self.hero_class == 'Wizard':
            spells_data = self.load_spells_from_database('spell_book')
        elif self.hero_class == 'Fighter':
            spells_data = self.load_spells_from_database('sword_book')
        else:
            return "Неверный класс героя."

        level_spells = [spell for spell in spells_data if spell[3] == self.level]
        selected_spells = random.sample(level_spells, 1)

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
                'complexity': spell[4],
                'damage': spell[5]
            }
            self.techniques.append(spell_dict)
            out += f"Вы освоили заклинание {spell_dict['level']} уровня '{spell_dict['name']}': {spell_dict['description']}\n"
        return out
    
    def add_curr_spell(self, spell_name):
        if self.hero_class == 'Wizard':
            spells_data = self.load_spells_from_database('spell_book')
        elif self.hero_class == 'Fighter':
            spells_data = self.load_spells_from_database('sword_book')
        else:
            return "Неверный класс героя."

        level_spells = [spell for spell in spells_data if spell[0] == spell_name]
        selected_spells = random.sample(level_spells, 1)

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
                'complexity': spell[4],
                'damage': spell[5]
            }
            self.techniques.append(spell_dict)
            out += f"Вы освоили заклинание {spell_dict['level']} уровня '{spell_dict['name']}': {spell_dict['description']}\n"
        return out

    def get_spell_usage(self, index):
        for spell in self.techniques:
            if spell['index'] == index:
                return spell['usage']
        return "Заклинание не найдено."
    
    def level_up(self):
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level += 1000
        self.max_hp += 100
        self.hp = self.max_hp
        self.max_mana += 100
        self.mana = self.max_mana 
        #main stats
        self.strength += 1
        self.dexterity += 1
        self.constitution += 1
        self.intelligence += 1
        self.wisdom += 1
        self.charisma += 1
        #new spell
        self.level += 1
        return self.add_spell()
    
    def spell_complexity(self, spell):
        mana = (spell['complexity'] + spell['damage'] - 1)
        if mana == 1: complexity = 'Очень низкое'
        elif mana == 2: complexity = 'Низкое'
        elif mana == 3: complexity = 'Ниже среднего'
        elif mana == 4: complexity = 'Среднее'
        elif mana == 5: complexity = 'Выше среднего'
        elif mana == 6: complexity = 'Высокое'
        else: complexity = 'Очень высокое'
        stats = f"\tПотребление маны: {complexity}({mana * 10})"
        if spell['complexity'] == 1: complexity = 'Высокая'
        elif spell['complexity'] == 2: complexity = 'Значительная'
        elif spell['complexity'] == 3: complexity = 'Приемлемая'
        elif spell['complexity'] == 4: complexity = 'Умеренная' 
        elif spell['complexity'] == 5: complexity = 'Невысокая'
        elif spell['complexity'] == 6: complexity = 'Низкая'
        else: complexity = 'Очень низкая'
        stats += f"\n\tВероятность успеха: {complexity}(кубик > {spell['complexity'] * 2})"
        damage = spell['damage'] + spell['complexity']
        if self.level < 3: damage += self.level
        if damage == 2: complexity = 'Очень низкий'
        elif damage == 3: complexity = 'Низкий'
        elif damage == 4: complexity = 'Ниже среднего'
        elif damage == 5: complexity = 'Средний'
        elif damage == 6: complexity = 'Выше среднего'
        elif damage == 7: complexity = 'Высокий'
        else: complexity = 'Очень высокий'
        stats += f"\n\tУрон: {complexity}"
        return stats
    
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
        info += "\n Уровень: " + str(self.level)
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
        # info += "\n\t Hero level: " + str(self.level)
        # info += "\n\t Hero exp: " + str(self.exp)
        return info
    
    def stats(self) :
        # info = "\n       Имя: " + self.name
        info = "================"
        curr_out = 'default'
        if self.hero_class == "Wizard": curr_out = 'Волшебник'
        if self.hero_class == "Fighter": curr_out = 'Воин'
        info += "\n  Класс: " + curr_out
        curr_out = 'default'
        if self.race == "Human": curr_out = 'Человек'
        if self.race == "Elf": curr_out = 'Эльф'
        if self.race == "Dwarf": curr_out = 'Дварф'
        info += "\n  Раса: " + curr_out
        info += "\n  Уровень: " + str(self.level)
        info += "\n\n  Сила: " + str(self.strength)
        info += "\n  Ловкость: " + str(self.dexterity)
        info += "\n  Телосложение: " + str(self.constitution)
        info += "\n  Интеллект: " + str(self.intelligence)
        info += "\n  Мудрость: " + str(self.wisdom)
        info += "\n  Харизма: " + str(self.charisma)
        info += "\n\n  Деньги:\n " + self.format_Money(self.money)
        info += "================"
        return info
    
    def stats_weapon(self) :
        info = "  Название: " + self.weapon.name
        info += "\n  Тип: " + self.weapon.type
        info += "\n  Урон: " + f" от {self.weapon.damage[0]} до {self.weapon.damage[1]}"
        info += "\n  Вес: " + str(self.weapon.weight)
        return info

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
            return "0 бронзовых\n"

        return result
    

class Enemy:
    def __init__(self, name, health=50, damage=5, armor=5, exp=100):
        self.name = name
        self.health = health
        self.damage = damage
        self.armor = armor
        self.exp = exp

    def take_damage(self, damage):
        self.health -= damage + self.armor
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0
    

class Goblin(Enemy):
    def __init__(self, name="Гоблин", health=60, damage=10, armor=0, exp=200):
        super().__init__(name, health, damage, armor, exp)

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
        if dice >= 10:
            return "Стремительно развернувшись, вы начали бежать со всех ног. Вскоре вы выбролись из темного леса, оставив за собой грозную атмосферу и опасность, что скрывалась в его чащах."
        else:
            attack_damage = random.randint(self.damage, self.damage * 3) * 2
            hero.take_damage(attack_damage)
            return f"Вы ринулись вперед, стремясь выбраться из леса, однако внезапно гоблин запрыгнул на вас и вонзил свой нож вам в спину нанеся {attack_damage} урона."
        

class Ogre(Enemy):
    def __init__(self, name="Огр", health=300, damage=35, armor=15, exp=1000):
        super().__init__(name, health, damage, armor, exp)

    def attack(self, hero, dice):
        choose_attack = random.randint(1, 2)
        if choose_attack == 1:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Огр делает мощный мах топором, но вы ловко блокируете его атаку. Ваш щит защищает вас от урона."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage)
                hero.take_damage(attack_damage)
                return f"Огр делает мощный мах топором, острый топор Огра вонзается в ваши доспехи, нанося вам {attack_damage} урона."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 2
                hero.take_damage(attack_damage)
                return f"Огр атакует с неистовой яростью, разрубая вашу броню сильнейшим ударом и нанося вам {attack_damage} урона."
        elif choose_attack == 2:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Огр кидает камень, но промахивается. Камень пролетает мимо вас, не представляя опасности."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage)
                hero.take_damage(attack_damage)
                return f"Огр бросает камень, который попадает в вас. Вы чувствуете острую боль, когда камень ударяется о вас, нанося вам {attack_damage} урона."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 3
                hero.take_damage(attack_damage)
                return f"Огр метает огромный камень с неистовой силой и меткостью. Камень попадает в вас и разбивает ваши кости, нанося вам {attack_damage} урона."
               
    def escape_attack(self, hero, dice):
        if dice >= 10:
            return "Стремительно развернувшись, вы начали бежать со всех ног. Вскоре вы выбролись из темного леса, оставив за собой грозную атмосферу и опасность, что скрывалась в его чащах."
        else:
            attack_damage = random.randint(self.damage, self.damage * 3) * 2
            hero.take_damage(attack_damage)
            return f"Вы ринулись вперед, стремясь выбраться из леса, однако не учли силу врага. Огр метнул в вас огромный камень, попав прямо вам в спину, нанеся {attack_damage} урона."
        
        
class Robber(Enemy):
    def __init__(self, name="Разбойник", health=150, damage=20, armor=5, exp=500):
        super().__init__(name, health, damage, armor, exp)

    def attack(self, hero, dice):
        choose_attack = random.randint(1, 3)
        if choose_attack == 1:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Разбойник пытается вас ударить кинжалом, но вы ловко уклоняетесь, и его атака промахивается. Вы своими волосами ощущаете ветер от проходящего мимо кинжала."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage)
                hero.take_damage(attack_damage)
                return f"Разбойник атакует вас кинжалом, который ранит вас, вы теряете {attack_damage} здоровья."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 2
                hero.take_damage(attack_damage)
                return f"Разбойник выпив загадочное зелье, нападает с невероятной яростью и скоростью, его кинжал проникает в вашу броню, сильно раня вас и нанося {attack_damage} урона."
        elif choose_attack == 2:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Разбойник метает маленький нож, но его бросок не точен. Нож проходит мимо вас, не представляя угрозы."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage)
                hero.take_damage(attack_damage)
                return f"Разбойник метает нож, который попадает в вас. Вы чувствуете острую боль, когда нож задевает вас, вы теряете {attack_damage} здоровья."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 3
                hero.take_damage(attack_damage)
                return f"Разбойник метко бросает несколько ножей, которые точно попадают в вас и наносят {attack_damage} урона."
        elif choose_attack == 3:
            if dice >= 15:
                attack_damage = 0
                hero.take_damage(attack_damage)
                return "Разбойник начинает атаковать вас быстрыми ударами кинжала, но ваше умение и проворство позволяют вам избежать его ударов."
            elif dice >= 5:
                attack_damage = random.randint(self.damage // 2, self.damage)
                hero.take_damage(attack_damage)
                return f"Разбойник атакует вас быстрыми ударами кинжала, каждый удар находит свою цель. Вы чувствуете, как кинжалы царапают вас, вы теряете {attack_damage} здоровья."
            else:
                attack_damage = random.randint(self.damage // 2, self.damage) * 4
                hero.take_damage(attack_damage)
                return f"Разбойник выпив загадочное зелье, нападает с нескончаемой агрессией и скоростью, каждый удар находит свою цель. Его удары проникают глубоко в ваши ткани, нанося {attack_damage} урона."

    def escape_attack(self, hero, dice):
        if dice >= 10:
            return "Стремительно развернувшись, вы начали бежать со всех ног. Вскоре вы выбролись из темного леса, оставив за собой грозную атмосферу и опасность, что скрывалась в его чащах."
        else:
            attack_damage = random.randint(self.damage, self.damage * 3) * 2
            hero.take_damage(attack_damage)
            return f"Вы ринулись вперед, стремясь выбраться из леса, однако разбойник не сдался. Он метко метнул свой кинжал, попав вам в спину, нанеся {attack_damage} урона."

def create_dialog(title, message):
    app = QApplication(sys.argv)

    # Создание диалогового окна
    dialog = QMessageBox()
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setStandardButtons(QMessageBox.Ok)
    dialog.exec_()

class Inventory(QDialog):
    windowClosed = pyqtSignal()
    def __init__(self, hero, StatsWindow):
        super().__init__()
        self.hero = hero
        self.StatsWindow = StatsWindow
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Инвентарь')
        self.setGeometry(100, 100, 1200, 520)  # Устанавливаем размер окна
        
        self.main_layout = QGridLayout()

        # Добавим блок с информацией о текущем оружии
        self.weapon_info_layout = QVBoxLayout()
        self.weapon_label = QLabel("Оружие:")
        self.weapon_label.setAlignment(Qt.AlignCenter)
        self.weapon_label.setStyleSheet("""
            color: white; 
            font-weight: bold;
            font-size: 20
        """)

        weapon_image_label = QLabel()
        weapon_image_label.setFixedSize(200, 468)  # Растягиваем прямоугольник 1:3
        weapon_image = QPixmap(f'Images/weapons/{self.hero.weapon.image}')
        weapon_image_label.setPixmap(weapon_image.scaled(200, 468, Qt.KeepAspectRatio))
        weapon_image_label.setAlignment(Qt.AlignCenter)
        # weapon_image_label.setStyleSheet("border-image: url('Images/InventoryBackgroundWeapon.png') 0 0 0 0 stretch stretch;")  # Устанавливаем цвет фона
        weapon_image_label.setStyleSheet("""
            QWidget {
                background-color: #9e7654;
                border-radius: 10px;
            }
        """) 

        image_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        weapon_image_label.setSizePolicy(image_policy)

        self.weapon_info_label = QLabel(self.hero.stats_weapon())
        
        self.weapon_info_label.setStyleSheet("""
            color: white; 
            font-weight: bold;
            border-image: url('Images/InventoryBackgroundWeapon_H.png') 0 0 0 0 stretch stretch;
            font-size: 20;
            padding: 10px;
        """)

        # self.weapon_info_layout.addWidget(weapon_label)
        self.weapon_info_layout.addWidget(weapon_image_label)
        self.weapon_info_layout.addWidget(self.weapon_info_label)

        self.inventory_layout = QGridLayout()
        for row in range(4):  # Создаем 6 строк
            for col in range(6):  # В каждой строке создаем 3 квадрата
                if len(self.hero.inventory) > row * 6 + col:
                    item = self.hero.inventory[row * 6 + col]
                    item_label = QPushButton()  # Изменяем QLabel на QPushButton
                    item_label.setIcon(QIcon(f'Images/{item.image}'))
                    item_label.setIconSize(QSize(80, 80))
                    item_label.setFixedSize(130, 130)  # Устанавливаем размер 100x100 пикселей
                    item_label.setStyleSheet("border-image: url('Images/InventoryBackground.png') 0 0 0 0 stretch stretch;")  # Устанавливаем цвет фона
                    item_label.setStyleSheet(
                        "QPushButton {"
                        "border-image: url('Images/InventoryBackground.png') 0 0 0 0 stretch stretch;"
                        "}"
                        "QPushButton:pressed {"
                        "border: 2px solid red;"
                        "}"
                    )
                    item_label.clicked.connect(lambda _, item=item: self.use_item(item))
                    self.inventory_layout.addWidget(item_label, row, col)
                else:
                    item_label = QLabel()
                    item_label.setFixedSize(130, 130)  # Устанавливаем размер 100x100 пикселей
                    item_label.setStyleSheet("""
                        border-image: url('Images/InventoryBackground.png') 0 0 0 0 stretch stretch;
                    """)  # Устанавливаем цвет фона
                    item_label.setAlignment(Qt.AlignCenter)  # Выравнивание по центру
                    self.inventory_layout.addWidget(item_label, row, col)

        self.main_layout.addLayout(self.inventory_layout, 0, 0)
        self.main_layout.addLayout(self.weapon_info_layout, 0, 6, 4, 1)
        self.setLayout(self.main_layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #443025; /* Цвет фона окна */
            }
        """) 

    def closeEvent(self, event):
        self.windowClosed.emit()
        super().closeEvent(event)

    def use_item(self, item):
        self.StatsWindow.use_item(item)
        self.hero.inventory.remove(item)
        self.update_inventory()
    
    def update_inventory(self):
        weapon_image_label = QLabel()
        weapon_image_label.setFixedSize(200, 468)  # Растягиваем прямоугольник 1:3
        weapon_image_label.setStyleSheet("border-image: url('Images/InventoryBackgroundWeapon.png') 0 0 0 0 stretch stretch;")  # Устанавливаем цвет фона
        weapon_image = QPixmap(f'Images/weapons/{self.hero.weapon.image}')
        weapon_image_label.setPixmap(weapon_image.scaled(200, 468, Qt.KeepAspectRatio))
        weapon_image_label.setAlignment(Qt.AlignCenter)

        image_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        weapon_image_label.setSizePolicy(image_policy)

        self.weapon_info_label = QLabel(f"Ваше оружие: \n{self.hero.stats_weapon()}")

        for i in reversed(range(self.inventory_layout.count())):
            item = self.inventory_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            self.inventory_layout.removeItem(item)

        for row in range(4):  # Создаем 4 строки
            for col in range(6):  # В каждой строке создаем 6 квадратов
                if len(self.hero.inventory) > row * 6 + col:
                    item = self.hero.inventory[row * 6 + col]
                    item_label = QPushButton()
                    item_label.setIcon(QIcon(f'Images/{item.image}'))
                    item_label.setIconSize(QSize(80, 80))
                    item_label.setFixedSize(130, 130)
                    item_label.setStyleSheet("border-image: url('Images/InventoryBackground.png') 0 0 0 0 stretch stretch;")
                    item_label.setStyleSheet(
                        "QPushButton {"
                        "border-image: url('Images/InventoryBackground.png') 0 0 0 0 stretch stretch;"
                        "}"
                        "QPushButton:pressed {"
                        "border: 2px solid red;"
                        "}"
                    )
                    item_label.clicked.connect(lambda _, item=item: self.use_item(item))
                    self.inventory_layout.addWidget(item_label, row, col)
                else:
                    item_label = QLabel()
                    item_label.setFixedSize(130, 130)
                    item_label.setStyleSheet("border-image: url('Images/InventoryBackground.png') 0 0 0 0 stretch stretch;")
                    item_label.setAlignment(Qt.AlignCenter)
                    self.inventory_layout.addWidget(item_label, row, col)

        self.setLayout(self.main_layout)


class StatsWindow(QWidget):
    print_text_signal = pyqtSignal(str)
    def __init__(self, hero):
        super().__init__()
        self.hero = hero
        self.text_queue = []
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
        self.pixmap = QPixmap(f'Images/{self.hero.hero_class}{self.hero.race}.jpg')
        self.pixmap = self.pixmap.scaled(200, 300, Qt.KeepAspectRatio)
        self.image_label.setAlignment(Qt.AlignCenter)  # Выравниваем по центру
        self.image_label.setPixmap(self.pixmap)
        layout_stats.addWidget(self.image_label)
        
        info = self.hero.stats()
        self.stats_label = QLabel(info)
        layout_stats.addWidget(self.stats_label)
        layout.addLayout(layout_stats)
        
        open_hero_button = QPushButton('Открыть инвентарь', self)
        open_hero_button.clicked.connect(self.open_hero_form)
        open_hero_button.setStyleSheet("""
            QWidget {
                padding: 5px;
                background-color: #6b4d2d;
                border-radius: 10px;
            }
        """) 
        layout.addWidget(open_hero_button)

        open_hero_button = QPushButton('Сохранить персонажа', self)
        open_hero_button.clicked.connect(self.hero_save)
        open_hero_button.setStyleSheet("""
            QWidget {
                padding: 5px;
                background-color: #6b4d2d;
                border-radius: 10px;
            }
        """) 
        layout.addWidget(open_hero_button)

        open_hero_button = QPushButton('Сохранить игру', self)
        open_hero_button.setStyleSheet("""
            QWidget {
                padding: 5px;
                background-color: #6b4d2d;
                border-radius: 10px;
            }
        """) 
        open_hero_button.clicked.connect(self.save_game)
        layout.addWidget(open_hero_button)

        open_hero_button = QPushButton('Загрузить персонажа', self)
        open_hero_button.setStyleSheet("""
            QWidget {
                padding: 5px;
                background-color: #6b4d2d;
                border-radius: 10px;
            }
        """) 
        open_hero_button.clicked.connect(self.hero_load)
        layout.addWidget(open_hero_button)
        # self.info_label = QLabel("\t Оружие: \n" + self.hero.stats_weapon())
        # layout.addWidget(self.info_label)
        
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

    def use_item(self, item):
        self.text_queue.append(item.use(self.hero))
        self.update_stats()

    def open_hero_form(self):
        hero_form = Inventory(self.hero, self)
        hero_form.windowClosed.connect(self.function_to_run_on_close)
        hero_form.exec_()

    def hero_save(self):
        self.hero.save()
        create_dialog("Диалоговое окно", "Ваш персонаж успешно сохранён")
        self.update_stats()
        
    def save_game(self):
        self.hero.save()
        create_dialog("Диалоговое окно", "Напишите в основном окне команду /txt")
        self.update_stats()

    def hero_load(self):
        self.hero.load()
        create_dialog("Диалоговое окно", "Ваш персонаж успешно загружен")
        self.update_stats()

    def function_to_run_on_close(self):
        message = "Сообщение, которое вы хотите передать в ChatWindow"
        self.print_text_signal.emit(message)

    def update_stats(self):
        # Обновим информацию о герое, включая hp_bar
        print("update")
        print(self.hero.hp)
        self.hp_bar.setValue(int(self.hero.hp / (self.hero.max_hp / 100)))
        self.mana_bar.setValue(int(self.hero.mana / (self.hero.max_mana / 100)))
        self.exp_bar.setValue(int(self.hero.exp / (self.hero.exp_to_next_level / 100)))
        self.hp_bar.setMaximum(int(self.hero.max_hp / (self.hero.max_hp / 100)))
        self.mana_bar.setMaximum(int(self.hero.max_mana / (self.hero.max_mana / 100)))
        self.exp_bar.setMaximum(int(self.hero.exp_to_next_level / (self.hero.exp_to_next_level / 100)))

        self.pixmap = QPixmap(f'Images/{self.hero.hero_class}{self.hero.race}.jpg')
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

        # self.info_label.setText("\t Оружие: \n" + self.hero.stats_weapon())
        # self.info_label.repaint()  # Перерисовать метку

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
        # self.info_label.setStyleSheet("""
        #     background-color: #d2c0ad; /* Немного темнее цвет пергамента */
        #     color: #241c14;
        #     border-radius: 10px;
        # """)
        if self.hero.money < 1000:
            self.image_label.setStyleSheet("""
                background-color: #443525; /* Немного темнее старой бумаги */
                border-radius: 3px;
            """)
        else:
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
        # self.info_label.setStyleSheet("""
        #     background-color: #333; /* Немного темнее цвет пергамента */
        #     color: white;
        #     border-radius: 10px;
        # """)
        if self.hero.money < 1000:
            self.image_label.setStyleSheet("""
                background-color: #333;
                border-radius: 3px;
            """)
        else:
            self.image_label.setStyleSheet("""
                background-color: #333;
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
            image_path = f'Dice/d{i}.png'
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