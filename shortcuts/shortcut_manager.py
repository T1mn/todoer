import json
from shortcuts.shortcut import ShortcutHandler


class ShortcutManager:
    def __init__(self, config_file):
        self.config_file = config_file

    def load_shortcuts(self, target):
        with open(self.config_file, 'r') as f:
            config = json.load(f)
            for shortcut in config.get('shortcuts', []):
                key = shortcut.get('key')
                action = shortcut.get('action')
                if key and action:
                    handler = getattr(target, action, None)
                    if handler:
                        ShortcutHandler(key, handler).set_shortcut(target)
                    else:
                        print(f"[ShortcutManager] Action '{action}' not found in target.")
                        print(f"[ShortcutManager] Target: {target}, Key: {key}, Action: {action}")