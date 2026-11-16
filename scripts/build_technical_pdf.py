from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
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
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "docs" / "MingBian-technical-document.pdf"

PAGE_W, PAGE_H = A4
LEFT, RIGHT = 18 * mm, 18 * mm
CONTENT = PAGE_W - LEFT - RIGHT

INK = colors.HexColor("#183743")
BLUE = colors.HexColor("#2F7898")
DEEP_BLUE = colors.HexColor("#245F78")
PALE_BLUE = colors.HexColor("#D7EDF6")
BLUE_2 = colors.HexColor("#BFDFEA")
PALE_MINT = colors.HexColor("#E7F3EC")
LIME = colors.HexColor("#CCEB72")
ORANGE = colors.HexColor("#F06C43")
PAPER = colors.HexColor("#F6F4EE")
SURFACE = colors.HexColor("#FFFDF9")
LINE = colors.HexColor("#CBDDE4")
MUTED = colors.HexColor("#5D7885")
WHITE = colors.white


def register_fonts() -> tuple[str, str]:
    paths = {
        "body": ("/Applications/Microsoft Word.app/Contents/Resources/DFonts/msyh.ttc", 0),
        "display": ("/Applications/Microsoft Word.app/Contents/Resources/DFonts/msyhbd.ttc", 0),
    }
    result = {}
    for key, (path, index) in paths.items():
        name = f"MingBian-{key}"
        try:
            pdfmetrics.registerFont(TTFont(name, path, subfontIndex=index))
            result[key] = name
        except Exception:
            result[key] = "Helvetica"
    return result["body"], result["display"]


BODY, DISPLAY = register_fonts()
styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        "MB-Body",
        fontName=BODY,
        fontSize=9,
        leading=15.5,
        textColor=INK,
        spaceAfter=7,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Small",
        fontName=BODY,
        fontSize=7.3,
        leading=11,
        textColor=MUTED,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Eyebrow",
        fontName=BODY,
        fontSize=7,
        leading=10,
        textColor=ORANGE,
        tracking=1.1,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        "MB-H1",
        fontName=DISPLAY,
        fontSize=27,
        leading=34,
        textColor=INK,
        spaceAfter=12,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-H2",
        fontName=DISPLAY,
        fontSize=16,
        leading=22,
        textColor=DEEP_BLUE,
        spaceBefore=12,
        spaceAfter=6,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Quote",
        fontName=DISPLAY,
        fontSize=12,
        leading=19,
        textColor=DEEP_BLUE,
        leftIndent=12,
        rightIndent=12,
        borderPadding=10,
        backColor=PALE_MINT,
        spaceBefore=8,
        spaceAfter=8,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Caption",
        fontName=BODY,
        fontSize=7,
        leading=10,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=9,
    )
)
styles.add(
    ParagraphStyle(
        "MB-Cover",
        fontName=DISPLAY,
        fontSize=36,
        leading=44,
        textColor=INK,
        spaceAfter=4,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Cover-Doc",
        fontName=DISPLAY,
        fontSize=23,
        leading=31,
        textColor=BLUE,
        spaceAfter=14,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Cover-Slogan",
        fontName=DISPLAY,
        fontSize=19,
        leading=28,
        textColor=DEEP_BLUE,
        spaceAfter=14,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Cover-Sub",
        fontName=BODY,
        fontSize=10.5,
        leading=18,
        textColor=MUTED,
        wordWrap="CJK",
    )
)


def clean(text: str) -> str:
    return text.replace("\u2011", "-").replace("—", "-")


def p(text: str, style: str = "MB-Body") -> Paragraph:
    return Paragraph(clean(text), styles[style])


def block(title: str, subtitle: str | None = None) -> list:
    values = [p(title.upper(), "MB-Eyebrow"), p(title, "MB-H1")]
    if subtitle:
        values.append(p(subtitle, "MB-Quote"))
    return values


def table(rows: list[list[str]], widths: list[float]) -> Table:
    data = []
    for row_index, row in enumerate(rows):
        data.append(
            [
                p(f"<b>{value}</b>" if row_index == 0 else value, "MB-Small")
                for value in row
            ]
        )
    result = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    result.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PALE_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), INK),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return result


def shot(name: str, caption: str, width: float = CONTENT) -> list:
    path = ASSETS / name
    if not path.exists():
        return []
    with PILImage.open(path) as image:
        ratio = image.height / image.width
    return [
        KeepTogether(
            [
                Spacer(1, 3),
                Image(str(path), width=width, height=width * ratio),
                p(caption, "MB-Caption"),
            ]
        )
    ]


class Mark(Flowable):
    def __init__(self, size: float = 58):
        super().__init__()
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        c.setStrokeColor(INK)
        c.setLineWidth(1)
        c.circle(29, 29, 24, stroke=1, fill=0)
        c.line(8, 36, 50, 22)
        c.line(34, 8, 37, 52)
        c.setFillColor(LIME)
        c.circle(27, 36, 5, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.circle(47, 17, 3.5, fill=1, stroke=0)


class AgentFlow(Flowable):
    def __init__(self):
        super().__init__()
        self.width = CONTENT
        self.height = 230

    def draw(self):
        c = self.canv
        boxes = [
            ("01", "可疑消息"),
            ("02", "本地脱敏"),
            ("03", "知识检索"),
            ("04", "模型生成"),
            ("05", "安全复核"),
        ]
        gap = 18
        box_w = (CONTENT - gap * (len(boxes) - 1)) / len(boxes)
        box_y = 126
        box_h = 60

        def horizontal_arrow(x1: float, y1: float, x2: float, y2: float):
            c.setStrokeColor(colors.HexColor("#8DBDD0"))
            c.setLineWidth(1)
            c.line(x1, y1, x2 - 3, y2)
            c.line(x2 - 7, y2 + 3, x2, y2)
            c.line(x2 - 7, y2 - 3, x2, y2)

        def vertical_arrow(x: float, y1: float, y2: float):
            c.setStrokeColor(colors.HexColor("#8DBDD0"))
            c.setLineWidth(1)
            c.line(x, y1, x, y2 + 7)
            c.line(x - 3, y2 + 7, x, y2)
            c.line(x + 3, y2 + 7, x, y2)

        for index, (code, label) in enumerate(boxes):
            x = index * (box_w + gap)
            c.setFillColor(BLUE_2 if index in (0, 4) else PALE_BLUE)
            c.setStrokeColor(colors.HexColor("#B8D8E4"))
            c.setLineWidth(0.6)
            c.roundRect(x, box_y, box_w, box_h, 9, fill=1, stroke=1)
            c.setFillColor(ORANGE)
            c.setFont(BODY, 6)
            c.drawString(x + 9, box_y + 43, code)
            c.setFillColor(INK)
            c.setFont(BODY, 8)
            c.drawCentredString(x + box_w / 2, box_y + 20, label)
            if index < len(boxes) - 1:
                horizontal_arrow(
                    x + box_w + 4,
                    box_y + box_h / 2,
                    x + box_w + gap - 4,
                    box_y + box_h / 2,
                )

        panel_y = 22
        panel_h = 54
        c.setFillColor(PALE_MINT)
        c.setStrokeColor(colors.HexColor("#C7DFD5"))
        c.roundRect(0, panel_y, CONTENT, panel_h, 9, fill=1, stroke=1)
        c.setFillColor(DEEP_BLUE)
        c.setFont(BODY, 8)
        c.drawString(14, panel_y + 32, "浏览器页面与结果展示")

        chip_labels = ["风险报告", "情景复盘", "智能回答"]
        chip_w = 78
        chip_gap = 8
        chip_x = CONTENT - 14 - (chip_w * 3 + chip_gap * 2)
        for index, label in enumerate(chip_labels):
            x = chip_x + index * (chip_w + chip_gap)
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.HexColor("#D2E5EB"))
            c.roundRect(x, panel_y + 17, chip_w, 22, 6, fill=1, stroke=1)
            c.setFillColor(MUTED)
            c.setFont(BODY, 6.5)
            c.drawCentredString(x + chip_w / 2, panel_y + 25, label)

        connector_x = box_w * 2.5 + gap * 2
        vertical_arrow(connector_x, box_y - 1, panel_y + panel_h)
        c.setFillColor(MUTED)
        c.setFont(BODY, 6.3)
        c.drawString(connector_x + 8, panel_y + panel_h + 17, "结构化结果返回页面")


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PALE_BLUE)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#C7E4EF"))
    canvas.circle(PAGE_W + 35, PAGE_H - 95, 250, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#86BFD3"))
    canvas.circle(PAGE_W - 10, PAGE_H - 170, 190, fill=0, stroke=1)
    canvas.circle(PAGE_W - 10, PAGE_H - 170, 130, fill=0, stroke=1)
    canvas.setFillColor(ORANGE)
    canvas.circle(PAGE_W - 90, PAGE_H - 112, 8, fill=1, stroke=0)
    canvas.setFillColor(LIME)
    canvas.circle(PAGE_W - 235, PAGE_H - 258, 5, fill=1, stroke=0)
    canvas.setFillColor(INK)
    canvas.setFont(BODY, 6.5)
    canvas.drawString(LEFT, 18 * mm, "2026 传智杯网页开发挑战赛")
    canvas.drawRightString(PAGE_W - RIGHT, 18 * mm, "技术设计文档")
    canvas.restoreState()


def body_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setStrokeColor(LINE)
    canvas.line(LEFT, PAGE_H - 13 * mm, PAGE_W - RIGHT, PAGE_H - 13 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont(BODY, 6.2)
    canvas.drawString(LEFT, PAGE_H - 17 * mm, "智能反诈训练系统")
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 17 * mm, "技术设计")
    canvas.line(LEFT, 13 * mm, PAGE_W - RIGHT, 13 * mm)
    canvas.drawString(LEFT, 8.5 * mm, "校园反诈训练")
    canvas.drawRightString(PAGE_W - RIGHT, 8.5 * mm, f"{canvas.getPageNumber():02d}")
    canvas.restoreState()


def story() -> list:
    content = [
        Spacer(1, 28 * mm),
        Mark(),
        Spacer(1, 14 * mm),
        p("2026 传智杯网页开发挑战赛", "MB-Eyebrow"),
        p("智能反诈训练系统", "MB-Cover"),
        p("项目技术文档", "MB-Cover-Doc"),
        p("识破一次，才能真正学会拒绝。", "MB-Cover-Slogan"),
        p(
            "面向大学生的校园反诈陪练。<br/>"
            "从可疑消息检测，到压力情景演练，再到真实新闻证据与智能助手。",
            "MB-Cover-Sub",
        ),
        Spacer(1, 10 * mm),
        p(
            "本文件说明作品的问题定义、信息架构、核心算法、模型调用边界、数据结构、"
            "安全设计、测试结果与部署方式，并配合关键页面截图展示实际实现。"
        ),
        Spacer(1, 16 * mm),
        table(
            [
                ["01", "02", "03"],
                ["多页面结构", "可追溯智能", "真实新闻"],
                ["独立任务页面", "规则 + 检索 + 安全复核", "公开案例直达原文"],
            ],
            [CONTENT / 3] * 3,
        ),
        NextPageTemplate("Body"),
        PageBreak(),
    ]

    content += [
        *block("01 产品概述", "智能反诈训练系统把反诈从“知识阅读”推进到“压力下练习”。"),
        p(
            "大学生常见的诈骗场景集中在兼职刷单、冒充客服、冒充公检法、注销校园贷、门票私下交易和游戏账号交易。"
            "普通宣传页通常只展示警示口号，用户看懂之后仍可能在对方持续施压时作出错误操作。"
        ),
        p(
            "本作品的核心问题不是“学生是否听过反诈提醒”，而是“当对方要求立刻转账、共享屏幕或提供验证码时，"
            "学生能否识别风险并用安全的方式拒绝”。因此，产品把反诈教育拆成识别、解释、示范、演练和复盘五个环节，"
            "每一步都提供可操作的下一步，而不只是停留在警告口号。"
        ),
        p("目标用户与设计原则", "MB-H2"),
        p(
            "主要用户为本科生、应届毕业生、研究生或博士生，以及需要开展学生安全教育的老师和辅导员。"
            "产品不要求填写真实手机号、身份证或银行卡信息，演示时可以使用虚构消息和虚构对话完成全部训练。"
        ),
        table(
            [
                ["设计目标", "具体做法", "验证结果"],
                ["降低识别门槛", "给出可疑原句、风险标签和通俗解释", "用户能看到“为什么危险”"],
                ["形成正确反应", "用压力对话练习拒绝、核验和止损", "训练结果转化为安全分"],
                ["建立可信证据", "连接本地知识与公开新闻案例", "每个分析结论可有来源"],
                ["适应真实设备", "桌面端与手机端独立布局", "390px 宽度无横向溢出"],
            ],
            [110, 210, 140],
        ),
        p(
            "系统把完整过程拆为：设置安全档案、检测可疑消息、阅读风险与证据、进入同类情景演练、查看成长记录、随时咨询智能助手。"
            "每个任务都由独立路由承载，避免把所有功能堆在首页。",
        ),
        table(
            [
                ["页面", "任务", "用户结果"],
                ["/", "建立产品认知", "选择检测或演练入口"],
                ["/scan", "粘贴可疑消息", "触发风险检测"],
                ["/report/:id", "查看独立报告", "理解信号、证据和行动"],
                ["/practice", "压力对话演练", "练习拒绝与核验"],
                ["/cases", "阅读真实案例", "点击进入新闻原文"],
                ["/dashboard", "查看成长记录", "识别薄弱风险类型"],
                ["/assistant", "连续咨询", "获得带来源的安全回答"],
            ],
            [88, 160, 210],
        ),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("02 信息架构", "一个路由只承担一个主要任务。"),
        p(
            "顶部导航在当前页面保持明确激活状态。检测输入与报告结果分离；报告内部使用标签页；"
            "案例页直接跳转外部新闻；情景演练不追加在首页下方，而是使用独立的聊天工作台。",
        ),
        p(
            "前端采用 Vue 3 与 Vue Router 构建单页应用外壳，但每个业务任务拥有独立 URL、独立标题和独立页面边界。"
            "路由切换时只替换主内容区，顶部导航、账户状态和全局提示保持稳定。这样既保留单页应用的流畅切换，"
            "也避免把所有模块堆叠成一张需要不断下拉的展示页。"
        ),
        table(
            [
                ["层次", "实现", "职责"],
                ["界面层", "Vue 组件与独立路由", "输入、展示与交互反馈"],
                ["状态层", "响应式状态与 localStorage", "账户状态、检测记录、训练进度"],
                ["服务层", "Python HTTP API", "接口路由、参数校验与安全复核"],
                ["智能层", "规则引擎、RAG 与 DeepSeek", "风险解释、角色扮演和问答"],
                ["数据层", "JSON 知识库与案例库", "反诈知识、公开案例和挑战题库"],
            ],
            [85, 180, 195],
        ),
        p(
            "路由之外，首页情报台承担“导航中枢”的作用：校园诈骗雷达可切换风险主题，并直接携带分类参数进入案例页，"
            "或携带场景参数进入演练页。这样用户在首页看到的不是静态装饰，而是能够进入具体训练任务的交互入口。"
        ),
        AgentFlow(),
        p("图 2-1 从输入到安全复核的请求链路", "MB-Caption"),
        p(
            "本地规则先完成敏感信息处理和稳定风险命中，智能模型再在此基础上生成解释、角色扮演或问答。"
            "这一分工可以降低模型漏判，也避免网络波动导致演示完全不可用。",
            "MB-Quote",
        ),
        *shot("home.png", "图 2-2 系统首页：训练情报台、动态风险雷达与独立入口"),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("03 风险检测", "规则负责召回，模型负责把风险说清楚。"),
        p(
            "风险检测请求首先经过本地安全处理，再进入规则匹配和知识检索，最后才调用智能模型。"
            "该顺序保证真实手机号、邮箱、证件号和银行卡号不会直接进入模型请求，同时让纯规则能力在网络异常时仍能工作。"
        ),
        table(
            [
                ["步骤", "处理内容", "失败时的策略"],
                ["1. 输入检查", "限制长度并检查有效消息", "返回明确表单提示"],
                ["2. 本地脱敏", "屏蔽手机号、邮箱、证件号和银行卡", "只将脱敏后的文本送入后续流程"],
                ["3. 规则召回", "匹配刷单、身份冒充、共享屏幕等信号", "保留确定性结果"],
                ["4. 知识检索", "召回相关反诈知识和相似案例", "返回本地证据条目"],
                ["5. 模型解释", "在给定资料范围内生成通俗说明", "回退到规则生成的解释"],
                ["6. 安全复核", "过滤危险建议并整理行动清单", "输出可控、可执行的安全步骤"],
            ],
            [86, 230, 145],
        ),
        *shot("scan.png", "图 3-1 风险检测工作台：指标、快捷模板和检测记录", CONTENT - 5),
        p(
            "检测规则覆盖刷单返利、冒充公检法、假客服、校园贷、虚假票务、游戏交易、虚假投资和冒充熟人等高频风险，"
            "并对屏幕共享、验证码、安全账户、保证金、先转账和网贷等动作额外加权。"
            "系统优先返回证据检索结果，再允许模型在证据范围内生成解释。",
        ),
        p(
            "风险分数用于课堂训练中的相对判断，不等同于司法或警方结论。高分表示消息中出现多项高风险特征，"
            "需要立即暂停转账、共享屏幕或提交验证码；低分也不代表绝对安全。报告中同时保留触发信号、消息原句、"
            "风险解释和建议行动，让用户能够看到分数之外的具体依据。"
        ),
        p("输出结构与交互", "MB-H2"),
        p(
            "检测完成后先打开详情窗口，集中展示风险级别、风险类型、原文证据、行动核对进度和完整报告入口。"
            "用户完成建议行动后可以勾选清单，进度条会实时变化；需要深入阅读时再进入独立报告页，"
            "在“风险诊断 / 案例参照 / 行动清单”三个标签之间切换。"
        ),
        table(
            [
                ["信号", "处理方式"],
                ["手机号 / 证件号 / 邮箱 / 银行卡", "模型调用前本地脱敏"],
                ["刷单、垫付、返利", "匹配刷单返利规则和知识条目"],
                ["屏幕共享、验证码", "标记为关键高风险动作"],
                ["公检法、涉案、安全账户", "匹配权威冒充与恐惧施压模式"],
                ["订单冻结、二次转账", "匹配客服退款和虚假交易模式"],
            ],
            [180, 260],
        ),
        p(
            "模型只接收脱敏文本、规则命中结果和检索到的知识片段，并被要求输出结构化 JSON。"
            "服务端会检查字段类型、风险级别和行动建议，再补充来源列表与本地兜底内容。"
            "因此即使模型超时或返回格式不完整，用户仍能看到风险类型、关键原句和基础处置步骤。"
        ),
        *shot("scan-detail.png", "图 3-2 检测详情窗口：风险发现与行动核对"),
        *shot("report.png", "图 3-3 独立报告页：风险分、可疑原句与证据标签"),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("04 真实新闻案例", "点击卡片即可前往对应新闻原文。"),
        p(
            "案例页当前收录 11 条公开报道，覆盖刷单返利、冒充公检法、演唱会门票、注销校园贷、游戏账号交易、"
            "虚假投资理财、冒充熟人、教育退费、虚假购物、免费游戏皮肤和假助学金。"
            "应用只保存标题、摘要、来源、日期、损失金额与教育要点，不复制整篇新闻。",
        ),
        p("来源筛选与呈现原则", "MB-H2"),
        p(
            "案例优先选择公安机关、官方媒体和公开新闻报道，并保留来源名称、发布日期、损失金额与原文链接。"
            "产品只摘录与识别风险有关的事实，不复制整篇报道，也不对具体案件作法律判断。"
            "每个案例都提炼“本案警示”，把新闻事实转换为用户能直接使用的判断原则。"
        ),
        p(
            "案例数据采用独立 JSON 保存，字段包括分类、标题、来源、日期、损失、摘要、警示、标签和原文 URL。"
            "前端按分类生成筛选按钮，首页雷达也能通过查询参数直达指定分类。外链统一使用新窗口打开，"
            "避免用户离开训练系统后丢失当前页面状态。"
        ),
        *shot("cases.png", "图 4-1 真实案例档案与分类筛选", CONTENT - 5),
        table(
            [
                ["来源", "案例", "教育重点"],
                ["人民网吉林频道", "大学生刷单被骗 4.2 万元", "拒绝先垫付与返利任务"],
                ["上观新闻", "冒充电信诈骗损失 142 万余元", "公安不会电话索要保证金"],
                ["泉州网", "演唱会门票被骗 4.8 万余元", "留在官方票务担保平台"],
                ["杭州网警", "注销校园贷诈骗", "拒绝征信话术和屏幕共享"],
                ["镇江市公安局", "游戏账号交易被骗 4000 元", "拒绝解冻费与伪造平台"],
                ["河池市公安局", "投资、熟人、退费、购物等 6 类案例", "拒绝陌生链接、先缴费与私下转账"],
            ],
            [105, 190, 170],
        ),
        p(
            "所有原文链接都在应用卡片上直接展示，便于评审快速核验来源。"
            "案例详情不依赖模型临时生成，确保新闻标题、来源和日期能够被复核；模型只负责把用户问题与有关案例建立联系。",
        ),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("05 情景演练", "智能模型不是答题器，它要制造可控制的压力。"),
        *shot("practice.png", "图 5-1 多轮演练：对方施压、用户拒绝、对方继续追问与即时复盘", CONTENT - 5),
        p(
            "用户可从 10 个校园高频场景中选择，智能模型以虚构诈骗角色持续施压。每次回复后，系统给出风险反馈、"
            "更安全的表达和安全分变化。场景禁止使用真实账户、电话或可执行诈骗资源。",
        ),
        p("对话状态与评分机制", "MB-H2"),
        p(
            "每个场景包含开场话术、训练目标、连续施压步骤和安全规则。用户发送回复时，前端将场景 id 和经过清理的"
            "对话历史提交给服务端；服务端先执行危险关键词与防御性表达的确定性判断，再允许模型生成下一句虚构话术。"
            "这样既能保持角色扮演的自然感，也不会把安全评分完全交给模型随机决定。"
        ),
        p(
            "页面将互动包装成“模拟来电”：展示虚构来电身份、通话计时、动态紧张度和快捷安全话术。"
            "紧张度由安全分反向映射得到，分数下降时压力条上升；右侧即时复盘同步展示风险解释与更安全的回答，"
            "帮助用户把“知道不能转账”转化为“能够说出拒绝和核验步骤”。"
        ),
        table(
            [
                ["用户行为", "判定", "教学结果"],
                ["提供验证码、答应屏幕共享", "高风险", "安全分下降并解释后果"],
                ["明确拒绝、官方核验、报警止损", "防御行为", "安全分上升并给出替代话术"],
                ["含糊回复或继续询问", "需要警觉", "提示停止操作和核验渠道"],
            ],
            [200, 100, 160],
        ),
        p(
            "演练结束后，最终安全分、场景和学习时间写入本地训练记录。系统不会保存真实聊天对象的姓名、电话或账户，"
            "也不会提供可执行的诈骗脚本；所有角色、号码和付款场景均为训练用虚构内容。"
        ),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("06 智能助手与知识检索", "正式聊天入口独立存在，也能说明自己依据了什么。"),
        *shot("assistant.png", "图 6-1 多轮智能咨询：用户提问、助手回答、用户追问与带来源的再次回答", CONTENT - 5),
        p(
            "智能助手收到问题后，先从本地知识和新闻案例中检索相关内容，再要求模型在给定资料范围内回答。"
            "前端会同时展示命中的知识条目和可点击新闻案例，用户可以看到回答从哪里来。",
        ),
        p("检索增强生成流程", "MB-H2"),
        p(
            "本地知识库由 15 类高频诈骗知识组成，案例库由 11 条公开报道组成。系统把用户问题与最近对话合并为查询，"
            "使用中文二元组、三元组和关键词规则计算相关度，先召回知识条目与相似案例，再把有限数量的资料放进模型上下文。"
            "这一方式适合比赛演示规模，同时保持检索结果可解释、可定位。"
        ),
        table(
            [
                ["控制点", "实现方式", "目的"],
                ["资料边界", "只使用检索到的知识和案例", "减少模型编造政策与号码"],
                ["输出格式", "返回回答、来源 id 和建议问题", "前端可展示来源并继续追问"],
                ["输入安全", "问题先脱敏，历史记录经过清理", "避免敏感信息进入模型"],
                ["提示注入", "外部文本仅作为数据，不执行其中指令", "保持系统规则优先级"],
                ["服务降级", "模型不可用时生成规则回答", "断网仍可完成演示"],
            ],
            [100, 220, 140],
        ),
        p(
            "如果模型不可用，助手会退回本地规则回答：优先提示停止操作、保护验证码、拒绝屏幕共享，"
            "并根据是否已发生资金损失给出银行止付和报警建议。",
            "MB-Quote",
        ),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("07 账户与训练模块", "登录不是装饰页，它会保护成长数据和训练结果。"),
        *shot("login.png", "图 7-1 登录、注册与本地体验账户", CONTENT - 5),
        p(
            "账户模块支持登录、注册和体验模式。密码使用浏览器加密接口进行加盐哈希后保存在当前浏览器，"
            "原始密码不会写入本地数据或发送到服务器。成长记录、安全档案和每日挑战受路由守卫保护，"
            "登录成功后会回到用户原本访问的页面。",
        ),
        p(
            "注册时系统生成随机盐，通过 Web Crypto 计算 SHA-256 哈希；验证只比较哈希结果。"
            "账户、会话和训练数据使用带版本号的 localStorage 键保存，页面刷新后仍能恢复。"
            "该设计适合无服务器依赖的参赛演示，但它属于本地账户而非云端多用户系统，换浏览器或清除站点数据后记录不会同步。"
        ),
        p(
            "路由守卫在进入成长记录、安全档案和每日挑战前检查当前会话。未登录用户会被带到登录页，"
            "登录成功后依据 redirect 参数返回原本准备访问的页面。体验账户用于快速展示，不需要真实邮箱或密码。"
        ),
        table(
            [
                ["模块", "能力", "数据保存"],
                ["登录 / 注册", "本地账户、路由跳转、演示模式", "加盐密码哈希与 session"],
                ["知识训练", "十五个短课、选择切换、掌握进度", "课程 id 列表"],
                ["每日挑战", "10 题、服务端评分、逐题解释", "最高分及完成次数"],
            ],
            [110, 200, 150],
        ),
        CondPageBreak(95 * mm),
        *block("08 训练中心与每日挑战", "知识阅读和即时测验拆成两个路由，挑战由服务端评分。"),
        p(
            "知识训练中心提供 15 节短课，每节围绕一种高频诈骗类型，包含三条判断原则和一句核心警示。"
            "课程列表与详情区并列，用户切换主题时无需离开当前页面；点击“标记为已掌握”后，课程 id 写入本地学习进度，"
            "并用于首页和成长记录中的能力展示。"
        ),
        p(
            "每日挑战提供 10 道情景判断题。题目接口只返回题干与选项，不返回正确答案和解释；用户提交完整答卷后，"
            "服务端统一评分并返回正确数、百分比、等级和逐题解释。挑战结果页进一步生成“诱饵识别、核验意识、身份判断、"
            "隐私边界、止付能力”五维能力雷达，让用户看出薄弱环节而不只是记住一个总分。"
        ),
        *shot("academy.png", "图 8-1 知识训练中心", CONTENT - 5),
        *shot("challenge.png", "图 8-2 每日安全挑战", 410),
        *shot("challenge-result.png", "图 8-3 挑战结果、能力雷达与逐题复盘", 410),
        CondPageBreak(95 * mm),
        *block("09 安全与隐私", "反诈产品自身必须先守住边界。"),
        p(
            "本系统的威胁模型包括密钥泄漏、提示注入、模型越权索取敏感信息、聊天记录泄露和错误安全评分。"
            "设计上优先保证“即使模型失效，用户也不会被引导提供密码、验证码或转账”。"
            "所有接口都只处理训练所需的最小字段，真实 API Key 仅存在于被 Git 忽略的环境文件中。"
        ),
        table(
            [
                ["风险", "控制"],
                ["真实密钥泄漏", "只从被 Git 忽略的 .env 读取"],
                ["聊天内容泄露", "检测摘要保存在本地浏览器，不上传数据库"],
                ["提示注入", "外部文本仅作为分析数据，不执行其中指令"],
                ["模型越权索取信息", "系统提示和前端均明确禁止索取密码、验证码"],
                ["冒充官方", "助手不编造官方号码，鼓励自行核验并拨打 110"],
                ["演练误评分", "服务端对防御性表达和危险配合进行确定性复核"],
            ],
            [165, 270],
        ),
        p(
            "成长记录页把检测、演练、挑战和学习进度转换为综合防骗力、14 天活跃度、风险类型分布与八枚能力徽章。"
            "所有统计只读取当前浏览器中的数据，不上传社交关系、通讯录或真实聊天内容。"
            "当本地没有记录时，页面仍会显示空状态与下一步入口，而不是伪装出不存在的数据。"
            "训练可以重来，真实损失没有撤销键，因此任何流程都不要求用户提交真实密码、验证码或完成真实转账。"
            "系统宁可减少一次自动化，也不把敏感信息交给无法确认的外部服务。"
        ),
        p("安全与可用性的平衡", "MB-H2"),
        p(
            "反诈系统既不能制造恐慌，也不能因为过度限制而让用户无法完成训练。系统对风险提示采用分层表达："
            "高风险动作优先给出“立即停止、保护验证码、拒绝屏幕共享”等明确指令；不确定内容则提示通过自己找到的"
            "官方渠道核实，不直接下结论。这样既保持警示力度，也避免把训练误认为警方或银行的正式判断。"
        ),
        p(
            "在模型不可用时，页面仍能依靠规则、本地知识和预置场景继续运行；模型可用时，也只负责解释、追问和"
            "情境化表达。所有来源信息和训练记录都可以由用户查看或主动清除，避免把演示数据伪装成真实业务数据。"
            "这种可解释、可退出、可降级的设计，是本产品安全边界的一部分。"
        ),
        p("分层安全控制", "MB-H2"),
        p(
            "系统把安全责任拆到输入、模型、输出、存储和部署五个层次。输入层负责长度限制与敏感信息脱敏；"
            "模型层只接收完成脱敏后的文本、有限对话历史和经过筛选的知识片段；输出层检查字段结构、风险等级、"
            "行动建议和来源引用；存储层按用途分别保存最小字段；部署层通过环境变量隔离真实密钥。"
        ),
        table(
            [
                ["控制层", "主要措施", "验证方式"],
                ["输入层", "手机号、邮箱、证件号、银行卡号先脱敏", "自动化脱敏测试与接口返回检查"],
                ["模型层", "限定角色、资料范围和输出 JSON 结构", "字段校验、异常捕获与本地兜底"],
                ["输出层", "禁止索取密码、验证码，过滤不安全话术", "危险/防御性表达的正负向评分测试"],
                ["存储层", "使用带版本号键名，限制记录数量与保存字段", "本地会话、历史记录与退出流程检查"],
                ["部署层", "密钥只从被 Git 忽略的环境文件读取", "仓库密钥扫描与公开文件检查"],
            ],
            [82, 230, 150],
        ),
        p(
            "隐私最小化不仅体现在“少收集”，也体现在“少保存”。检测与演练只保留训练复盘所需的风险类型、分数、"
            "时间与摘要，不保存完整的真实聊天原文；模型来源在界面上统一转换用户可理解的中文名称。"
            "如果用户选择退出登录，当前会话立即清除；训练记录可以由用户主动清除，系统不会暗中恢复。"
        ),
        Spacer(1, 12),
        *shot("dashboard.png", "图 9-1 成长记录页：综合防骗力、训练活跃度、风险分布和徽章"),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("10 测试与部署", "在线可联调，离线也能演示。"),
        p(
            "后端自动化测试覆盖高风险消息分类、冒充公检法识别、公开案例返回、敏感信息脱敏、助手知识回答、"
            "演练正负向评分、挑战答案保护、挑战评分和内容数量下限。前端通过脚本语法检查、浏览器控制台监控、"
            "桌面与 390px 手机宽度截图检查确认主要页面无运行错误和横向溢出。"
        ),
        table(
            [
                ["验证", "结果"],
                ["刷单消息风险类型与分数", "通过"],
                ["冒充公检法场景识别", "通过"],
                ["真实新闻案例返回", "通过"],
                ["手机号、邮箱和证件号脱敏", "通过"],
                ["智能助手本地知识回答", "通过"],
                ["危险演练回复负向评分", "通过"],
                ["防御性演练回复正向评分", "通过"],
            ["挑战题不泄漏正确答案", "通过"],
            ["每日挑战评分", "通过"],
            ["案例、知识、演练和挑战均不少于 10 项", "通过"],
            ],
            [280, 160],
        ),
        p(
            "测试重点不是证明模型永远正确，而是验证确定性边界：危险消息能够被规则召回，敏感信息先脱敏，"
            "危险配合会扣分，明确拒绝和核验会加分，挑战接口不会提前泄露答案。"
            "上述内容均为可在本地重复执行的自动化用例，便于后续迭代时做回归检查。"
        ),
        p("运行命令", "MB-H2"),
        p(
            "<font name='Courier'>cp .env.example .env</font><br/>"
            "<font name='Courier'>python3 server/app.py</font><br/>"
            "<font name='Courier'>python3 -m unittest discover -s tests -v</font>",
            "MB-Quote",
        ),
        p(
            "前端框架运行库已放入项目目录，运行网站不依赖外部资源站点。智能模型仅通过服务端接口调用。",
        ),
        p("后续部署", "MB-H2"),
        p(
            "正式部署应增加 HTTPS、反向代理、请求限流、日志脱敏、依赖扫描和内容监控。"
            "新闻链接需在评审网络环境中定期复核，避免转载页失效。",
        ),
        p(
            "部署时需要把 DEEPSEEK_API_KEY 放入平台环境变量，确认静态资源、API 路由和健康检查地址均可访问。"
            "若外部模型暂时不可用，系统仍然可以依靠规则与本地知识库完成检测、情景演练和挑战流程。"
        ),
        CondPageBreak(95 * mm),
    ]

    content += [
        *block("11 创新点与社会价值"),
        p("技术创新", "MB-H2"),
        p(
            "第一，规则引擎与智能模型形成双通道识别。规则负责稳定命中结构化风险，模型负责把风险解释成用户能理解的语言；"
            "即使模型不可用，系统也能给出基础判断。第二，本地知识与公开新闻案例共同支撑回答，"
            "用户可以看到回答所依据的知识条目和可点击的新闻来源，减少“AI 随口回答”的不信任感。"
        ),
        p(
            "第三，情景演练把教育内容转化为压力下的行为训练。系统不仅问用户“是否正确”，还会连续施压、"
            "计算安全分并给出替代话术。第四，确定性安全评分复核能够纠正模型对“我不会共享屏幕”等防御性表达的误判，"
            "让结果更适合反复训练和比较。"
        ),
        p("应用创新", "MB-H2"),
        p(
            "产品用独立路由拆分识别、报告、训练、案例、成长和助手，避免一张长页面同时承担所有任务。"
            "真实新闻卡直接跳转原文，首页可交互雷达把案例数据、风险说明和训练入口连接起来。"
            "安全档案与成长记录围绕本地数据构建，减少敏感信息上传，适合校园内快速部署和演示。"
        ),
        p("当前边界与后续方向", "MB-H2"),
        p(
            "当前账户和训练记录保存在本地浏览器，适合单设备体验，但跨设备同步能力有限；案例为人工整理的公开教育材料，"
            "需要持续核验链接与内容时效；风险分数用于训练判断，不替代警方、银行或法律机构的正式结论。"
            "后续可增加服务端账户、教师班级管理、训练结果导出和区域化案例库，但应继续保持最小化收集和脱敏原则。"
        ),
        p(
            "系统的价值不只是帮助学生记住反诈口号，而是提供一次可重复的低风险训练。"
            "高校保卫处、辅导员和学生组织也可以使用相同框架开展定制化安全教育。",
            "MB-Quote",
        ),
        CondPageBreak(95 * mm),
        *block("12 附录：主要接口与数据字段", "查看页面之外的接口边界，便于复现与后续维护。"),
        p(
            "系统前端通过相对路径调用同源 API，不把模型密钥暴露给浏览器。以下接口均返回 JSON，"
            "参数校验失败时返回可读的错误信息；情景演练和助手接口会对聊天历史做长度及敏感信息清理。"
        ),
        table(
            [
                ["接口", "主要输入", "主要输出", "用途"],
                ["POST /api/detect", "可疑消息文本", "分数、等级、分类、信号、证据、行动", "可疑消息检测"],
                ["POST /api/practice", "场景 id 与对话历史", "角色回复、反馈、安全分变化、结束标记", "压力情景演练"],
                ["POST /api/assistant", "问题与最近对话", "回答、知识证据、新闻案例、模型来源", "智能问答"],
                ["POST /api/challenges/grade", "题目 id 与所选答案", "分数、正确数、等级、逐题解释", "挑战评分"],
                ["GET /api/stats", "无", "案例、知识类型、场景数量", "首页数据展示"],
            ],
            [125, 150, 190, 100],
        ),
        p("浏览器本地数据", "MB-H2"),
        table(
            [
                ["存储键", "内容", "生命周期"],
                ["mingbian-profile-v1", "身份、关注场景、提示强度", "当前浏览器长期保存"],
                ["mingbian-reports-v1", "检测摘要与报告字段", "当前浏览器，最多保留 30 条"],
                ["mingbian-practice-v1", "演练场景、安全分、时间", "当前浏览器，最多保留 40 条"],
                ["mingbian-learning-v1", "已掌握课程 id", "当前浏览器长期保存"],
                ["mingbian-challenges-v1", "挑战分数与复盘结果", "当前浏览器，最多保留 30 条"],
                ["mingbian-session-v1", "当前登录会话", "退出登录后清除"],
            ],
            [185, 230, 150],
        ),
        p(
            "数据结构使用带版本号的键名，便于后续升级时迁移或清理。检测与演练记录只保存训练需要的最小字段，"
            "不保存完整聊天原文；真实账户密码只保存加盐哈希，不保存明文。"
        ),
        Spacer(1, 20),
        p("智能反诈训练系统", "MB-H2"),
        p(
            "2026 传智杯网页开发挑战赛参赛项目。"
            "本应用用于风险教育，不替代警方、银行或法律专业机构的正式结论。",
            "MB-Small",
        ),
    ]
    return content


def build():
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=LEFT,
        rightMargin=RIGHT,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="智能反诈训练系统技术文档",
        subject="2026 传智杯网页开发挑战赛",
        author="dAm0825",
    )
    cover_frame = Frame(LEFT, 18 * mm, CONTENT, PAGE_H - 36 * mm)
    body_frame = Frame(LEFT, 20 * mm, CONTENT, PAGE_H - 43 * mm)
    doc.addPageTemplates(
        [
            PageTemplate("Cover", [cover_frame], onPage=cover),
            PageTemplate("Body", [body_frame], onPage=body_page),
        ]
    )
    doc.build(story())
    print(f"Built {OUTPUT}")


if __name__ == "__main__":
    build()

