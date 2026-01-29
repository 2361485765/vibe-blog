<template>
  <footer class="footer">
    <div class="footer-content">
      <p class="footer-info">
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" class="beian-link">京ICP备2026002630号-1</a>
        <span class="separator">|</span>
        <a href="https://www.beian.gov.cn/portal/index?token=" target="_blank" rel="noopener noreferrer" class="beian-link">京公网安备11010602202215号</a>
        <span class="separator">|</span>
        本作品采用 <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh" target="_blank" rel="noopener noreferrer" class="license-link">知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议</a> (CC BY-NC-SA 4.0) 进行许可
      </p>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.footer {
  width: 100%;
  padding: 24px 16px;
  background: var(--bg-secondary, #f8fafc);
  border-top: 1px solid var(--border-color, #e2e8f0);
  margin-top: 40px;
}

.dark-mode .footer {
  background: var(--bg-secondary, #1e293b);
  border-top-color: var(--border-color, #334155);
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-info {
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
  word-break: break-word;
}

.dark-mode .footer-info {
  color: #94a3b8;
}

.beian-link,
.license-link {
  color: #3b82f6;
  text-decoration: underline;
  transition: color 0.2s ease;
  cursor: pointer;
}

.beian-link:hover,
.license-link:hover {
  color: #2563eb;
}

.dark-mode .beian-link,
.dark-mode .license-link {
  color: #60a5fa;
}

.dark-mode .beian-link:hover,
.dark-mode .license-link:hover {
  color: #93c5fd;
}

.separator {
  margin: 0 6px;
  color: #94a3b8;
}

.dark-mode .separator {
  color: #64748b;
}

@media (max-width: 768px) {
  .footer {
    padding: 16px 12px;
  }

  .footer-info {
    font-size: 11px;
  }

  .separator {
    margin: 0 4px;
  }
}
</style>
