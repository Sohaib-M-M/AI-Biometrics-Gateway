import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub
import os

# إعدادات الصفحة
st.set_page_config(page_title="Biometric Proof", page_icon="📊", layout="wide")

st.title("📊 The Science Behind Keystroke Dynamics")
st.markdown("### Proving the Uniqueness of Human Motor Memory")
st.divider()

# تحميل البيانات الأكاديمية (مخزنة في الذاكرة المؤقتة لسرعة الأداء)
@st.cache_data
def load_academic_data():
    path = kagglehub.dataset_download("carnegiecylab/keystroke-dynamics-benchmark-data-set")
    csv_file_path = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')][0]
    df = pd.read_csv(csv_file_path)
    
    # تنظيف البيانات واستخراج المتوسطات
    df_cleaned = df.drop(columns=['sessionIndex', 'rep'], errors='ignore')
    hold_cols = [col for col in df_cleaned.columns if col.startswith('H.')]
    flight_cols = [col for col in df_cleaned.columns if col.startswith('UD.')]
    
    df_cleaned['Avg_Hold_Time'] = df_cleaned[hold_cols].mean(axis=1)
    df_cleaned['Avg_Flight_Time'] = df_cleaned[flight_cols].mean(axis=1)
    
    # أخذ عينة من 5 مستخدمين لسهولة العرض
    sample_subjects = df_cleaned['subject'].unique()[:5]
    return df_cleaned[df_cleaned['subject'].isin(sample_subjects)]

with st.spinner('Loading CMU Keystroke dataset and generating biometric charts...'):
    df_sample = load_academic_data()
    
    # تنسيق الرسوم البيانية
    sns.set_theme(style="darkgrid")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Density of Average Hold Time")
        st.write("Notice how each user (color) has a distinct peak, representing their unique muscle memory speed.")
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        sns.kdeplot(data=df_sample, x='Avg_Hold_Time', hue='subject', fill=True, palette='tab10', ax=ax1)
        ax1.set_xlabel('Average Hold Time (Seconds)')
        ax1.set_ylabel('Density')
        st.pyplot(fig1)
        
    with col2:
        st.subheader("2. Behavioral Clustering")
        st.write("Plotting Hold Time vs Flight Time shows clear isolation between different operators.")
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        sns.scatterplot(data=df_sample, x='Avg_Hold_Time', y='Avg_Flight_Time', hue='subject', palette='tab10', alpha=0.7, s=60, ax=ax2)
        ax2.set_xlabel('Average Hold Time (Seconds)')
        ax2.set_ylabel('Average Flight Time (Seconds)')
        st.pyplot(fig2)

st.info("💡 **Engineering Conclusion:** The physical distance and neurological processing time required to transition between specific keys form a stable, predictable pattern (Biometric Signature) that is nearly impossible to mimic.")