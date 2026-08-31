import streamlit as st
import os
import joblib
import sklearn
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="System Diagnostics", page_icon="🛠️", layout="wide")

st.title("🛠️ Server Diagnostics & Model Health")
st.markdown("### SCADA AI-Engine Telemetry")
st.divider()

# 1. فحص إصدارات المكتبات على السيرفر
st.subheader("1. Environment Telemetry")
st.write(f"**🟢 Server Scikit-Learn Version:** `{sklearn.__version__}`")

# 2. البحث عن ملف الذكاء الاصطناعي
st.subheader("2. File System Check")
parent_dir = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(parent_dir, 'biometric_model.pkl')

if os.path.exists(model_path):
    st.success(f"✅ Model file successfully located at: `{model_path}`")
    file_size = os.path.getsize(model_path) / 1024
    st.write(f"**File Size:** `{file_size:.2f} KB`")
    
    # 3. اختبار تحميل النموذج للذاكرة
    st.subheader("3. Memory Allocation Test")
    try:
        data = joblib.load(model_path)
        model = data['model']
        features = data['features']
        st.success("✅ AI Model injected into RAM successfully.")
        st.write(f"**Expected Matrix Dimensions:** `{len(features)} Features`")
        
        # 4. اختبار التنبؤ (لمعرفة هل سينهار السيرفر بسبب الإصدارات أم لا)
        st.subheader("4. Execution Engine Test")
        dummy_data = pd.DataFrame([0]*len(features)).T
        dummy_data.columns = features
        
        pred = model.predict(dummy_data)
        st.success(f"✅ Prediction Engine is fully operational! Dummy output: `{pred[0]}`")
        
    except Exception as e:
        st.error(f"❌ CRITICAL FAILURE: Engine crashed during execution.")
        st.code(str(e))
else:
    st.error("❌ CRITICAL FAILURE: 'biometric_model.pkl' NOT FOUND on the cloud server!")