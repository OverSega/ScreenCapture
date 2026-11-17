import json
import os


CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "hotkeys": {
        "screenshot": "",
        "send": "",
        "fullscreen": ""
    },
    "clear_after_send": True,
    "first_run": True
}


def load_config():
    """Загружает конфигурацию из файла. Если файла нет — создает с дефолтными значениями."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))  # Глубокая копия
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Проверяем наличие всех полей (на случай обновления структуры)
            if "clear_after_send" not in config:
                config["clear_after_send"] = True
            if "first_run" not in config:
                config["first_run"] = True
            return config
    except (json.JSONDecodeError, IOError):
        save_config(DEFAULT_CONFIG)
        return json.loads(json.dumps(DEFAULT_CONFIG))


def save_config(config):
    """Сохраняет конфигурацию в файл."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_hotkey(config, key_type):
    """Возвращает горячую клавишу по типу."""
    return config.get("hotkeys", {}).get(key_type, "")


def set_hotkey(config, key_type, key_value):
    """Устанавливает горячую клавишу."""
    if "hotkeys" not in config:
        config["hotkeys"] = {}
    config["hotkeys"][key_type] = key_value