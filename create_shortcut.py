import os
import sys
import ctypes
import win32com.client

def create_shortcut():
    try:
        # デスクトップのパスを取得
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        
        # ショートカットのパス
        shortcut_path = os.path.join(desktop, 'Turbo Switch.lnk')
        
        # ターゲットのパス（Pythonスクリプトの絶対パス）
        target = os.path.abspath(sys.executable)
        
        # 作業ディレクトリ
        work_dir = os.path.dirname(os.path.abspath(__file__))
        
        # アイコンのパス
        icon_path = os.path.join(work_dir, 'icon.ico')
        
        # シェルオブジェクトを作成
        shell = win32com.client.Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        
        # ショートカットのプロパティを設定
        shortcut.TargetPath = target
        shortcut.Arguments = '\"' + os.path.join(work_dir, 'main.py') + '"'
        shortcut.WorkingDirectory = work_dir
        
        # 管理者として実行するように設定
        shortcut_handle = shell.CreateShortCut(shortcut_path)
        shortcut_handle.TargetPath = 'powershell.exe'
        shortcut_handle.Arguments = f'Start-Process "{target}" -ArgumentList "\"{os.path.join(work_dir, 'main.py')}\"" -Verb RunAs'
        shortcut_handle.WorkingDirectory = work_dir
        
        if os.path.exists(icon_path):
            shortcut_handle.IconLocation = icon_path
        
        # ショートカットを保存
        shortcut_handle.Save()
        
        print(f'ショートカットが作成されました: {shortcut_path}')
        return True
    except Exception as e:
        print(f'ショートカットの作成中にエラーが発生しました: {e}')
        return False

if __name__ == '__main__':
    create_shortcut()
