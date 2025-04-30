from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QLineEdit, QComboBox, QSpinBox,
                             QProgressBar, QTableWidget, QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from worker import Worker
from tools.utils import load_user_agents, import_paths

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("WebBatchRequest ProMax")
        self.resize(800, 600)
        # 主布局
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # --- 目标输入区 ---
        tgt_layout = QVBoxLayout()
        tgt_layout.addWidget(QLabel("目标(域名/IP，一行一个)："))
        self.text_targets = QTextEdit()
        tgt_layout.addWidget(self.text_targets)
        # 导入目标按钮
        btn_import = QPushButton("导入目标文件")
        btn_import.clicked.connect(self.import_targets)
        tgt_layout.addWidget(btn_import)
        layout.addLayout(tgt_layout)

        # --- 路径输入区 ---
        path_layout = QVBoxLayout()
        path_layout.addWidget(QLabel("路径（多对多组合, 一行一个）："))
        self.text_paths = QTextEdit()
        path_layout.addWidget(self.text_paths)
        # 导入路径按钮
        btn_import_paths = QPushButton("导入路径文件")
        btn_import_paths.clicked.connect(self.import_paths)
        path_layout.addWidget(btn_import_paths)
        layout.addLayout(path_layout)

        # --- 请求参数配置 ---
        cfg_layout = QHBoxLayout()
        # 请求方法选择
        cfg_layout.addWidget(QLabel("请求方式："))
        self.combo_method = QComboBox()
        self.combo_method.addItems(["GET", "POST", "HEAD", "OPTIONS"])
        cfg_layout.addWidget(self.combo_method)
        # 内容类型选择
        cfg_layout.addWidget(QLabel("Content-Type："))
        self.combo_ct = QComboBox()
        self.combo_ct.addItems(["application/x-www-form-urlencoded", "application/json"])
        cfg_layout.addWidget(self.combo_ct)
        # User-Agent
        cfg_layout.addWidget(QLabel("User-Agent："))
        self.combo_ua = QComboBox()
        # 加载 User-Agent 列表
        ualist = load_user_agents("tools/resources/user_agents.txt")
        self.combo_ua.addItems(ualist)
        cfg_layout.addWidget(self.combo_ua)
        # 自定义 Cookie
        cfg_layout.addWidget(QLabel("Cookie："))
        self.edit_cookie = QLineEdit()
        cfg_layout.addWidget(self.edit_cookie)
        # HTTP 代理
        cfg_layout.addWidget(QLabel("HTTP 代理："))
        self.edit_http_proxy = QLineEdit()
        self.edit_http_proxy.setPlaceholderText("http://ip:port")
        cfg_layout.addWidget(self.edit_http_proxy)
        # SOCKS5 代理
        cfg_layout.addWidget(QLabel("SOCKS5 代理："))
        self.edit_socks_proxy = QLineEdit()
        self.edit_socks_proxy.setPlaceholderText("socks5://ip:port")
        cfg_layout.addWidget(self.edit_socks_proxy)
        # 线程数
        cfg_layout.addWidget(QLabel("线程数："))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 100)
        self.spin_threads.setValue(10)
        cfg_layout.addWidget(self.spin_threads)
        # 超时设置
        cfg_layout.addWidget(QLabel("超时(s)："))
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setRange(1, 60)
        self.spin_timeout.setValue(10)
        cfg_layout.addWidget(self.spin_timeout)
        layout.addLayout(cfg_layout)

        # --- 操作按钮 ---
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("开始扫描")
        self.btn_start.clicked.connect(self.start_scan)
        btn_layout.addWidget(self.btn_start)
        self.btn_stop = QPushButton("停止扫描")
        self.btn_stop.clicked.connect(self.stop_scan)
        btn_layout.addWidget(self.btn_stop)
        self.btn_clear = QPushButton("清空结果")
        self.btn_clear.clicked.connect(self.clear_results)
        btn_layout.addWidget(self.btn_clear)
        self.btn_export = QPushButton("导出 CSV")
        self.btn_export.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.btn_export)
        # 浏览器打开链接（使用配置的浏览器）
        self.btn_open = QPushButton("在浏览器中打开选中链接")
        self.btn_open.clicked.connect(self.open_in_browser)
        btn_layout.addWidget(self.btn_open)
        layout.addLayout(btn_layout)

        # --- 进度条 ---
        self.progress = QProgressBar()
        layout.addWidget(self.progress)

        # --- 结果表格 ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["状态码", "URL", "Title", "Server", "内容长度", "耗时(ms)"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        layout.addWidget(self.table)

        # 线程池列表，用于管理 Worker 线程
        self.workers = []
        self.is_scanning = False

    def import_targets(self):
        """从文件导入目标列表（每行一个域名/IP）"""
        file, _ = QFileDialog.getOpenFileName(self, "导入目标文件", "", "CSV文件 (*.csv);;文本文件 (*.txt)")
        if file:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                data = f.read().strip()
            self.text_targets.setPlainText(data)

    def import_paths(self):
        """从文件导入路径列表（每行一个相对路径）"""
        file, _ = QFileDialog.getOpenFileName(self, "导入路径文件", "", "文本文件 (*.txt);;CSV文件 (*.csv)")
        if file:
            data = import_paths(file)  # 自定义函数：读取路径文件内容
            self.text_paths.setPlainText("\n".join(data))

    def start_scan(self):
        """开始扫描：读取输入内容并启动工作线程"""
        if self.is_scanning:
            return
        self.is_scanning = True
        targets = [t.strip() for t in self.text_targets.toPlainText().splitlines() if t.strip()]
        paths = [p.strip() for p in self.text_paths.toPlainText().splitlines() if p.strip()]
        if not targets:
            return  # 没有目标则不执行
        # 生成 URL 列表，多对多组合域名+路径；若无自定义路径，则只用域名
        urls = []
        for tgt in targets:
            base = tgt if tgt.startswith("http") else f"http://{tgt}"
            if paths:
                for p in paths:
                    # 拼接确保单个斜杠
                    url = base.rstrip("/") + "/" + p.lstrip("/")
                    urls.append(url)
            else:
                urls.append(base)
        total = len(urls)
        self.progress.setMaximum(total)
        self.table.setRowCount(0)

        # 请求参数
        method = self.combo_method.currentText()
        content_type = self.combo_ct.currentText()
        headers = {}
        headers['User-Agent'] = self.combo_ua.currentText()
        # 可扩展：增加其他自定义 Header，例如从界面输入 Host 碰撞

        cookie = self.edit_cookie.text()
        if cookie:
            headers['Cookie'] = cookie

        # 代理设置
        http_proxy = self.edit_http_proxy.text().strip()
        socks_proxy = self.edit_socks_proxy.text().strip()

        num_threads = self.spin_threads.value()
        timeout = self.spin_timeout.value()

        # 按照 thread 数量分批启动 Worker 线程（这里简化为同时启动所有，实际可用信号控制并发数量）
        for i, url in enumerate(urls):
            worker = Worker(url, method=method, headers=headers, cookie=cookie,
                            http_proxy=http_proxy, socks_proxy=socks_proxy,
                            timeout=timeout, content_type=content_type,
                            ehole_path=self.config.get("eholePath"))
            worker.result_signal.connect(self.add_result)  # 将结果添加到表格
            worker.progress_signal.connect(self.update_progress)
            worker.finished.connect(self.thread_finished)
            self.workers.append(worker)
            worker.start()

    def stop_scan(self):
        """停止扫描：终止所有工作线程"""
        for w in self.workers:
            w.stop()  # 自定义方法尝试停止线程
        self.workers.clear()
        self.is_scanning = False

    def clear_results(self):
        """清空结果表格"""
        self.table.setRowCount(0)
        self.progress.setValue(0)

    def add_result(self, result):
        """将 Worker 线程发回的结果添加到表格"""
        # result 是一个字典，包含 url、status、title、server、length、elapsed 等键
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(result.get("status"))))
        self.table.setItem(row, 1, QTableWidgetItem(result.get("url")))
        self.table.setItem(row, 2, QTableWidgetItem(result.get("title")))
        self.table.setItem(row, 3, QTableWidgetItem(result.get("server")))
        self.table.setItem(row, 4, QTableWidgetItem(str(result.get("length"))))
        self.table.setItem(row, 5, QTableWidgetItem(str(result.get("elapsed"))))

    def update_progress(self):
        """更新进度条"""
        self.progress.setValue(self.progress.value() + 1)

    def thread_finished(self):
        """线程完成后移除引用，检查是否全部完成"""
        # 清理已经完成的线程
        self.workers = [w for w in self.workers if w.isRunning()]
        if not self.workers:
            self.is_scanning = False
            # 扫描全部完成，可在此处触发排序或提示
            self.sort_results()

    def sort_results(self):
        """扫描结束后对结果进行智能排序（示例：按响应时间升序）"""
        # 这里简单按“耗时”列排序
        self.table.sortItems(5, order=Qt.AscendingOrder)

    def export_csv(self):
        """将结果导出为 CSV 文件"""
        file, _ = QFileDialog.getSaveFileName(self, "导出 CSV", "", "CSV 文件 (*.csv)")
        if file:
            import csv
            with open(file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写表头
                headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                writer.writerow(headers)
                # 写内容
                for row in range(self.table.rowCount()):
                    row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" 
                                for col in range(self.table.columnCount())]
                    writer.writerow(row_data)

    def open_in_browser(self):
        """在配置的浏览器中打开所选的链接"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        url = selected_items[1].text()
        browser_path = self.config.get("browserPath")
        if browser_path:
            import subprocess
            # 使用自定义浏览器打开链接
            subprocess.Popen([browser_path, url])
        else:
            import webbrowser
            webbrowser.open(url)
