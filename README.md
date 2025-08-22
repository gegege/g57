# g57 -  Power Control Tools

UIからCPU電力のMAX(%, 以下PL))を調整する
95% 100%

普段電力リミットを95%で運用して
ターボボタンを押したら30分100%になる
時間が来たら自動で切95%に戻る

## 動作形態

常駐 & UI

## 常駐

下記をコンテキストから捜査したい

・現在のPLの表示
・95%/100%の切り替え
・ターボモードON（ターボ中(100%)かどうか）
・ターボモードOFF
・ターボモードの残り時間表示
・ターボ延長ボタン(turbo_time)
・終了

## config

config.jsonで設定可能
実行ファイルと同じ場所に配置、なければ下記の値をデフォルトとする

limit_high: 100 ... 電力リミット(HIGH)
limit_low: 95 ... 電力リミット(LOW)
turbo_time: 30(min) ... ターボモード1回の時間

## 技術的な詳細

このツールはWindowsの`powercfg`コマンドを使用して、プロセッサの最大状態を制御します。

- プロセッサの電源管理GUID: `54533251-82be-4824-96c1-47b60b740d00`
- 最大のプロセッサの状態GUID: `bc5038f7-23e0-4960-96da-33abaf5935ec`

現在の設定を確認するには、コマンドプロンプトで以下を実行:
```
powercfg /query SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX
```

## 参考

```
powercfg /GETACTIVESCHEME
電源設定の GUID: 9897998c-92de-4669-853f-b7cd3ecb2790  (AMD Ryzen™ Balanced)
D:\pj\ge3\g57>powercfg /QUERY SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX
電源設定の GUID: 9897998c-92de-4669-853f-b7cd3ecb2790  (AMD Ryzen™ Balanced)
  サブグループの GUID: 54533251-82be-4824-96c1-47b60b740d00  (プロセッサの電源管理)
    GUID エイリアス: SUB_PROCESSOR
    電源設定の GUID: bc5038f7-23e0-4960-96da-33abaf5935ec  (最大のプロセッサの状態)
      GUID エイリアス: PROCTHROTTLEMAX
      利用可能な設定の最小値: 0x00000000
      利用可能な設定の最大値: 0x00000064
      利用可能な設定の増分: 0x00000001
      利用可能な設定の単位: %
    現在の AC 電源設定のインデックス: 0x0000005f
    現在の DC 電源設定のインデックス: 0x00000064
```

下記の対象値をコントロールする

```
現在の AC 電源設定のインデックス: 0x0000005f
```
  
## APP

Tauri (Rust + TS/React)

