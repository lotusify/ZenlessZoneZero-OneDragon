from qfluentwidgets import FluentIcon, HyperlinkCard
from one_dragon.utils.i18_utils import gt


class HelpCard(HyperlinkCard):
    def __init__(self,
                 url: str = '',
                 text: str = gt('点此查看指南'),
                 title: str = gt('使用说明'),
                 content: str = gt('先看说明 再使用与提问'),
                 parent=None):
        super().__init__(url, text, FluentIcon.HELP, gt(title), gt(content), parent)
        self.setFixedHeight(50)
        if not url:
            self.linkButton.setVisible(False)