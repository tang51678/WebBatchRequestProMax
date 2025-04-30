import configparser

class ConfigManager:
    def __init__(self, filename):
        self.config = {}
        parser = configparser.ConfigParser()
        # configparser 解析需要 [section]，这里使用默认 section
        parser.read_dict({'DEFAULT': {}})
        parser.read(filename, encoding='utf-8')
        # 读取配置项
        self.config['browserPath'] = parser['DEFAULT'].get('browserPath', '')
        self.config['eholePath']   = parser['DEFAULT'].get('eholePath', '')

    def get(self, key, default=None):
        return self.config.get(key, default)
