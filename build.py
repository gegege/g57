import os
import sys
import shutil
import subprocess
import PyInstaller.__main__

def build():
    try:
        # ビルド前に必要なディレクトリをクリーンアップ
        build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')
        dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist')
        
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        
        # PyInstallerでビルド
        PyInstaller.__main__.run([
            '--name=TurboSwitch',
            '--onefile',
            '--windowed',
            '--icon=icon.ico',
            '--add-data=config.json;.',
            'main.py'
        ])
        
        print('\nビルドが完了しました。distフォルダに実行ファイルが生成されています。')
        print('配布するには、distフォルダ全体をコピーしてください。')
        
    except Exception as e:
        print(f'ビルド中にエラーが発生しました: {e}')
        return False
    
    return True

if __name__ == '__main__':
    build()
