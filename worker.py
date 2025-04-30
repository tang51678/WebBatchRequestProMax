import re
import time
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):
    # 定义线程信号：result 用于传递结果字典，progress 用于进度更新
    result_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal()

    def __init__(self, url, method="GET", headers=None, cookie=None,
                 http_proxy=None, socks_proxy=None, timeout=10,
                 content_type="application/x-www-form-urlencoded",
                 ehole_path=None):
        super().__init__()
        self.url = url
        self.method = method
        self.headers = headers or {}
        if cookie:
            self.headers['Cookie'] = cookie
        self.timeout = timeout
        self.ehole_path = ehole_path
        # 设置 Content-Type，如果是 POST 请求则使用该内容类型
        self.content_type = content_type
        if self.method == "POST":
            self.headers['Content-Type'] = content_type
        # 配置代理
        self.proxies = {}
        if http_proxy:
            self.proxies['http'] = http_proxy
            self.proxies['https'] = http_proxy
        if socks_proxy:
            self.proxies['http'] = socks_proxy
            self.proxies['https'] = socks_proxy

        self._is_running = True

    def stop(self):
        """尝试停止线程"""
        self._is_running = False

    def run(self):
        """执行请求操作"""
        if not self._is_running:
            return
        result = {
            "url": self.url,
            "status": None, "title": "", "server": "",
            "length": 0, "elapsed": 0
        }
        try:
            start = time.time()
            # 发送请求，allow_redirects 默认为 True（跟随 302/301）
            resp = requests.request(self.method, self.url,
                                    headers=self.headers,
                                    proxies=self.proxies,
                                    timeout=self.timeout,
                                    allow_redirects=True)
            elapsed = int((time.time() - start) * 1000)  # 毫秒
            result["elapsed"] = elapsed
            result["status"] = resp.status_code
            result["length"] = len(resp.content)
            # 提取 Server Banner
            result["server"] = resp.headers.get("Server", "")
            # 提取标题 Title
            result["title"] = self.get_title(resp.text)
            # 如果配置了 EHole，则调用指纹识别（示例：假设 EHole 命令行工具）
            # if self.ehole_path:
            #     self.run_ehole(resp.text)
        except Exception as e:
            # 请求失败时记录错误
            result["title"] = f"Error: {e}"
        # 发出结果并更新进度
        self.result_signal.emit(result)
        self.progress_signal.emit()

    def get_title(self, html):
        """解析 HTML 内容获取 <title> 标签文本"""
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def run_ehole(self, html):
        """调用外部 EHole 工具进行指纹识别（根据配置的 ehole_path）"""
        # 这里可以使用 subprocess 调用 EHole 的命令行接口，并解析输出指纹结果
        pass
