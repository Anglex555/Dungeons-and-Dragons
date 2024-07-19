import sys
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QWidget, \
    QGraphicsDropShadowEffect, QPushButton, QGridLayout, QSpacerItem, \
    QSizePolicy, QApplication, QProgressBar
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


class Sword:
    def __init__(self, name, damage):
        self.name = name
        self.damage = (damage - 5, damage + 5)  # Диапазон урона
        self.weight = 40  # Вес
        self.type = "Меч"


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
        self.name = "name"
        self.hero_class = 'Wizard'
        self.race = 'Elf'
        self.hp = 100
        self.mana = 100
        self.weapon = Sword('обычный меч', 15)
        self.money = 4132
        self.exp = 0
        self.exp_to_next_level = 1000
        self.lvl = 1

    def load_spells_from_database(self, table_name):
        connection = sqlite3.connect('hero_database.db')
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
        if self.hero_class == "Wizard": curr_out = 'Волшебник'
        if self.hero_class == "Fighter": curr_out = 'Воин'
        info += "\n Класс: " + curr_out
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
        info = "\n\t Имя: " + self.name
        if self.hero_class == "Wizard": curr_out = 'Волшебник'
        if self.hero_class == "Fighter": curr_out = 'Воин'
        info += "\n\n Класс: " + curr_out
        if self.race == "Human": curr_out = 'Человек'
        if self.race == "Elf": curr_out = 'Эльф'
        if self.race == "Dwarf": curr_out = 'Дварф'
        info += "\n Раса: " + curr_out
        info += "\n Уровень: " + str(self.lvl)
        info += "\n\n Сила: " + str(self.strength)
        info += "\n Ловкость: " + str(self.dexterity)
        info += "\n Телосложение: " + str(self.constitution)
        info += "\n Интеллект: " + str(self.intelligence)
        info += "\n Мудрость: " + str(self.wisdom)
        info += "\n Харизма: " + str(self.charisma)
        info += "\n\n Деньги:\n " + self.format_Money(self.money)
        return info
    
    def stats_weapon(self) :
        info = " Название: " + self.weapon.name
        info += "\n Тип: " + self.weapon.type
        info += "\n Урон: " + f" от {self.weapon.damage[0]} до {self.weapon.damage[1]}"
        info += "\n Вес: " + str(self.weapon.weight)
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
    

class HeroWindow(QWidget):
    def __init__(self, hero):
        super().__init__()
        self.hero = Hero()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Информация о герое')
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout()

        layout_stats = QHBoxLayout()
        # Создание и отображение картинки (замените 'your_hero_image.png' на путь к вашей картинке)
        image_label = QLabel(self)
        pixmap = QPixmap(f'c:/Ультилиты/2/Mai/DnD/Images/{self.hero.hero_class}{self.hero.race}.jpg')
        pixmap = pixmap.scaled(200, 300, Qt.KeepAspectRatio)
        image_label.setAlignment(Qt.AlignCenter)  # Выравниваем по центру
        image_label.setPixmap(pixmap)
        layout_stats.addWidget(image_label)
        
        info = self.hero.stats()
        info_label = QLabel(info)
        layout_stats.addWidget(info_label)
        layout.addLayout(layout_stats)
        
        hp_bar = QProgressBar(self)
        hp_bar.setValue(int(self.hero.hp / (self.hero.max_hp / 100)))
        hp_bar.setMaximum(int(self.hero.max_hp / (self.hero.max_hp / 100)))
        print(f"{self.hero.hp} из {self.hero.max_hp}")
        hp_bar.setAlignment(Qt.AlignCenter)
        hp_bar.setTextVisible(False)  # Отключение текстового значения
        hp_bar.setStyleSheet('QProgressBar {border: 2px solid grey; border-radius: 6px; background: #E0E0E0; height: 20px;}'
                             'QProgressBar::chunk {background: #FF0000; border-radius: 5px; margin: 1px;}')
        layout.addWidget(QLabel('Здоровье:'))
        layout.addWidget(hp_bar)

        mana_bar = QProgressBar(self)
        mana_bar.setValue(int(self.hero.mana / (self.hero.max_mana / 100)))
        mana_bar.setMaximum(int(self.hero.max_mana / (self.hero.max_mana / 100)))
        print(f"{self.hero.mana} из {self.hero.max_mana}")
        mana_bar.setAlignment(Qt.AlignCenter)
        mana_bar.setTextVisible(False)  # Отключение текстового значения
        mana_bar.setStyleSheet('QProgressBar {border: 2px solid grey; border-radius: 6px; background: #E0E0E0; height: 20px;}'
                             'QProgressBar::chunk {background: #347deb; border-radius: 5px; margin: 1px;}')
        layout.addWidget(QLabel('Мана:'))
        layout.addWidget(mana_bar)

        exp_bar = QProgressBar(self)
        exp_bar.setValue(int(self.hero.exp / (self.hero.exp_to_next_level / 100)))
        exp_bar.setMaximum(int(self.hero.exp_to_next_level / (self.hero.exp_to_next_level / 100)))
        print(f"{self.hero.exp} из {self.hero.exp_to_next_level}")
        exp_bar.setAlignment(Qt.AlignCenter)
        exp_bar.setTextVisible(False)  # Отключение текстового значения
        exp_bar.setStyleSheet('QProgressBar {border: 2px solid grey; border-radius: 6px; background: #E0E0E0; height: 20px;}'
                             'QProgressBar::chunk {background: #c9ab47; border-radius: 5px; margin: 1px;}')
        layout.addWidget(QLabel('Опыт:'))
        layout.addWidget(exp_bar)
        # Отображение статистики героя
        layout.addWidget(QLabel("\n\t Оружие: "))
        info = self.hero.stats_weapon()
        # Добавьте остальные поля статистики здесь

        info_label = QLabel(info)
        layout.addWidget(info_label)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hero = Hero()
    window = HeroWindow(hero)
    window.show()
    sys.exit(app.exec_())