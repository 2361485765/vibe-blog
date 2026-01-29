<template>
  <div class="result-card">
    <!-- 终端风格头部 -->
    <div class="terminal-header">
      <div class="terminal-dots">
        <span class="dot red"></span>
        <span class="dot yellow"></span>
        <span class="dot green"></span>
      </div>
      <span class="terminal-title">$ blog-output</span>
      <span class="terminal-status">ready</span>
    </div>

    <!-- 结果内容 -->
    <div class="result-content">
      <!-- 文章信息 -->
      <div class="article-info">
        <div class="info-row">
          <span class="info-label">$ title:</span>
          <span class="info-value">{{ blog.title }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">$ type:</span>
          <span class="info-value tag" :class="blog.type">{{ blog.type }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">$ length:</span>
          <span class="info-value">{{ blog.length }} 字</span>
        </div>
        <div class="info-row">
          <span class="info-label">$ created:</span>
          <span class="info-value">{{ formatDate(blog.createdAt) }}</span>
        </div>
      </div>

      <!-- 文章摘要 -->
      <div class="article-summary">
        <div class="summary-header">
          <span class="font-mono text-xs text-muted-foreground">$ cat summary.md</span>
        </div>
        <div class="summary-content">
          {{ blog.summary }}
        </div>
      </div>

      <!-- 标签 -->
      <div class="article-tags">
        <span class="tag-label">$ tags:</span>
        <div class="tags-list">
          <span
            v-for="tag in blog.tags"
            :key="tag"
            class="tag"
          >
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-label">章节数</div>
          <div class="stat-value">{{ blog.sections }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">配图数</div>
          <div class="stat-value">{{ blog.images }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">代码块</div>
          <div class="stat-value">{{ blog.codeBlocks }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">阅读时间</div>
          <div class="stat-value">{{ blog.readTime }}分钟</div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="actions">
        <button class="btn-primary" @click="$emit('view')">
          $ view
        </button>
        <button class="btn-secondary" @click="$emit('edit')">
          $ edit
        </button>
        <button class="btn-secondary" @click="$emit('download')">
          $ download
        </button>
        <button class="btn-secondary" @click="$emit('share')">
          $ share
        </button>
      </div>

      <!-- 代码块预览 -->
      <div class="code-preview" v-if="showCodePreview">
        <div class="preview-header">
          <span class="font-mono text-xs text-muted-foreground">$ head -20 article.md</span>
          <button class="close-btn" @click="showCodePreview = false">×</button>
        </div>
        <pre class="preview-content"><code>{{ blog.content.substring(0, 500) }}...</code></pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Blog {
  id: string
  title: string
  type: string
  length: number
  createdAt: Date
  summary: string
  tags: string[]
  sections: number
  images: number
  codeBlocks: number
  readTime: number
  content: string
}

interface Props {
  blog: Blog
}

withDefaults(defineProps<Props>(), {})

const emit = defineEmits<{
  view: []
  edit: []
  download: []
  share: []
}>()

const showCodePreview = ref(false)

const formatDate = (date: Date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.result-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  margin: 24px 0;
}

.terminal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
}

.terminal-dots {
  display: flex;
  gap: 6px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.red { background: #ef4444; }
.dot.yellow { background: #eab308; }
.dot.green { background: #22c55e; }

.terminal-title {
  flex: 1;
  color: #64748b;
}

.terminal-status {
  color: #22c55e;
  font-weight: 600;
}

.result-content {
  padding: 20px;
}

.article-info {
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(139, 92, 246, 0.05);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 6px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #8b5cf6;
  font-weight: 600;
  min-width: 80px;
}

.info-value {
  color: #1e293b;
  flex: 1;
}

.info-value.tag {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 4px;
  font-size: 12px;
}

.article-summary {
  margin-bottom: 20px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  overflow: hidden;
}

.summary-header {
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
}

.summary-content {
  padding: 12px;
  font-size: 13px;
  line-height: 1.6;
  color: #475569;
  max-height: 150px;
  overflow-y: auto;
}

.article-tags {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}

.tag-label {
  color: #8b5cf6;
  font-weight: 600;
  flex-shrink: 0;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  display: inline-block;
  padding: 6px 12px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 4px;
  font-size: 12px;
  color: #8b5cf6;
  transition: all 0.3s;
}

.tag:hover {
  background: rgba(139, 92, 246, 0.2);
  border-color: #8b5cf6;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 6px;
  text-align: center;
}

.stat-label {
  font-size: 11px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #3b82f6;
  font-family: 'JetBrains Mono', monospace;
}

.actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-primary {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid #8b5cf6;
  color: #8b5cf6;
  flex: 1;
  min-width: 100px;
}

.btn-primary:hover {
  background: rgba(139, 92, 246, 0.2);
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
}

.btn-secondary {
  background: rgba(100, 116, 139, 0.1);
  border: 1px solid #cbd5e1;
  color: #64748b;
}

.btn-secondary:hover {
  background: rgba(100, 116, 139, 0.2);
}

.code-preview {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  overflow: hidden;
  margin-top: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.08);
  border-bottom: 1px solid #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #64748b;
}

.preview-content {
  padding: 12px;
  margin: 0;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #475569;
  max-height: 200px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.5);
}

@media (max-width: 768px) {
  .actions {
    flex-direction: column;
  }

  .btn-primary,
  .btn-secondary {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
