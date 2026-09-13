# NeuroType: Keystroke Dynamics Biometrics Gateway

## 1. Project Architecture & Directory Mapping
- **`app.py`**: Main Streamlit application and entry point. Responsible for loading the ML model, instantiating the SCADA UI, receiving live keystrokes, and evaluating them against the Isolation Forest model.
- **`pages/`**:
  - `1_📊_Academic_Proof.py`: (Assumed documentation/academic references).
  - `2_⚙️_System_Calibration.py`: Enrollment portal. Captures 15 keystroke attempts, processes features, trains the `IsolationForest` model, and saves it with a `StandardScaler`.
  - `3_🔍_Deep_Biometric_Analysis.py`: Diagnostics tool to analyze typing speed, hold times, and flight times of free text.
  - `4_🛠️_System_Diagnostics.py`: Server telemetry, checks library versions, and verifies the ML model can be loaded and executed.
- **Plugins (HTML/JS + Streamlit component wrappers)**:
  - `keystroke_plugin/`: The main JS frontend simulating the SCADA terminal and capturing inference keystrokes.
  - `enrollment_plugin/`: The JS frontend used in Calibration to capture the 15 baseline samples.
  - `free_typing_plugin/`: The JS frontend for deep biometric analysis.
  - `components_loader.py`: Python wrapper to load the above HTML/JS plugins into Streamlit.
- **`biometric_model.pkl`**: Serialized `joblib` dictionary containing the trained Isolation Forest `model`, `scaler`, and `features` list.

## 2. Data Flow
1. **Browser JS Events**: 
   - `keydown` and `keyup` listeners capture timestamps. 
   - When the user presses "Enter" and the text matches the exact command `OVERRIDE-HYDRA-7745`, a "Reverse Backtracking" algorithm extracts the relevant keypress events.
2. **Streamlit Communication**: 
   - The JS sends an array of objects `[ {key, hold_time, flight_time}, ... ]` to Python via `postMessage`.
3. **Preprocessing Pipeline**: 
   - Python extracts aggregate features: `total_time`, `avg_hold`, `avg_flight`, `std_hold`, `std_flight`.
   - Python extracts sequential features: `digraph_trans_1`, `digraph_trans_2`, ..., `digraph_trans_N`.
   - Missing features are padded with `0`. The vector is then normalized using the saved `StandardScaler`.
4. **Isolation Forest Inference**: 
   - The normalized vector is passed to `ai_model.decision_function()`.
   - The confidence score is compared against the `SECURITY_THRESHOLD`.

## 3. Active Hyperparameters & Features
- **Model Parameters (Enrollment)**:
  - Algorithm: `IsolationForest`
  - `n_estimators`: 150
  - `contamination`: 0.20 (20%)
  - `random_state`: 42
- **Preprocessing Mechanisms**:
  - Outlier Capping (0.40s): *Missing/Not implemented in current codebase.*
  - Rhythm Percentage Normalization: *Missing. Flight times are currently absolute.*
  - Scaling: `StandardScaler` (Z-score normalization).
- **Decision Boundary**:
  - `SECURITY_THRESHOLD = 0.0100` in `app.py`.
