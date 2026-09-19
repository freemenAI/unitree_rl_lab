# Rough Raycaster Sim2Sim

訓練完成後，需要使用 `unitree_rl_lab/sim2sim` 進行 MuJoCo sim2sim 驗證。這個 sim2sim 不透過 DDS 通訊，而是直接在 Python 中載入 MuJoCo、讀取 raycaster `sensordata`、組合觀測值並執行 policy。


### 1. 下載並編譯 MuJoCo Raycaster 外掛

sim2sim 中的 height scanner 依賴 MuJoCo raycaster 外掛：

* 外掛 Repository：[`https://github.com/Albusgive/mujoco_ray_caster.git`](https://github.com/Albusgive/mujoco_ray_caster.git)
* 編譯步驟：直接參考外掛 Repository 的 README。

需要注意：編譯外掛時使用的 MuJoCo 版本，應與 Python 執行時載入的 MuJoCo 版本一致，否則可能出現 `plugin mujoco.sensor.ray_caster not found` 或 ABI 不相容問題。

編譯成功後，需要找到產生的動態函式庫路徑，例如：

```text
/path/to/mujoco/build/lib/libsensor_raycaster.so
```

後續需要將實際路徑填入 `sim2sim/config.py` 中的 `RAYCASTER_PLUGIN_LIBRARY`。

### 2. 設定 `sim2sim/config.py`

開啟：

```text
/path/to/sim2sim/config.py
```

至少需要檢查以下幾項：

```python
SIM2SIM_DIR = "/path/to/sim2sim"
ASSETS_DIR = os.path.join(SIM2SIM_DIR, "assets")
TRAIN_RUN_DIR = ("/path/to/unitree_rl_lab/logs/rsl_rl/" "unitree_g1_29dof_velocity_rough/<run_time>")
ROBOT_SCENE = os.path.join(ASSETS_DIR, "scene_terrain_raycaster.xml")
RAYCASTER_PLUGIN_LIBRARY = "/path/to/mujoco/build/lib/libsensor_raycaster.so"
POLICY_PATH = os.path.join(TRAIN_RUN_DIR, "model_14000.pt")
DEPLOY_CONFIG = os.path.join(TRAIN_RUN_DIR, "params", "deploy.yaml")
```

其中最重要的是：

* `RAYCASTER_PLUGIN_LIBRARY`：指向實際存在的 `libsensor_raycaster.so`。
* `ROBOT_SCENE`：指向 `sim2sim/assets/` 下的 `scene_terrain_raycaster.xml`。
* `TRAIN_RUN_DIR`：指向本次粗糙地形訓練產生的 log 目錄。
* `POLICY_PATH`：指向實際要測試的 checkpoint。
* `DEPLOY_CONFIG`：指向該 run 目錄下的 `params/deploy.yaml`。

如果路徑設定錯誤，常見錯誤包括：

* `plugin mujoco.sensor.ray_caster not found`
* `Error opening file scene_terrain_raycaster.xml`
* `No such file or directory: model_xxxx.pt`
* 觀測維度與 policy 輸入維度不一致

### 3. 執行 Sim2Sim

先使用無視窗模式進行快速檢查：

```bash
cd /path/to/unitree_rl_lab/sim2sim
python sim2sim_raycaster.py --no-viewer --steps 20
```

如果無視窗模式檢查正常，再啟動視覺化與鍵盤控制：

```bash
python sim2sim_raycaster.py
```

鍵盤控制：

* `方向鍵 ↑/↓` 或 `數字鍵盤 8/2`：前進／後退速度
* `方向鍵 ←/→` 或 `數字鍵盤 4/6`：左／右轉向角速度
* `Space` 或 `數字鍵盤 5`：停止
* `R`：重置模擬
