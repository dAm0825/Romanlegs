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
    Flowable,
    Frame,
    Image,
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

INK = colors.HexColor("#071B27")
GREEN = colors.HexColor("#0D3E42")
LIME = colors.HexColor("#CCEB72")
ORANGE = colors.HexColor("#F06C43")
PAPER = colors.HexColor("#F4F1E9")
SURFACE = colors.HexColor("#FBFAF6")
LINE = colors.HexColor("#D8D2C5")
MUTED = colors.HexColor("#65736D")
WHITE = colors.white


def register_fonts() -> tuple[str, str]:
    paths = {
        "body": ("/System/Library/Fonts/STHeiti Light.ttc", 0),
        "display": ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
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
        textColor=GREEN,
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
        textColor=GREEN,
        leftIndent=12,
        rightIndent=12,
        borderPadding=10,
        backColor=colors.HexColor("#EDF3D9"),
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
        fontSize=39,
        leading=48,
        textColor=WHITE,
        spaceAfter=17,
        wordWrap="CJK",
    )
)
styles.add(
    ParagraphStyle(
        "MB-Cover-Sub",
        fontName=BODY,
        fontSize=11,
        leading=19,
        textColor=colors.HexColor("#B9C8C4"),
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
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
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
        Spacer(1, 3),
        Image(str(path), width=width, height=width * ratio),
        p(caption, "MB-Caption"),
    ]


class Mark(Flowable):
    def __init__(self, size: float = 58):
        super().__init__()
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        c.setStrokeColor(WHITE)
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
        self.height = 210

    def draw(self):
        c = self.canv
        boxes = [
            ("输入", "可疑消息"),
            ("本地", "脱敏 / 规则"),
            ("检索", "知识 / 案例"),
            ("模型", "解释 / 演练"),
            ("复核", "安全边界"),
        ]
        gap = 9
        box_w = (CONTENT - gap * (len(boxes) - 1)) / len(boxes)
        for index, (code, label) in enumerate(boxes):
            x = index * (box_w + gap)
            c.setFillColor(INK if index in (0, 4) else colors.HexColor("#E8EAE2"))
            c.roundRect(x, 105, box_w, 58, 8, fill=1, stroke=0)
            c.setFillColor(LIME if index in (0, 4) else ORANGE)
            c.setFont(BODY, 6)
            c.drawString(x + 7, 146, code)
            c.setFillColor(WHITE if index in (0, 4) else INK)
            c.setFont(BODY, 7)
            c.drawString(x + 7, 122, label)
            if index < len(boxes) - 1:
                c.setStrokeColor(LINE)
                c.line(x + box_w, 134, x + box_w + gap, 134)
        c.setFillColor(PAPER)
        c.roundRect(0, 18, CONTENT, 56, 8, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.setFont(BODY, 7)
        c.drawString(12, 45, "浏览器页面")
        c.drawRightString(CONTENT - 12, 45, "报告 / 情景反馈 / 智能回答")
        c.line(CONTENT / 2, 104, CONTENT / 2, 74)
        c.line(CONTENT / 2, 74, CONTENT / 2, 56)
        c.line(CONTENT / 2 - 3, 61, CONTENT / 2, 56)
        c.line(CONTENT / 2 + 3, 61, CONTENT / 2, 56)


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#102D39"))
    canvas.circle(PAGE_W + 35, PAGE_H - 95, 250, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#304A52"))
    canvas.circle(PAGE_W - 10, PAGE_H - 170, 190, fill=0, stroke=1)
    canvas.circle(PAGE_W - 10, PAGE_H - 170, 130, fill=0, stroke=1)
    canvas.setFillColor(ORANGE)
    canvas.circle(PAGE_W - 90, PAGE_H - 112, 8, fill=1, stroke=0)
    canvas.setFillColor(LIME)
    canvas.circle(PAGE_W - 235, PAGE_H - 258, 5, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
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
    canvas.drawString(LEFT, PAGE_H - 17 * mm, "明辨 · 校园反诈陪练")
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
        p("项目技术文档", "MB-Eyebrow"),
        p("识破一次，<br/>才能真正学会拒绝。", "MB-Cover"),
        p(
            "面向大学生的校园反诈陪练。<br/>"
            "从可疑消息检测，到压力情景演练，再到真实新闻证据与智能助手。",
            "MB-Cover-Sub",
        ),
        Spacer(1, 35 * mm),
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
        *block("01 产品概述", "明辨把反诈从“知识阅读”推进到“压力下练习”。"),
        p(
            "大学生常见的诈骗场景集中在兼职刷单、冒充客服、冒充公检法、注销校园贷、门票私下交易和游戏账号交易。"
            "普通宣传页通常只展示警示口号，用户看懂之后仍可能在对方持续施压时作出错误操作。"
        ),
        p(
            "明辨把完整过程拆为：设置安全档案、检测可疑消息、阅读风险与证据、进入同类情景演练、查看成长记录、随时咨询智能助手。"
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
        PageBreak(),
    ]

    content += [
        *block("02 信息架构", "一个路由只承担一个主要任务。"),
        p(
            "顶部导航在当前页面保持明确激活状态。检测输入与报告结果分离；报告内部使用标签页；"
            "案例页直接跳转外部新闻；情景演练不追加在首页下方，而是使用独立的聊天工作台。",
        ),
        AgentFlow(),
        p("图 2-1 从输入到安全复核的请求链路", "MB-Caption"),
        p(
            "本地规则先完成敏感信息处理和稳定风险命中，智能模型再在此基础上生成解释、角色扮演或问答。"
            "这一分工可以降低模型漏判，也避免网络波动导致演示完全不可用。",
            "MB-Quote",
        ),
        *shot("home.png", "图 2-2 明辨首页：品牌、风险示意和三个独立功能入口"),
        PageBreak(),
    ]

    content += [
        *block("03 风险检测", "规则负责召回，模型负责把风险说清楚。"),
        *shot("scan.png", "图 3-1 可疑消息输入和 Agent 处理轨迹", CONTENT - 5),
        p(
            "检测规则覆盖 7 类高频风险，并对屏幕共享、验证码、安全账户、保证金、先转账和网贷等动作额外加权。"
            "系统优先返回证据检索结果，再允许模型在证据范围内生成解释。",
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
        *shot("report.png", "图 3-2 独立报告页：风险分、可疑原句与证据标签"),
        PageBreak(),
    ]

    content += [
        *block("04 真实新闻案例", "点击卡片即可前往对应新闻原文。"),
        p(
            "案例页当前收录 5 条公开报道，覆盖刷单返利、冒充公检法、演唱会门票、注销校园贷和游戏账号交易。"
            "应用只保存标题、摘要、来源、日期、损失金额与教育要点，不复制整篇新闻。",
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
            ],
            [105, 190, 170],
        ),
        p(
            "所有原文链接都在应用卡片上直接展示，便于评审快速核验来源。",
        ),
        PageBreak(),
    ]

    content += [
        *block("05 情景演练", "智能模型不是答题器，它要制造可控制的压力。"),
        *shot("practice.png", "图 5-1 情景、聊天与即时复盘三栏工作台", CONTENT - 5),
        p(
            "用户选择兼职、客服或奖学金场景后，智能模型以虚构诈骗角色持续施压。每次回复后，系统给出风险反馈、"
            "更安全的表达和安全分变化。场景禁止使用真实账户、电话或可执行诈骗资源。",
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
        PageBreak(),
    ]

    content += [
        *block("06 智能助手与知识检索", "正式聊天入口独立存在，也能说明自己依据了什么。"),
        *shot("assistant.png", "图 6-1 独立智能助手页面与来源展示", CONTENT - 5),
        p(
            "智能助手收到问题后，先从本地知识和新闻案例中检索相关内容，再要求模型在给定资料范围内回答。"
            "前端会同时展示命中的知识条目和可点击新闻案例，用户可以看到回答从哪里来。",
        ),
        p(
            "如果模型不可用，助手会退回本地规则回答：优先提示停止操作、保护验证码、拒绝屏幕共享，"
            "并根据是否已发生资金损失给出银行止付和报警建议。",
            "MB-Quote",
        ),
        PageBreak(),
    ]

    content += [
        *block("07 账户与训练模块", "登录不是装饰页，它会保护成长数据和训练结果。"),
        *shot("login.png", "图 7-1 登录、注册与本地体验账户", CONTENT - 5),
        p(
            "账户模块支持登录、注册和体验模式。密码使用浏览器加密接口进行加盐哈希后保存在当前浏览器，"
            "原始密码不会写入本地数据或发送到服务器。成长记录、安全档案和每日挑战受路由守卫保护，"
            "登录成功后会回到用户原本访问的页面。",
        ),
        table(
            [
                ["模块", "能力", "数据保存"],
                ["登录 / 注册", "本地账户、路由跳转、演示模式", "加盐密码哈希与 session"],
                ["知识训练", "六个短课、选择切换、掌握进度", "课程 id 列表"],
                ["每日挑战", "8 题、服务端评分、逐题解释", "最高分及完成次数"],
            ],
            [110, 200, 150],
        ),
        PageBreak(),
        *block("08 训练中心与每日挑战", "知识阅读和即时测验拆成两个路由，挑战由服务端评分。"),
        *shot("academy.png", "图 8-1 知识训练中心", CONTENT - 5),
        *shot("challenge.png", "图 8-2 每日安全挑战", CONTENT - 5),
        PageBreak(),
        *block("09 安全与隐私", "反诈产品自身必须先守住边界。"),
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
        Spacer(1, 12),
        *shot("dashboard.png", "图 9-1 成长记录页：本地统计、风险分布和徽章"),
        PageBreak(),
    ]

    content += [
        *block("10 测试与部署", "在线可联调，离线也能演示。"),
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
            ],
            [280, 160],
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
        PageBreak(),
    ]

    content += [
        *block("11 创新点与社会价值"),
        p("技术创新", "MB-H2"),
        p("- 规则引擎与智能模型双通道识别，结构化风险不依赖模型随机发挥。"),
        p("- 本地知识与公开新闻案例共同支撑助手回答。"),
        p("- 可交互情景演练让用户从“看懂”进入“练会”。"),
        p("- 确定性安全评分复核，纠正模型对防御性表达的误判。"),
        p("应用创新", "MB-H2"),
        p("- 用独立路由拆分识别、报告、训练、案例、成长和助手。"),
        p("- 真实新闻卡直接跳到原文，增强内容可信度。"),
        p("- 安全档案与成长记录均围绕本地数据构建，减少敏感信息上传。"),
        p(
            "明辨的价值不只是帮助学生记住反诈口号，而是提供一次可重复的低风险训练。"
            "高校保卫处、辅导员和学生组织也可以使用相同框架开展定制化安全教育。",
            "MB-Quote",
        ),
        Spacer(1, 20),
        p("明辨 · 校园反诈陪练", "MB-H2"),
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
        title="明辨校园反诈陪练技术文档",
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

