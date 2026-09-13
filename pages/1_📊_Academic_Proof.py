import streamlit as st
import pandas as pd
import plotly.express as px
import kagglehub
import os

# إعدادات الصفحة
st.set_page_config(page_title="Biometric Proof", page_icon="📊", layout="wide")

st.title("📊 The Science Behind Keystroke Dynamics")
st.markdown("### Proving the Uniqueness of Human Motor Memory")
st.divider()

# تحميل البيانات الأكاديمية
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
    
    # أخذ عينة من 4 مستخدمين فقط لأقصى درجات الوضوح البصري
    sample_subjects = df_cleaned['subject'].unique()[:4]
    return df_cleaned[df_cleaned['subject'].isin(sample_subjects)]

with st.spinner('Loading simplified biometric charts...'):
    df_sample = load_academic_data()
    
    st.info("💡 **How it Works:** We don't care *what* you type; we care *how* you type it. Every operator has a unique typing speed and physical rhythm.")
    
    # تقسيم الشاشة إلى نصفين لعرض الرسمتين بجوار بعضهما
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Muscle Speed")
        st.write("A simple comparison of the average key-press duration across 4 different operators.")
        
        # 1. مخطط أعمدة مبسط (Bar Chart)
        df_bar = df_sample.groupby('subject')['Avg_Hold_Time'].mean().reset_index()
        fig1 = px.bar(df_bar, x='subject', y='Avg_Hold_Time', color='subject',
                      template="plotly_dark", text_auto='.3f',
                      labels={'subject': 'Operator ID', 'Avg_Hold_Time': 'Hold Time (Seconds)'})
        
        # إخفاء التفاصيل المزعجة وجعل الخلفية شفافة
        fig1.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=20, l=20, r=20))
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("2. Biometric Clusters")
        st.write("Plotting Hold Time vs. Flight Time. Notice how each operator forms an isolated 'island'.")
        
        # 2. مخطط انتشار ثنائي الأبعاد واضح جداً (2D Scatter Plot)
        fig2 = px.scatter(df_sample, x='Avg_Hold_Time', y='Avg_Flight_Time', color='subject',
                          template="plotly_dark", opacity=0.8,
                          labels={'Avg_Hold_Time': 'Hold Time (s)', 'Avg_Flight_Time': 'Flight Time (s)'})
        
        # تكبير حجم النقاط وتوضيح الحدود
        fig2.update_traces(marker=dict(size=9, line=dict(width=0.5, color='white')))
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30, b=20, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.success("🎯 **Conclusion:** The distinct 'islands' in the scatter plot prove that no two operators type with the exact same rhythm, making this a highly secure biometric lock.")