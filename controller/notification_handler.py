
import subprocess
from PySide6.QtWidgets import QSystemTrayIcon, QApplication

try:
    from utils.logger import module_logger
    def log_controller(action: str, details: str):
        module_logger.log_controller_action(action, details)
except ImportError:
    def log_controller(action: str, details: str):
        print(f"[TIMER-NOTIFICATION-{action}] {details}")

class NotificationHandler:
    """处理系统通知的辅助类"""

    @staticmethod
    def show_notification():
        """显示跨平台兼容的系统通知"""
        if NotificationHandler._try_notify_send():
            return
        if NotificationHandler._try_qt_tray():
            return
        NotificationHandler._fallback_print()

    @staticmethod
    def _try_notify_send() -> bool:
        """尝试使用 notify-send 发送通知"""
        try:
            if subprocess.run(['which', 'notify-send'], capture_output=True, check=False).returncode == 0:
                subprocess.run([
                    'notify-send', '🍅 番茄时间', '时间到！休息一下吧~\n\n请记录您刚才完成的事情',
                    '--urgency=normal', '--expire-time=8000', '--icon=dialog-information'
                ], check=False)
                log_controller("show_notification", "系统通知已发送 (notify-send)")
                return True
        except Exception as e:
            log_controller("show_notification_exception", f"notify-send 失败: {e}")
        return False

    @staticmethod
    def _try_qt_tray() -> bool:
        """尝试使用 Qt 系统托盘发送通知"""
        try:
            if QSystemTrayIcon.isSystemTrayAvailable():
                app = QApplication.instance()
                if app:
                    tray = QSystemTrayIcon()
                    if tray.supportsMessages():
                        tray.show()
                        tray.showMessage("🍅 番茄时间", "时间到！休息一下吧~\n请记录您刚才完成的事情", QSystemTrayIcon.Information, 8000)
                        log_controller("show_notification", "系统通知已发送 (Qt托盘)")
                        # 这只是一个变通方法，因为showMessage是非阻塞的
                        # 我们不能在这里隐藏托盘图标，否则消息可能不会显示
                        return True
        except Exception as e:
            log_controller("show_notification_exception", f"Qt托盘通知失败: {e}")
        return False

    @staticmethod
    def _fallback_print():
        """备用方案：在终端打印通知"""
        log_controller("show_notification", "所有通知方式均失败，回退到终端输出")
        print("\n" + "="*50)
        print("🍅 番茄时间完成！")
        print("时间到！休息一下吧~")
        print("请记录您刚才完成的事情")
        print("="*50 + "\n")

    @staticmethod
    def play_notification_sound():
        """播放通知声音"""
        sound_commands = [
            ['paplay', '/usr/share/sounds/alsa/Front_Right.wav'],
            ['aplay', '/usr/share/sounds/alsa/Front_Right.wav'],
            ['play', '/usr/share/sounds/sound-icons/bell.oga'],
            ['speaker-test', '-t', 'sine', '-f', '800', '-l', '1']
        ]
        for cmd in sound_commands:
            if NotificationHandler._try_play_sound(cmd):
                break

    @staticmethod
    def _try_play_sound(command: list) -> bool:
        """尝试使用指定命令播放声音"""
        try:
            if subprocess.run(['which', command[0]], capture_output=True, check=False).returncode == 0:
                subprocess.run(command, capture_output=True, check=False)
                log_controller("play_sound", f"使用 {command[0]} 播放声音")
                return True
        except Exception as e:
            log_controller("play_sound_exception", f"使用 {command[0]} 播放声音失败: {e}")
        return False 