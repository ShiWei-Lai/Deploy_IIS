from flask import Flask, request, jsonify
from flask_app.views import JsonView
from qt_ui.main_window import MainWindow
from utils.logger import log_message
import subprocess
import os
import shutil
import threading
from datetime import datetime
import time

def setup_routes(app):
    """配置路由"""
    
    # 設定目錄
    UPLOAD_FOLDER = r"C:\project\HotelBookingSystem_Full"
    BACKUP_FOLDER = r"C:\project\backups"
    WEB_CONFIG_SOURCE = r"C:\project\web.config"
    LOG_FILE = "app.log"

    # 初始化目錄
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    
    lock = threading.Lock()
    
    def check_iis_status():
        """檢查 IIS 服務狀態"""
        try:
            # 执行命令获取服务状态
            result = subprocess.run(["sc", "query", "W3SVC"], capture_output=True, text=True, shell=True)
            output = result.stdout + result.stderr

            # 判断服务状态
            if "RUNNING" in output:
                return "RUNNING"
            elif "STOPPED" in output:
                return "STOPPED"
            else:
                return "UNKNOWN"
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    @app.route('/api/status', methods=['GET'])
    def iis_status():
        """檢查 IIS 服務狀態並更新 PyQt5 界面"""
        try:
            # 提取客戶端的真實 IP
            forwarded_for = request.headers.get('X-Forwarded-For', None)
            real_ip = forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr
    
            # 獲取當前時間
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]  # 精確到毫秒
    
            # 執行命令檢查 IIS 服務狀態
            result = subprocess.run(["sc", "query", "W3SVC"], capture_output=True, text=True, shell=True)
            output = result.stdout + result.stderr
    
            # 訪問請求信息
            method = request.method
            path = request.path
    
            # 分析輸出結果
            if "RUNNING" in output:
                message = (
                    f"{timestamp} - INFO - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                    f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務狀態: RUNNING"
                )
                if MainWindow.instance:
                    MainWindow.instance.append_message(message)  # 更新 PyQt5 界面
                log_message(message, "info")
                return jsonify({"status": "success", "message": "IIS 服務狀態: RUNNING"}), 200
    
            elif "STOPPED" in output:
                message = (
                    f"{timestamp} - INFO - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                    f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務狀態: STOPPED"
                )
                if MainWindow.instance:
                    MainWindow.instance.append_message(message)  # 更新 PyQt5 界面
                log_message(message, "info")
                return jsonify({"status": "success", "message": "IIS 服務狀態: STOPPED"}), 200
    
            else:
                message = (
                    f"{timestamp} - WARNING - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                    f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務狀態: UNKNOWN"
                )
                if MainWindow.instance:
                    MainWindow.instance.append_message(message)  # 更新 PyQt5 界面
                log_message(message, "warning")
                return jsonify({"status": "success", "message": "IIS 服務狀態: UNKNOWN"}), 200
    
        except Exception as e:
            # 異常處理
            error_message = (
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} - ERROR - 檢查 IIS 狀態時發生錯誤: {str(e)}"
            )
            log_message(error_message, "error")  # 記錄日誌
            if MainWindow.instance:
                MainWindow.instance.append_message(error_message)  # 更新 PyQt5 界面
            return jsonify({"status": "error", "message": error_message}), 500
            
    @app.route('/api/stop-iis', methods=['POST'])
    def stop_iis():
        """停止 IIS 服務並更新 PyQt5 界面"""
        with lock:
            try:
                # 提取客戶端的真實 IP
                forwarded_for = request.headers.get('X-Forwarded-For', None)
                real_ip = forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr

                # 获取当前时间
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

                # 检查当前 IIS 服务状态
                status = check_iis_status()

                # 请求信息
                method = request.method
                path = request.path

                # 如果已停止，直接返回
                if status == "STOPPED":
                    message = (
                        f"{timestamp} - INFO - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                        f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務已經停止"
                    )
                    log_message(message, "info")
                    if MainWindow.instance:
                        MainWindow.instance.append_message(message)
                    return jsonify({"status": "success", "message": "IIS 服務已經停止"}), 200

                # 执行停止 IIS 服务的命令
                result = subprocess.run(["net", "stop", "W3SVC"], capture_output=True, text=True, shell=True)
                output = result.stdout + result.stderr

                # 根据命令结果分析
                if "成功停止" in output or "successfully stopped" in output.lower():
                    message = (
                        f"{timestamp} - INFO - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                        f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務已成功停止"
                    )
                    log_message(message, "info")
                    if MainWindow.instance:
                        MainWindow.instance.append_message(message)
                    return jsonify({"status": "success", "message": "IIS 服務目前停止"}), 200
                else:
                    message = (
                        f"{timestamp} - ERROR - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                        f"\"{method} {path} HTTP/1.0\" 500 - 停止 IIS 服務失敗: {output.strip()}"
                    )
                    log_message(message, "error")
                    if MainWindow.instance:
                        MainWindow.instance.append_message(message)
                    return jsonify({"status": "error", "message": output.strip()}), 500

            except Exception as e:
                # 异常处理
                error_message = (
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} - ERROR - 停止 IIS 時發生錯誤: {str(e)}"
                )
                log_message(error_message, "error")
                if MainWindow.instance:
                    MainWindow.instance.append_message(error_message)
                return jsonify({"status": "error", "message": str(e)}), 500
    
    @app.route('/api/start-iis', methods=['POST'])
    def start_iis():
        """啟動 IIS 服務並更新 PyQt5 界面"""
        with lock:
            try:
                # 提取客户端的真实 IP
                forwarded_for = request.headers.get('X-Forwarded-For', None)
                real_ip = forwarded_for.split(',')[0].strip() if forwarded_for else request.remote_addr

                # 获取当前时间
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]

                # 检查当前 IIS 服务状态
                status = check_iis_status()

                # 请求信息
                method = request.method
                path = request.path

                # 如果服务已经启动
                if status == "RUNNING":
                    message = (
                        f"{timestamp} - INFO - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                        f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務已經啟動"
                    )
                    log_message(message, "info")
                    if MainWindow.instance:
                        MainWindow.instance.append_message(message)
                    return jsonify({"status": "success", "message": "IIS 服務已經啟動"}), 200

                # 执行启动命令
                result = subprocess.run(["net", "start", "W3SVC"], capture_output=True, text=True, shell=True)
                output = result.stdout + result.stderr

                # 如果命令输出包含 "正在啟動"，继续检查状态
                if "正在啟動" in output or "starting" in output.lower():
                    log_message("IIS 服務正在啟動，進行狀態確認...", "info")

                # 增加多次检查状态逻辑
                for attempt in range(1, 6):  # 最多检查 5 次
                    time.sleep(2)  # 每次等待 2 秒
                    status = check_iis_status()
                    if status == "RUNNING":
                        message = (
                            f"{timestamp} - INFO - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                            f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務已成功啟動"
                        )
                        log_message(message, "info")
                        if MainWindow.instance:
                            MainWindow.instance.append_message(message)
                        return jsonify({"status": "success", "message": "IIS 服務已成功啟動"}), 200

                    log_message(f"第 {attempt} 次檢查：IIS 服務狀態為 {status}", "info")

                # 如果多次检查后仍未运行
                if "已經啟動成功" in output:
                    message = (
                        f"{timestamp} - INFO - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                        f"\"{method} {path} HTTP/1.0\" 200 - IIS 服務報告已啟動成功，但狀態未知"
                    )
                    log_message(message, "info")
                    if MainWindow.instance:
                        MainWindow.instance.append_message(message)
                    return jsonify({"status": "success", "message": "IIS 服務已啟動成功"}), 200

                message = (
                    f"{timestamp} - ERROR - {real_ip} - - [{datetime.now().strftime('%d/%b/%Y %H:%M:%S')}] "
                    f"\"{method} {path} HTTP/1.0\" 500 - 啟動 IIS 服務失敗: {output.strip()}"
                )
                log_message(message, "error")
                if MainWindow.instance:
                    MainWindow.instance.append_message(message)
                return jsonify({"status": "error", "message": "IIS 啟動失敗"}), 500

            except Exception as e:
                # 异常处理
                error_message = (
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]} - ERROR - 啟動 IIS 時發生錯誤: {str(e)}"
                )
                log_message(error_message, "error")
                if MainWindow.instance:
                    MainWindow.instance.append_message(error_message)
                return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/upload-files', methods=['POST'])
    def upload_files():
        """上傳檔案，去除最外層資料夾並儲存到指定目錄"""
        try:
            # 检查是否有上传的文件
            if 'files' not in request.files:
                error_message = "沒有檔案可上傳"
                log_message(error_message, "error")
                if MainWindow.instance:
                    MainWindow.instance.append_message(f"錯誤: {error_message}")
                return jsonify({"status": "error", "message": error_message}), 400

            files = request.files.getlist('files')
            if not files:
                error_message = "檔案列表為空"
                log_message(error_message, "error")
                if MainWindow.instance:
                    MainWindow.instance.append_message(f"錯誤: {error_message}")
                return jsonify({"status": "error", "message": error_message}), 400

            saved_files = []

            # 清空 UPLOAD_FOLDER 目录
            if os.path.exists(UPLOAD_FOLDER):
                shutil.rmtree(UPLOAD_FOLDER)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            # 创建备份目录
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            backup_dir = os.path.join(BACKUP_FOLDER, timestamp)
            os.makedirs(backup_dir, exist_ok=True)

            for file in files:
                # 去除最外层目录
                relative_path = os.path.normpath(file.filename)
                cleaned_path = relative_path.split(os.sep, 1)[-1]

                # 保存文件到目标目录
                save_path = os.path.join(UPLOAD_FOLDER, cleaned_path)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                file.save(save_path)

                # 备份文件
                backup_path = os.path.join(backup_dir, cleaned_path)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(save_path, backup_path)

                saved_files.append(cleaned_path)

            # 复制 web.config
            if os.path.exists(WEB_CONFIG_SOURCE):
                shutil.copy2(WEB_CONFIG_SOURCE, os.path.join(UPLOAD_FOLDER, "web.config"))

            #success_message = f"成功上傳檔案並保留結構: {saved_files}"
            success_message = f"成功上傳檔案並保留結構"
            log_message(success_message, "info")
            if MainWindow.instance:
                MainWindow.instance.append_message(success_message)

            return jsonify({
                "status": "success",
                "message": "檔案已成功上傳至目標目錄",
                "files": saved_files
            }), 200

        except Exception as e:
            # 捕获异常并返回错误
            error_message = f"檔案上傳時發生錯誤: {str(e)}"
            log_message(error_message, "error")
            if MainWindow.instance:
                MainWindow.instance.append_message(f"錯誤: {error_message}")
            return jsonify({"status": "error", "message": str(e)}), 500


