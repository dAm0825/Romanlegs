(function () {
  const { reactive } = Vue;

  const storageKeys = {
    profile: "mingbian-profile-v1",
    reports: "mingbian-reports-v1",
    practice: "mingbian-practice-v1",
  };

  function read(key, fallback) {
    try {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : fallback;
    } catch {
      return fallback;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      // Local persistence is optional; the current route still works.
    }
  }

  const state = reactive({
    profile: read(storageKeys.profile, {
      role: "在校学生",
      scenarios: ["兼职招聘", "二手交易"],
      cautionLevel: "标准",
      nickname: "同学",
    }),
    reports: read(storageKeys.reports, []),
    practiceHistory: read(storageKeys.practice, []),
    toast: { visible: false, message: "", tone: "info" },
  });

  let toastTimer;

  function showToast(message, tone = "info") {
    clearTimeout(toastTimer);
    state.toast = { visible: true, message, tone };
    toastTimer = setTimeout(() => {
      state.toast.visible = false;
    }, 2600);
  }

  function saveProfile(profile) {
    state.profile = { ...profile };
    write(storageKeys.profile, state.profile);
    showToast("安全档案已保存在当前浏览器", "success");
  }

  function saveReport(report) {
    state.reports = [report, ...state.reports.filter((item) => item.id !== report.id)].slice(0, 30);
    write(storageKeys.reports, state.reports);
  }

  function getReport(id) {
    return state.reports.find((item) => item.id === id);
  }

  function recordPractice(record) {
    state.practiceHistory = [record, ...state.practiceHistory].slice(0, 40);
    write(storageKeys.practice, state.practiceHistory);
  }

  function clearHistory() {
    state.reports = [];
    state.practiceHistory = [];
    write(storageKeys.reports, []);
    write(storageKeys.practice, []);
    showToast("本地记录已清除");
  }

  async function api(path, options = {}) {
    const response = await fetch(path, {
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
      },
      ...options,
    });
    let body;
    try {
      body = await response.json();
    } catch {
      throw new Error("服务返回了无法解析的内容");
    }
    if (!response.ok) {
      throw new Error(body.error || "请求失败，请稍后重试");
    }
    return body;
  }

  window.MingBianStore = {
    state,
    showToast,
    saveProfile,
    saveReport,
    getReport,
    recordPractice,
    clearHistory,
    api,
  };
})();

