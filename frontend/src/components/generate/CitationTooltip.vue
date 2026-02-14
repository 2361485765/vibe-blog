<template>
  <div
    v-if="visible && citation"
    class="citation-tooltip"
    :style="{ top: position.top + 'px', left: position.left + 'px' }"
  >
    <div class="citation-index">[{{ index }}]</div>
    <div class="citation-domain">{{ citation.domain }}</div>
    <div class="citation-title">{{ citation.title }}</div>
    <div class="citation-snippet">{{ citation.snippet }}</div>
    <div class="citation-footer">
      <span v-if="citation.relevance" class="citation-relevance">
        ⭐ 相关性: {{ citation.relevance }}%
      </span>
      <a :href="citation.url" target="_blank" class="citation-link">🔗 打开原文</a>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Citation {
  url: string
  title: string
  domain: string
  snippet: string
  relevance?: number
}

interface Props {
  visible: boolean
  citation: Citation | null
  index: number
  position: { top: number; left: number }
}

defineProps<Props>()
</script>

<style scoped>
.citation-tooltip {
  position: fixed;
  z-index: 10000;
  width: 320px;
  padding: var(--space-md);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xl);
  font-family: var(--font-mono);
  font-size: var(--font-size-xs);
}

.citation-index {
  color: var(--color-text-muted);
  font-weight: var(--font-weight-bold);
  margin-bottom: 2px;
}

.citation-domain {
  color: var(--color-terminal-string, #22c55e);
  margin-bottom: 4px;
}

.citation-title {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-semibold);
  margin-bottom: 4px;
  line-height: var(--line-height-snug);
}

.citation-snippet {
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--space-sm);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.citation-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--space-xs);
  border-top: 1px solid var(--color-border);
}

.citation-relevance {
  color: var(--color-warning, #eab308);
}

.citation-link {
  color: var(--color-primary);
  text-decoration: none;
  transition: var(--transition-all);
}

.citation-link:hover {
  text-decoration: underline;
}
</style>
