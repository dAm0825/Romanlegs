#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "OfferGuard-technical-document.pdf"
ASSETS = ROOT / "assets"

INK = colors.HexColor("#17231E")
MUTED = colors.HexColor("#5B675F")
GREEN = colors.HexColor("#0D5A49")
GREEN_DEEP = colors.HexColor("#083C32")
LIME = colors.HexColor("#D6EE82")
CORAL = colors.HexColor("#DB6550")
MUSTARD = colors.HexColor("#D6A43F")
PAPER = colors.HexColor("#F4EFE4")
CREAM = colors.HexColor("#FCFAF4")
LINE = colors.HexColor("#D7D1C5")

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 19 * mm
RIGHT = 19 * mm
TOP = 21 * mm
BOTTOM = 18 * mm
CONTENT_WIDTH = PAGE_WIDTH - LEFT - RIGHT


def register_fonts() -> tuple[str, str]:
    candidates = {
        "body": [
            ("/System/Library/Fonts/STHeiti Light.ttc", 0),
            ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ],
        "display": [
            ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
            ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ],
    }
    registered = {}
    for name, options in candidates.items():
        for path, index in options:
            if not Path(path).exists():
                continue
            try:
                font_name = f"OfferGuard-{name}"
                pdfmetrics.registerFont(TTFont(font_name, path, subfontIndex=index))
                registered[name] = font_name
                break
            except Exception:
                continue
        if name not in registered:
            registered[name] = "Helvetica"
    return registered["body"], registered["display"]


BODY_FONT, DISPLAY_FONT = register_fonts()

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="OG-Body",
        fontName=BODY_FONT,
        fontSize=9.2,
        leading=16,
        textColor=INK,
        spaceAfter=8,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Small",
        fontName=BODY_FONT,
        fontSize=7.7,
        leading=12,
        textColor=MUTED,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Caption",
        fontName=BODY_FONT,
        fontSize=7.5,
        leading=11,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=5,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Eyebrow",
        fontName=BODY_FONT,
        fontSize=7,
        leading=10,
        textColor=GREEN,
        tracking=1.2,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="OG-H1",
        fontName=DISPLAY_FONT,
        fontSize=28,
        leading=35,
        textColor=INK,
        spaceBefore=4,
        spaceAfter=15,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        name="OG-H2",
        fontName=DISPLAY_FONT,
        fontSize=16,
        leading=22,
        textColor=GREEN,
        spaceBefore=17,
        spaceAfter=8,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        name="OG-H3",
        fontName=BODY_FONT,
        fontSize=10.2,
        leading=15,
        textColor=INK,
        spaceBefore=10,
        spaceAfter=5,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Bullet",
        parent=styles["OG-Body"],
        leftIndent=12,
        firstLineIndent=-8,
        bulletIndent=2,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Quote",
        parent=styles["OG-Body"],
        fontName=DISPLAY_FONT,
        fontSize=13,
        leading=21,
        textColor=GREEN_DEEP,
        leftIndent=14,
        rightIndent=14,
        borderColor=LIME,
        borderWidth=0,
        borderPadding=12,
        backColor=colors.HexColor("#EEF3DD"),
        spaceBefore=9,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Cover-Title",
        fontName=DISPLAY_FONT,
        fontSize=41,
        leading=50,
        textColor=colors.white,
        spaceAfter=18,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Cover-Sub",
        fontName=BODY_FONT,
        fontSize=12,
        leading=21,
        textColor=colors.HexColor("#C9D1CC"),
        spaceAfter=15,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Cover-Kicker",
        fontName=BODY_FONT,
        fontSize=7.5,
        leading=11,
        textColor=LIME,
        tracking=1.5,
        spaceAfter=28,
    )
)
styles.add(
    ParagraphStyle(
        name="OG-Cover-Meta",
        fontName=BODY_FONT,
        fontSize=8.7,
        leading=14,
        textColor=colors.white,
        spaceAfter=0,
        wordWrap="CJK",
    )
)


def clean(text: str) -> str:
    return (
        text.replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("—", "-")
        .replace("**", "")
    )


def p(text: str, style: str = "OG-Body") -> Paragraph:
    return Paragraph(clean(text), styles[style])


def bullet(text: str) -> Paragraph:
    return Paragraph(clean(text), styles["OG-Bullet"], bulletText="•")


def section(number: str, title: str, subtitle: str | None = None) -> list:
    content = [
        Spacer(1, 5),
        p(f"{number} / SECTION", "OG-Eyebrow"),
        p(title, "OG-H1"),
    ]
    if subtitle:
        content.append(p(subtitle, "OG-Quote"))
    return content


def rule(width: float = CONTENT_WIDTH) -> Table:
    table = Table([[""]], colWidths=[width], rowHeights=[1])
    table.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.6, LINE)]))
    return table


def two_col(left_text: str, right_text: str, left_title: str, right_title: str) -> Table:
    data = [
        [p(f"<b>{left_title}</b>", "OG-H3"), p(f"<b>{right_title}</b>", "OG-H3")],
        [p(left_text), p(right_text)],
    ]
    table = Table(data, colWidths=[CONTENT_WIDTH / 2 - 5, CONTENT_WIDTH / 2 - 5], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 18),
                ("RIGHTPADDING", (1, 0), (1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def styled_table(rows: list[list[str]], widths: list[float], header: bool = True) -> Table:
    data = []
    for row_index, row in enumerate(rows):
        data.append(
            [
                p(f"<b>{cell}</b>" if header and row_index == 0 else cell, "OG-Small")
                for cell in row
            ]
        )
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.45, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), GREEN_DEEP))
        commands.append(("TEXTCOLOR", (0, 0), (-1, 0), colors.white))
    else:
        commands.append(("BACKGROUND", (0, 0), (-1, -1), CREAM))
    table.setStyle(TableStyle(commands))
    return table


def screenshot(filename: str, caption: str, max_width: float = CONTENT_WIDTH) -> list:
    path = ASSETS / filename
    if not path.exists():
        return []
    with PILImage.open(path) as image:
        ratio = image.height / image.width
    width = min(max_width, CONTENT_WIDTH)
    return [
        Spacer(1, 4),
        Image(str(path), width=width, height=width * ratio),
        p(caption, "OG-Caption"),
    ]


class ArchitectureDiagram(Flowable):
    def __init__(self):
        super().__init__()
        self.height = 292
        self.width = CONTENT_WIDTH

    def draw(self):
        c = self.canv
        width = self.width
        self._box(c, 0, 225, width, 52, GREEN_DEEP, "WEB CLIENT", colors.white)
        self._box(
            c,
            0,
            154,
            width,
            46,
            colors.HexColor("#E8E1D3"),
            "INPUT  /  AGENT TRACE  /  RISK REPORT  /  HUMAN CONFIRMATION",
            INK,
            font_size=6.8,
        )
        self._box(c, 0, 48, width, 78, CREAM, "", INK)
        c.setStrokeColor(GREEN)
        c.setLineWidth(1)
        c.line(18, 48, 18, 126)
        stages = [
            ("1", "PII\nSHIELD"),
            ("2", "CLAUSE\nSCOUT"),
            ("3", "TOOL\nPLANNER"),
            ("4", "GROUNDED\nRAG"),
            ("5", "RISK\nENGINE"),
            ("6", "SAFETY\nREVIEW"),
        ]
        box_width = (width - 54) / len(stages)
        for index, (number, label) in enumerate(stages):
            x = 18 + index * box_width
            self._mini_box(c, x, 63, box_width - 7, 48, number, label)
            if index < len(stages) - 1:
                c.line(x + box_width - 7, 87, x + box_width - 1, 87)
        self._box(c, 0, 0, width, 30, INK, "DEEPSEEK  PLANNER + SYNTHESIZER  ·  LOCAL KNOWLEDGE  ·  MCP TOOLS", colors.white, font_size=6.3)
        for y1, y2 in ((52, 48), (30, 0)):
            c.line(width / 2, y1, width / 2, y2)
            c.line(width / 2 - 4, y2 + 5, width / 2, y2)
            c.line(width / 2 + 4, y2 + 5, width / 2, y2)

    @staticmethod
    def _box(c, x, y, width, height, fill, label, text_color, font_size=7.4):
        c.setFillColor(fill)
        c.setStrokeColor(fill)
        c.roundRect(x, y, width, height, 8, stroke=1, fill=1)
        if label:
            c.setFillColor(text_color)
            c.setFont(BODY_FONT, font_size)
            c.drawCentredString(x + width / 2, y + height / 2 - 2, label)

    @staticmethod
    def _mini_box(c, x, y, width, height, number, label):
        c.setFillColor(colors.white)
        c.setStrokeColor(LINE)
        c.roundRect(x, y, width, height, 5, stroke=1, fill=1)
        c.setFillColor(CORAL)
        c.setFont(BODY_FONT, 5.5)
        c.drawString(x + 6, y + height - 10, f"0{number}")
        c.setFillColor(INK)
        c.setFont(BODY_FONT, 5.8)
        lines = label.split("\n")
        for line_index, line in enumerate(lines):
            c.drawString(x + 6, y + 20 - line_index * 8, line)


class CoverMark(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 70
        self.height = 70

    def draw(self):
        c = self.canv
        c.setStrokeColor(colors.white)
        c.setLineWidth(1.2)
        c.circle(35, 35, 30, stroke=1, fill=0)
        c.line(10, 47, 60, 24)
        c.line(39, 7, 41, 64)
        c.setFillColor(LIME)
        c.circle(30, 43, 6, stroke=0, fill=1)
        c.setFillColor(CORAL)
        c.circle(54, 16, 4, stroke=0, fill=1)


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#20312A"))
    canvas.circle(PAGE_WIDTH + 20, PAGE_HEIGHT - 80, 250, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#34463E"))
    canvas.setLineWidth(0.7)
    canvas.circle(PAGE_WIDTH - 30, PAGE_HEIGHT - 180, 180, stroke=1, fill=0)
    canvas.circle(PAGE_WIDTH - 30, PAGE_HEIGHT - 180, 126, stroke=1, fill=0)
    canvas.setFillColor(CORAL)
    canvas.circle(PAGE_WIDTH - 83, PAGE_HEIGHT - 125, 8, stroke=0, fill=1)
    canvas.setFillColor(MUSTARD)
    canvas.circle(PAGE_WIDTH - 212, PAGE_HEIGHT - 246, 5, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont(BODY_FONT, 7)
    canvas.drawString(LEFT, 20 * mm, "2026 CHUANZHI CUP · AI WEB CHALLENGE")
    canvas.drawRightString(PAGE_WIDTH - RIGHT, 20 * mm, "TECHNICAL DESIGN DOCUMENT")
    canvas.restoreState()


def body_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(LEFT, PAGE_HEIGHT - 13 * mm, PAGE_WIDTH - RIGHT, PAGE_HEIGHT - 13 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont(BODY_FONT, 6.6)
    canvas.drawString(LEFT, PAGE_HEIGHT - 17 * mm, "OfferGuard · 职途罗盘")
    canvas.drawRightString(PAGE_WIDTH - RIGHT, PAGE_HEIGHT - 17 * mm, "TECHNICAL DESIGN / 2026")
    canvas.line(LEFT, 13 * mm, PAGE_WIDTH - RIGHT, 13 * mm)
    canvas.drawString(LEFT, 8.5 * mm, "AI 就业风险侦察 Agent · 技术文档")
    canvas.drawRightString(PAGE_WIDTH - RIGHT, 8.5 * mm, f"{canvas.getPageNumber():02d}")
    canvas.restoreState()


def cover_story() -> list:
    story = [
        Spacer(1, 34 * mm),
        CoverMark(),
        Spacer(1, 15 * mm),
        p("OFFERGUARD / 职途罗盘", "OG-Cover-Kicker"),
        p("看见每一份 offer<br/>的隐藏代价。", "OG-Cover-Title"),
        p(
            "面向高校毕业生的 AI 就业风险侦察 Agent。<br/>"
            "让 AI 负责发现，让你保留决定权。",
            "OG-Cover-Sub",
        ),
        Spacer(1, 20 * mm),
    ]
    meta = Table(
        [
            [
                p("<font color='#D6EE82'>01</font><br/><br/><b>AGENT</b><br/>原生工具调用", "OG-Cover-Meta"),
                p("<font color='#D6EE82'>02</font><br/><br/><b>GROUNDED RAG</b><br/>可追溯证据链", "OG-Cover-Meta"),
                p("<font color='#D6EE82'>03</font><br/><br/><b>HUMAN LOOP</b><br/>人工确认门", "OG-Cover-Meta"),
            ]
        ],
        colWidths=[CONTENT_WIDTH / 3] * 3,
    )
    meta.setStyle(
        TableStyle(
            [
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.HexColor("#405048")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#405048")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.extend([meta, NextPageTemplate("Body"), PageBreak()])
    return story


def build_story() -> list:
    story = cover_story()
    story.extend(
        [
            *section("00", "文档导航", "项目背景、技术要求、架构与可复现验证。"),
            styled_table(
                [
                    ["章节", "内容", "对应官方关注点"],
                    ["01", "项目背景与需求分析", "真实场景、实用性"],
                    ["02", "竞品拆解与差异化", "选题创新、模式创新"],
                    ["03", "系统架构与技术选型", "前端工程质量"],
                    ["04", "AI Agent、RAG 与工具调用", "AI 技术深度"],
                    ["05", "安全、隐私与人工边界", "AI 安全与可控性"],
                    ["06", "核心功能与界面实现", "用户体验、交互"],
                    ["07", "测试、部署与复现", "可用性与工程完整度"],
                    ["08", "创新点、局限与展望", "社会价值和商业潜力"],
                ],
                [55, 220, 210],
            ),
            Spacer(1, 12),
            p(
                "设计原则：不把 AI 做成只输出结论的黑箱。每个风险发现都应回到一份合同原文、一条可信证据和一个可由用户执行的下一步。",
                "OG-Quote",
            ),
            two_col(
                "面向正在签约的应届毕业生、实习生和研究生。输入真实 offer 或劳动合同，输出可解释风险地图。",
                "规则发现保证稳定召回，DeepSeek 负责工具规划与自然语言合成，服务端负责安全复核。",
                "目标用户",
                "技术主线",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("01", "项目背景与需求分析", "毕业生面对的不是信息太少，而是判断成本太高。"),
            p(
                "校招 offer 与劳动合同常把试用期、工资结构、工时、社保、竞业限制和违约责任分散在长文本中。普通关键词搜索只能告诉用户“这里出现了试用期”，却不能解释合同期限、工资比例和后续行动之间的关系。",
            ),
            styled_table(
                [
                    ["真实痛点", "传统方式", "OfferGuard"],
                    ["不知道哪些条款值得看", "逐段阅读或依赖他人的经验", "规则库先定位高影响条款"],
                    ["无法验证法规依据", "通用聊天回答无法追溯", "知识库检索 + 引用白名单"],
                    ["不知道下一步怎么做", "停留在“有风险”的焦虑", "书面澄清问题与证据清单"],
                    ["担心隐私泄露", "把完整合同直接发给 AI", "模型调用前本地脱敏"],
                ],
                [150, 175, 175],
            ),
            Spacer(1, 10),
            p("核心用户旅程", "OG-H2"),
            p(
                "粘贴文本 → 本地扫描 → Agent 规划与工具调用 → 条款风险卡 → 展开原文与政策证据 → 勾选人工确认 → 生成可编辑沟通草稿。",
                "OG-Quote",
            ),
            p("功能边界", "OG-H2"),
            bullet("输入：TXT/MD 上传、文本粘贴、内置示例合同。"),
            bullet("处理：20 至 60000 字符；个人标识本地脱敏；六阶段处理轨迹。"),
            bullet("输出：风险指数、风险等级、条款解释、证据编号、行动清单、Markdown 报告。"),
            bullet("限制：不自动签署、不自动联系 HR、不构成正式法律意见。"),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("02", "竞品拆解与产品差异化", "从优秀作品的完整平台结构里，寻找尚未被做深的一层。"),
            styled_table(
                [
                    ["公开优秀作品", "主要结构", "值得借鉴", "OfferGuard 的差异"],
                    ["健康守护", "健康咨询、饮食、运动、心理陪伴", "服务入口清晰", "把 AI 放进单条决策链"],
                    ["旅行觅点", "筛选、推荐、收藏、评论", "真实信息痛点", "强调依据而不是推荐"],
                    ["智能健身教练", "训练计划、陪练、进度", "视觉主题统一", "展示 Agent 工具调用过程"],
                    ["心理智能疏导", "测评、疏导、记录", "隐私与社会价值", "人工确认门和风险升级"],
                    ["陶韵智境", "文化展示、论坛、地图、AI、后台", "内容与技术组织丰富", "减少平台堆叠，专注可解释决策"],
                ],
                [88, 168, 118, 126],
            ),
            Spacer(1, 12),
            p(
                "产品收束不是删掉功能，而是把每个功能都绑定到用户的一次关键决定：这份文件是否值得直接确认？我还需要问什么？哪些事实必须留证？",
                "OG-Quote",
            ),
            two_col(
                "多数 AI 助手只在用户提出问题后工作，但毕业生往往不知道该问什么。系统主动形成问题清单，减少认知门槛。",
                "回答下方直接展示法规来源、原文引用和行动按钮，让“为什么”与“怎么办”同时可见。",
                "从问答到侦察",
                "从答案到行动",
            ),
            Spacer(1, 8),
            two_col(
                "关键沟通不会由模型自动执行，草稿生成必须经过用户核对。把责任边界变成可感知的产品交互。",
                "合同、手机号、身份证等敏感内容不进入服务端存储，模型只接收脱敏文本，公开仓库不包含密钥。",
                "人工保留最终决定权",
                "隐私优先",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("03", "界面与核心工作流", "用一张页面承载输入、Agent 轨迹、证据报告和人工确认。"),
            *screenshot("landing-screen.png", "图 3-1 产品首屏：风险侦察定位与 Agent 风险示意"),
            p(
                "首屏用编辑式排版建立可信感，并通过文档扫描动画、风险仪表盘和证据卡说明产品机制。主操作直接进入示例合同，降低评审和用户的首次使用成本。",
            ),
            p(
                "工作台左侧用于输入合同，右侧持续显示 Agent 六阶段轨迹；报告生成后自动滚动到风险地图。移动端改为纵向布局，保留完整功能。",
            ),
            *screenshot("workspace-screen.png", "图 3-2 Agent 轨迹与风险报告同屏展示", CONTENT_WIDTH - 4),
            PageBreak(),
            *screenshot("report-screen.png", "图 3-3 风险仪表盘、条款原文和可展开证据"),
            p(
                "风险仪表盘用于快速定位严重程度，条款卡承担可解释分析。每张卡都包含合同 quote、风险原因、建议动作和 citation chip。点击 citation 可查看法规名称与知识库原文。",
            ),
            *screenshot("action-screen.png", "图 3-4 人工确认后解锁行动清单与沟通草稿", CONTENT_WIDTH - 4),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("04", "系统架构", "轻量化全栈结构，优先保证现场可复现与过程可解释。"),
            ArchitectureDiagram(),
            p("图 4-1 OfferGuard 六阶段 Agent 架构", "OG-Caption"),
            styled_table(
                [
                    ["层次", "方案", "选择理由"],
                    ["Web Client", "HTML5 + CSS + ES Modules", "无构建依赖，便于评审直接运行"],
                    ["HTTP Server", "Python http.server", "标准库部署，接口边界清楚"],
                    ["LLM", "DeepSeek deepseek-chat", "中文合同理解、JSON 与 Tool Calling"],
                    ["Retrieval", "中文 n-gram + 类别加权 TF-IDF", "小知识库稳定、可解释、低延迟"],
                    ["Tool Layer", "Function Calling + MCP stdio", "在线 Agent 与开放工具复用"],
                    ["Storage", "无合同持久化；LocalStorage 摘要", "降低敏感数据留存风险"],
                ],
                [100, 175, 225],
            ),
            p(
                "系统将“确定性组件”与“生成式组件”明确分层。正则脱敏、规则命中、风险计算、原文校验和引用白名单均由服务端控制，模型只在受约束的上下文中完成规划和表达。",
                "OG-Quote",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("05", "AI Agent 与工具调用", "Planner 决定调用什么，服务端决定允许做什么。"),
            p("六阶段工作流", "OG-H2"),
            styled_table(
                [
                    ["阶段", "负责者", "输入", "输出"],
                    ["隐私屏障", "确定性代码", "原始合同", "脱敏文本、脱敏数量"],
                    ["条款侦察", "风险规则库", "脱敏文本", "finding id、原句、严重度"],
                    ["工具规划", "DeepSeek", "合同摘要、发现列表、工具 schema", "原生 tool_calls"],
                    ["证据检索", "本地 RAG", "查询与类别", "证据列表、citation id"],
                    ["报告合成", "DeepSeek", "发现 + 证据 + 工具结果", "受约束 JSON 报告"],
                    ["安全复核", "服务端", "原文、发现、引用", "校验结果与兜底"],
                ],
                [86, 116, 150, 148],
            ),
            Spacer(1, 12),
            p(
                "DeepSeek 使用 OpenAI 兼容的 tools 参数返回 tool_calls。服务端只接受四个白名单工具，并对参数中的 finding id 做二次校验。若模型没有选择必需工具，则自动执行检索与风险计算，确保离线演示稳定。",
            ),
            p("可用工具", "OG-H2"),
            bullet("<b>search_local_policy</b>：从本地可信知识库检索法规证据。"),
            bullet("<b>calculate_contract_risk</b>：结合规则权重计算风险指数和严重度统计。"),
            bullet("<b>build_evidence_checklist</b>：根据发现生成书面澄清与留证清单。"),
            bullet("<b>review_legal_safety</b>：识别竞业、高额费用或社保问题的人工升级边界。"),
            p(
                "MCP 服务使用 stdio JSON-RPC 提供同一组能力，支持 tools/list 与 tools/call，使其他 AI 客户端也可以复用知识库和风险工具。",
                "OG-Quote",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("06", "可解释 RAG", "检索结果不是装饰，而是模型允许引用的全部证据空间。"),
            p(
                "知识库目前包含 15 条证据，重点覆盖书面劳动合同、必备条款、试用期、工资下限、加班、社保、竞业限制、违约金与解除合同。每条证据有稳定 id、法规标题、来源、类别和正文。",
            ),
            p("检索方法", "OG-H2"),
            bullet("把中文文本切为二元和三元字符片段，避免依赖分词词典。"),
            bullet("用逆文档频率降低常见词影响，并结合 clause category 加权。"),
            bullet("每条发现优先使用人工指定的 preferred evidence，随后才使用检索排序结果。"),
            bullet("返回 score 作为调试信息，前端只展示可理解证据，不把内部排序分当作法律确定度。"),
            p("示例证据", "OG-H2"),
            p(
                "<b>LCL-19 试用期期限限制</b><br/>来源：《中华人民共和国劳动合同法》第十九条<br/><br/>"
                "劳动合同期限三个月以上不满一年的，试用期不得超过一个月；一年以上不满三年的，试用期不得超过二个月；三年以上固定期限和无固定期限的劳动合同，试用期不得超过六个月。",
                "OG-Quote",
            ),
            p("引用闭环", "OG-H2"),
            styled_table(
                [
                    ["检查", "实现"],
                    ["模型只能引用什么", "Prompt 提供 finding id 与 evidence id 白名单"],
                    ["模型引用了不存在编号", "validate_citations 移除越权引用"],
                    ["模型没有给引用", "按 preferred evidence 和 category 自动补足"],
                    ["发现是否来自原文", "quote 必须能在用户原文中精确匹配"],
                    ["提示注入如何处理", "检测标记，合同始终标记为待分析数据"],
                ],
                [180, 315],
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("07", "隐私、安全与可控性", "在模型看到合同之前，先减少它能看到什么。"),
            p("模型前脱敏", "OG-H2"),
            p(
                "服务端使用正则表达式遮蔽 18 位身份证号、11 位手机号、邮箱地址和 16 至 19 位银行卡号。前端只接收脱敏数量，不展示原值。合同原文不写入服务端存储或日志。",
            ),
            p("安全控制矩阵", "OG-H2"),
            styled_table(
                [
                    ["风险类型", "控制措施", "产品表现"],
                    ["敏感信息外泄", "模型前脱敏、无持久化、密钥环境变量", "“本地先脱敏”提示"],
                    ["法规幻觉", "知识库白名单、引用再校验", "证据编号可展开"],
                    ["原文幻觉", "quote 原句匹配", "失效发现不入报告"],
                    ["提示注入", "合同视为数据、标记检测", "安全复核轨迹"],
                    ["AI 越权", "人工确认门、草稿不发送", "确认后才解锁按钮"],
                    ["高风险争议", "明确升级建议", "页脚免责声明与法务出口"],
                ],
                [115, 230, 150],
            ),
            Spacer(1, 12),
            p(
                "OfferGuard 不追求模仿律师提供确定结论。它把不确定性、证据来源和升级路径直接呈现给用户，避免模型在信息不足时制造虚假的安心感。",
                "OG-Quote",
            ),
            p("人工确认门", "OG-H2"),
            p(
                "关键交互只有一步：用户必须主动勾选“我已打开合同原文，并核对上述条款”。在这之前，沟通草稿按钮保持禁用。草稿只进入可编辑文本框，系统没有任何自动发送 API。",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("08", "测试与运行数据", "离线可测试，在线可真调用。"),
            p("自动化验证", "OG-H2"),
            styled_table(
                [
                    ["测试", "预期结果", "当前状态"],
                    ["敏感信息脱敏", "手机号、邮箱、身份证均被替换", "通过"],
                    ["示例合同关键规则", "试用期、工时、社保至少命中", "通过"],
                    ["原文引用", "每个 quote 均存在于原文", "通过"],
                    ["证据引用", "所有 citation 均属于检索结果", "通过"],
                    ["Agent 轨迹", "六阶段名称与顺序一致", "通过"],
                    ["短文本输入", "少于 20 字符被拒绝", "通过"],
                    ["MCP", "initialize 与 tools/list 正常", "通过"],
                ],
                [170, 245, 80],
            ),
            Spacer(1, 10),
            p("真实联调", "OG-H2"),
            p(
                "在示例合同上，DeepSeek 两阶段调用约在 7 至 10 秒内完成。模型规划阶段触发原生 Tool Calling，检索阶段召回 8 条证据，最终生成 8 项条款发现和 5 项行动。离线模式下同一流程通常低于 1 秒完成。",
            ),
            p("复现命令", "OG-H2"),
            p(
                "cp .env.example .env<br/>python3 server/app.py<br/>python3 -m unittest discover -s tests -v",
                "OG-Quote",
            ),
            p(
                "项目运行时只依赖 Python 标准库。若未配置 DeepSeek Key，或设置 OFFERGUARD_OFFLINE=true，应用自动切换为本地 Agent，从而保证比赛现场演示不依赖外网。",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("09", "创新点与社会价值", "把 AI 的效率，限制在用户仍能理解与控制的范围内。"),
            p("技术创新", "OG-H2"),
            bullet("<b>双通道风险发现：</b>规则负责稳定召回，模型负责规划与解释。"),
            bullet("<b>可追溯 RAG：</b>每个结论都绑定合同原句与法规证据。"),
            bullet("<b>引用白名单：</b>模型无法越过本次检索结果凭空生成来源。"),
            bullet("<b>Tool Calling + MCP：</b>工具层既能服务 Web Agent，也能被其他 AI 客户端复用。"),
            p("应用创新", "OG-H2"),
            bullet("<b>决策工作流：</b>不做通用法律问答，只完成签约前的一次判断闭环。"),
            bullet("<b>透明过程：</b>Agent 轨迹直接进入产品界面，而不是隐藏在开发者日志中。"),
            bullet("<b>人工决策门：</b>AI 负责整理，用户保留最终表达和责任。"),
            bullet("<b>隐私前置：</b>在模型调用前完成脱敏，符合合同场景的高敏感特征。"),
            p(
                "社会价值不只是“帮助个人少吃亏”，还在于降低初入职场者与用人单位之间的信息不对称。同样的可解释工作流可以扩展到实习协议、租房合同和校园服务规则，为高校就业辅导提供低成本工具。",
                "OG-Quote",
            ),
            PageBreak(),
        ]
    )

    story.extend(
        [
            *section("10", "局限与后续路线", "清楚说明不能做什么，与展示能做什么同样重要。"),
            styled_table(
                [
                    ["当前局限", "下一阶段方案"],
                    ["只支持文本输入", "增加 DOCX/PDF 解析与页面级原文定位"],
                    ["规则库覆盖高频校园招聘条款", "引入律师复核的版本管理和引用时效"],
                    ["未内置城市工资和社保基数", "按城市与年份接入官方参数"],
                    ["单用户本地报告", "为高校就业中心提供匿名趋势看板"],
                    ["仅中文劳动合同", "扩展多语言与跨境就业场景"],
                ],
                [215, 280],
            ),
            Spacer(1, 14),
            p("部署强化路线", "OG-H2"),
            p(
                "正式公网部署将增加 HTTPS、反向代理、请求限流、脱敏访问日志、依赖扫描与管理端监控。知识库每次变更都记录版本、生效时间和复核人，避免过期法规继续被引用。",
            ),
            p("产品演进原则", "OG-H2"),
            p(
                "新增功能必须同时回答两个问题：它是否帮助用户做出更清楚的签约决定？它是否让证据或人工边界更透明？如果答案是否定的，就不进入主流程。",
                "OG-Quote",
            ),
            Spacer(1, 20),
            rule(),
            Spacer(1, 12),
            p(
                "OfferGuard · 职途罗盘<br/>2026 传智杯 AI Web 网页开发挑战赛参赛项目",
                "OG-H2",
            ),
            p(
                "本技术文档描述了当前可运行版本。项目输出用于就业风险识别与沟通准备，不构成正式法律意见。",
                "OG-Small",
            ),
        ]
    )
    return story


def build() -> None:
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=TOP,
        bottomMargin=BOTTOM,
        title="OfferGuard 职途罗盘技术文档",
        author="dAm0825",
        subject="2026 传智杯 AI Web 网页开发挑战赛",
    )
    cover_frame = Frame(LEFT, BOTTOM, CONTENT_WIDTH, PAGE_HEIGHT - TOP - BOTTOM, id="cover")
    body_frame = Frame(
        LEFT,
        20 * mm,
        CONTENT_WIDTH,
        PAGE_HEIGHT - 30 * mm - 20 * mm,
        id="body",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="Cover", frames=[cover_frame], onPage=cover_page),
            PageTemplate(id="Body", frames=[body_frame], onPage=body_page),
        ]
    )
    story = build_story()
    doc.build(story)
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    build()

