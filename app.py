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
    
    # استخراج مؤشر الثقة الدقيق
    confidence_score = ai_model.decision_function(X_test_scaled)[0]
    
    # 🛑 هندسة عتبة الأمان (Security Threshold)
    # أي شخص يحصل على أقل من 0.03 سيتم رفضه فوراً حتى لو كان يكتب بسرعة
    SECURITY_THRESHOLD = 0.0300
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(label="🔍 Neurological Confidence Score", value=f"{confidence_score:.4f}")
        
        # التقييم بناءً على العتبة الصارمة بدلاً من التقييم الافتراضي
        if confidence_score >= SECURITY_THRESHOLD:
            st.success("🟢 OVERRIDE AUTHORIZED: Operator typing dynamics verified.")
        else:
            st.error("🔴 SYSTEM LOCKDOWN: Unauthorized physical access detected or confidence too low!")