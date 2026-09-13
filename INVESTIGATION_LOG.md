# Investigation Log: False Rejection Rate (FRR) Diagnostic

## 1. Hypotheses Formed
- **Hypothesis 1: Flawed "Reverse Backtracking" in JS.** The logic isolates the correct sequence of characters for `OVERRIDE-HYDRA-7745`. However, if the user makes a typo, deletes it, and types the correct letter, the `flight_time` calculation (`cleanSeq[i].down - cleanSeq[i - 1].up`) includes the entire duration of the mistake and correction. This produces a massive, artificial outlier in the timing vector, guaranteeing a false rejection.
- **Hypothesis 2: Lack of Rhythm Normalization.** The system currently relies on *absolute* flight and hold times. Natural motor pauses or a slight change in the user's global typing speed (e.g., typing 5% faster or slower overall) will alter every single absolute feature. The system needs "relative rhythm" features (e.g., flight time as a percentage of total time) which remain stable even if overall speed fluctuates.
- **Hypothesis 3: Missing Outlier Capping.** The `0.40s` capping mechanism mentioned in the directive is absent in the codebase. Without clipping extreme flight times (which happen during natural cognitive pauses or minor distractions), the `StandardScaler` variance is severely distorted, pushing natural attempts out of bounds.
- **Hypothesis 4: Overly Aggressive Model Contamination.** During calibration, `IsolationForest` is trained with `contamination=0.20` on only 15 samples. This explicitly labels 3 of the user's *own baseline attempts* as outliers, forcing an artificially tight decision boundary around the remaining 12. Combined with a hard positive `SECURITY_THRESHOLD` of `0.0100` in inference, this guarantees high FRR because the model was told to be extremely skeptical of the user's own data.
- **Hypothesis 5: JS Timestamp Precision.** `Date.now()` is used instead of `performance.now()`. `Date.now()` is subject to clock adjustments and only has 1ms resolution, which can introduce jitter in millisecond-scale biometrics.

## 2. Problematic Code Blocks Identified
1. **`keystroke_plugin/index.html` & `enrollment_plugin/index.html` (Reverse Backtracking):**
   ```javascript
   let flight = i > 0 ? (cleanSeq[i].down - cleanSeq[i - 1].up) / 1000.0 : 0;
   ```
   *Issue*: Does not account for intermediate mistaken keystrokes.
2. **`pages/2_⚙️_System_Calibration.py` (Model Initialization):**
   ```python
   model = IsolationForest(n_estimators=150, contamination=0.20, random_state=42)
   ```
   *Issue*: 20% contamination on 15 samples is too aggressive.
3. **`app.py` & `pages/2_⚙️_System_Calibration.py` (Feature Extraction):**
   ```python
   f_dict[f'digraph_trans_{i}'] = flight_times[i]
   ```
   *Issue*: Uses absolute times instead of relative rhythm proportions. Missing the 0.40s cap.

## 3. Applied Remediations & Execution Notes
1. **Frontend JS**: 
   - Upgraded `Date.now()` to `performance.now()` in `keystroke_plugin/index.html`, `enrollment_plugin/index.html`, and `free_typing_plugin/index.html` to provide sub-millisecond precision.
   - Refactored `keyup`/`keydown` tracking to map active keys and append to `rawLog` on `keydown`. This preserves true chronological sequence and solves dropped event errors during high-speed key rollover.
2. **Python Preprocessing**: 
   - Applied the `0.40s` flight time cap in `app.py` and `pages/2_⚙️_System_Calibration.py` using `df['flight_time'].clip(upper=0.40)` *before* any aggregate metrics are calculated.
   - Converted absolute flight times to relative rhythm ratios (`flight_times[i] / safe_total_flight`) to ensure resilience against minor global speed fluctuations.
   - Converted absolute hold times to relative hold ratios (`hold_times[i] / safe_total_hold`) to stabilize dwell times during varied typing speeds.
3. **ML Model**: 
   - Lowered `contamination` in `pages/2_⚙️_System_Calibration.py` to `0.05` to prevent discarding valid baseline variance.
   - Replaced `StandardScaler` with `RobustScaler` to protect against low-variance traps and extreme Z-scores.

## 4. Verification & Re-enrollment Guide
1. Launch the Streamlit application (`streamlit run app.py`).
2. Navigate to the **⚙️ System Calibration** page from the sidebar.
3. Type the emergency command `OVERRIDE-HYDRA-7745` exactly 15 times to generate a new baseline model that incorporates the new relative rhythm features.
4. Return to the main page (**HYDRA-1 SCADA Control**) and type the command to test authorization. The confidence score should now be stable and well above the `0.01` threshold.
