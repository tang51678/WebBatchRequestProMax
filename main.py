import sys
from PyQt5.QtWidgets import QApplication
from tools.config import ConfigManager
from gui import MainWindow

def main():
    # 加载配置文件
    config = ConfigManager("config.properties")
    # 启动 Qt 应用
    app = QApplication(sys.argv)
    # 创建主窗口并传入配置
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
