import sys
import subprocess
from PyQt5.QtWidgets import QApplication
from game import Dialog

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Dialog()
    w.exec_()
    subprocess.Popen(['python', 'game.py'])
    app.quit()
    sys.exit(app.exec_())