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
SCREENS = ROOT / "tmp" / "pdfs" / "current-technical-doc"
OUTPUT = Path(
    "/Users/yimu/Documents/Codex/2026-11-14/"
    "https-www-boxuegu-com-matchtrack-detail-2/outputs/"
    "智能反诈训练系统技术文档.pdf"
)

PAGE_W, PAGE_H = A4
LEFT = RIGHT = 18 * mm
CONTENT = PAGE_W - LEFT - RIGHT

INK = colors.HexColor("#071B27")
MIDNIGHT = colors.HexColor("#102D39")
GREEN = colors.HexColor("#0D4C55")
SKY = colors.HexColor("#D8EDF6")
MINT = colors.HexColor("#E7F4EF")
LIME = colors.HexColor("#CCEB72")
ORANGE = colors.HexColor("#F06C43")
PAPER = colors.HexColor("#F4F1E9")
SURFACE = colors.HexColor("#FBFAF6")
LINE = colors.HexColor("#D7D1C4")
MUTED = colors.HexColor("#64736D")
WHITE = colors.white


def register_fonts() -> tuple[str, str]:
    candidates = {
        "body": "/System/Library/Fonts/STHeiti Medium.ttc",
        "display": "/System/Library/Fonts/Supplemental/Songti.ttc",
    }
    names: dict[str, str] = {}
    for key, path in candidates.items():
        font_name = f"MingBianDoc-{key}"
        try:
            pdfmetrics.registerFont(TTFont(font_name, path, subfontIndex=0))
            names[key] = font_name
        except Exception:
            names[key] = "Helvetica"
    return names["body"], names["display"]


BODY, DISPLAY = register_fonts()
base = getSampleStyleSheet()
for style in [
    ParagraphStyle(
        "DocBody",
        fontName=BODY,
        fontSize=9.2,
        leading=16,
        textColor=INK,
        spaceAfter=7,
        wordWrap="CJK",
    ),
    ParagraphStyle(
        "DocSmall",
        fontName=BODY,
        fontSize=7.5,
        leading=11.5,
        textColor=MUTED,
        wordWrap="CJK",
    ),
    ParagraphStyle(
        "DocLabel",
        fontName=BODY,
        fontSize=7,
        leading=10,
        textColor=ORANGE,
        tracking=0.9,
        spaceAfter=7,
    ),
    ParagraphStyle(
        "DocH1",
        fontName=DISPLAY,
        fontSize=24,
        leading=31,
        textColor=INK,
        spaceAfter=10,
        wordWrap="CJK",
    ),
    ParagraphStyle(
        "DocH2",
        fontName=DISPLAY,
        fontSize=14,
        leading=20,
        textColor=GREEN,
        spaceBefore=10,
        spaceAfter=6,
        wordWrap="CJK",
    ),
    ParagraphStyle(
        "DocQuote",
        fontName=DISPLAY,
        fontSize=11,
        leading=18,
        textColor=GREEN,
        leftIndent=10,
        rightIndent=10,
        borderPadding=10,
        backColor=MINT,
        spaceBefore=7,
        spaceAfter=8,
        wordWrap="CJK",
    ),
    ParagraphStyle(
        "DocCaption",
        fontName=BODY,
        fontSize=7,
        leading=10,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=9,
    ),
    ParagraphStyle(
        "CoverTitle",
        fontName=DISPLAY,
        fontSize=36,
        leading=46,
        textColor=WHITE,
        spaceAfter=18,
        wordWrap="CJK",
    ),
    ParagraphStyle(
        "CoverSub",
        fontName=BODY,
        fontSize=11,
        leading=19,
        textColor=colors.HexColor("#B9C8C4"),
        wordWrap="CJK",
    ),
]:
    base.add(style)


def clean(text: str) -> str:
    return (
        text.replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


def p(text: str, style: str = "DocBody") -> Paragraph:
    return Paragraph(clean(text), base[style])


def chapter(number: str, title: str, lead: str) -> list:
    return [
        p(f"{number} / 技术设计文档", "DocLabel"),
        p(title, "DocH1"),
        p(lead, "DocQuote"),
    ]


def data_table(rows: list[list[str]], widths: list[float]) -> Table:
    data = []
    for row_index, row in enumerate(rows):
        data.append(
            [
                p(f"<b>{value}</b>" if row_index == 0 else value, "DocSmall")
                for value in row
            ]
        )
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.45, LINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def screenshot(name: str, caption: str, width: float = CONTENT - 4) -> list:
    path = SCREENS / name
    if not path.exists():
        return []
    with PILImage.open(path) as image:
        ratio = image.height / image.width
    height = width * ratio
    if height > 126 * mm:
        height = 126 * mm
        width = height / ratio
    return [
        Spacer(1, 2),
        Image(str(path), width=width, height=height),
        p(caption, "DocCaption"),
    ]


class Pipeline(Flowable):
    def __init__(self):
        super().__init__()
        self.width = CONTENT
        self.height = 188

    def draw(self):
        c = self.canv
        nodes = [
            ("输入", "可疑消息"),
            ("清洗", "脱敏规整"),
            ("规则", "风险召回"),
            ("检索", "知识与案例"),
            ("模型", "解释与演练"),
            ("复核", "确定性防线"),
        ]
        gap = 6
        box_w = (CONTENT - gap * (len(nodes) - 1)) / len(nodes)
        for index, (label, detail) in enumerate(nodes):
            x = index * (box_w + gap)
            fill = INK if index in (0, 5) else SKY
            c.setFillColor(fill)
            c.roundRect(x, 104, box_w, 58, 7, fill=1, stroke=0)
            c.setFillColor(LIME if index in (0, 5) else ORANGE)
            c.setFont(BODY, 7)
            c.drawString(x + 7, 148, label)
            c.setFillColor(WHITE if index in (0, 5) else INK)
            c.setFont(BODY, 6.4)
            c.drawString(x + 7, 125, detail)
            if index < len(nodes) - 1:
                c.setStrokeColor(LINE)
                c.line(x + box_w + 1, 133, x + box_w + gap - 1, 133)
        c.setFillColor(MINT)
        c.roundRect(0, 22, CONTENT, 56, 8, fill=1, stroke=0)
        c.setFillColor(MUTED)
        c.setFont(BODY, 7)
        c.drawString(12, 51, "浏览器任务页")
        c.drawRightString(CONTENT - 12, 51, "检测报告 / 演练反馈 / 带来源回答")
        c.setStrokeColor(GREEN)
        c.line(CONTENT / 2, 103, CONTENT / 2, 78)
        c.line(CONTENT / 2 - 4, 84, CONTENT / 2, 78)
        c.line(CONTENT / 2 + 4, 84, CONTENT / 2, 78)


class DataFlow(Flowable):
    def __init__(self):
        super().__init__()
        self.width = CONTENT
        self.height = 155

    def draw(self):
        c = self.canv
        columns = [
            ("前端", ["页面路由", "任务组件", "本地会话", "安全档案"]),
            ("服务端", ["请求路由", "规则引擎", "知识与案例", "评分策略"]),
            ("模型层", ["深度求索对话模型", "结构化输出", "本地回退"]),
        ]
        col_w = (CONTENT - 18) / 3
        for index, (heading, lines) in enumerate(columns):
            x = index * (col_w + 9)
            c.setFillColor(INK if index == 1 else colors.HexColor("#E3F0F3"))
            c.roundRect(x, 20, col_w, 118, 8, fill=1, stroke=0)
            c.setFillColor(LIME if index == 1 else ORANGE)
            c.setFont(BODY, 7)
            c.drawString(x + 9, 119, heading)
            c.setFillColor(WHITE if index == 1 else INK)
            for line_index, line in enumerate(lines):
                c.setFont(BODY, 7)
                c.drawString(x + 9, 94 - line_index * 18, line)
            if index < 2:
                c.setStrokeColor(GREEN)
                c.line(x + col_w + 2, 78, x + col_w + 7, 78)


class Mark(Flowable):
    def __init__(self, size: float = 56):
        super().__init__()
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        c.setStrokeColor(WHITE)
        c.setLineWidth(1)
        c.circle(28, 28, 23, stroke=1, fill=0)
        c.line(8, 34, 48, 22)
        c.line(33, 7, 36, 49)
        c.setFillColor(LIME)
        c.circle(26, 34, 4.5, fill=1, stroke=0)
        c.setFillColor(ORANGE)
        c.circle(45, 16, 3.2, fill=1, stroke=0)


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(MIDNIGHT)
    canvas.circle(PAGE_W + 30, PAGE_H - 80, 245, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#304A52"))
    canvas.circle(PAGE_W - 10, PAGE_H - 160, 185, fill=0, stroke=1)
    canvas.circle(PAGE_W - 10, PAGE_H - 160, 125, fill=0, stroke=1)
    canvas.setFillColor(ORANGE)
    canvas.circle(PAGE_W - 88, PAGE_H - 105, 8, fill=1, stroke=0)
    canvas.setFillColor(LIME)
    canvas.circle(PAGE_W - 225, PAGE_H - 246, 5, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont(BODY, 6.5)
    canvas.drawString(LEFT, 17 * mm, "2026 传智杯网页开发挑战赛")
    canvas.drawRightString(PAGE_W - RIGHT, 17 * mm, "技术设计文档")
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
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 17 * mm, "技术设计文档")
    canvas.line(LEFT, 13 * mm, PAGE_W - RIGHT, 13 * mm)
    canvas.drawString(LEFT, 8.5 * mm, "校园反诈训练")
    canvas.drawRightString(PAGE_W - RIGHT, 8.5 * mm, f"{canvas.getPageNumber():02d}")
    canvas.restoreState()


def story() -> list:
    content = [
        Spacer(1, 25 * mm),
        Mark(),
        Spacer(1, 13 * mm),
        p("智能反诈训练系统", "DocLabel"),
        p("识破一次，<br/>才能真正学会拒绝。", "CoverTitle"),
        p(
            "面向大学生的校园反诈训练与风险解释平台。<br/>"
            "规则引擎负责稳定召回，检索增强生成负责解释与陪练，确定性复核负责守住边界。",
            "CoverSub",
        ),
        Spacer(1, 31 * mm),
        data_table(
            [
                ["15 类", "11 条", "10 个"],
                ["高频风险知识", "公开新闻案例", "校园情景演练"],
                ["覆盖常见校园诈骗", "均可跳转原文核验", "用于压力下练习"],
            ],
            [CONTENT / 3] * 3,
        ),
        NextPageTemplate("Body"),
        PageBreak(),
    ]

    content += [
        *chapter("00", "文档信息", "本文档对应第九届传智杯人工智能网页开发挑战赛作品省赛提交版本。"),
        data_table(
            [
                ["项目", "内容"],
                ["项目名称", "智能反诈训练系统"],
                ["参赛方向", "人工智能网页开发挑战赛"],
                ["文档版本", "省赛最终提交版"],
                ["技术形态", "Vue 3 单页应用 + Python 服务端"],
                ["核心场景", "可疑消息检测、风险解释、情景演练、知识训练、每日挑战"],
                ["设计原则", "本地优先、来源可查、规则可解释、模型有边界"],
            ],
            [95, 330],
        ),
        p("文档结构", "DocH2"),
        data_table(
            [
                ["章节", "内容"],
                ["01", "项目概述"],
                ["02", "需求分析"],
                ["03", "系统架构设计"],
                ["04", "人工智能技术方案"],
                ["05", "核心功能实现与界面说明"],
                ["06", "测试与部署"],
                ["07", "创新点说明"],
                ["08", "总结与展望"],
            ],
            [62, 363],
        ),
        PageBreak(),
    ]

    content += [
        *chapter("01", "项目概述", "把反诈从被动阅读，变成可重复、低压力的主动训练。"),
        p(
            "大学生遭遇的诈骗通常不是缺少警句，而是在对方制造紧急感、权威感或利益诱惑时，无法快速识别异常动作。"
            "本项目将常见风险拆成可以观察、解释和练习的行为信号，形成从消息检测到安全反应的完整闭环。",
        ),
        data_table(
            [
                ["用户问题", "产品回应"],
                ["看不懂一条兼职消息是否可靠", "逐句提取风险信号并给出风险分"],
                ["知道有风险但不知道下一步做什么", "输出停止操作、独立核验、留证和报警清单"],
                ["只记住结论，遇到压力仍会配合", "进入同类情景，练习拒绝、核验和止损"],
                ["不知道案例是否真实", "公开新闻卡直接跳转原文"],
                ["训练后看不到薄弱点", "成长记录展示风险类型、挑战分数和连续训练"],
            ],
            [190, 235],
        ),
        p(
            "项目当前覆盖刷单返利、冒充公检法、假客服、注销校园贷、票务私售、游戏交易、兼职收费、"
            "高风险操作、应急处置、官方核验、虚假投资、冒充熟人、教育退费、奖助学金和粉丝福利等主题。",
            "DocQuote",
        ),
        PageBreak(),
    ]

    content += [
        *chapter("02", "需求分析", "用户需要的不是更多口号，而是能在真实压力下执行的步骤。"),
        data_table(
            [
                ["用户角色", "核心诉求", "典型场景"],
                ["在校学生", "快速判断消息风险，知道下一步怎么做", "兼职、退款、票务、熟人借钱"],
                ["学生工作者", "用统一工具开展反诈教育", "班会、安全教育、新生入学"],
                ["指导教师", "展示项目完整性、可解释性与技术深度", "课堂演示与竞赛评审"],
            ],
            [100, 170, 155],
        ),
        p("功能需求", "DocH2"),
        data_table(
            [
                ["要求", "实现"],
                ["消息风险检测", "本地规则召回、敏感信息脱敏、模型解释"],
                ["风险报告", "风险分、可疑原句、关键动作、证据和行动清单"],
                ["情景演练", "角色压力对话、安全分变化、替代话术"],
                ["真实案例", "分类筛选、新闻原文跳转、教育要点"],
                ["知识训练", "十五个短课与掌握进度"],
                ["每日挑战", "十道情景题、服务端评分与逐题复盘"],
                ["成长记录", "训练活跃度、风险分布、徽章和挑战结果"],
                ["账户与档案", "本地账户、会话保护、场景偏好与提示强度"],
            ],
            [135, 288],
        ),
        p("非功能需求", "DocH2"),
        p(
            "隐私：手机号、证件号、邮箱和银行卡号在模型调用前脱敏；稳定：模型不可用时保留规则和本地知识回答；"
            "可信：案例与知识均提供可核验来源；可维护：规则、知识、新闻和挑战均使用独立数据文件；"
            "可解释：检测结果必须给出命中信号与行动建议，而不是只返回一个分数。",
        ),
        PageBreak(),
    ]

    content += [
        *chapter("03", "系统架构设计", "前端独立页面负责任务，服务端分层负责识别、检索、生成与复核。"),
        DataFlow(),
        p("图 3-1 前端、服务端与模型层职责划分", "DocCaption"),
        data_table(
            [
                ["层级", "主要文件", "职责"],
                ["页面与路由", "前端页面脚本", "首页、检测、报告、演练、案例、成长、训练与助手"],
                ["本地状态", "浏览器状态模块", "会话、报告摘要、安全档案、学习进度和挑战记录"],
                ["请求编排", "Python 服务端", "输入校验、接口路由、错误处理和静态资源服务"],
                ["规则引擎", "风险分析模块", "关键词、关键动作、紧急话术和金额线索评分"],
                ["知识检索", "知识库模块", "中文词项匹配、风险分类加权、案例关联"],
                ["模型调用", "模型客户端", "结构化解释、角色扮演、回答生成"],
                ["安全复核", "安全模块", "脱敏、历史裁剪、边界提示和防御行为纠偏"],
            ],
            [92, 110, 223],
        ),
        PageBreak(),
    ]

    content += [
        *chapter("04", "人工智能技术方案", "人工智能负责解释和陪练，确定性系统负责事实、规则和最后一道安全边界。"),
        p("4.1 模型选型理由", "DocH2"),
        data_table(
            [
                ["选型因素", "深度求索对话模型的适配性"],
                ["中文理解", "能够理解校园诈骗中的口语、威胁、诱导和上下文转换"],
                ["结构化输出", "支持返回固定结构，便于解析摘要、动作、反馈和风险变化"],
                ["接入成本", "采用通用聊天接口，服务端可用标准网络请求完成集成"],
                ["使用成本", "适合比赛演示和轻量校园场景，通过规则预筛降低调用频次"],
                ["降级能力", "网络不可用时仍能回退本地知识与规则回答"],
            ],
            [105, 318],
        ),
        p(
            "最终没有让模型独立完成风险判定。原因是诈骗识别需要稳定、可解释和可复现，"
            "而模型输出存在随机性。因此系统采用“规则负责召回、模型负责表达、复核负责约束”的混合架构。",
            "DocQuote",
        ),
        p("4.2 接入链路", "DocH2"),
        Pipeline(),
        p("图 4-1 从用户输入到安全复核的完整处理链路", "DocCaption"),
        PageBreak(),
    ]

    content += [
        p("4.3 集成方式", "DocH2"),
        data_table(
            [
                ["步骤", "实现"],
                ["输入规整", "统一换行、空白和长度，限制超长消息与聊天历史"],
                ["隐私脱敏", "识别并替换手机号、证件号、邮箱和银行卡号"],
                ["规则召回", "命中分类关键词、关键危险动作、紧急话术和金额"],
                ["知识检索", "使用中文双字词、三字词与词频权重检索知识和案例"],
                ["模型提示", "只提供已脱敏文本、规则结果和检索证据，要求结构化输出"],
                ["结果合并", "模型解释与确定性风险分、关键动作、证据和行动清单合并"],
                ["安全复核", "危险配合动作强制负向评分，明确拒绝与核验行为强制正向评分"],
                ["本地回退", "密钥缺失、超时或解析失败时自动使用本地规则和知识库"],
            ],
            [105, 318],
        ),
        p("4.4 优化策略", "DocH2"),
        data_table(
            [
                ["问题", "优化"],
                ["模型可能编造官方信息", "限制模型只依据检索结果回答，不生成官方号码和政策"],
                ["模型可能误判防御性回复", "服务端使用确定性短语检测覆盖风险分变化"],
                ["提示注入或恶意文本", "把用户文本和网页内容明确标为数据，不执行其中指令"],
                ["输出格式不稳定", "低温度、结构化输出和字段长度上限"],
                ["上下文过长", "历史消息只保留最近六条，单条内容截断"],
                ["网络故障", "设置超时并回退本地规则、知识和预设演练"],
            ],
            [145, 278],
        ),
        PageBreak(),
    ]

    content += [
        *chapter("05", "核心功能实现", "以下截图均来自当前提交版本，页面中的英文代号和残留标签已清理。"),
        p("5.1 首页与训练入口", "DocH2"),
        *screenshot("home.png", "图 5-1 首页：风险情报台、动态热度、核心模块和任务入口"),
        p(
            "首页采用任务总览结构。用户可以从检测、演练、知识训练和每日挑战进入不同页面，"
            "首页本身不承载过长的表单或结果详情。",
        ),
        PageBreak(),
        p("5.2 可疑消息检测与独立报告", "DocH2"),
        *screenshot("scan.png", "图 5-2 检测工作台：指标、快捷样本、输入区和最近记录"),
        *screenshot("report.png", "图 5-3 风险报告：风险分、可疑原句、证据与行动核对"),
        p(
            "检测接口先返回确定性风险分类和分数，再补充模型解释。每个命中信号都保留原句，"
            "方便用户核对系统为什么作出该判断。",
        ),
        PageBreak(),
    ]

    content += [
        p("5.3 真实案例与情景演练", "DocH2"),
        *screenshot("cases.png", "图 5-4 公开校园诈骗新闻案例与原文入口"),
        *screenshot("practice.png", "图 5-5 反诈情景演练：压力对话、即时反馈、安全话术"),
        p(
            "案例模块提供内容可信度，演练模块把案例中的典型话术转化为可以反复练习的低风险对话。"
            "系统记录安全分变化，并给出更稳妥的表达方式。",
        ),
        PageBreak(),
    ]

    content += [
        p("5.4 智能助手与来源展示", "DocH2"),
        *screenshot("assistant.png", "图 5-6 智能助手：连续对话、知识依据和新闻案例"),
        p(
            "助手把问题与最近对话一起用于本地检索，然后将知识和案例交给模型生成回答。"
            "前端同时展示命中的知识条目与案例入口，使智能回答能够被复核。",
        ),
        PageBreak(),
        p("5.5 账户与安全档案", "DocH2"),
        *screenshot("login.png", "图 5-7 登录、注册与本地体验账户"),
        PageBreak(),
        *screenshot("profile.png", "图 5-8 安全档案：身份、常见场景与提示强度"),
        p(
            "账户数据、安全档案、学习进度和报告摘要均保存在当前浏览器。密码使用浏览器加密能力加盐哈希，"
            "不要求手机号、身份证、真实银行卡或可识别个人身份的信息。",
        ),
        PageBreak(),
    ]

    content += [
        p("5.6 知识训练、每日挑战与成长记录", "DocH2"),
        *screenshot("academy.png", "图 5-9 知识训练中心：十五个高频主题短课"),
        *screenshot("challenge.png", "图 5-10 每日安全挑战：情景题与中文选项"),
        PageBreak(),
        *screenshot("dashboard.png", "图 5-11 成长记录：综合防骗力、训练活跃度、风险分布与徽章"),
        p(
            "成长记录将检测、演练和挑战统一转化为可视化训练轨迹。它不评价用户人格，"
            "只呈现当前薄弱风险类型和下一步训练建议。",
        ),
        PageBreak(),
    ]

    content += [
        *chapter("06", "测试与部署", "测试覆盖风险识别、隐私保护、知识回答、演练反馈和挑战评分。"),
        p("6.1 自动化测试", "DocH2"),
        data_table(
            [
                ["测试项", "验证目标", "结果"],
                ["刷单消息检测", "识别返利、垫付与任务链", "通过"],
                ["公检法冒充检测", "识别权威身份、安全账户与恐惧话术", "通过"],
                ["新闻案例查询", "公开案例接口正常返回", "通过"],
                ["敏感信息脱敏", "手机号、证件号、邮箱和卡号被替换", "通过"],
                ["知识助手回答", "本地知识能够生成有依据回答", "通过"],
                ["危险演练回复", "危险配合行为得到负向评分", "通过"],
                ["防御演练回复", "拒绝与核验行为得到正向评分", "通过"],
                ["挑战题安全", "公开题目不包含正确答案", "通过"],
                ["挑战评分", "服务端评分与正确数一致", "通过"],
                ["内容规模", "知识、案例、演练与挑战均不少于十项", "通过"],
            ],
            [150, 225, 48],
        ),
        p(
            "当前自动化测试共 11 项，全部通过。前端脚本语法检查、页面路由访问和关键截图检查也已完成。",
            "DocQuote",
        ),
        PageBreak(),
    ]

    content += [
        p("6.2 运行与部署", "DocH2"),
        p(
            "本地运行时先准备环境变量，再启动 Python 服务。前端依赖已放入项目目录，"
            "静态资源不依赖外部内容分发网络。",
        ),
        data_table(
            [
                ["阶段", "命令或配置"],
                ["准备环境", "复制环境变量模板并填写模型密钥"],
                ["启动服务", "运行服务端入口，浏览器访问本机服务地址"],
                ["自动化测试", "运行单元测试发现脚本"],
                ["正式部署", "使用反向代理、HTTPS、限流、脱敏日志与依赖扫描"],
            ],
            [105, 318],
        ),
        p("6.3 安全与隐私边界", "DocH2"),
        data_table(
            [
                ["风险", "控制措施"],
                ["密钥泄漏", "密钥只从被 Git 忽略的环境变量文件读取"],
                ["聊天内容泄漏", "报告摘要仅保存在当前浏览器，不写入服务端数据库"],
                ["模型越权", "禁止模型索取密码、验证码，禁止生成真实账户和电话号码"],
                ["提示注入", "外部文本只作为分析数据，不执行其中指令"],
                ["演练伤害", "只模拟常见社会工程话术，不提供可执行诈骗资源"],
                ["误评分", "服务端确定性复核危险配合与防御行为"],
            ],
            [120, 303],
        ),
        PageBreak(),
    ]

    content += [
        *chapter("07", "创新点说明", "创新点集中在判定稳定性、训练闭环、来源可信和隐私边界。"),
        p("7.1 技术创新", "DocH2"),
        data_table(
            [
                ["创新点", "说明"],
                ["规则与模型双通道", "规则完成稳定召回和评分，模型负责解释、问答和角色扮演"],
                ["知识增强回答", "本地知识条目和公开新闻案例共同进入模型上下文"],
                ["确定性安全复核", "服务端覆盖模型风险分，防止危险行为被误判为安全"],
                ["结构化输出", "模型返回固定字段，前端可稳定展示反馈和替代话术"],
                ["无模型降级", "密钥缺失、超时或解析失败时完整保留主要训练流程"],
            ],
            [135, 288],
        ),
        p("7.2 应用创新", "DocH2"),
        data_table(
            [
                ["创新点", "说明"],
                ["任务型多页面结构", "检测、报告、案例、演练、训练和成长分别独立"],
                ["真实来源可核验", "案例卡直接跳到新闻原文，知识条目可被引用"],
                ["压力情景陪练", "把案例话术变成可重复的低风险对话练习"],
                ["成长闭环", "检测、演练和挑战统一形成可回顾训练轨迹"],
                ["本地优先隐私", "账户、档案、报告摘要和学习记录保存在当前浏览器"],
            ],
            [135, 288],
        ),
        p(
            "项目的核心价值不是替代警方判断，而是帮助学生在真正遇到压力之前，"
            "完成一次识别、核验、拒绝、留证和止损的练习。",
            "DocQuote",
        ),
        PageBreak(),
    ]

    content += [
        *chapter("08", "总结与展望", "从“知道这是诈骗”继续推进到“在压力下做出正确动作”。"),
        p(
            "系统已经形成一条完整训练链路：通过规则与模型识别可疑消息，通过独立报告解释风险，"
            "通过真实案例建立可信度，通过情景演练练习安全反应，再通过挑战和成长记录形成训练反馈。"
            "当前版本适合比赛演示、高校反诈主题班会和基础安全训练。",
        ),
        p("后续迭代方向", "DocH2"),
        data_table(
            [
                ["方向", "目标"],
                ["多模态输入", "识别聊天截图、网页截图和语音转写内容"],
                ["专家审核后台", "由教师或反诈工作人员维护知识、案例和演练策略"],
                ["校本部署", "按学校通知渠道和常见风险生成定制训练内容"],
                ["实时数据看板", "匿名统计高频风险类型，用于校园安全教育改进"],
                ["模型评测集", "持续测量错误拒答、误判、编造和防御行为识别效果"],
            ],
            [120, 303],
        ),
        p(
            "智能反诈训练系统不会替代警方结论。若已经转账、泄露验证码或受到持续威胁，"
            "应立即停止操作，联系银行止付，并拨打 110 或向学校保卫部门求助。",
            "DocQuote",
        ),
        p(
            "2026 传智杯网页开发挑战赛<br/>"
            "技术文档 · 省赛最终提交版",
            "DocSmall",
        ),
    ]
    return content


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
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
    print(OUTPUT)


if __name__ == "__main__":
    build()
