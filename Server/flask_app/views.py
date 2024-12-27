from flask import jsonify

class JsonView:
    """定義 Flask 的 JSON 輸出格式"""

    @staticmethod
    def render_status(status_message):
        return jsonify({"status": "success", "message": status_message})

    @staticmethod
    def render_success(message):
        return jsonify({"status": "success", "message": message})

    @staticmethod
    def render_error(message):
        return jsonify({"status": "error", "message": message}), 500
