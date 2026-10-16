<template>
  <footer class="app-footer">
    <span class="footer-brand">韩途</span>
    <span class="footer-sep">·</span>
    <span class="footer-tagline">韩国语学习平台</span>
    <span class="footer-sep">·</span>
    <span class="footer-copy">© 2026</span>
  </footer>
</template>

<style scoped>
.app-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 0 1.25rem;
  font-size: 0.75rem;
  color: var(--text-subtle);
  letter-spacing: 0.03em;
  user-select: none;
}

.footer-brand {
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.05em;
}

.footer-sep {
  opacity: 0.35;
}
</style>
