import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, 
                            QVBoxLayout, QLabel, QPushButton, QMessageBox)
from PyQt6.QtCore import QTimer, Qt, QSize
from PyQt6.QtGui import QIcon, QAction
import psutil
import ctypes
from power_manager import PowerManager

class TurboSwitchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.turbo_mode = False
        self.remaining_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.power_manager = PowerManager()
        
        self.init_ui()
        self.init_tray_icon()
        self.update_power_limit()
    
    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        default_config = {
            'limit_high': 100,
            'limit_low': 95,
            'turbo_time': 30
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # 設定のバリデーション
                    config['limit_high'] = min(100, max(0, config.get('limit_high', 100)))
                    config['limit_low'] = min(100, max(0, config.get('limit_low', 95)))
                    config['turbo_time'] = max(1, config.get('turbo_time', 30))
                    return config
        except Exception as e:
            print(f"設定ファイルの読み込みエラー: {e}")
        
        # デフォルト設定を保存
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    def init_ui(self):
        self.setWindowTitle('Turbo Switch')
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # 現在の状態表示
        self.status_label = QLabel('現在の状態: 通常モード')
        self.power_label = QLabel(f'現在の電力制限: {self.get_current_power_limit()}%')
        self.timer_label = QLabel('')
        
        # ボタン
        self.turbo_button = QPushButton('ターボモードを開始')
        self.turbo_button.clicked.connect(self.toggle_turbo_mode)
        
        # レイアウトに追加
        layout.addWidget(self.status_label)
        layout.addWidget(self.power_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.turbo_button)
        
        self.setLayout(layout)
    
    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(
            getattr(self.style().StandardPixmap, 'SP_ComputerIcon')))
        
        menu = QMenu()
        
        self.turbo_action = QAction('ターボモードを開始', self)
        self.turbo_action.triggered.connect(self.toggle_turbo_mode)
        
        exit_action = QAction('終了', self)
        exit_action.triggered.connect(QApplication.quit)
        
        menu.addAction(self.turbo_action)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def toggle_turbo_mode(self):
        if not self.turbo_mode:
            self.start_turbo_mode()
        else:
            self.stop_turbo_mode()
    
    def start_turbo_mode(self):
        self.turbo_mode = True
        self.remaining_time = self.config['turbo_time'] * 60  # 分を秒に変換
        self.timer.start(1000)  # 1秒ごとに更新
        self.update_power_limit()
        self.update_ui()
        self.tray_icon.showMessage('ターボモード', 'ターボモードを開始しました', 
                                 QSystemTrayIcon.MessageIcon.Information, 3000)
    
    def stop_turbo_mode(self):
        self.turbo_mode = False
        self.timer.stop()
        self.remaining_time = 0
        self.update_power_limit()
        self.update_ui()
        self.tray_icon.showMessage('ターボモード', 'ターボモードを終了しました', 
                                 QSystemTrayIcon.MessageIcon.Information, 3000)
    
    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.stop_turbo_mode()
        self.update_ui()
    
    def update_ui(self):
        if self.turbo_mode:
            self.status_label.setText('現在の状態: ターボモード')
            self.turbo_button.setText('ターボモードを終了')
            self.turbo_action.setText('ターボモードを終了')
            
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.timer_label.setText(f'残り時間: {minutes:02d}:{seconds:02d}')
        else:
            self.status_label.setText('現在の状態: 通常モード')
            self.turbo_button.setText('ターボモードを開始')
            self.turbo_action.setText('ターボモードを開始')
            self.timer_label.setText('')
        
        self.power_label.setText(f'現在の電力制限: {self.get_current_power_limit()}%')
    
    def get_current_power_limit(self):
        try:
            return self.power_manager.get_current_power_limit()
        except Exception as e:
            print(f"電力制限の取得に失敗しました: {e}")
            return self.config['limit_high'] if self.turbo_mode else self.config['limit_low']
    
    def update_power_limit(self):
        target_limit = self.config['limit_high'] if self.turbo_mode else self.config['limit_low']
        try:
            if self.power_manager.set_power_limit(target_limit):
                print(f"電力制限を{target_limit}%に設定しました")
            else:
                print(f"電力制限の設定に失敗しました")
        except Exception as e:
            print(f"電力制限の設定中にエラーが発生しました: {e}")
            QMessageBox.critical(
                self, 
                "エラー", 
                f"電力制限の設定中にエラーが発生しました。\n管理者権限で実行しているか確認してください。\n{str(e)}"
            )
    
    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            QMessageBox.information(self, '情報',
                                 'アプリケーションはタスクトレイで動作しています。\n'
                                 '終了するにはタスクトレイアイコンを右クリックして「終了」を選択してください。')
            self.hide()
            event.ignore()

def main():
    # 管理者権限の確認
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # 管理者権限で再起動
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    
    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        # アプリケーションアイコンを設定
        if hasattr(sys, '_MEIPASS'):
            # PyInstallerでビルドされた場合
            icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
        else:
            # 開発中
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
        
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        window = TurboSwitchApp()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "エラー", f"アプリケーションの起動中にエラーが発生しました:\n{str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
