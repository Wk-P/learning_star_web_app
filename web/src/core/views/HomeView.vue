<template>
  <div class="home">
    <!-- ── 首屏 ─────────────────────────────────────────────── -->
    <section class="hero">
      <div class="hero-bg" aria-hidden="true">
        <span class="orb o1" /><span class="orb o2" />
      </div>
      <span class="badge enter" style="--d: 0">{{ BRAND_TAGLINE }}</span>
      <h1 class="title enter" style="--d: 1">
        一个账号，<span class="grad">学韩语，也学课程</span>
      </h1>
      <p class="sub enter" style="--d: 2">
        韩语 TOPIK 的视频、听力与资料，加上数学、英语、计算机的精选课程，都在这里。
      </p>
      <div class="cta enter" style="--d: 3">
        <template v-if="auth.isLoggedIn">
          <RouterLink v-if="lastSection" :to="lastSection.to" class="btn-primary press">
            继续学习{{ lastSection.short }}
            <AppIcon name="arrow" :size="18" :stroke="2.2" />
          </RouterLink>
          <a href="#sections" class="btn-ghost press">选择栏目</a>
        </template>
        <template v-else>
          <RouterLink :to="{ name: 'login' }" class="btn-primary press">
            登录开始学习
            <AppIcon name="arrow" :size="18" :stroke="2.2" />
          </RouterLink>
          <RouterLink :to="{ name: 'login', query: { tab: 'register' } }" class="btn-ghost press">注册新账号</RouterLink>
        </template>
      </div>
    </section>

    <!-- ── 两个栏目 ─────────────────────────────────────────── -->
    <section id="sections" class="sections">
      <RouterLink
        v-for="(s, i) in cards" :key="s.key" v-reveal="i"
        :to="s.to" class="section-card lift" :style="{ '--c': s.color }"
      >
        <div class="section-text">
          <span class="section-icon"><AppIcon :name="s.icon" :size="24" /></span>
          <h2 class="section-name">{{ s.label }}</h2>
          <p class="section-desc">{{ s.desc }}</p>
          <ul class="section-tabs">
            <li v-for="t in s.tabs" :key="t.to">{{ t.label }}</li>
          </ul>
          <span class="section-go">进入{{ s.short }} <AppIcon name="arrow" :size="16" :stroke="2.2" /></span>
        </div>
        <div class="section-art">
          <picture>
            <source type="image/webp" :srcset="srcset(s.img)" sizes="(max-width: 860px) 60vw, 280px" />
            <img :src="asset(s.fallback)" :alt="s.alt" class="img-fade" loading="lazy" decoding="async" @load="onImgLoad" />
          </picture>
        </div>
      </RouterLink>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/core/stores/auth'
import { BRAND_TAGLINE, SECTIONS } from '@/core/brand'
import AppIcon from '@/core/components/AppIcon.vue'
import { asset, srcset } from '@shared/asset'
import { onImgLoad } from '@shared/reveal'
import { getHistory } from '@/topik/composables/useHistory'

const auth = useAuthStore()

const cards = [
  {
    ...SECTIONS.topik,
    img: [['img/home-hero-540.webp', 540], ['img/home-hero.webp', 1080]] as Array<[string, number]>,
    fallback: 'img/home-hero.png',
    alt: '韩语学习笔记插画',
  },
  {
    ...SECTIONS.course,
    img: [['mindmaps/cs-720.webp', 720], ['mindmaps/cs.webp', 1448]] as Array<[string, number]>,
    fallback: 'mindmaps/cs.png',
    alt: '计算机学习体系思维导图',
  },
]

// 有韩语学习记录就优先推荐继续韩语，否则推荐课程
const lastSection = computed(() => (getHistory().length ? SECTIONS.topik : SECTIONS.course))
</script>

<style scoped>
.home { overflow-x: clip; }

/* ── hero ──────────────────────────────────────────────── */
.hero {
  position: relative; isolation: isolate;
  display: flex; flex-direction: column; align-items: center; text-align: center;
  padding: clamp(3.5rem, 11vh, 7rem) clamp(1rem, 4vw, 2rem) clamp(2.5rem, 6vh, 4rem);
}
.hero-bg { position: absolute; inset: 0; z-index: -1; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.35; animation: drift 16s var(--ease-in-out) infinite alternate; }
.o1 { width: 420px; height: 420px; background: #2ec4c0; top: -120px; left: 12%; }
.o2 { width: 380px; height: 380px; background: #1e4fa8; top: -60px; right: 10%; animation-delay: -8s; }
[data-theme="light"] .orb { opacity: 0.22; }
@keyframes drift { to { transform: translate(40px, 30px) scale(1.1); } }

.enter { animation: enter 0.8s var(--ease-out) both; animation-delay: calc(var(--d) * 90ms + 60ms); }
@keyframes enter { from { opacity: 0; transform: translateY(18px); } }

.badge {
  padding: 0.3rem 0.9rem; border-radius: 999px;
  font-size: 0.8rem; font-weight: 600; color: var(--text-muted);
  background: var(--surface-1); border: 1px solid var(--border-strong);
}
.title {
  margin: 1.2rem 0 1rem; max-width: 15em;
  font-size: clamp(2.2rem, 5.6vw, 4.2rem); font-weight: 800; line-height: 1.12; letter-spacing: -0.035em;
}
.grad {
  background: linear-gradient(100deg, #2ec4c0 0%, #1e4fa8 85%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.sub { max-width: 34em; font-size: clamp(1rem, 1.5vw, 1.15rem); line-height: 1.75; color: var(--text-muted); }
.cta { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.75rem; margin-top: 2rem; }

.btn-primary, .btn-ghost {
  display: inline-flex; align-items: center; justify-content: center; gap: 0.45rem;
  height: 48px; padding: 0 1.6rem; border-radius: 999px; font-size: 1rem; font-weight: 600; white-space: nowrap;
  transition: box-shadow var(--t), background var(--t), transform var(--dur-1) var(--ease-out);
}
.btn-primary { color: #fff; background: linear-gradient(135deg, #2ec4c0, #1e4fa8); box-shadow: 0 10px 28px rgba(30, 79, 168, 0.32); }
.btn-primary:hover { box-shadow: 0 14px 36px rgba(30, 79, 168, 0.42); }
.btn-primary svg { transition: transform var(--t); }
.btn-primary:hover svg { transform: translateX(3px); }
.btn-ghost { color: var(--text); background: var(--surface-1); border: 1px solid var(--border-strong); }
.btn-ghost:hover { background: var(--surface-2); }

/* ── section cards ─────────────────────────────────────── */
.sections {
  max-width: 1160px; margin: 0 auto; padding: 0 clamp(1rem, 4vw, 2rem) 4rem;
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem;
  scroll-margin-top: 80px;
}
.section-card {
  position: relative; overflow: hidden; isolation: isolate;
  display: grid; grid-template-columns: 1fr 42%; align-items: center; gap: 1rem;
  min-height: 320px; padding: 1.75rem;
  border-radius: 24px; color: var(--text);
  background: var(--surface-1); border: 1px solid var(--border);
}
.section-card::before {
  content: ''; position: absolute; inset: 0; z-index: -1;
  background: radial-gradient(90% 80% at 0% 0%, color-mix(in srgb, var(--c) 20%, transparent), transparent 65%);
  opacity: 0.7; transition: opacity var(--dur-3) ease;
}
.section-card:hover { border-color: color-mix(in srgb, var(--c) 50%, transparent); box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2); }
.section-card:hover::before { opacity: 1; }

.section-icon {
  width: 48px; height: 48px; border-radius: 14px; display: grid; place-items: center;
  color: var(--c); background: color-mix(in srgb, var(--c) 15%, transparent);
  transition: transform 0.35s var(--ease-spring);
}
.section-card:hover .section-icon { transform: scale(1.08) rotate(-4deg); }
.section-name { margin-top: 1rem; font-size: 1.6rem; font-weight: 750; letter-spacing: -0.02em; }
.section-desc { margin-top: 0.4rem; color: var(--text-muted); line-height: 1.65; }
.section-tabs { list-style: none; display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 1rem; }
.section-tabs li {
  padding: 0.18rem 0.65rem; border-radius: 999px; font-size: 0.78rem; color: var(--text-muted);
  background: var(--surface-2); border: 1px solid var(--border);
}
.section-go { display: inline-flex; align-items: center; gap: 0.3rem; margin-top: 1.4rem; font-weight: 650; color: var(--c); }
.section-go svg { transition: transform var(--t); }
.section-card:hover .section-go svg { transform: translateX(4px); }

.section-art { align-self: stretch; display: grid; place-items: center; }
.section-art img {
  width: 100%; height: auto; max-height: 260px; object-fit: cover; aspect-ratio: 1;
  border-radius: 18px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.3), 0 0 0 1px var(--border-strong);
  transform: rotate(3deg);
  transition: transform 0.5s var(--ease-out), opacity var(--dur-4) var(--ease-out);
}
.section-card:hover .section-art img { transform: rotate(0deg) scale(1.03); }

@media (max-width: 900px) {
  .sections { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .hero { padding-top: 2.5rem; }
  .cta { width: 100%; }
  .btn-primary, .btn-ghost { flex: 1; padding: 0 1rem; font-size: 0.95rem; }
  .section-card { grid-template-columns: 1fr; min-height: 0; padding: 1.25rem; }
  .section-art { order: -1; }
  .section-art img { max-height: 160px; aspect-ratio: 16 / 9; transform: none; }
  .section-name { font-size: 1.3rem; margin-top: 0.75rem; }
}
</style>
