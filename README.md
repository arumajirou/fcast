# fcast

時系列予測（宝くじ系の数字選択式データ）を対象に、**メタDB（forecast_meta）** と **Lakehouse（forecast_lake）** を分離しつつ、
`run_plan`（実行計画）をDB駆動で回すための実装テンプレートです。

- メタDB: SQLite（デフォルト） / PostgreSQL（任意）
- Lake: Parquet（デフォルト） / Delta（任意で拡張）

## 目的
- ライブラリ（Nixtla系＋非Nixtla＋Foundation model）を追加しても壊れにくい
- 引数・型・制約をDB化し、実行前検証（validator）でエラーを潰す
- Notebookで段階的に動作確認し、pytestでHTMLレポートを出す

---

## クイックスタート（uv）
> Windows PowerShell 例

```powershell
cd C:\fcast
uv venv
uv pip install -e .[dev]
pytest -q --html=reports\pytest\report.html --self-contained-html
```

Notebook:
```powershell
jupyter lab
```

---

## クイックスタート（conda）
```powershell
cd C:\fcast
conda env create -f environment.yml
conda activate fcast
pytest -q --html=reports\pytest\report.html --self-contained-html
jupyter lab
```

---

## DB（デフォルト）
- `forecast_meta` : `sqlite:///./forecast_meta.db`
- `forecast_lake` : `./forecast_lake/`

`.env` を作って上書きできます（`.env.example`参照）。

---

## Notebook（段階実行）
- `notebooks/00_bootstrap.ipynb` : 環境確認・フォルダ作成
- `notebooks/10_meta_init.ipynb` : メタDBテーブル作成＆確認
- `notebooks/20_seed_registry.ipynb` : registryへサンプル登録（NeuralForecast等）
- `notebooks/30_games_slots.ipynb` : 宝くじゲーム定義（増減に対応）
- `notebooks/40_build_sample_data.ipynb` : サンプルデータ生成→silver/gold
- `notebooks/50_plan_7models.ipynb` : LOTO6の7モデル（N1..N6+ALL）を計画化
- `notebooks/60_run_mock_pipeline.ipynb` : Mockで疑似実行→結果をDB/Parquetで確認

---

## テスト（HTML出力）
```powershell
scripts\test.ps1
```

---

## パッケージZIP作成（増殖管理）
```powershell
scripts\pack.ps1
```

`dist\fcast_latest.zip` を上書きし、古いZIPは `dist\archive\` に退避（世代数はスクリプト内で制限）。
# fcast
