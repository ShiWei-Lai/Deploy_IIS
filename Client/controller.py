from PyQt5.QtWidgets import QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtCore import QObject, Qt
import os


class Controller(QObject):
    def __init__(self, model, view):
        super().__init__()
        self.model = model
        self.view = view

        # 绑定按钮点击事件
        self.view.pushButton.clicked.connect(self.save_api_url)
        self.view.pushButton_2.clicked.connect(self.check_iis_status)
        self.view.pushButton_3.clicked.connect(self.stop_iis)
        self.view.pushButton_4.clicked.connect(self.start_iis)
        self.view.pushButton_5.clicked.connect(self.upload_folder)
        # 初始化视图
        self.load_api_url()

    def save_api_url(self):
        """保存域名到文件"""
        base_url = self.view.lineEdit.text()
        self.model.save_data(base_url)
        self.view.textBrowser.append(f"儲存成功: {base_url}")

    def load_api_url(self):
        """加载文件中的域名"""
        base_url = self.model.load_data()
        if base_url:
            self.view.lineEdit.setText(base_url)
            self.view.textBrowser.append(f"已載入: {base_url}")

    def check_iis_status(self):
        """检查 IIS 状态"""
        api_url = self.model.get_api_url("api/status")
        if not api_url:
            self.view.textBrowser.append("錯誤: 未配置 API URL")
            return

        # 清空 textBrowser
        self.view.textBrowser.clear()
        self.view.textBrowser.append(f"調用 API: {api_url}")

        result = self.model.fetch_iis_status(api_url)
        if "error" in result:
            self.view.textBrowser.append(f"調用失敗: {result['error']}")
        else:
            # 提取特定字段
            message = result.get("message", "未知狀態")
            self.view.textBrowser.append(f"{message}")
            
    def stop_iis(self):
        """停用 IIS 服务"""
        api_url = self.model.get_api_url("api/stop-iis")
        if not api_url:
            self.view.textBrowser.append("錯誤: 未配置 API URL")
            return

        # 清空 textBrowser
        self.view.textBrowser.clear()
        self.view.textBrowser.append(f"調用 API: {api_url}")

        result = self.model.fetch_stop_iis(api_url)
        if "error" in result:
            self.view.textBrowser.append(f"調用失敗: {result['error']}")
        else:
            # 提取特定字段
            message = result.get("message", "未知結果")
            self.view.textBrowser.append(f"IIS 停用結果: {message}")
            
    def start_iis(self):
        """启动 IIS 服务"""
        api_url = self.model.get_api_url("api/start-iis")
        if not api_url:
            self.view.textBrowser.append("錯誤: 未配置 API URL")
            return

        # 清空 textBrowser
        self.view.textBrowser.clear()
        self.view.textBrowser.append(f"調用 API: {api_url}")

        result = self.model.fetch_start_iis(api_url)
        if "error" in result:
            self.view.textBrowser.append(f"調用失敗: {result['error']}")
        else:
            message = result.get("message", "未知結果")
            self.view.textBrowser.append(f"IIS 啟動結果: {message}")
            
    def upload_folder(self):
            """
            上传整个文件夹到服务器
            """
            # 弹出文件夹选择对话框
            folder_path = QFileDialog.getExistingDirectory(self.view, "選擇要上傳的資料夾")
            if not folder_path:
                self.view.textBrowser.append("取消上傳")
                return
    
            # 计算文件总数
            total_files = self.calculate_file_count(folder_path)
            if total_files == 0:
                QMessageBox.warning(self.view, "無檔案", "選擇的資料夾中沒有檔案可上傳")
                return
    
            # 弹出确认对话框
            reply = QMessageBox.question(
                self.view,
                "確認上傳",
                f"即將上傳 {total_files} 個檔案，是否繼續？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                self.view.textBrowser.append("用戶取消上傳")
                return
    
            # 开始上传
            api_url = self.model.get_api_url("api/upload-files")
            if not api_url:
                self.view.textBrowser.append("錯誤: 未配置 API URL")
                return
    
            self.view.textBrowser.clear()
            self.view.textBrowser.append(f"正在上傳資料夾: {folder_path}")
    
            # 调用模型上传文件夹
            result = self.model.upload_folder(api_url, folder_path)
            if result["status"] == "error":
                self.view.textBrowser.append(f"上傳失敗: {result['message']}")
            else:
                self.view.textBrowser.append("上傳成功！")
                for file in result.get("files", []):
                    self.view.textBrowser.append(f"已上傳: {file}")
    
            self.view.textBrowser.append("資料夾上傳完成！")

    def calculate_file_count(self, folder_path):
        """
        计算文件夹中所有文件的总数
        :param folder_path: 文件夹路径
        :return: 文件总数
        """
        file_count = 0
        for _, _, files in os.walk(folder_path):
            file_count += len(files)
        return file_count
