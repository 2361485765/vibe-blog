<template>
  <section class="hero">
    <h1>&gt; Browse Blog Posts<span class="cursor"></span></h1>
    <p>$ find ./blogs -type f -name "*.md" | wc -l</p>
  </section>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 60px 20px 40px;
  animation: fadeIn 0.6s ease-out;
}

.hero h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-foreground);
  margin-bottom: 16px;
  font-family: var(--font-mono), monospace;
}

.hero p {
  font-size: 1rem;
  color: var(--color-muted-foreground);
  font-family: var(--font-mono), monospace;
}

.cursor {
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background: var(--color-primary);
  margin-left: 4px;
  animation: blink 1s infinite;
  vertical-align: middle;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes blink {
  0%, 49%, 100% {
    opacity: 1;
  }
  50%, 99% {
    opacity: 0.3;
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .hero {
    padding: 40px 16px 24px;
  }

  .hero h1 {
    font-size: 1.75rem;
  }

  .hero p {
    font-size: 0.875rem;
  }
}
</style>
