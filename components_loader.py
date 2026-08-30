import os
import streamlit.components.v1 as components

# الحصول على المسار الرئيسي للمشروع بشكل مطلق ومستقر
_parent_dir = os.path.dirname(os.path.abspath(__file__))
_plugin_path = os.path.join(_parent_dir, "enrollment_plugin")

# تعريف المكون هنا يمنع خطأ (module is None)
enrollment_plugin = components.declare_component("enrollment_plugin", path=_plugin_path)

# أضف هذا أسفل الكود الموجود
_free_typing_path = os.path.join(_parent_dir, "free_typing_plugin")
free_typing_plugin = components.declare_component("free_typing_plugin", path=_free_typing_path)