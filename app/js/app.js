const FALLBACK_SAMPLE = `录用通知书

你好，欢迎加入星河科技。以下为你的录用条件，请于收到本通知后 3 天内回复确认。

一、岗位
岗位名称为“产品运营培训生”，工作地点为上海，公司可根据业务需要调整岗位和工作地点，员工应无条件服从。

二、合同与试用期
首次签订期限为一年，其中试用期为三个月。试用期工资为每月 6000 元，转正后月薪为 8000 元，其中绩效工资占 40%。

三、工作时间
执行大小周工作制，周一至周五原则上工作 9 小时，每两周周六正常上班。公司提倡奋斗文化，工作日延时工作不计加班。

四、社会保险
员工转正后开始缴纳社会保险，试用期按实习关系管理。住房公积金根据公司当年度经营情况决定是否缴纳。

五、保密、竞业与离职
员工入职即需签署保密和竞业限制协议。离职后两年内不得从事任何与公司业务相关的行业。如员工主动离职，应提前七天提交申请，并向公司支付招聘及培训损失 30000 元。

六、其他
公司有权根据绩效考核结果单方面调整薪资。员工请假、离职及绩效规则以公司内部制度为准，员工确认后视为完全知悉并同意。`;

const STAGE_ORDER = [
  "pii_shield",
  "clause_scout",
  "policy_rag",
  "risk_engine",
  "action_planner",
  "safety_reviewer",
];

const PRIORITY_LABELS = {
  now: "优先处理",
  before_sign: "签约前",
  archive: "留证",
};

const state = {
  result: null,
  filter: "all",
  analysisTimer: null,
  stageTimer: null,
  toastTimer: null,
};

const elements = {};

function cacheElements() {
  for (const id of [
    "modelPill",
    "contractInput",
    "charCount",
    "sampleButton",
    "uploadButton",
    "fileInput",
    "clearButton",
    "analyzeButton",
    "heroDemoButton",
    "agentEmpty",
    "agentSteps",
    "agentState",
    "resultsSection",
    "riskGauge",
    "riskScore",
    "riskLevel",
    "summaryText",
    "providerName",
    "traceDuration",
    "disclaimerText",
    "reportId",
    "findingCount",
    "findingsList",
    "actionCount",
    "actionList",
    "confirmCheckbox",
    "generateDraftButton",
    "draftCard",
    "draftText",
    "copyDraftButton",
    "copyReportButton",
    "downloadReportButton",
    "toast",
  ]) {
    elements[id] = document.getElementById(id);
  }
}

function escapeHtml(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function showToast(message) {
  clearTimeout(state.toastTimer);
  elements.toast.textContent = message;
  elements.toast.classList.add("visible");
  state.toastTimer = setTimeout(() => elements.toast.classList.remove("visible"), 2800);
}

async function copyText(text, successMessage = "已复制到剪贴板") {
  try {
    await navigator.clipboard.writeText(text);
    showToast(successMessage);
  } catch {
    const helper = document.createElement("textarea");
    helper.value = text;
    helper.style.position = "fixed";
    helper.style.opacity = "0";
    document.body.appendChild(helper);
    helper.select();
    document.execCommand("copy");
    helper.remove();
    showToast(successMessage);
  }
}

function updateCharacterCount() {
  elements.charCount.textContent = `${elements.contractInput.value.length.toLocaleString("zh-CN")} 字符`;
}

function resetAgentTrace() {
  elements.agentEmpty.hidden = false;
  elements.agentSteps.classList.remove("is-visible");
  elements.agentState.textContent = "等待输入";
  elements.agentSteps.querySelectorAll("li").forEach((row) => {
    row.classList.remove("is-running", "is-done");
    row.querySelector(".step-time").textContent = "—";
  });
}

function startLiveTrace() {
  elements.agentEmpty.hidden = true;
  elements.agentSteps.classList.add("is-visible");
  elements.agentState.textContent = "工作中";
  const rows = [...elements.agentSteps.querySelectorAll("li")];
  rows.forEach((row) => row.classList.remove("is-running", "is-done"));
  rows[0].classList.add("is-running");

  let stage = 0;
  state.stageTimer = setInterval(() => {
    if (stage < rows.length - 1) {
      rows[stage].classList.remove("is-running");
      rows[stage].classList.add("is-done");
      rows[stage].querySelector(".step-time").textContent = "done";
      stage += 1;
      rows[stage].classList.add("is-running");
    }
  }, 650);
}

function completeLiveTrace(result) {
  clearInterval(state.stageTimer);
  const rows = [...elements.agentSteps.querySelectorAll("li")];
  const stepMap = new Map(result.agent.steps.map((step) => [step.name, step]));
  rows.forEach((row) => {
    const step = stepMap.get(row.dataset.step);
    row.classList.remove("is-running");
    row.classList.add("is-done");
    row.querySelector(".step-time").textContent = step ? `${step.duration_ms} ms` : "done";
  });
  elements.agentState.textContent = "已完成";
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Health check failed");
    const data = await response.json();
    elements.modelPill.classList.add("online");
    elements.modelPill.querySelector("span").textContent = data.model_configured
      ? "DEEPSEEK AGENT ONLINE"
      : "LOCAL DEMO READY";
  } catch {
    elements.modelPill.querySelector("span").textContent = "OFFLINE DEMO";
  }
}

async function loadSample({ autoAnalyze = false } = {}) {
  elements.sampleButton.disabled = true;
  try {
    const response = await fetch("/api/demo-contract", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("Demo unavailable");
    const data = await response.json();
    elements.contractInput.value = data.text;
  } catch {
    elements.contractInput.value = FALLBACK_SAMPLE;
  } finally {
    elements.sampleButton.disabled = false;
    updateCharacterCount();
    elements.contractInput.focus({ preventScroll: true });
    if (autoAnalyze) {
      await runAnalysis();
    }
  }
}

async function handleFileUpload(file) {
  if (!file) return;
  if (!/\.(txt|md)$/i.test(file.name)) {
    showToast("请选择 TXT 或 Markdown 文件");
    return;
  }
  if (file.size > 90_000) {
    showToast("文件过大，请控制在 90KB 以内");
    return;
  }
  try {
    elements.contractInput.value = await file.text();
    updateCharacterCount();
    showToast(`已读取 ${file.name}`);
  } catch {
    showToast("文件读取失败，请重试");
  }
}

async function runAnalysis() {
  const contractText = elements.contractInput.value.trim();
  if (contractText.length < 20) {
    showToast("请先粘贴至少 20 个字符的合同内容");
    elements.contractInput.focus();
    return;
  }

  elements.analyzeButton.disabled = true;
  elements.analyzeButton.classList.add("is-loading");
  elements.analyzeButton.querySelector("span").textContent = "正在侦察";
  elements.resultsSection.hidden = true;
  startLiveTrace();

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ contract_text: contractText }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "分析失败，请稍后重试");
    }
    state.result = data;
    completeLiveTrace(data);
    renderResult(data);
    persistLastResult(data);
    window.setTimeout(() => {
      elements.resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 80);
  } catch (error) {
    clearInterval(state.stageTimer);
    resetAgentTrace();
    elements.agentState.textContent = "分析失败";
    showToast(error.message || "分析失败，请稍后重试");
  } finally {
    elements.analyzeButton.disabled = false;
    elements.analyzeButton.classList.remove("is-loading");
    elements.analyzeButton.querySelector("span").textContent = "开始风险侦察";
  }
}

function persistLastResult(result) {
  try {
    localStorage.setItem(
      "offerguard-last-report",
      JSON.stringify({
        id: result.id,
        created_at: result.created_at,
        score: result.score,
        level: result.level,
        findingCount: result.findings.length,
        provider: result.agent.provider,
      }),
    );
  } catch {
    // Storage may be disabled; history is a convenience, not a requirement.
  }
}

function animateScore(target) {
  const started = performance.now();
  const duration = 850;
  const initial = 0;
  const tick = (now) => {
    const progress = Math.min(1, (now - started) / duration);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(initial + (target - initial) * eased);
    elements.riskScore.textContent = String(current);
    elements.riskGauge.style.setProperty("--score", String(current));
    if (progress < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function renderResult(result) {
  elements.resultsSection.hidden = false;
  elements.reportId.textContent = `OG-${result.id}`;
  elements.riskLevel.textContent = result.level;
  elements.summaryText.textContent = result.summary;
  elements.providerName.textContent = result.agent.provider;
  elements.traceDuration.textContent = `${(result.agent.duration_ms / 1000).toFixed(2)} 秒 · ${result.agent.steps.length} 步`;
  elements.disclaimerText.textContent = result.disclaimer;
  elements.findingCount.textContent = `${result.findings.length} 项发现`;
  elements.actionCount.textContent = `${result.actions.length} ITEMS`;
  elements.confirmCheckbox.checked = false;
  elements.generateDraftButton.disabled = true;
  elements.draftCard.hidden = true;
  elements.draftText.value = "";
  state.filter = "all";
  document.querySelectorAll(".severity-filters button").forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === "all");
  });

  animateScore(result.score);
  renderFindings();
  renderActions(result.actions);
}

function renderFindings() {
  if (!state.result) return;
  const findings =
    state.filter === "all"
      ? state.result.findings
      : state.result.findings.filter((finding) => finding.severity === state.filter);
  elements.findingCount.textContent =
    state.filter === "all"
      ? `${state.result.findings.length} 项发现`
      : `${findings.length} 项 / 共 ${state.result.findings.length} 项`;

  if (!findings.length) {
    elements.findingsList.innerHTML = '<div class="empty-findings">这一等级下暂无发现。</div>';
    return;
  }

  const evidenceMap = new Map(state.result.evidence.map((item) => [item.id, item]));
  elements.findingsList.innerHTML = findings
    .map(
      (finding, index) => `
        <article class="finding-card ${index === 0 && state.filter === "all" ? "open" : ""}" data-id="${escapeHtml(finding.id)}">
          <button class="finding-trigger" type="button" aria-expanded="${index === 0 && state.filter === "all"}">
            <span class="finding-title-row">
              <i class="severity-mark ${escapeHtml(finding.severity)}"></i>
              <span>
                <span class="finding-title">${escapeHtml(finding.title)}</span>
                <span class="finding-quote">${escapeHtml(finding.quote)}</span>
              </span>
            </span>
            <span class="finding-confidence">${Math.round(finding.confidence * 100)}% MATCH</span>
            <i class="finding-chevron" aria-hidden="true"></i>
          </button>
          <div class="finding-body">
            <blockquote class="quote-block">${escapeHtml(finding.quote)}</blockquote>
            <div class="finding-explain">
              <p><strong>为什么需要核对</strong>${escapeHtml(finding.why)}</p>
              <p><strong>建议动作</strong>${escapeHtml(finding.suggestion)}</p>
              <div class="citation-row" aria-label="证据编号">
                ${(finding.citations || [])
                  .map(
                    (citationId) =>
                      `<button class="citation-chip" data-evidence="${escapeHtml(citationId)}" type="button">${escapeHtml(citationId)} ↗</button>`,
                  )
                  .join("")}
              </div>
            </div>
            <div class="evidence-drawer" aria-live="polite"></div>
          </div>
        </article>
      `,
    )
    .join("");

  elements.findingsList.querySelectorAll(".citation-chip").forEach((chip) => {
    chip.addEventListener("click", (event) => {
      event.stopPropagation();
      const evidence = evidenceMap.get(chip.dataset.evidence);
      const drawer = chip.closest(".finding-card").querySelector(".evidence-drawer");
      if (!evidence) return;
      drawer.innerHTML = `
        <div class="evidence-drawer-head">
          <strong>${escapeHtml(evidence.title)}</strong>
          <span>${escapeHtml(evidence.id)}</span>
        </div>
        <p><b>${escapeHtml(evidence.source)}</b><br />${escapeHtml(evidence.text)}</p>
      `;
      drawer.classList.add("visible");
      drawer.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });
}

function renderActions(actions) {
  elements.actionList.innerHTML = actions
    .map(
      (action, index) => `
        <li class="action-item">
          <span class="action-index">${String(index + 1).padStart(2, "0")}</span>
          <div class="action-copy">
            <h3>${escapeHtml(action.title)}</h3>
            <p>${escapeHtml(action.detail)}</p>
          </div>
          <span class="priority-tag ${escapeHtml(action.priority)}">${escapeHtml(
            PRIORITY_LABELS[action.priority] || action.priority,
          )}</span>
        </li>
      `,
    )
    .join("");
}

function generateDraft() {
  if (!state.result) return;
  const actions = state.result.actions
    .filter((action) => action.priority !== "archive")
    .slice(0, 5)
    .map((action, index) => `${index + 1}. ${action.title}：${action.detail}`);
  const questions = state.result.questions.length
    ? `\n我还想补充确认：\n${state.result.questions.map((item) => `• ${item}`).join("\n")}`
    : "";
  elements.draftText.value = `您好，感谢您发送录用通知。为了在确认前准确理解双方权益与义务，我认真核对了合同文本，希望先就以下事项书面澄清：

${actions.join("\n")}
${questions}

这些问题确认清楚后，我会及时回复。感谢您的理解与协助。`;
  elements.draftCard.hidden = false;
  elements.draftCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
  elements.draftText.focus({ preventScroll: true });
}

function downloadReport() {
  if (!state.result) return;
  const blob = new Blob([state.result.report_markdown], { type: "text/markdown;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `OfferGuard-${state.result.id}.md`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
  showToast("Markdown 报告已导出");
}

function bindEvents() {
  elements.contractInput.addEventListener("input", updateCharacterCount);
  elements.sampleButton.addEventListener("click", () => loadSample());
  elements.heroDemoButton.addEventListener("click", () => {
    document.getElementById("workspace").scrollIntoView({ behavior: "smooth", block: "start" });
    loadSample({ autoAnalyze: true });
  });
  elements.uploadButton.addEventListener("click", () => elements.fileInput.click());
  elements.fileInput.addEventListener("change", () => {
    handleFileUpload(elements.fileInput.files[0]);
    elements.fileInput.value = "";
  });
  elements.clearButton.addEventListener("click", () => {
    elements.contractInput.value = "";
    updateCharacterCount();
    resetAgentTrace();
    elements.contractInput.focus();
  });
  elements.analyzeButton.addEventListener("click", runAnalysis);

  document.querySelector(".severity-filters").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-filter]");
    if (!button) return;
    state.filter = button.dataset.filter;
    document.querySelectorAll(".severity-filters button").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    renderFindings();
  });

  elements.findingsList.addEventListener("click", (event) => {
    const trigger = event.target.closest(".finding-trigger");
    if (!trigger) return;
    const card = trigger.closest(".finding-card");
    const willOpen = !card.classList.contains("open");
    card.classList.toggle("open", willOpen);
    trigger.setAttribute("aria-expanded", String(willOpen));
  });

  elements.confirmCheckbox.addEventListener("change", () => {
    elements.generateDraftButton.disabled = !elements.confirmCheckbox.checked;
  });
  elements.generateDraftButton.addEventListener("click", generateDraft);
  elements.copyDraftButton.addEventListener("click", () =>
    copyText(elements.draftText.value, "沟通草稿已复制；请确认收件人后再发送"),
  );
  elements.copyReportButton.addEventListener("click", () => {
    if (state.result) copyText(state.result.report_markdown, "风险报告已复制");
  });
  elements.downloadReportButton.addEventListener("click", downloadReport);
}

document.addEventListener("DOMContentLoaded", async () => {
  cacheElements();
  bindEvents();
  updateCharacterCount();
  await loadHealth();
});

