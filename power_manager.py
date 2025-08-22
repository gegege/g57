import ctypes
import ctypes.wintypes
import os
import sys

# Windows APIの定義
class GUID(ctypes.Structure):
    _fields_ = [
        ('Data1', ctypes.wintypes.DWORD),
        ('Data2', ctypes.wintypes.WORD),
        ('Data3', ctypes.wintypes.WORD),
        ('Data4', ctypes.c_ubyte * 8)
    ]

    def __init__(self, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
        self.Data1 = l
        self.Data2 = w1
        self.Data3 = w2
        self.Data4[0] = b1
        self.Data4[1] = b2
        self.Data4[2] = b3
        self.Data4[3] = b4
        self.Data4[4] = b5
        self.Data4[5] = b6
        self.Data4[6] = b7
        self.Data4[7] = b8

# 必要なGUID
GUID_PROCESSOR_SETTINGS_SUBGROUP = GUID(0x54533251, 0x82BE, 0x4824, 0x96, 0xC1, 0x47, 0xB6, 0x3B, 0x6F, 0x4A, 0x94)
GUID_PROCESSOR_THROTTLE_MAXIMUM = GUID(0xBC5038F7, 0x23E0, 0x4960, 0x96, 0xDA, 0x33, 0xAB, 0xAF, 0xB5, 0x9F, 0xE7)
GUID_PROCESSOR_THROTTLE_MINIMUM = GUID(0x893DEE8E, 0x2BEF, 0x41E0, 0x89, 0xC6, 0xB8, 0x5D, 0x83, 0x56, 0x8C, 0x4D)

# 必要な関数の定義
class PowerManager:
    def __init__(self):
        self.power_settings = ctypes.windll.powrprof
        self.advapi32 = ctypes.windll.advapi32
        
        # 必要な権限を有効化
        self.enable_privilege()
    
    def enable_privilege(self):
        """管理者権限を有効化"""
        try:
            # プロセストークンを取得
            hToken = ctypes.wintypes.HANDLE()
            if not self.advapi32.OpenProcessToken(
                ctypes.windll.kernel32.GetCurrentProcess(),
                0x00000020 | 0x0008,  # TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
                ctypes.byref(hToken)
            ):
                raise ctypes.WinError()
            
            # 権限を有効化
            luid = ctypes.wintypes.LUID()
            if not self.advapi32.LookupPrivilegeValueW(
                None,
                "SeSystemEnvironmentPrivilege",
                ctypes.byref(luid)
            ):
                raise ctypes.WinError()
            
            tp = (ctypes.wintypes.LUID_AND_ATTRIBUTES * 1)()
            tp[0].Luid = luid
            tp[0].Attributes = 0x00000002  # SE_PRIVILEGE_ENABLED
            
            self.advapi32.AdjustTokenPrivileges(
                hToken,
                False,
                ctypes.byref(tp),
                0,
                None,
                None
            )
            
            if ctypes.get_last_error() != 0:
                raise ctypes.WinError()
                
        except Exception as e:
            print(f"権限の有効化に失敗しました: {e}")
    
    def set_power_limit(self, percentage):
        """CPUの電力制限を設定"""
        try:
            # パーセンテージを0-100の範囲に制限
            percentage = max(0, min(100, percentage))
            
            # アクティブな電源スキームを取得
            active_policy = ctypes.c_uint64()
            if self.power_settings.PowerGetActiveScheme(
                None,
                ctypes.byref(ctypes.pointer(active_policy))
            ) != 0:
                raise ctypes.WinError()
            
            # 最大・最小スロットル値を設定
            value = ctypes.c_uint32(int(percentage * 100))  # パーセンテージを100倍して設定
            
            # 最大スロットル値を設定
            if self.power_settings.PowerWriteACValueIndex(
                None,
                ctypes.pointer(active_policy),
                ctypes.byref(GUID_PROCESSOR_SETTINGS_SUBGROUP),
                ctypes.byref(GUID_PROCESSOR_THROTTLE_MAXIMUM),
                value
            ) != 0:
                raise ctypes.WinError()
            
            # 最小スロットル値も同じ値に設定
            if self.power_settings.PowerWriteACValueIndex(
                None,
                ctypes.pointer(active_policy),
                ctypes.byref(GUID_PROCESSOR_SETTINGS_SUBGROUP),
                ctypes.byref(GUID_PROCESSOR_THROTTLE_MINIMUM),
                value
            ) != 0:
                raise ctypes.WinError()
            
            # 電源設定を適用
            if self.power_settings.PowerSetActiveScheme(
                None,
                ctypes.pointer(active_policy)
            ) != 0:
                raise ctypes.WinError()
            
            return True
            
        except Exception as e:
            print(f"電力制限の設定に失敗しました: {e}")
            return False
    
    def get_current_power_limit(self):
        """現在の電力制限を取得"""
        try:
            # アクティブな電源スキームを取得
            active_policy = ctypes.c_uint64()
            if self.power_settings.PowerGetActiveScheme(
                None,
                ctypes.byref(ctypes.pointer(active_policy))
            ) != 0:
                raise ctypes.WinError()
            
            # 最大スロットル値を取得
            value = ctypes.c_uint32()
            if self.power_settings.PowerReadACValueIndex(
                None,
                ctypes.pointer(active_policy),
                ctypes.byref(GUID_PROCESSOR_SETTINGS_SUBGROUP),
                ctypes.byref(GUID_PROCESSOR_THROTTLE_MAXIMUM),
                ctypes.byref(value)
            ) != 0:
                raise ctypes.WinError()
            
            # パーセンテージに変換して返す
            return value.value / 100.0
            
        except Exception as e:
            print(f"電力制限の取得に失敗しました: {e}")
            return 100.0  # デフォルト値

# テスト用
if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("管理者権限で実行してください。")
        sys.exit(1)
    
    pm = PowerManager()
    current = pm.get_current_power_limit()
    print(f"現在の電力制限: {current}%")
    
    if len(sys.argv) > 1:
        try:
            new_limit = float(sys.argv[1])
            if pm.set_power_limit(new_limit):
                print(f"電力制限を{new_limit}%に設定しました。")
            else:
                print("電力制限の設定に失敗しました。")
        except ValueError:
            print("有効な数値を指定してください。")
