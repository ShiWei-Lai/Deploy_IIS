import sys
from PyQt5.QtWidgets import QApplication
from view import View
from controller import Controller
from model import Model

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 初始化 MVC
    model = Model()
    view = View()
    controller = Controller(model, view)

    # 显示视图
    view.show()

    sys.exit(app.exec_())
