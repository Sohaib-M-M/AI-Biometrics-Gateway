import os
import streamlit.components.v1 as components

# الحصول على المسار الرئيسي للمشروع بشكل مطلق ومستقر
_parent_dir = os.path.dirname(os.path.abspath(__file__))

# 1. تعريف مكون اللوحة الرئيسية (SCADA)
_keystroke_path = os.path.join(_parent_dir, "keystroke_plugin")
keystroke_plugin = components.declare_component("keystroke_plugin", path=_keystroke_path)

# 2. تعريف مكون واجهة التدريب (Enrollment)
_plugin_path = os.path.join(_parent_dir, "enrollment_plugin")
enrollment_plugin = components.declare_component("enrollment_plugin", path=_plugin_path)

# 3. تعريف مكون صندوق النص الحر (Free Typing)
_free_typing_path = os.path.join(_parent_dir, "free_typing_plugin")
free_typing_plugin = components.declare_component("free_typing_plugin", path=_free_typing_path)