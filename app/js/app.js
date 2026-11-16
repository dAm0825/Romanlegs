(function () {
  const { createApp, computed, ref, watch } = Vue;
  const { createRouter, createWebHistory, useRoute, useRouter } = VueRouter;
  const store = window.MingBianStore;
  const pages = window.MingBianPages;

  const routes = [
    { path: "/", name: "home", component: pages.HomePage, meta: { title: "首页" } },
    { path: "/scan", name: "scan", component: pages.ScanPage, meta: { title: "风险检测" } },
    { path: "/report/:id", name: "report", component: pages.ReportPage, meta: { title: "风险报告" } },
    { path: "/practice", name: "practice", component: pages.PracticePage, meta: { title: "情景演练" } },
    { path: "/academy", name: "academy", component: pages.AcademyPage, meta: { title: "知识训练" } },
    { path: "/challenge", name: "challenge", component: pages.ChallengePage, meta: { title: "每日挑战", requiresAuth: true } },
    { path: "/cases", name: "cases", component: pages.CasesPage, meta: { title: "真实案例" } },
    { path: "/dashboard", name: "dashboard", component: pages.DashboardPage, meta: { title: "成长记录", requiresAuth: true } },
    { path: "/assistant", name: "assistant", component: pages.AssistantPage, meta: { title: "智能助手" } },
    { path: "/profile", name: "profile", component: pages.ProfilePage, meta: { title: "安全档案", requiresAuth: true } },
    { path: "/login", name: "login", component: pages.LoginPage, meta: { title: "登录" } },
    { path: "/:pathMatch(.*)*", redirect: "/" },
  ];

  const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
      if (savedPosition) return savedPosition;
      if (to.path === from.path && to.query.tab === from.query.tab) return false;
      return { top: 0, behavior: "smooth" };
    },
  });

  router.afterEach((to) => {
    document.title = `${to.meta.title || "首页"} · 智能反诈训练系统`;
  });

  router.beforeEach((to) => {
    if (to.meta.requiresAuth && !store.state.auth.user) {
      return { path: "/login", query: { redirect: to.fullPath } };
    }
  });

  const navItems = [
    { label: "首页", to: "/", icon: "home" },
    { label: "风险检测", to: "/scan", icon: "scan" },
    { label: "情景演练", to: "/practice", icon: "shield" },
    { label: "知识训练", to: "/academy", icon: "book" },
    { label: "每日挑战", to: "/challenge", icon: "target" },
    { label: "真实案例", to: "/cases", icon: "news" },
    { label: "成长记录", to: "/dashboard", icon: "chart" },
    { label: "智能助手", to: "/assistant", icon: "spark" },
  ];

  const Icon = {
    props: { name: { type: String, default: "spark" } },
    template: `
      <svg v-if="name === 'home'" viewBox="0 0 24 24"><path d="m3 11 9-8 9 8v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>
      <svg v-else-if="name === 'scan'" viewBox="0 0 24 24"><path d="M8 3H4a1 1 0 0 0-1 1v4M16 3h4a1 1 0 0 1 1 1v4M8 21H4a1 1 0 0 1-1-1v-4M16 21h4a1 1 0 0 0 1-1v-4M7 12h10M12 7v10"/></svg>
      <svg v-else-if="name === 'shield'" viewBox="0 0 24 24"><path d="M12 3 4.5 6v5.4c0 4.7 3.1 8.1 7.5 9.6 4.4-1.5 7.5-4.9 7.5-9.6V6zM8.8 12l2.1 2.1 4.5-4.8"/></svg>
      <svg v-else-if="name === 'news'" viewBox="0 0 24 24"><path d="M5 4h14v16H5zM8 8h8M8 12h8M8 16h5"/></svg>
      <svg v-else-if="name === 'chart'" viewBox="0 0 24 24"><path d="M4 20V10m6 10V4m6 16v-7m4 7H2"/></svg>
      <svg v-else-if="name === 'spark'" viewBox="0 0 24 24"><path d="M12 2 9.8 9.8 2 12l7.8 2.2L12 22l2.2-7.8L22 12l-7.8-2.2z"/></svg>
      <svg v-else-if="name === 'book'" viewBox="0 0 24 24"><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H11v18H6.5A2.5 2.5 0 0 0 4 22zM20 4.5A2.5 2.5 0 0 0 17.5 2H13v18h4.5A2.5 2.5 0 0 1 20 22z"/></svg>
      <svg v-else-if="name === 'target'" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>
      <svg v-else-if="name === 'user'" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>
      <svg v-else-if="name === 'arrow'" viewBox="0 0 24 24"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>
      <svg v-else-if="name === 'external'" viewBox="0 0 24 24"><path d="M13 5h6v6M19 5l-9 9"/><path d="M10 6H5v13h13v-5"/></svg>
      <svg v-else viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/></svg>
    `,
  };

  const Shell = {
    components: { AppIcon: Icon },
    setup() {
      const route = useRoute();
      const router = useRouter();
      const menuOpen = ref(false);
      const profileOpen = ref(false);

      const activePath = computed(() => route.path);
      const initials = computed(
        () => (store.state.auth.user?.guest ? "T" : (store.state.auth.user?.nickname || "同")).slice(0, 1),
      );
      const userLabel = computed(() => {
        if (!store.state.auth.user) return "登录 / 注册";
        return store.state.auth.user.guest ? "test" : store.state.auth.user.nickname;
      });

      watch(
        () => route.fullPath,
        () => {
          menuOpen.value = false;
          profileOpen.value = false;
        },
      );

      function isActive(item) {
        if (item.to === "/") return activePath.value === "/";
        return activePath.value.startsWith(item.to);
      }

      function openProfile() {
        if (!store.state.auth.user) {
          router.push({ path: "/login", query: { redirect: route.fullPath } });
          return;
        }
        profileOpen.value = !profileOpen.value;
      }

      function logout() {
        profileOpen.value = false;
        store.logout();
        router.push("/");
      }

      return {
        navItems,
        route,
        store,
        menuOpen,
        profileOpen,
        initials,
        userLabel,
        isActive,
        openProfile,
        logout,
      };
    },
    template: `
      <div class="app-shell">
        <header class="top-shell">
          <div class="topline">
            <router-link class="brand" to="/">
              <span class="brand-symbol"><i></i><i></i></span>
              <span class="brand-copy">
                <strong>智能反诈训练系统</strong>
              </span>
            </router-link>
            <div class="top-actions">
              <button class="profile-button" type="button" @click="openProfile">
                <span class="avatar">{{ initials }}</span>
                <span class="profile-label">{{ userLabel }}</span>
                <svg viewBox="0 0 16 16"><path d="m4 6 4 4 4-4"/></svg>
              </button>
              <button class="mobile-menu" type="button" @click="menuOpen = !menuOpen" aria-label="打开菜单">
                <span></span><span></span>
              </button>
              <div v-if="profileOpen" class="profile-popover">
                <span>{{ store.state.auth.user?.guest ? '本地体验账户' : '已登录账户' }}</span>
                <strong>{{ store.state.auth.user?.guest ? 'test' : store.state.auth.user?.nickname }}</strong>
                <small>{{ store.state.auth.user?.email }}</small>
                <router-link to="/profile">编辑安全档案 <app-icon name="arrow"/></router-link>
                <button type="button" @click="logout">退出登录</button>
              </div>
            </div>
          </div>
          <nav class="main-nav" :class="{ open: menuOpen }" aria-label="主要导航">
            <router-link
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              class="nav-item"
              :class="{ active: isActive(item) }"
            >
              <app-icon :name="item.icon" />
              <span>{{ item.label }}</span>
            </router-link>
            <router-link to="/profile" class="nav-item mobile-only" :class="{ active: activePath === '/profile' }">
              <app-icon name="user"/>
              <span>安全档案</span>
            </router-link>
          </nav>
        </header>
        <main class="route-stage">
          <router-view v-slot="{ Component }">
            <transition name="page" mode="out-in">
              <component :is="Component" :key="route.fullPath" />
            </transition>
          </router-view>
        </main>
        <footer class="global-footer">
          <div>
            <strong>智能反诈训练系统</strong>
            <span>识破一次，才能真正学会拒绝。</span>
          </div>
          <p>反诈识别不替代警方结论。如已转账或泄露信息，请立即联系银行并拨打 110。</p>
          <span class="footer-code">2026 传智杯 · 网页开发挑战赛</span>
        </footer>
        <transition name="toast">
          <div v-if="store.state.toast.visible" class="toast" :class="store.state.toast.tone">
            {{ store.state.toast.message }}
          </div>
        </transition>
      </div>
    `,
  };

  const app = createApp(Shell);
  app.component("AppIcon", Icon);
  app.use(router);
  app.mount("#app");
})();
