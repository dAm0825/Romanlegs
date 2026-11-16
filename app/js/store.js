(function () {
  const { reactive } = Vue;

  const storageKeys = {
    profile: "mingbian-profile-v1",
    reports: "mingbian-reports-v1",
    practice: "mingbian-practice-v1",
    users: "mingbian-users-v1",
    session: "mingbian-session-v1",
    learning: "mingbian-learning-v1",
    challenges: "mingbian-challenges-v1",
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
    auth: {
      user: read(storageKeys.session, null),
    },
    learningProgress: read(storageKeys.learning, []),
    challengeHistory: read(storageKeys.challenges, []),
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

  async function hashPassword(password, salt) {
    const value = new TextEncoder().encode(`${salt}:${password}`);
    const digest = await crypto.subtle.digest("SHA-256", value);
    return Array.from(new Uint8Array(digest))
      .map((byte) => byte.toString(16).padStart(2, "0"))
      .join("");
  }

  function persistSession(user) {
    state.auth.user = user;
    write(storageKeys.session, user);
  }

  async function register({ nickname, email, password }) {
    const cleanEmail = String(email || "").trim().toLowerCase();
    const cleanNickname = String(nickname || "").trim();
    if (cleanNickname.length < 2) throw new Error("昵称至少需要 2 个字符");
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) throw new Error("请输入有效邮箱");
    if (String(password || "").length < 8) throw new Error("密码至少需要 8 个字符");
    const users = read(storageKeys.users, []);
    if (users.some((item) => item.email === cleanEmail)) {
      throw new Error("这个邮箱已在当前浏览器注册");
    }
    const salt = crypto.randomUUID();
    const passwordHash = await hashPassword(password, salt);
    const user = {
      id: crypto.randomUUID(),
      nickname: cleanNickname,
      email: cleanEmail,
      salt,
      passwordHash,
      createdAt: new Date().toISOString(),
    };
    users.push(user);
    write(storageKeys.users, users);
    persistSession({ id: user.id, nickname: user.nickname, email: user.email });
    showToast("账户已创建，登录状态保存在当前浏览器", "success");
  }

  async function login({ email, password }) {
    const cleanEmail = String(email || "").trim().toLowerCase();
    const users = read(storageKeys.users, []);
    const user = users.find((item) => item.email === cleanEmail);
    if (!user) throw new Error("当前浏览器没有找到该账户");
    const passwordHash = await hashPassword(password, user.salt);
    if (passwordHash !== user.passwordHash) throw new Error("邮箱或密码错误");
    persistSession({ id: user.id, nickname: user.nickname, email: user.email });
    showToast("登录成功", "success");
  }

  function guestLogin() {
    persistSession({
      id: "local-demo",
      nickname: "体验同学",
      email: "demo@mingbian.local",
      guest: true,
    });
    showToast("已进入本地体验模式", "success");
  }

  function logout() {
    state.auth.user = null;
    write(storageKeys.session, null);
    showToast("已退出登录");
  }

  function markLearned(courseId) {
    if (!state.learningProgress.includes(courseId)) {
      state.learningProgress.push(courseId);
      write(storageKeys.learning, state.learningProgress);
      showToast("本节已完成", "success");
    }
  }

  function saveChallengeResult(result) {
    const record = {
      ...result,
      id: Date.now(),
      date: new Date().toISOString(),
    };
    state.challengeHistory = [record, ...state.challengeHistory].slice(0, 30);
    write(storageKeys.challenges, state.challengeHistory);
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
    register,
    login,
    guestLogin,
    logout,
    markLearned,
    saveChallengeResult,
    api,
  };
})();

