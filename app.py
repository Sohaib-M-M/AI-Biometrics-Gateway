import streamlit as st
import pandas as pd
import joblib

# استدعاء المكون من مدير المكونات الخارجي
from components_loader import keystroke_plugin

# 1. إعداد الصفحة
st.set_page_config(page_title="HYDRA-1 SCADA Control", page_icon="☢️", layout="wide", initial_sidebar_state="collapsed")

# 2. حقن كود CSS
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        footer {visibility: hidden;}
        header[data-testid="stHeader"] { background: transparent !important; }
        [data-testid="collapsedControl"] svg { fill: #33ff99 !important; width: 2rem !important; height: 2rem !important; }
        [data-testid="stAppViewContainer"] {
            background-color: #0c0f11 !important;
            background-image:
                linear-gradient(rgba(51, 255, 153, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(51, 255, 153, 0.02) 1px, transparent 1px) !important;
            background-size: 40px 40px !important;
        }
        [data-testid="stMetricLabel"] p { color: #c7d1d6 !important; font-size: 16px !important; font-family: monospace !important; }
        [data-testid="stMetricValue"] { color: #33ff99 !important; font-family: monospace !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. تحميل النموذج والمُسوّي (Scaler)
@st.cache_resource
def load_model():
    data = joblib.load('biometric_model.pkl')
    # نستخدم data.get لتجنب انهيار النظام إذا كان الملف القديم ما زال في الذاكرة
    scaler = data.get('scaler', None)
    return data['model'], scaler, data['features']

ai_model, ai_scaler, required_features = load_model()

# 4. عرض لوحة SCADA
raw_keystrokes = keystroke_plugin(height=1100, key="scada_main_terminal")

# 5. معالجة البيانات
if raw_keystrokes:
    test_df = pd.DataFrame(raw_keystrokes)
    
    f_dict = {
        'total_time': test_df['hold_time'].sum() + test_df['flight_time'].sum(),
        'avg_hold': test_df['hold_time'].mean(),
        'avg_flight': test_df['flight_time'].mean(),
        'std_hold': test_df['hold_time'].std() if len(test_df) > 1 else 0,
        'std_flight': test_df['flight_time'].std() if len(test_df) > 1 else 0
    }
    
    flight_times = test_df['flight_time'].tolist()
    for i in range(1, len(flight_times)):
        f_dict[f'digraph_trans_{i}'] = flight_times[i]
        
    X_test_live = pd.DataFrame([f_dict]).fillna(0)
    
    for col in required_features:
        if col not in X_test_live.columns:
            X_test_live[col] = 0
    X_test_live = X_test_live[required_features]
    
    # تطبيق الـ Scaler إذا كان موجوداً
    if ai_scaler:
        X_test_live = pd.DataFrame(ai_scaler.transform(X_test_live), columns=X_test_live.columns)
    
    prediction = ai_model.predict(X_test_live)
    confidence_score = ai_model.decision_function(X_test_live)[0]
    
    # 🛑 هندسة عتبة الأمان (Security Threshold)
    SECURITY_THRESHOLD = 0.0300
    is_authorized = confidence_score >= SECURITY_THRESHOLD
    
    # --- تصميم الواجهة البصرية المتفاعلة (Dynamic UI) ---
    theme_color = "#33ff99" if is_authorized else "#ff3b47"
    bg_color = "rgba(51, 255, 153, 0.05)" if is_authorized else "rgba(255, 59, 71, 0.05)"
    status_text = "OVERRIDE AUTHORIZED: Operator typing dynamics verified." if is_authorized else "SYSTEM LOCKDOWN: Unauthorized physical access detected."
    icon = "🔓" if is_authorized else "🔒"
    
    bar_pct = min(100, max(0, (confidence_score / 0.08) * 100))
    
    # كود HTML مصمم بدون مسافات بادئة لمنع ظهور صندوق الأكواد
    custom_dashboard = f"""
<div style="border: 1px solid {theme_color}; background-color: {bg_color}; padding: 24px; margin-top: 10px; font-family: 'SFMono-Regular', ui-monospace, Menlo, Consolas, monospace; text-align: center; box-shadow: 0 0 20px {bg_color}, inset 0 0 15px {bg_color};">
<div style="color: #c7d1d6; font-size: 13px; letter-spacing: 3px; text-transform: uppercase;">Neurological Confidence Score</div>
<div style="color: {theme_color}; font-size: 48px; font-weight: bold; margin: 12px 0; text-shadow: 0 0 12px {theme_color}; letter-spacing: 2px;">{confidence_score:.4f}</div>
<div style="width: 60%; margin: 0 auto; background-color: #0c0f11; border: 1px solid #2c363c; height: 12px; position: relative;">
<div style="width: {bar_pct}%; background: linear-gradient(90deg, transparent, {theme_color}); height: 100%; box-shadow: 0 0 10px {theme_color}; transition: width 0.8s ease-in-out;"></div>
</div>
<div style="color: {theme_color}; font-size: 14px; letter-spacing: 1.5px; margin-top: 20px; text-transform: uppercase;">{icon} {status_text}</div>
</div>
"""
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown(custom_dashboard, unsafe_allow_html=True)