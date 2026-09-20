"""
多选下拉框组件演示

演示 MultiSelectionComboBox 和 MultiSelectionComboBoxSettingCard 组件的使用方法。
采用 Fluent Design 风格设计。
支持主题切换功能。
"""

from one_dragon.utils.i18_utils import gt
import sys
from enum import Enum

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from qfluentwidgets import (
    setTheme, Theme, qconfig, FluentIcon,
    PushButton, FluentWindow,
    SubtitleLabel, BodyLabel, CaptionLabel, StrongBodyLabel
)
from one_dragon_qt.widgets.multi_selection_combo_box import MultiSelectionComboBox
from one_dragon_qt.widgets.setting_card.multi_selection_combo_box_setting_card import MultiSelectionComboBoxSettingCard
from one_dragon.base.config.config_item import ConfigItem


class ModeEnum(Enum):
    """模式枚举示例 - 文本长度不同，方便观察标签宽度计算和换行效果"""
    SHORT = ConfigItem(label="短", value="short", desc=gt("短文本"))
    MEDIUM = ConfigItem(label=gt("中等长度文本"), value="medium", desc=gt("中等长度"))
    LONG = ConfigItem(label=gt("这是一个非常非常长的文本标签"), value="long", desc=gt("长文本"))
    WORK = ConfigItem(label=gt("工作"), value="work", desc=gt("高效办公"))
    GAME = ConfigItem(label=gt("游戏"), value="game", desc=gt("娱乐和游戏"))
    STUDY = ConfigItem(label=gt("学习"), value="study", desc=gt("专注学习"))
    REST = ConfigItem(label=gt("休息"), value="rest", desc=gt("放松休息"))
    SPORT = ConfigItem(label=gt("运动健身"), value="sport", desc=gt("运动和健身"))
    READING = ConfigItem(label=gt("阅读书籍"), value="reading", desc=gt("阅读好书"))
    SOCIAL = ConfigItem(label=gt("社交互动"), value="social", desc=gt("朋友聚会"))
    ENTERTAINMENT = ConfigItem(label=gt("娱乐休闲放松"), value="entertainment", desc=gt("休闲娱乐"))
    CREATION = ConfigItem(label=gt("创作设计"), value="creation", desc=gt("设计创作"))
    MEDITATION = ConfigItem(label=gt(gt("冥想放松")), value="meditation", desc="冥想放松")


class MultiSelectionComboBoxDemo(FluentWindow):
    """多选下拉框演示窗口"""

    def __init__(self) -> None:
        """初始化演示窗口"""
        super().__init__()
        self.setWindowTitle(gt("MultiSelectionComboBox - Fluent Design 风格演示"))
        self.resize(600, 500)

        # 创建子界面
        self.demo_interface = QWidget()
        self.demo_interface.setObjectName("demoInterface")
        self.addSubInterface(
            self.demo_interface,
            FluentIcon.GAME,
            gt("组件演示")
        )

        # 创建布局
        layout = QVBoxLayout(self.demo_interface)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # 创建主题切换按钮
        self.theme_btn = PushButton(gt(gt("🌙 切换到暗色主题")))
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        # 创建组件演示区域
        self._create_demo_section(layout)

        layout.addStretch()

        # 根据当前主题更新按钮文本
        self._update_theme_btn()

    def _create_demo_section(self, layout: QVBoxLayout) -> None:
        """创建组件演示区域"""
        # 标题
        title_label = SubtitleLabel(gt("MultiSelectionComboBox 组件演示"))
        layout.addWidget(title_label)

        # 说明
        info_label = BodyLabel(
            gt("下方展示了两种使用方式：\n"
            "1. 基础组件：MultiSelectionComboBox\n"
            "2. 设置卡片：MultiSelectionComboBoxSettingCard（适用于设置界面）\n\n"
            "选项文本长度不同（短/中/长），方便观察标签宽度计算和自动换行效果。\n"
            "点击下拉框选择多个选项，选中的项会以标签形式显示。\n"
            "点击标签的 ✕ 按钮可以删除该选项。")
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 1. 基础组件（固定宽度）
        basic_title = StrongBodyLabel(gt("1. 基础组件（固定宽度 400px）"))
        layout.addWidget(basic_title)

        self.combo_box = MultiSelectionComboBox(
            fixed_width=400  # 固定宽度
        )
        self.combo_box.set_placeholder_text(gt("选择模式..."))

        # 从枚举获取所有 ConfigItem
        items = [mode.value for mode in ModeEnum]
        self.combo_box.add_items(items)
        self.combo_box.selection_changed.connect(self._on_selection_changed)

        layout.addWidget(self.combo_box)

        # 显示当前选中的值
        self.result_label = CaptionLabel(gt("当前选中: 无"))
        layout.addWidget(self.result_label)

        # 2. SettingCard（使用 min/max_width，在 setting card 可用宽度内自适应）
        card_title = StrongBodyLabel(gt("2. 设置卡片 (SettingCard, min=200px, max=自动计算)"))
        layout.addWidget(card_title)

        self.setting_card = MultiSelectionComboBoxSettingCard(
            icon=FluentIcon.GAME,
            title=gt("模式选择"),
            content=gt("选择运行模式"),
            options_enum=ModeEnum
        )
        self.setting_card.value_changed.connect(lambda v: print(f"gt(SettingCard 选中: ){v}"))
        layout.addWidget(self.setting_card)

    def _toggle_theme(self) -> None:
        """切换主题"""
        current_theme = qconfig.theme
        new_theme = Theme.DARK if current_theme == Theme.LIGHT else Theme.LIGHT
        setTheme(new_theme)
        self._update_theme_btn()

    def _update_theme_btn(self) -> None:
        """更新主题按钮文本"""
        if qconfig.theme == Theme.LIGHT:
            self.theme_btn.setText("🌙 切换到暗色主题")
        else:
            self.theme_btn.setText(gt("☀️ 切换到亮色主题"))

    def _on_selection_changed(self, values: list) -> None:
        """当选择改变时更新显示"""
        if values:
            self.result_label.setText(f"gt(✅ 当前选中 (){len(values)}gt(项): ){', '.join(str(v) for v in values)}")
        else:
            self.result_label.setText(gt("❌ 当前选中: 无"))


def main() -> None:
    """主函数"""
    app = QApplication(sys.argv)
    window = MultiSelectionComboBoxDemo()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
