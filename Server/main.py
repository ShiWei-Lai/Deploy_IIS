import sys
from threading import Thread
from flask_app import create_app
from qt_ui.main_window import run_pyqt_ui

# 創建 Flask 應用
flask_app = create_app()

def run_flask():
    """啟動 Flask 應用"""
    flask_app.run(host="127.0.0.1", port=5500, debug=False, use_reloader=False)

if __name__ == "__main__":
    # 啟動 Flask 子執行緒
    flask_thread = Thread(target=run_flask)
    flask_thread.setDaemon(True)
    flask_thread.start()

    # 啟動 PyQt5 界面
    run_pyqt_ui()
