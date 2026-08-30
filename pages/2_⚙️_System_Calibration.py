import streamlit as st
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

# استدعاء المكون الجاهز من الملف الذي أنشأناه في الخارج
from components_loader import enrollment_plugin

# إعدادات الصفحة
st.set_page_config(page_title="System Calibration", page_icon="⚙️", layout="wide")

st.title("⚙️ Keystroke Dynamics Calibration")
st.markdown("### 🔐 Secure Enrollment Portal")
st.divider()

st.info("To train the system on a new operator or a new environment, type the emergency command **15 times**. The system enforces a mandatory 3-second cooldown to capture natural muscle memory.")

# استدعاء واجهة الجافا سكريبت
enrollment_data = enrollment_plugin(height=320)

# معالجة البيانات عند الانتهاء من 15 محاولة
if enrollment_data:
    st.warning("⏳ Training Neural Engine on provided physical dynamics...")
    
    df = pd.DataFrame(enrollment_data)
    features_list = []
    
    for attempt_id, group in df.groupby('attempt'):
        group = group.sort_index() 
        f_dict = {
            'total_time': group['hold_time'].sum() + group['flight_time'].sum(),
            'avg_hold': group['hold_time'].mean(),
            'avg_flight': group['flight_time'].mean(),
            'std_hold': group['hold_time'].std() if len(group) > 1 else 0,
            'std_flight': group['flight_time'].std() if len(group) > 1 else 0
        }
        
        flight_times = group['flight_time'].tolist()
        for i in range(1, len(flight_times)):
            f_dict[f'digraph_trans_{i}'] = flight_times[i]
            
        features_list.append(f_dict)
        
    X_enroll = pd.DataFrame(features_list).fillna(0)
    
    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(X_enroll)
    
    exported_data = {
        'model': model,
        'features': X_enroll.columns.tolist()
    }
    
    # تحديد مسار الحفظ في المجلد الرئيسي
    import os
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    model_save_path = os.path.join(parent_dir, 'biometric_model.pkl')
    
    joblib.dump(exported_data, model_save_path)
    
    st.cache_resource.clear()
    
    st.success(f"✅ Calibration Successful! AI Model trained on {len(X_enroll)} natural samples and saved securely.")
    st.balloons()