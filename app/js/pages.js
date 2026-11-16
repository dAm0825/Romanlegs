(function () {
  const { computed, onMounted, reactive, ref, watch } = Vue;
  const { useRoute, useRouter } = VueRouter;
  const store = window.MingBianStore;

  const PageHead = {
    props: {
      index: String,
      eyebrow: String,
      title: String,
      description: String,
    },
    template: `
      <header class="page-head">
        <div>
          <p class="eyebrow"><span>{{ index }}</span>{{ eyebrow }}</p>
          <h1>{{ title }}</h1>
        </div>
        <p class="page-description">{{ description }}</p>
      </header>
    `,
  };

  const samples = [
    {
      label: "刷单兼职",
      text: "你好，我们招聘兼职点赞员，每单佣金 20 元。第一单已经返款，你只要继续垫付 980 元完成连单，就能一起提现。系统显示账户冻结，请打开屏幕共享，我帮你处理。",
    },
    {
      label: "假客服",
      text: "我是平台客服，你的订单误开通了年度会员，每月会自动扣费。我现在帮你取消，请把刚收到的短信验证码告诉我，并下载会议软件打开屏幕共享。",
    },
    {
      label: "假公检法",
      text: "这里是公安机关，你名下银行账户涉嫌诈骗，必须立即保密，不能告诉老师和家人。请先缴纳取保候审保证金到安全账户，否则马上逮捕。",
    },
    {
      label: "门票转让",
      text: "我有一张内部票原价转给你，但不要走平台，直接扫码付款。付款后系统说你没有备注，订单冻结了，需要再转一笔刷流水才能退款。",
    },
  ];

  const categoryScenario = {
    刷单返利: "part-time",
    虚假招聘: "part-time",
    冒充电商客服: "customer",
    注销校园贷: "customer",
    冒充公检法: "scholarship",
  };

  function scoreTone(score) {
    if (score >= 75) return "danger";
    if (score >= 55) return "warning";
    if (score >= 30) return "attention";
    return "safe";
  }

  const HomePage = {
    components: { PageHead },
    setup() {
      const profile = computed(() => store.state.profile);
      const stats = reactive({
        cases: 11,
        knowledge_types: 15,
        scenarios: 10,
      });
      onMounted(async () => {
        try {
          const data = await store.api("/api/stats");
          Object.assign(stats, data);
        } catch {
          // The bundled counts remain available if the stats request fails.
        }
      });
      return { profile, stats };
    },
    template: `
      <section class="home-page">
        <div class="home-hero">
          <div class="hero-text">
            <p class="eyebrow"><span>01</span>反诈训练</p>
            <h1>智能反诈训练系统</h1>
            <p class="hero-description">
              检测可疑消息，阅读真实案例，练习识破常见骗局。
            </p>
            <div class="hero-cta">
              <router-link class="primary-button" to="/scan">
                检测可疑消息
                <app-icon name="arrow" />
              </router-link>
              <router-link class="secondary-button" to="/practice">
                <span class="button-dot"></span>
                开始情景演练
              </router-link>
            </div>
          </div>
        </div>

        <div class="home-stats">
          <div><strong>{{ stats.cases }}</strong><span>真实案例<br/>新闻直达</span></div>
          <div><strong>{{ stats.knowledge_types }}</strong><span>高频诈骗<br/>类型知识</span></div>
          <div><strong>{{ stats.scenarios }}</strong><span>可练习的<br/>互动场景</span></div>
          <div class="profile-snapshot">
            <small>你的当前档案</small>
            <strong>{{ profile.role }} · {{ profile.cautionLevel }}防护</strong>
            <router-link to="/profile">调整档案 <app-icon name="arrow"/></router-link>
          </div>
        </div>

        <section class="feature-section">
          <div class="section-title">
            <p class="eyebrow"><span>02</span>核心模块</p>
            <h2>核心功能</h2>
          </div>
          <div class="feature-grid">
            <router-link class="feature-card feature-scan" to="/scan">
              <span class="feature-index">01</span>
              <div class="feature-icon"><app-icon name="scan"/></div>
              <h3>可疑消息体检</h3>
              <p>逐句标出返利、恐吓、屏幕共享和二次转账信号，给出可核验的依据。</p>
              <span class="feature-link">打开检测页 <app-icon name="arrow"/></span>
            </router-link>
            <router-link class="feature-card feature-practice" to="/practice">
              <span class="feature-index">02</span>
              <div class="feature-icon"><app-icon name="shield"/></div>
              <h3>压力对话演练</h3>
              <p>智能模型扮演兼职招聘者、假客服或假老师，陪你练习拒绝、核验和止损。</p>
              <span class="feature-link">进入演练场 <app-icon name="arrow"/></span>
            </router-link>
            <router-link class="feature-card feature-cases" to="/cases">
              <span class="feature-index">03</span>
              <div class="feature-icon"><app-icon name="news"/></div>
              <h3>真实新闻案例</h3>
              <p>点击案例卡即可前往人民网、警方公众号等公开新闻原文，不靠虚构故事吓人。</p>
              <span class="feature-link">阅读真实案例 <app-icon name="arrow"/></span>
            </router-link>
          </div>
        </section>

        <section class="workflow-strip">
          <span>一条完整的防骗训练路径</span>
          <div><b>01</b>设置档案</div>
          <i></i>
          <div><b>02</b>检测消息</div>
          <i></i>
          <div><b>03</b>阅读证据</div>
          <i></i>
          <div><b>04</b>情景演练</div>
          <i></i>
          <div><b>05</b>复盘成长</div>
        </section>
      </section>
    `,
  };

  const ScanPage = {
    components: { PageHead },
    setup() {
      const router = useRouter();
      const message = ref("");
      const selectedSample = ref(0);
      const loading = ref(false);
      const error = ref("");
      const activeReport = ref(null);
      const checkedActions = reactive({});
      const reports = computed(() => store.state.reports);
      const highRiskCount = computed(() => reports.value.filter((item) => item.score >= 75).length);
      const todayCount = computed(() => {
        const today = new Date().toDateString();
        return reports.value.filter((item) => new Date(item.created_at).toDateString() === today).length;
      });
      const latestDate = computed(() =>
        reports.value.length
          ? new Date(reports.value[0].created_at).toLocaleDateString("zh-CN")
          : "暂无记录",
      );
      const modalTasks = computed(() => activeReport.value?.actions?.slice(0, 4) || []);
      const taskProgress = computed(() => {
        if (!modalTasks.value.length) return 0;
        return Math.round(
          (modalTasks.value.filter((_, index) => checkedActions[index]).length / modalTasks.value.length) * 100,
        );
      });

      function loadSample(index) {
        selectedSample.value = index;
        message.value = samples[index].text;
        error.value = "";
      }

      async function detect() {
        if (message.value.trim().length < 8) {
          error.value = "请粘贴至少 8 个字符的可疑消息";
          return;
        }
        loading.value = true;
        error.value = "";
        try {
          const result = await store.api("/api/detect", {
            method: "POST",
            body: JSON.stringify({ message: message.value }),
          });
          store.saveReport({ ...result, source_message: message.value });
          openDetail({ ...result, source_message: message.value });
        } catch (err) {
          error.value = err.message;
        } finally {
          loading.value = false;
        }
      }

      function openDetail(report) {
        activeReport.value = report;
        Object.keys(checkedActions).forEach((key) => delete checkedActions[key]);
      }

      function closeDetail() {
        activeReport.value = null;
      }

      function goToReport() {
        if (!activeReport.value) return;
        router.push(`/report/${activeReport.value.id}`);
      }

      return {
        message,
        selectedSample,
        samples,
        loading,
        error,
        reports,
        highRiskCount,
        todayCount,
        latestDate,
        activeReport,
        checkedActions,
        modalTasks,
        taskProgress,
        scoreTone,
        loadSample,
        detect,
        openDetail,
        closeDetail,
        goToReport,
      };
    },
    template: `
      <section class="workspace-page scan-page">
        <page-head
          index="02"
          eyebrow="可疑消息检测"
          title="风险检测工作台"
          description="分析可疑消息，核对高风险话术，并查看最近检测记录与后续行动。"
        />
        <div class="scan-metrics">
          <article>
            <span>今日检测</span>
            <strong>{{ todayCount }}</strong>
            <small>新增消息</small>
          </article>
          <article>
            <span>高风险记录</span>
            <strong>{{ highRiskCount }}</strong>
            <small>累计识别</small>
          </article>
          <article>
            <span>检测总数</span>
            <strong>{{ reports.length }}</strong>
            <small>保存在本机</small>
          </article>
          <article>
            <span>最近检测</span>
            <strong class="date-value">{{ latestDate }}</strong>
            <small>最近一次记录</small>
          </article>
        </div>

        <div class="scan-workbench">
          <div class="composer-card">
            <div class="card-label">
              <span>粘贴需要核验的内容</span>
              <span class="privacy-badge">本地脱敏</span>
            </div>
            <div class="sample-tabs">
              <button
                v-for="(sample, index) in samples"
                :key="sample.label"
                type="button"
                :class="{ active: selectedSample === index }"
                @click="loadSample(index)"
              >{{ sample.label }}</button>
            </div>
            <label class="sr-only" for="messageInput">可疑消息内容</label>
            <textarea
              id="messageInput"
              v-model="message"
              maxlength="20000"
              placeholder="例如：对方说完成点赞任务就能返佣金，现在让我先垫付一笔钱解冻账户……"
            ></textarea>
            <div class="composer-meta">
              <span><i></i>手机号、邮箱和证件号会在模型调用前脱敏</span>
              <span>{{ message.length.toLocaleString() }} / 20,000</span>
            </div>
            <p v-if="error" class="form-error">{{ error }}</p>
            <button class="analyze-primary" type="button" :disabled="loading" @click="detect">
              <span>{{ loading ? '正在检测' : '开始风险检测' }}</span>
              <app-icon name="arrow" />
            </button>
          </div>

          <aside class="scan-side-stack">
            <div class="quick-detection-card">
              <span class="side-card-label">快捷检测</span>
              <h3>常见风险模板</h3>
              <div class="quick-risk-list">
                <button
                  v-for="(sample, index) in samples"
                  :key="sample.label"
                  type="button"
                  @click="loadSample(index)"
                >
                  <span>0{{ index + 1 }}</span>
                  <b>{{ sample.label }}</b>
                  <i>→</i>
                </button>
              </div>
            </div>
            <div class="safety-reminder-card">
              <strong>三不原则</strong>
              <div><span>01</span>验证码不给</div>
              <div><span>02</span>屏幕不共享</div>
              <div><span>03</span>钱不转陌生账户</div>
            </div>
          </aside>
        </div>

        <section class="recent-detections">
          <div class="recent-head">
            <div><span>检测记录</span><h2>最近的消息检查</h2></div>
            <span>点击任意记录查看详情</span>
          </div>
          <div v-if="reports.length" class="detection-table">
            <button
              v-for="item in reports.slice(0, 6)"
              :key="item.id"
              type="button"
              @click="openDetail(item)"
            >
              <span class="risk-score-pill" :class="scoreTone(item.score)">{{ item.score }}</span>
              <div>
                <strong>{{ item.category }}</strong>
                <small>{{ new Date(item.created_at).toLocaleString('zh-CN') }}</small>
              </div>
              <span>{{ item.level }}</span>
              <span>{{ item.findings?.length || item.signals?.length || 0 }} 项发现</span>
              <app-icon name="arrow"/>
            </button>
          </div>
          <div v-else class="recent-empty">
            <p>还没有检测记录。载入一个示例，开始第一次风险检测。</p>
          </div>
        </section>

        <transition name="modal">
          <div v-if="activeReport" class="modal-backdrop" @click.self="closeDetail">
            <article class="detection-modal" role="dialog" aria-modal="true" aria-labelledby="detectionModalTitle">
              <header>
                <div>
                  <span>{{ activeReport.level }}</span>
                  <h2 id="detectionModalTitle">{{ activeReport.category }}</h2>
                  <p>{{ new Date(activeReport.created_at).toLocaleString('zh-CN') }}</p>
                </div>
                <button type="button" aria-label="关闭弹窗" @click="closeDetail">×</button>
              </header>
              <p class="modal-summary">{{ activeReport.summary }}</p>
              <div class="modal-progress">
                <div><span>行动核对进度</span><strong>{{ taskProgress }}%</strong></div>
                <i><b :style="{ width: taskProgress + '%' }"></b></i>
              </div>
              <div class="modal-columns">
                <div class="modal-signal-list">
                  <h3>风险发现</h3>
                  <div v-for="signal in (activeReport.signals || []).slice(0, 4)" :key="signal.keyword">
                    <span>{{ signal.keyword }}</span>
                    <p>{{ signal.quote }}</p>
                  </div>
                </div>
                <div class="modal-task-list">
                  <h3>建议行动</h3>
                  <label v-for="(action, index) in modalTasks" :key="index">
                    <input v-model="checkedActions[index]" type="checkbox" />
                    <span class="modal-check"></span>
                    <p>{{ action }}</p>
                  </label>
                </div>
              </div>
              <footer>
                <button type="button" class="modal-secondary" @click="closeDetail">关闭</button>
                <button type="button" class="modal-primary" @click="goToReport">查看完整报告 <app-icon name="arrow"/></button>
              </footer>
            </article>
          </div>
        </transition>
      </section>
    `,
  };

  const ReportPage = {
    setup() {
      const route = useRoute();
      const router = useRouter();
      const report = computed(() => store.getReport(route.params.id));
      const activeTab = ref("overview");
      const openEvidence = ref("");
      const isCopied = ref(false);

      const scenarioId = computed(() => (report.value ? categoryScenario[report.value.category] || "part-time" : "part-time"));
      const tone = computed(() => (report.value ? scoreTone(report.value.score) : "safe"));

      async function copyReport() {
        if (!report.value) return;
        await navigator.clipboard.writeText(report.value.report_markdown);
        isCopied.value = true;
        store.showToast("风险报告已复制", "success");
        setTimeout(() => (isCopied.value = false), 1800);
      }

      function startPractice() {
        router.push({ path: "/practice", query: { scenario: scenarioId.value } });
      }

      return {
        report,
        activeTab,
        openEvidence,
        tone,
        isCopied,
        startPractice,
        copyReport,
      };
    },
    template: `
      <section v-if="report" class="workspace-page report-page">
        <div class="report-head">
          <div>
            <p class="eyebrow"><span>03</span>风险报告 / {{ report.id }}</p>
            <h1>风险分析报告</h1>
          </div>
          <button class="secondary-button compact" type="button" @click="copyReport">
            {{ isCopied ? '已复制' : '复制报告' }}
          </button>
        </div>

        <div class="report-layout">
          <aside class="score-panel" :class="tone">
            <span class="panel-index">风险指数</span>
            <div class="score-ring" :style="{ '--score': report.score }">
              <div><strong>{{ report.score }}</strong><span>/100</span></div>
            </div>
            <div class="risk-label">{{ report.level }}</div>
            <p>{{ report.summary }}</p>
            <div class="score-meta">
              <span>识别类型</span>
              <strong>{{ report.category }}</strong>
            </div>
            <div class="score-meta">
              <span>分析来源</span>
              <strong>{{ report.provider }}</strong>
            </div>
            <button class="practice-cta" type="button" @click="startPractice">
              用同类场景练一次
              <app-icon name="arrow" />
            </button>
          </aside>

          <div class="report-main">
            <div class="report-tabs" role="tablist">
              <button :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">风险诊断</button>
              <button :class="{ active: activeTab === 'evidence' }" @click="activeTab = 'evidence'">核验依据</button>
              <button :class="{ active: activeTab === 'action' }" @click="activeTab = 'action'">行动清单</button>
            </div>

            <div v-if="activeTab === 'overview'" class="tab-panel">
              <div class="explain-card">
                <span>为什么可疑</span>
                <p>{{ report.explanation }}</p>
              </div>
              <div class="signal-list">
                <article v-for="(signal, index) in report.signals" :key="index" class="signal-item">
                  <span>{{ String(index + 1).padStart(2, '0') }}</span>
                  <div>
                    <strong>{{ signal.keyword }}</strong>
                    <p>{{ signal.quote }}</p>
                  </div>
                </article>
              </div>
              <div v-if="report.critical_actions.length" class="critical-strip">
                <strong>高风险动作</strong>
                <div>
                  <span v-for="item in report.critical_actions" :key="item.title">{{ item.title }}</span>
                </div>
              </div>
            </div>

            <div v-if="activeTab === 'evidence'" class="tab-panel">
              <div class="evidence-list">
                <article v-for="item in report.evidence" :key="item.id" class="evidence-item">
                  <button type="button" @click="openEvidence = openEvidence === item.id ? '' : item.id">
                    <span>{{ item.id }}</span>
                    <strong>{{ item.title }}</strong>
                    <i>{{ openEvidence === item.id ? '−' : '+' }}</i>
                  </button>
                  <p v-if="openEvidence === item.id">{{ item.text }}</p>
                </article>
              </div>
              <div class="related-news">
                <div class="mini-section-head">
                  <span>相似真实案例</span>
                  <router-link to="/cases">查看全部 <app-icon name="arrow"/></router-link>
                </div>
                <a v-for="item in report.related_cases" :key="item.id" :href="item.url" target="_blank" rel="noopener noreferrer">
                  <span>{{ item.category }}</span>
                  <strong>{{ item.title }}</strong>
                  <small>{{ item.source }} · {{ item.published }}</small>
                  <app-icon name="external"/>
                </a>
              </div>
            </div>

            <div v-if="activeTab === 'action'" class="tab-panel">
              <div class="action-headline">
                <span>停止 · 核验 · 保存证据</span>
                <h2>先停下来，再按顺序处理。</h2>
              </div>
              <ol class="action-plan">
                <li v-for="(action, index) in report.actions" :key="index">
                  <span>0{{ index + 1 }}</span>
                  <p>{{ action }}</p>
                </li>
              </ol>
              <div class="question-card">
                <strong>还需要确认</strong>
                <p v-for="question in report.questions" :key="question">{{ question }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      <section v-else class="missing-state">
        <span>报告未找到</span>
        <h1>这份报告不在当前浏览器里。</h1>
        <p>本地报告只保存在当前浏览器，或者链接已经过期。</p>
        <router-link class="primary-button" to="/scan">重新检测 <app-icon name="arrow"/></router-link>
      </section>
    `,
  };

  const CasesPage = {
    setup() {
      const cases = ref([]);
      const loading = ref(true);
      const active = ref("全部");
      const categories = computed(() => ["全部", ...new Set(cases.value.map((item) => item.category))]);
      const filtered = computed(() => (active.value === "全部" ? cases.value : cases.value.filter((item) => item.category === active.value)));

      onMounted(async () => {
        try {
          const data = await store.api("/api/news");
          cases.value = data.cases;
        } catch (err) {
          store.showToast(err.message, "error");
        } finally {
          loading.value = false;
        }
      });

      return { cases, loading, active, categories, filtered };
    },
    template: `
      <section class="workspace-page cases-page">
        <header class="cases-header">
          <div>
            <p class="eyebrow"><span>04</span>真实案例档案</p>
            <h1>真实校园诈骗案例</h1>
          </div>
          <div class="cases-intro">
            <span>仅收录公开新闻</span>
            <p>以下案例来自公开新闻和警方通报。点击任意卡片可前往原文，摘要仅用于风险教育。</p>
          </div>
        </header>

        <div class="case-filter">
          <button
            v-for="category in categories"
            :key="category"
            type="button"
            :class="{ active: active === category }"
            @click="active = category"
          >{{ category }}</button>
        </div>

        <div v-if="loading" class="case-loading">
          <span></span><span></span><span></span>
        </div>
        <div v-else class="case-grid">
          <a
            v-for="(item, index) in filtered"
            :key="item.id"
            class="case-card"
            :href="item.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            <div class="case-card-top">
              <span class="case-number">{{ String(index + 1).padStart(2, '0') }}</span>
              <span class="case-category">{{ item.category }}</span>
              <app-icon name="external"/>
            </div>
            <h2>{{ item.title }}</h2>
            <p>{{ item.summary }}</p>
            <div class="case-lesson">
              <span>本案警示</span>
              <strong>{{ item.lesson }}</strong>
            </div>
            <div class="case-meta">
              <span>{{ item.source }}</span>
              <span>{{ item.published }}</span>
              <b>{{ item.loss }}</b>
            </div>
          </a>
        </div>
      </section>
    `,
  };

  const PracticePage = {
    setup() {
      const route = useRoute();
      const router = useRouter();
      const scenarios = ref([
        { id: "part-time", title: "高薪兼职", label: "刷单返利" },
        { id: "customer", title: "客服退款", label: "冒充电商客服" },
        { id: "scholarship", title: "奖学金认证", label: "冒充老师/机构" },
        { id: "authority", title: "假警察来电", label: "冒充公检法" },
        { id: "loan", title: "注销校园贷", label: "征信诈骗" },
        { id: "ticket", title: "低价演唱会票", label: "虚假票务" },
        { id: "game", title: "游戏账号交易", label: "虚假平台" },
        { id: "investment", title: "高收益投资", label: "虚假投资理财" },
        { id: "friend", title: "熟人在线求助", label: "冒充熟人" },
        { id: "merch", title: "免费明星周边", label: "粉丝福利诈骗" },
      ]);
      const selected = ref(route.query.scenario || "part-time");
      const messages = ref([]);
      const input = ref("");
      const loading = ref(false);
      const feedback = ref("");
      const saferReply = ref("");
      const score = ref(72);
      const finished = ref(false);
      const completed = ref(false);
      const chatRef = ref(null);

      function chooseScenario(id) {
        selected.value = id;
        router.replace({ path: "/practice", query: { scenario: id } });
        start();
      }

      async function start() {
        feedback.value = "";
        saferReply.value = "";
        score.value = 72;
        finished.value = false;
        completed.value = false;
        messages.value = [];
        loading.value = true;
        try {
          const data = await store.api("/api/scenarios");
          scenarios.value = data.scenarios;
          const current = scenarios.value.find((item) => item.id === selected.value) || scenarios.value[0];
          messages.value = [{ role: "assistant", content: current.opening, note: "角色扮演开始" }];
        } catch (err) {
          store.showToast(err.message, "error");
        } finally {
          loading.value = false;
        }
      }

      async function send() {
        const content = input.value.trim();
        if (!content || loading.value || finished.value) return;
        messages.value.push({ role: "user", content });
        input.value = "";
        loading.value = true;
        try {
          const data = await store.api("/api/practice", {
            method: "POST",
            body: JSON.stringify({ scenario_id: selected.value, history: messages.value }),
          });
          messages.value.push({ role: "assistant", content: data.reply, note: "模拟话术" });
          feedback.value = data.feedback;
          saferReply.value = data.safer_reply;
          score.value = Math.max(0, Math.min(100, score.value + data.risk_delta));
          finished.value = Boolean(data.finished);
          if (finished.value && !completed.value) {
            completed.value = true;
            store.recordPractice({
              id: Date.now(),
              scenario: selected.value,
              score: score.value,
              date: new Date().toISOString(),
            });
          }
          requestAnimationFrame(() => {
            if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight;
          });
        } catch (err) {
          store.showToast(err.message, "error");
        } finally {
          loading.value = false;
        }
      }

      onMounted(start);
      return {
        scenarios,
        selected,
        messages,
        input,
        loading,
        feedback,
        saferReply,
        score,
        finished,
        completed,
        chatRef,
        chooseScenario,
        start,
        send,
      };
    },
    template: `
      <section class="workspace-page practice-page">
        <div class="practice-top">
          <div>
            <p class="eyebrow"><span>05</span>情景压力演练</p>
            <h1>反诈情景演练</h1>
          </div>
          <div class="safety-score">
            <span>当前安全分</span>
            <strong :class="{ low: score < 50 }">{{ score }}</strong>
            <small>/ 100</small>
          </div>
        </div>

        <div class="practice-layout">
          <aside class="scenario-rail">
            <span class="rail-label">选择演练场景</span>
            <button
              v-for="(item, index) in scenarios"
              :key="item.id"
              type="button"
              :class="{ active: selected === item.id }"
              @click="chooseScenario(item.id)"
            >
              <span>{{ String(index + 1).padStart(2, '0') }}</span>
              <div><strong>{{ item.title }}</strong><small>{{ item.label }}</small></div>
            </button>
            <div class="practice-rules">
              <strong>演练规则</strong>
              <p>场景完全虚构，请勿输入真实密码、验证码或银行卡信息。</p>
            </div>
          </aside>

          <div class="chat-panel">
            <div class="chat-head">
              <div><span class="role-avatar">骗</span><div><strong>模拟对话对象</strong><small>智能角色扮演 · 请保持警觉</small></div></div>
              <button type="button" @click="start">重新开始</button>
            </div>
            <div ref="chatRef" class="chat-stream">
              <article v-for="(message, index) in messages" :key="index" class="chat-message" :class="message.role">
                <span class="message-author">{{ message.role === 'assistant' ? '对方' : '你' }}</span>
                <div>
                  <small>{{ message.note }}</small>
                  <p>{{ message.content }}</p>
                </div>
              </article>
              <div v-if="loading" class="thinking-line"><i></i><i></i><i></i><span>对方正在输入</span></div>
            </div>
            <div class="chat-composer">
              <textarea
                v-model="input"
                :disabled="finished"
                placeholder="你会怎么回复？"
                @keydown.enter.exact.prevent="send"
              ></textarea>
              <button type="button" :disabled="!input.trim() || loading || finished" @click="send">
                回复 <app-icon name="arrow"/>
              </button>
            </div>
            <div v-if="finished" class="practice-complete">
              <strong>本轮演练结束</strong>
              <span>最终安全分 {{ score }}</span>
              <button type="button" @click="start">再练一次</button>
            </div>
          </div>

          <aside class="coach-panel">
            <span class="rail-label">即时复盘</span>
            <div v-if="feedback" class="coach-feedback">
              <p>{{ feedback }}</p>
              <div>
                <strong>更安全的回答</strong>
                <p>{{ saferReply }}</p>
              </div>
            </div>
            <div v-else class="coach-empty">
              <app-icon name="spark"/>
              <p>发送第一句回复后，这里会指出风险、给出更安全的说法。</p>
            </div>
          </aside>
        </div>
      </section>
    `,
  };

  const DashboardPage = {
    components: { PageHead },
    setup() {
      const reports = computed(() => store.state.reports);
      const practices = computed(() => store.state.practiceHistory);
      const challenges = computed(() => store.state.challengeHistory);
      const avgRisk = computed(() => {
        if (!reports.value.length) return 0;
        return Math.round(reports.value.reduce((sum, item) => sum + item.score, 0) / reports.value.length);
      });
      const avgSafety = computed(() => {
        if (!practices.value.length) return 0;
        return Math.round(practices.value.reduce((sum, item) => sum + item.score, 0) / practices.value.length);
      });
      const categoryCounts = computed(() => {
        const result = {};
        reports.value.forEach((item) => {
          result[item.category] = (result[item.category] || 0) + 1;
        });
        return Object.entries(result)
          .map(([name, count]) => ({ name, count }))
          .sort((a, b) => b.count - a.count);
      });
      const achievements = computed(() => [
        { title: "第一次识别", active: reports.value.length > 0, icon: "scan" },
        { title: "完成演练", active: practices.value.length > 0, icon: "shield" },
        { title: "证据阅读者", active: reports.value.some((item) => item.evidence?.length), icon: "news" },
        { title: "连续练习", active: practices.value.length + challenges.value.length >= 3, icon: "spark" },
      ]);
      const bestChallenge = computed(() =>
        challenges.value.length ? Math.max(...challenges.value.map((item) => item.score)) : null,
      );
      const challengeSummary = computed(() =>
        challenges.value.length
          ? `已完成 ${challenges.value.length} 次挑战`
          : "完成一次挑战，检验你的反诈反射。",
      );
      return {
        reports,
        practices,
        challenges,
        avgRisk,
        avgSafety,
        categoryCounts,
        achievements,
        bestChallenge,
        challengeSummary,
        store,
      };
    },
    template: `
      <section class="workspace-page dashboard-page">
        <page-head
          index="06"
          eyebrow="个人成长"
          title="不是记住口号，而是看见自己的进步。"
          description="这里只保存当前浏览器里的检测摘要与演练记录，不保存你粘贴的完整聊天原文。"
        />

        <div class="metric-grid">
          <article><span>可疑消息检测</span><strong>{{ reports.length }}</strong><small>累计完成</small></article>
          <article><span>情景演练</span><strong>{{ practices.length }}</strong><small>累计完成</small></article>
          <article><span>平均识别风险</span><strong>{{ avgRisk }}</strong><small>高风险 ≠ 判断错误</small></article>
          <article><span>演练平均安全分</span><strong>{{ avgSafety || '—' }}</strong><small>目标 80+</small></article>
        </div>

        <div class="dashboard-layout">
          <section class="history-card">
            <div class="mini-section-head">
              <span>最近风险报告</span>
              <router-link to="/scan">新建检测 <app-icon name="arrow"/></router-link>
            </div>
            <div v-if="reports.length" class="history-list">
              <router-link v-for="item in reports.slice(0, 6)" :key="item.id" :to="'/report/' + item.id">
                <span class="history-score" :class="item.score >= 75 ? 'danger' : item.score >= 55 ? 'warning' : 'safe'">{{ item.score }}</span>
                <div><strong>{{ item.category }}</strong><small>{{ new Date(item.created_at).toLocaleString('zh-CN') }}</small></div>
                <span>{{ item.level }}</span>
                <app-icon name="arrow"/>
              </router-link>
            </div>
            <div v-else class="empty-panel">
              <app-icon name="scan"/>
              <p>还没有检测记录。先收藏一条可疑消息，再来拆解它。</p>
              <router-link to="/scan">开始第一次检测</router-link>
            </div>
          </section>

          <aside class="growth-side">
            <section class="challenge-summary-card">
              <span class="rail-label">每日挑战</span>
              <div>
                <strong>{{ bestChallenge === null ? '—' : bestChallenge }}</strong>
                <p>{{ challengeSummary }}</p>
              </div>
              <router-link to="/challenge">{{ challenges.length ? '再次挑战' : '开始挑战' }} <app-icon name="arrow"/></router-link>
            </section>
            <section class="category-card">
              <span class="rail-label">高频风险类型</span>
              <div v-if="categoryCounts.length" class="category-bars">
                <div v-for="item in categoryCounts" :key="item.name">
                  <span>{{ item.name }}</span><b>{{ item.count }}</b>
                  <i :style="{ width: Math.max(16, item.count / reports.length * 100) + '%' }"></i>
                </div>
              </div>
              <p v-else>完成检测后会显示你的风险主题分布。</p>
            </section>
            <section class="achievement-card">
              <span class="rail-label">能力徽章</span>
              <div class="achievement-grid">
                <div v-for="item in achievements" :key="item.title" :class="{ active: item.active }">
                  <app-icon :name="item.icon"/>
                  <span>{{ item.title }}</span>
                </div>
              </div>
            </section>
          </aside>
        </div>
      </section>
    `,
  };

  const AssistantPage = {
    setup() {
      const messages = ref([
        {
          role: "assistant",
          content: "我是反诈智能助手。你可以告诉我对方自称什么、要求你做什么，我会先帮你判断危险点，再给出核验和止损步骤。",
        },
      ]);
      const input = ref("");
      const loading = ref(false);
      const streamRef = ref(null);
      const suggestions = [
        "对方让我开启屏幕共享退款，怎么办？",
        "刷单兼职说要先垫付，能不能做？",
        "已经泄露验证码了，第一步做什么？",
        "怎么判断客服电话是不是真的？",
      ];

      async function ask(text) {
        const question = (text || input.value).trim();
        if (!question || loading.value) return;
        messages.value.push({ role: "user", content: question });
        input.value = "";
        loading.value = true;
        try {
          const data = await store.api("/api/assistant", {
            method: "POST",
            body: JSON.stringify({
              question,
              history: messages.value.slice(-8),
            }),
          });
          messages.value.push({
            role: "assistant",
            content: data.answer,
            evidence: data.evidence,
            cases: data.cases,
            provider: data.provider,
          });
          requestAnimationFrame(() => {
            if (streamRef.value) streamRef.value.scrollTop = streamRef.value.scrollHeight;
          });
        } catch (err) {
          store.showToast(err.message, "error");
        } finally {
          loading.value = false;
        }
      }

      return { messages, input, loading, streamRef, suggestions, ask };
    },
    template: `
      <section class="assistant-page">
        <div class="assistant-shell">
          <aside class="assistant-intro">
            <p class="eyebrow"><span>07</span>智能安全助手</p>
            <h1>反诈智能助手</h1>
            <p>不查你的真实账户，不索要密码。只根据官方知识和公开案例，帮你判断下一步。</p>
            <div class="assistant-boundaries">
              <div><span>01</span>先停止高风险操作</div>
              <div><span>02</span>使用自己找到的官方渠道核验</div>
              <div><span>03</span>已经受损时优先止损和报警</div>
            </div>
          </aside>
          <div class="assistant-chat">
            <div class="assistant-chat-head">
              <div><span class="ai-avatar"><app-icon name="spark"/></span><div><strong>反诈智能助手</strong><small>检索知识库 · 公开案例 · 安全边界</small></div></div>
              <span class="online-dot">在线</span>
            </div>
            <div ref="streamRef" class="assistant-stream">
              <article v-for="(message, index) in messages" :key="index" class="assistant-message" :class="message.role">
                <span class="message-role">{{ message.role === 'assistant' ? '助手' : '你' }}</span>
                <div class="message-body">
                  <p>{{ message.content }}</p>
                  <div v-if="message.evidence?.length" class="assistant-sources">
                    <span>参考知识</span>
                    <b v-for="item in message.evidence" :key="item.id">{{ item.title }}</b>
                  </div>
                  <div v-if="message.cases?.length" class="assistant-cases">
                    <a v-for="item in message.cases" :key="item.id" :href="item.url" target="_blank" rel="noopener noreferrer">
                      {{ item.title }} <app-icon name="external"/>
                    </a>
                  </div>
                  <small v-if="message.provider">{{ message.provider }}</small>
                </div>
              </article>
              <div v-if="loading" class="thinking-line"><i></i><i></i><i></i><span>正在检索知识和案例</span></div>
            </div>
            <div class="suggestion-row">
              <button v-for="item in suggestions" :key="item" type="button" @click="ask(item)">{{ item }}</button>
            </div>
            <div class="assistant-composer">
              <textarea v-model="input" placeholder="描述你遇到的情况，不要输入真实验证码或密码……" @keydown.enter.exact.prevent="ask()"></textarea>
              <button type="button" :disabled="!input.trim() || loading" @click="ask()">发送 <app-icon name="arrow"/></button>
            </div>
            <p class="assistant-disclaimer">模型输出仅作风险教育。如已转账或持续受到威胁，请立即联系银行并拨打 110。</p>
          </div>
        </div>
      </section>
    `,
  };

  const LoginPage = {
    setup() {
      const route = useRoute();
      const router = useRouter();
      const mode = ref(route.query.mode === "register" ? "register" : "login");
      const loading = ref(false);
      const error = ref("");
      const showPassword = ref(false);
      const form = reactive({
        nickname: "",
        email: "",
        password: "",
        confirm: "",
      });

      function switchMode(next) {
        mode.value = next;
        error.value = "";
      }

      async function submit() {
        error.value = "";
        loading.value = true;
        try {
          if (mode.value === "register") {
            if (form.password !== form.confirm) throw new Error("两次输入的密码不一致");
            await store.register(form);
          } else {
            await store.login(form);
          }
          const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/dashboard";
          await router.replace(redirect);
        } catch (err) {
          error.value = err.message;
        } finally {
          loading.value = false;
        }
      }

      async function enterGuest() {
        store.guestLogin();
        const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/dashboard";
        await router.replace(redirect);
      }

      async function continueSession() {
        await router.replace("/dashboard");
      }

      return {
        mode,
        form,
        loading,
        error,
        showPassword,
        submit,
        switchMode,
        enterGuest,
        continueSession,
        store,
      };
    },
    template: `
      <section class="login-page login-centered">
        <div class="login-card">
          <div class="login-simple-head">
            <h1>登录与注册</h1>
          </div>
          <div v-if="store.state.auth.user" class="session-card">
            <span>当前已登录</span>
            <strong>{{ store.state.auth.user.guest ? 'test' : store.state.auth.user.nickname }}</strong>
            <small>{{ store.state.auth.user.email }}</small>
            <button class="primary-button" type="button" @click="continueSession">进入成长记录 <app-icon name="arrow"/></button>
            <button class="text-action" type="button" @click="store.logout()">退出当前账户</button>
          </div>
          <template v-else>
            <div class="login-tabs">
              <button type="button" :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</button>
              <button type="button" :class="{ active: mode === 'register' }" @click="switchMode('register')">创建账户</button>
            </div>
            <form class="login-form" @submit.prevent="submit">
              <label v-if="mode === 'register'">
                <span>昵称</span>
                <input v-model="form.nickname" maxlength="16" autocomplete="nickname" placeholder="例如：小林" />
              </label>
              <label>
                <span>邮箱</span>
                <input v-model="form.email" type="email" autocomplete="email" placeholder="name@example.com" />
              </label>
              <label>
                <span>密码</span>
                <div class="password-field">
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
                    placeholder="至少 8 个字符"
                  />
                  <button type="button" @click="showPassword = !showPassword">{{ showPassword ? '隐藏' : '显示' }}</button>
                </div>
              </label>
              <label v-if="mode === 'register'">
                <span>确认密码</span>
                <input v-model="form.confirm" type="password" autocomplete="new-password" placeholder="再次输入密码" />
              </label>
              <p v-if="error" class="login-error">{{ error }}</p>
              <button class="login-submit" type="submit" :disabled="loading">
                {{ loading ? '请稍候' : mode === 'login' ? '登录' : '创建账户' }}
                <app-icon name="arrow"/>
              </button>
            </form>
            <div class="login-divider"><span>或者</span></div>
            <button class="guest-login" type="button" @click="enterGuest">使用本地体验账户</button>
            <p class="login-privacy">密码会加盐哈希后保存在当前浏览器，不会发送到服务器。</p>
          </template>
        </div>
      </section>
    `,
  };

  const courses = [
    {
      id: "brush",
      title: "刷单返利",
      code: "01",
      summary: "先返小钱，再诱导你为了“提现”继续投入。",
      principles: ["不存在需要先垫付的正规刷单兼职", "小额到账只是降低警觉的诱饵", "连续任务、操作错误和账户冻结都是追加付款话术"],
      warning: "不要为了拿回前一笔钱而继续转账。",
    },
    {
      id: "authority",
      title: "冒充公检法",
      code: "02",
      summary: "伪造身份、制造恐惧，再以保密为由隔离你。",
      principles: ["公安机关不会电话索要保证金", "不会要求你转入所谓安全账户", "不会阻止你向家人或属地派出所核实"],
      warning: "越要求保密，越应立即向外界求证。",
    },
    {
      id: "customer",
      title: "假客服退款",
      code: "03",
      summary: "退款通常原路返回，不需要共享屏幕。",
      principles: ["验证码不能提供给任何陌生人", "不要下载陌生会议或远程控制软件", "不要使用对方提供的客服入口核验"],
      warning: "屏幕共享会把你的短信和操作完整暴露给对方。",
    },
    {
      id: "loan",
      title: "注销校园贷",
      code: "04",
      summary: "用征信焦虑诱导学生先贷款、再转账。",
      principles: ["个人征信由中国人民银行统一管理", "不存在私人客服的资金清算账户", "不要为了注销记录去申请网贷"],
      warning: "先借款再“清账”会同时形成负债和资金损失。",
    },
    {
      id: "ticket",
      title: "票务私售",
      code: "05",
      summary: "低价内部票往往要求你绕开平台担保。",
      principles: ["票务交易应留在官方平台", "不扫陌生收款码", "付款后要求再转账才能退款的应立即停止"],
      warning: "脱离平台后，对方身份和订单都无法确认。",
    },
    {
      id: "game",
      title: "游戏交易",
      code: "06",
      summary: "虚假支付截图和伪造平台联合制造“冻结”。",
      principles: ["只使用官方交易渠道", "另行打开官网核验平台真实性", "拒绝保证金、解冻费和验资款"],
      warning: "支付成功截图不是资金到账的证明。",
    },
    {
      id: "recruitment",
      title: "兼职招聘收费",
      code: "07",
      summary: "以日结和轻松工作吸引报名，再层层收取费用。",
      principles: ["正规招聘不会在入职前收取培训费、服装费或押金", "高薪低门槛与立即上岗需要格外警惕", "工作内容、公司和收款主体应能独立核验"],
      warning: "任何入职前先交钱的兼职都应立即退出。",
    },
    {
      id: "red-lines",
      title: "高风险操作红线",
      code: "08",
      summary: "验证码、屏幕共享和远程控制会让账户失去保护。",
      principles: ["短信验证码等同于账户钥匙", "屏幕共享可能暴露短信、密码和余额", "不要安装陌生人发来的远程控制软件"],
      warning: "对方越急着让你共享屏幕，越要先停下来核实。",
    },
    {
      id: "emergency",
      title: "疑似被骗应急处置",
      code: "09",
      summary: "先止损、再留证、后报警，不要继续与骗子周旋。",
      principles: ["立即停止转账并联系银行申请止付", "保存聊天、订单、账户和转账记录", "拨打 110 或联系学校保卫部门寻求帮助"],
      warning: "不要寻找收费的“网络追款专家”，避免二次受骗。",
    },
    {
      id: "verification",
      title: "官方渠道核验",
      code: "10",
      summary: "不点击对方发来的链接，不按对方给的号码求证。",
      principles: ["优先通过自己已知的官方 App 或网站核验", "不要使用陌生人提供的客服电话和二维码", "涉及资金时同时联系银行和身边的可信人员"],
      warning: "用骗子的入口核验骗子，只会得到被设计好的答案。",
    },
    {
      id: "investment",
      title: "虚假投资理财",
      code: "11",
      summary: "收益截图和内部名额只是让人追加资金的诱饵。",
      principles: ["高收益、稳赚不赔本身就是危险信号", "不要下载网友发来的投资软件或安装包", "无法正常提现时应立即停止充值并保存证据"],
      warning: "群里晒收益的人，可能和“顾问”是一伙的。",
    },
    {
      id: "acquaintance",
      title: "冒充熟人",
      code: "12",
      summary: "头像、昵称和聊天语气都可能被复制。",
      principles: ["熟人账号借钱必须通过电话或视频独立确认", "不要仅凭语音片段判断对方身份", "紧急、保密和催促转账是常见施压方式"],
      warning: "帮熟人之前，先用你原本保存的联系方式确认本人。",
    },
    {
      id: "training-refund",
      title: "教育培训退费",
      code: "13",
      summary: "假退费专员会用陌生软件和保证金套取资金。",
      principles: ["退费通常通过原购买渠道办理", "不要从短信链接下载陌生软件", "正规退费不会要求先缴保证金或手续费"],
      warning: "先交钱才能退钱的流程不符合正常退费逻辑。",
    },
    {
      id: "financial-aid",
      title: "奖助学金诈骗",
      code: "14",
      summary: "冒充老师或资助人员，以发放补助为由索要费用。",
      principles: ["奖助学金通知应通过学校官方渠道确认", "正规资助不会要求学生先缴手续费", "不要把银行卡和验证码交给个人代为激活"],
      warning: "涉及奖助学金时，直接联系辅导员或学校资助中心。",
    },
    {
      id: "fan-benefit",
      title: "粉丝福利诈骗",
      code: "15",
      summary: "免费周边和明星福利常被包装成助力、返现任务。",
      principles: ["不要为所谓免费周边先购买商品", "后援会名额和签名专辑应通过官方活动核实", "支付密码、验证码不能用于证明粉丝身份"],
      warning: "先消费再返现的福利任务，本质仍是刷单骗局。",
    },
  ];

  const AcademyPage = {
    components: { PageHead },
    setup() {
      const selectedId = ref(courses[0].id);
      const selected = computed(() => courses.find((item) => item.id === selectedId.value) || courses[0]);
      const learned = computed(() => store.state.learningProgress);
      const progress = computed(() => Math.round((learned.value.length / courses.length) * 100));

      function selectCourse(id) {
        selectedId.value = id;
      }

      function complete() {
        store.markLearned(selected.value.id);
      }

      return { courses, selectedId, selected, learned, progress, selectCourse, complete };
    },
    template: `
      <section class="workspace-page academy-page">
        <page-head
          index="10"
          eyebrow="知识训练"
          title="反诈知识训练"
          description="十五个短课覆盖校园高频反诈主题。每个模块只讲关键判断，不堆成长篇宣传文章。"
        />
        <div class="academy-progress">
          <div><span>你的学习进度</span><strong>{{ progress }}%</strong></div>
          <i><b :style="{ width: progress + '%' }"></b></i>
          <router-link to="/challenge">参加每日挑战 <app-icon name="arrow"/></router-link>
        </div>
        <div class="academy-layout">
          <div class="course-grid">
            <button
              v-for="course in courses"
              :key="course.id"
              type="button"
              :class="{ active: selectedId === course.id, learned: learned.includes(course.id) }"
              @click="selectCourse(course.id)"
            >
              <span>{{ course.code }}</span>
              <div><strong>{{ course.title }}</strong><small>{{ course.summary }}</small></div>
              <b>{{ learned.includes(course.id) ? '已掌握' : '→' }}</b>
            </button>
          </div>
          <article class="course-detail">
            <div class="course-detail-head">
              <span>第 {{ selected.code }} 课</span>
              <strong>{{ selected.title }}</strong>
              <p>{{ selected.summary }}</p>
            </div>
            <ol>
              <li v-for="(item, index) in selected.principles" :key="item">
                <span>0{{ index + 1 }}</span><p>{{ item }}</p>
              </li>
            </ol>
            <div class="course-warning">
              <span>记住这一句</span>
              <p>{{ selected.warning }}</p>
            </div>
            <button class="primary-button" type="button" @click="complete">
              {{ learned.includes(selected.id) ? '已完成本节' : '标记为已掌握' }}
              <app-icon name="arrow"/>
            </button>
          </article>
        </div>
      </section>
    `,
  };

  const ChallengePage = {
    components: { PageHead },
    setup() {
      const loading = ref(true);
      const questions = ref([]);
      const currentIndex = ref(0);
      const answers = reactive({});
      const submitting = ref(false);
      const result = ref(null);
      const error = ref("");
      const current = computed(() => questions.value[currentIndex.value]);
      const selected = computed(() => (current.value ? answers[current.value.id] : null));
      const progress = computed(() => (questions.value.length ? ((currentIndex.value + 1) / questions.value.length) * 100 : 0));

      async function load() {
        loading.value = true;
        error.value = "";
        try {
          const data = await store.api("/api/challenges");
          questions.value = data.questions;
          currentIndex.value = 0;
          Object.keys(answers).forEach((key) => delete answers[key]);
          result.value = null;
        } catch (err) {
          error.value = err.message;
        } finally {
          loading.value = false;
        }
      }

      function choose(index) {
        if (!current.value || result.value) return;
        answers[current.value.id] = index;
      }

      async function next() {
        if (selected.value === null || selected.value === undefined) {
          store.showToast("请先选择一个答案", "error");
          return;
        }
        if (currentIndex.value < questions.value.length - 1) {
          currentIndex.value += 1;
          return;
        }
        submitting.value = true;
        try {
          result.value = await store.api("/api/challenges/grade", {
            method: "POST",
            body: JSON.stringify({ answers }),
          });
          store.saveChallengeResult(result.value);
        } catch (err) {
          store.showToast(err.message, "error");
        } finally {
          submitting.value = false;
        }
      }

      onMounted(load);
      return {
        loading,
        questions,
        currentIndex,
        answers,
        submitting,
        result,
        error,
        current,
        selected,
        progress,
        choose,
        next,
        load,
      };
    },
    template: `
      <section class="workspace-page challenge-page">
        <page-head
          index="11"
          eyebrow="每日安全挑战"
          title="每日安全挑战"
          description="每题都来自真实高发套路。完成后查看逐题解释，并把成绩保存在成长记录中。"
        />
        <div v-if="loading" class="case-loading"><span></span><span></span></div>
        <div v-else-if="error" class="challenge-error">{{ error }} <button type="button" @click="load">重新加载</button></div>
        <div v-else-if="result" class="challenge-result">
          <div class="result-score">
            <span>挑战得分</span>
            <strong>{{ result.score }}</strong>
            <small>{{ result.correct }} / {{ result.total }} 正确</small>
            <b>{{ result.level }}</b>
          </div>
          <div class="result-details">
            <div class="result-heading">
              <div><span>逐题复盘</span><h2>别只看分数，看看错在哪里。</h2></div>
              <button type="button" @click="load">再挑战一次</button>
            </div>
            <article v-for="item in result.details" :key="item.id" :class="{ correct: item.correct }">
              <span>{{ item.correct ? '✓' : '×' }}</span>
              <div><strong>{{ item.category }}</strong><p>{{ item.explanation }}</p></div>
            </article>
          </div>
        </div>
        <div v-else class="challenge-layout">
          <aside class="challenge-rail">
            <span>题目</span>
            <strong>{{ String(currentIndex + 1).padStart(2, '0') }}</strong>
            <small>/ {{ String(questions.length).padStart(2, '0') }}</small>
            <div class="challenge-progress"><i :style="{ height: progress + '%' }"></i></div>
            <p>完成后自动计入成长记录</p>
          </aside>
          <article v-if="current" class="question-card">
            <div class="question-label"><span>{{ current.category }}</span><b>单选</b></div>
            <h2>{{ current.question }}</h2>
            <div class="answer-list">
              <button
                v-for="(option, index) in current.options"
                :key="option"
                type="button"
                :class="{ selected: selected === index }"
                @click="choose(index)"
              >
                <span>{{ String.fromCharCode(65 + index) }}</span>
                <p>{{ option }}</p>
              </button>
            </div>
            <button
              class="challenge-next"
              :class="{ ready: selected !== null && selected !== undefined && !submitting }"
              type="button"
              :disabled="selected === null || selected === undefined || submitting"
              @click="next"
            >
              {{ currentIndex === questions.length - 1 ? (submitting ? '正在评分' : '提交答卷') : '下一题' }}
              <app-icon name="arrow"/>
            </button>
          </article>
        </div>
      </section>
    `,
  };

  const ProfilePage = {
    components: { PageHead },
    setup() {
      const form = reactive({ ...store.state.profile });
      if (form.role === "在校学生") form.role = "本科生";
      if (form.role === "研究生") form.role = "研究生或博士生";
      const identityOptions = [
        { value: "本科生", detail: "本科阶段在读" },
        { value: "应届毕业生", detail: "正在求职或签约" },
        { value: "研究生或博士生", detail: "硕士或博士阶段" },
        { value: "老师/辅导员", detail: "学生工作与就业指导" },
      ];
      const scenarioOptions = ["兼职招聘", "二手交易", "游戏交易", "票务演出", "校园贷款", "冒充老师"];
      const levels = ["轻提醒", "标准", "严格"];

      function toggleScenario(item) {
        form.scenarios = form.scenarios.includes(item)
          ? form.scenarios.filter((value) => value !== item)
          : [...form.scenarios, item];
      }

      function save() {
        store.saveProfile(form);
      }

      return { form, identityOptions, scenarioOptions, levels, toggleScenario, save };
    },
    template: `
      <section class="workspace-page profile-page">
        <page-head
          index="08"
          eyebrow="安全档案"
          title="个人安全档案"
          description="安全档案只保存在本机，用于调整检测和演练的侧重点，不需要填写手机号、身份证或真实账户。"
        />
        <div class="profile-layout">
          <form class="profile-form" @submit.prevent="save">
            <label>
              <span>我们怎么称呼你</span>
              <input v-model="form.nickname" maxlength="16" placeholder="例如：小林" />
            </label>
            <div class="form-group identity-field">
              <span>当前身份</span>
              <div class="identity-grid">
                <button
                  v-for="identity in identityOptions"
                  :key="identity.value"
                  type="button"
                  :class="{ selected: form.role === identity.value }"
                  @click="form.role = identity.value"
                >
                  <b>{{ identity.value }}</b>
                  <small>{{ identity.detail }}</small>
                  <i>{{ form.role === identity.value ? '✓' : '' }}</i>
                </button>
              </div>
            </div>
            <div class="form-group">
              <span>经常接触的场景</span>
              <div class="choice-grid">
                <button
                  v-for="item in scenarioOptions"
                  :key="item"
                  type="button"
                  :class="{ selected: form.scenarios.includes(item) }"
                  @click="toggleScenario(item)"
                >{{ item }}</button>
              </div>
            </div>
            <div class="form-group">
              <span>提示强度</span>
              <div class="level-options">
                <button
                  v-for="level in levels"
                  :key="level"
                  type="button"
                  :class="{ selected: form.cautionLevel === level }"
                  @click="form.cautionLevel = level"
                >{{ level }}</button>
              </div>
            </div>
            <button class="primary-button form-save" type="submit">保存安全档案 <app-icon name="arrow"/></button>
          </form>
          <aside class="profile-aside">
            <span>档案如何使用</span>
            <div><b>01</b><p>首页会优先展示与你有关的风险入口。</p></div>
            <div><b>02</b><p>情景演练会从常见场景中选择示例。</p></div>
            <div><b>03</b><p>不会上传通讯录，也不会向你发送提醒。</p></div>
            <button type="button" @click="store.clearHistory()">清除本机报告与演练记录</button>
          </aside>
        </div>
      </section>
    `,
  };

  window.MingBianPages = {
    HomePage,
    ScanPage,
    ReportPage,
    CasesPage,
    PracticePage,
    DashboardPage,
    AssistantPage,
    LoginPage,
    AcademyPage,
    ChallengePage,
    ProfilePage,
  };
})();
