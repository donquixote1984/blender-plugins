"""Internationalization support for Multi UV Management addon."""

translations = {
    "zh_CN": {
        ("*", "Multi UV Management"): "多UV管理",
        ("*", "Multi UV"): "多UV",
        ("*", "Batch Operation"): "批量操作",
        ("*", "UV Name:"): "UV名称:",
        ("*", "multiple names"): "多个名称",
        ("*", "Create"): "创建",
        ("*", "Rename"): "重命名",
        ("*", "Delete"): "删除",
        ("*", "Lock"): "锁定",
        ("*", "Copy"): "复制",
        ("*", "Paste"): "粘贴",
        ("*", "Restore"): "恢复",
        ("*", "Confirm"): "确认",
        ("*", "Cancel"): "取消",
        ("*", "Create Texture"): "创建纹理",
        ("*", "Need unify the UV name"): "需要统一UV名称",
        ("*", "Copy UV Layers From Active"): "从活动物体复制UV层",
        ("*", "Force UV Layers From Active"): "从活动物体强制UV层",
        ("*", "Selected objects have different active UV"): "选中物体的激活UV不同",
        ("*", "Not all selected objects have UV1, click Create to unify the UV slots"): "并非所有选中物体都有UV1，点击创建以统一UV槽",
        ("*", "Not all selected objects have UV2, click Create to unify the UV slots"): "并非所有选中物体都有UV2，点击创建以统一UV槽",
        ("*", "Not all selected objects have UV3, click Create to unify the UV slots"): "并非所有选中物体都有UV3，点击创建以统一UV槽",
        ("*", "Not all selected objects have UV4, click Create to unify the UV slots"): "并非所有选中物体都有UV4，点击创建以统一UV槽",
        ("*", "objects selected"): "个物体已选中",
    },
    "zh_TW": {
        ("*", "Multi UV Management"): "多UV管理",
        ("*", "Multi UV"): "多UV",
        ("*", "Batch Operation"): "批量操作",
        ("*", "UV Name:"): "UV名稱:",
        ("*", "multiple names"): "多個名稱",
        ("*", "Create"): "創建",
        ("*", "Rename"): "重命名",
        ("*", "Delete"): "刪除",
        ("*", "Lock"): "鎖定",
        ("*", "Copy"): "複製",
        ("*", "Paste"): "貼上",
        ("*", "Restore"): "恢復",
        ("*", "Confirm"): "確認",
        ("*", "Cancel"): "取消",
        ("*", "Create Texture"): "創建紋理",
        ("*", "Need unify the UV name"): "需要統一UV名稱",
        ("*", "Copy UV Layers From Active"): "從活動物體複製UV層",
        ("*", "Force UV Layers From Active"): "從活動物體強制UV層",
        ("*", "Selected objects have different active UV"): "選中物體的啟用UV不同",
        ("*", "Not all selected objects have UV1, click Create to unify the UV slots"): "並非所有選中物體都有UV1，點擊創建以統一UV槽",
        ("*", "Not all selected objects have UV2, click Create to unify the UV slots"): "並非所有選中物體都有UV2，點擊創建以統一UV槽",
        ("*", "Not all selected objects have UV3, click Create to unify the UV slots"): "並非所有選中物體都有UV3，點擊創建以統一UV槽",
        ("*", "Not all selected objects have UV4, click Create to unify the UV slots"): "並非所有選中物體都有UV4，點擊創建以統一UV槽",
        ("*", "objects selected"): "個物體已選中",
    },
}


def register():
    import bpy
    bpy.app.translations.register(__name__, translations)


def unregister():
    import bpy
    bpy.app.translations.unregister(__name__)
