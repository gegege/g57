import requests
import os

def download_icon():
    try:
        # シンプルなターボアイコンをダウンロード
        url = "https://raw.githubusercontent.com/twbs/icons/main/icons/lightning-charge-fill.svg"
        response = requests.get(url)
        response.raise_for_status()
        
        # SVGをICOに変換するための一時ファイルとして保存
        svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.svg')
        with open(svg_path, 'wb') as f:
            f.write(response.content)
        
        print(f'アイコンをダウンロードしました: {svg_path}')
        print('注: SVGからICOへの変換には別のツールが必要です。')
        print('オンラインのSVGからICOへのコンバータを使用するか、Inkscapeなどのツールを使用して変換してください。')
        
        return True
    except Exception as e:
        print(f'アイコンのダウンロード中にエラーが発生しました: {e}')
        return False

if __name__ == '__main__':
    download_icon()
