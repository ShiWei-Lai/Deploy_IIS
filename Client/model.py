import os
import requests

class Model:
    def __init__(self, config_file="config.txt"):
        self.config_file = config_file

    def save_data(self, data):
        """保存域名到文件"""
        with open(self.config_file, "w") as file:
            file.write(data)

    def load_data(self):
        """从文件读取域名"""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return file.read().strip()
        return ""

    def get_api_url(self, endpoint):
        """构造完整的 API URL"""
        base_url = self.load_data()
        if base_url:
            return f"{base_url}/{endpoint}"
        return None

    def fetch_iis_status(self, api_url):
        """调用 API 获取 IIS 状态"""
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            return response.json()  # 假设返回 JSON 格式
        except requests.RequestException as e:
            return {"error": str(e)}

    def fetch_stop_iis(self, api_url):
        """调用 API 停用 IIS 服务"""
        try:
            response = requests.post(api_url, timeout=10)  # 使用 POST 请求
            response.raise_for_status()
            return response.json()  # 假设返回 JSON 格式
        except requests.RequestException as e:
            return {"error": str(e)}

    def fetch_start_iis(self, api_url):
        """调用 API 启动 IIS 服务"""
        try:
            response = requests.post(api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
        
    def upload_folder(self, api_url, folder_path):
            """
            上传整个文件夹，并保留完整目录结构。
            :param api_url: 上传文件的 API 端点
            :param folder_path: 本地要上传的文件夹路径
            :return: API 的返回结果
            """
            if not os.path.exists(folder_path):
                return {"status": "error", "message": "資料夾不存在"}
    
            try:
                # 获取根文件夹名
                base_folder = os.path.basename(folder_path.rstrip(os.sep))
                files = []
                file_handles = []  # 保存文件句柄，避免文件被提前关闭
    
                for root, _, file_names in os.walk(folder_path):
                    for file_name in file_names:
                        file_path = os.path.join(root, file_name)
                        relative_path = os.path.relpath(file_path, folder_path).replace("\\", "/")
                        full_relative_path = os.path.join(base_folder, relative_path).replace("\\", "/")
    
                        file_handle = open(file_path, "rb")
                        file_handles.append(file_handle)
                        files.append(("files", (full_relative_path, file_handle, "application/octet-stream")))
    
                # 发送 POST 请求
                response = requests.post(api_url, files=files)
                for f in file_handles:
                    f.close()  # 确保所有文件句柄在请求完成后关闭
    
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"status": "error", "message": response.text}
    
            except Exception as e:
                return {"status": "error", "message": str(e)}
            
    def upload_folder_with_progress(self, api_url, folder_path):
        """
        上传整个文件夹，并逐文件返回上传状态以更新进度条。
        :param api_url: 上传文件的 API 端点
        :param folder_path: 本地要上传的文件夹路径
        :yield: 每个文件的上传状态
        """
        if not os.path.exists(folder_path):
            yield {"status": "error", "file": None, "message": "資料夾不存在"}
            return

        try:
            # 获取根文件夹名（如 HotelBookingSystem_Full）
            base_folder = os.path.basename(folder_path.rstrip(os.sep))

            for root, _, file_names in os.walk(folder_path):
                for file_name in file_names:
                    file_path = os.path.join(root, file_name)

                    # 构造完整相对路径，包含根文件夹
                    relative_path = os.path.relpath(file_path, folder_path).replace("\\", "/")
                    full_relative_path = os.path.join(base_folder, relative_path).replace("\\", "/")

                    try:
                        with open(file_path, "rb") as file_handle:
                            # 使用相对路径作为文件名传递到服务器
                            files = [("files", (full_relative_path, file_handle, "application/octet-stream"))]
                            response = requests.post(api_url, files=files)

                        if response.status_code == 200:
                            yield {"status": "success", "file": full_relative_path}
                        else:
                            yield {"status": "error", "file": full_relative_path, "message": response.text}

                    except Exception as e:
                        yield {"status": "error", "file": full_relative_path, "message": str(e)}

        except Exception as e:
            yield {"status": "error", "file": None, "message": str(e)}
