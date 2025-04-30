import csv

def load_user_agents(path):
    """从文件读取 User-Agent 列表，每行一个"""
    agents = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                ua = line.strip()
                if ua:
                    agents.append(ua)
    except FileNotFoundError:
        # 默认列表
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
            "Mozilla/5.0 (X11; Linux x86_64)...",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
            "curl/7.68.0"
        ]
    return agents

def import_paths(filepath):
    """导入路径文件，返回路径列表"""
    paths = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f) if filepath.endswith(".csv") else f
            if filepath.endswith(".csv"):
                for row in reader:
                    if row:
                        paths.append(row[0].strip())
            else:
                for line in f:
                    line = line.strip()
                    if line:
                        paths.append(line)
    except Exception as e:
        print(f"导入路径文件失败：{e}")
    return paths
