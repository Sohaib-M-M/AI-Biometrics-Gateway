import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import joblib

# 1. إعداد الصفحة لتكون واسعة بالكامل وإخفاء القائمة الجانبية مبدئياً
st.set_page_config(page_title="HYDRA-1 SCADA Control", page_icon="☢️", layout="wide", initial_sidebar_state="collapsed")

# 2. حقن كود CSS لإزالة جميع هوامش Streamlit الافتراضية وجعل الشاشة كاملة
# 2. حقن كود CSS لإزالة جميع هوامش Streamlit وجعل الشاشة كاملة ومتجانسة

# 2. حقن كود CSS لجعل الشاشة كاملة ومتجانسة، وإظهار زر الهامبرغر بلون نيون

# 2. حقن كود CSS لجعل الشاشة كاملة ومتجانسة، وإظهار زر الهامبرغر بلون نيون
st.markdown("""
    <style>
        /* إزالة المساحات الفارغة من الجوانب والأعلى */
        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        
        /* إخفاء القائمة السفلية */
        footer {visibility: hidden;}
        
        /* جعل الشريط العلوي شفافاً لكي تندمج اللوحة */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
        
        /* 🟢 السر هنا: إظهار زر الهامبرغر وتلوينه بالأخضر النيون ليناسب الواجهة */
        [data-testid="collapsedControl"] svg {
            fill: #33ff99 !important;
            width: 2rem !important;
            height: 2rem !important;
        }
        
        /* تلوين خلفية Streamlit بالكامل لتطابق تصميم SCADA */
        [data-testid="stAppViewContainer"] {
            background-color: #0c0f11 !important;
            background-image:
                linear-gradient(rgba(51, 255, 153, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(51, 255, 153, 0.02) 1px, transparent 1px) !important;
            background-size: 40px 40px !important;
        }
        
        /* تعديل ألوان خطوط النتائج الأمنية السفلية */
        [data-testid="stMetricLabel"] p { color: #c7d1d6 !important; font-size: 16px !important; font-family: monospace !important; }
        [data-testid="stMetricValue"] { color: #33ff99 !important; font-family: monospace !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. تحميل النموذج 
@st.cache_resource
def load_model():
    data = joblib.load('biometric_model.pkl')
    return data['model'], data['features']

ai_model, required_features = load_model()

# 4. تسجيل المكون
keystroke_plugin = components.declare_component("keystroke_plugin", path="keystroke_plugin")

# 5. عرض لوحة SCADA بكامل الارتفاع (1100 بكسل)
raw_keystrokes = keystroke_plugin(height=1100)

# 6. معالجة البيانات عند استلامها من المتصفح
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
    
    prediction = ai_model.predict(X_test_live)
    confidence_score = ai_model.decision_function(X_test_live)[0]
    
    # عرض النتيجة أسفل اللوحة مباشرة
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(label="🔍 Neurological Confidence Score", value=f"{confidence_score:.4f}")
        if prediction[0] == 1:
            st.success("🟢 OVERRIDE AUTHORIZED: Operator typing dynamics verified.")
        else:
            st.error("🔴 SYSTEM LOCKDOWN: Unauthorized physical access detected!")