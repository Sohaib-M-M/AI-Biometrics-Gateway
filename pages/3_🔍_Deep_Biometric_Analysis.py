import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# استدعاء المكون من مدير المكونات
from components_loader import free_typing_plugin

# إعدادات الصفحة
st.set_page_config(page_title="Deep Biometric Analysis", page_icon="🔍", layout="wide")

st.title("🔍 Deep Biometric Analysis")
st.markdown("### Text-Independent Footprint Generator")
st.divider()

st.info("Write any text in the box below. The system will ignore *what* you write, and focus purely on *how* your muscle memory executes the keystrokes.")

# استدعاء صندوق النص الحر
raw_data = free_typing_plugin(height=280)

if raw_data:
    df = pd.DataFrame(raw_data)
    
    st.success("✅ Neurological mapping complete! Here is your unique biometric footprint:")
    
    # --- استخراج المؤشرات الرئيسية (KPIs) ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_time_minutes = (df['hold_time'].sum() + df['flight_time'].sum()) / 60.0
    chars_typed = len(df)
    # حساب الكلمات في الدقيقة (المعيار العالمي: الكلمة = 5 أحرف)
    wpm = (chars_typed / 5) / (total_time_minutes if total_time_minutes > 0 else 1)
    
    avg_hold = df['hold_time'].mean() * 1000  # تحويل إلى ملي ثانية
    avg_flight = df['flight_time'].mean() * 1000
    rhythm_variance = df['flight_time'].std()
    
    col1.metric("⚡ Typing Speed", f"{wpm:.0f} WPM")
    col2.metric("⏱️ Avg Hold Time", f"{avg_hold:.1f} ms")
    col3.metric("🚀 Avg Flight Time", f"{avg_flight:.1f} ms")
    col4.metric("🧠 Neurological Variance", f"{rhythm_variance:.3f}")
    
    st.divider()
    
    # --- الرسوم البيانية العميقة ---
    st.markdown("### 📊 Micro-Dynamics Breakdown")
    
    # رسم بياني تفاعلي من Streamlit للنبض الحركي
    st.markdown("#### Muscle Rhythm Over Time (Sequential Keystrokes)")
    st.line_chart(df[['hold_time', 'flight_time']].rename(columns={'hold_time': 'Hold Time (s)', 'flight_time': 'Flight Time (s)'}))
    
    # رسوم Matplotlib متقدمة مع ضبط الألوان للوضع الداكن
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("#### Hold Time Distribution (Muscle Speed)")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        sns.histplot(df['hold_time'], kde=True, color='#33ff99', ax=ax1)
        ax1.set_xlabel('Hold Time (Seconds)')
        ax1.set_ylabel('Frequency')
        # دمج الألوان مع تصميم SCADA
        ax1.set_facecolor('#0c0f11')
        fig1.patch.set_facecolor('#0c0f11')
        ax1.tick_params(colors='#c7d1d6')
        ax1.xaxis.label.set_color('#c7d1d6')
        ax1.yaxis.label.set_color('#c7d1d6')
        for spine in ax1.spines.values(): spine.set_edgecolor('#2c363c')
        st.pyplot(fig1)
        
    with colB:
        st.markdown("#### Flight Time Dispersion (Cognitive Pauses)")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.scatterplot(data=df, x='id', y='flight_time', color='#ff3b47', ax=ax2)
        ax2.set_xlabel('Keystroke Sequence')
        ax2.set_ylabel('Flight Time (Seconds)')
        ax2.set_facecolor('#0c0f11')
        fig2.patch.set_facecolor('#0c0f11')
        ax2.tick_params(colors='#c7d1d6')
        ax2.xaxis.label.set_color('#c7d1d6')
        ax2.yaxis.label.set_color('#c7d1d6')
        for spine in ax2.spines.values(): spine.set_edgecolor('#2c363c')
        st.pyplot(fig2)