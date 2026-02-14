<template>
  <div v-if="visible" class="quality-dialog-overlay" @click.self="$emit('close')">
    <div class="quality-dialog">
        <!-- 加载态 -->
        <div v-if="loading" class="quality-loading">
          <span class="loading-spinner">◐</span>
          <span class="loading-text">$ evaluate --verbose</span>
        </div>

        <!-- 评估结果 -->
        <template v-else-if="evaluation">
          <div class="quality-header">
            <div class="quality-grade">
              <span class="grade-badge" :class="gradeColorClass">{{ evaluation.grade }}</span>
              <span class="quality-overall">{{ evaluation.overall_score }}/100</span>
            </div>
            <button class="dialog-close-btn" @click="$emit('close')">✕</button>
          </div>

          <!-- 6 维度评分 -->
          <div class="quality-scores">
            <div v-for="(label, key) in scoreLabels" :key="key" class="score-row">
              <span class="score-label">{{ label }}</span>
              <div class="score-bar">
                <div class="score-bar-fill" :style="{ width: `${evaluation.scores[key]}%` }"></div>
              </div>
              <span class="score-value">{{ evaluation.scores[key] }}%</span>
            </div>
          </div>

          <!-- 统计信息 -->
          <div class="quality-stats">
            <span class="stat-item">📝 {{ evaluation.word_count }} 字</span>
            <span class="stat-item">📎 {{ evaluation.citation_count }} 引用</span>
            <span class="stat-item">🖼️ {{ evaluation.image_count }} 图片</span>
            <span class="stat-item">💻 {{ evaluation.code_block_count }} 代码块</span>
          </div>

          <!-- 优点 -->
          <div v-if="evaluation.strengths?.length" class="quality-list strengths">
            <div class="list-title">✓ 优点</div>
            <div v-for="(item, i) in evaluation.strengths" :key="i" class="list-item">{{ item }}</div>
          </div>

          <!-- 不足 -->
          <div v-if="evaluation.weaknesses?.length" class="quality-list weaknesses">
            <div class="list-title">✗ 不足</div>
            <div v-for="(item, i) in evaluation.weaknesses" :key="i" class="list-item">{{ item }}</div>
          </div>

          <!-- 建议 -->
          <div v-if="evaluation.suggestions?.length" class="quality-list suggestions">
            <div class="list-title">→ 建议</div>
            <div v-for="(item, i) in evaluation.suggestions" :key="i" class="list-item">{{ item }}</div>
          </div>

          <!-- 总结 -->
          <div class="quality-summary">{{ evaluation.summary }}</div>
        </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Scores {
  factual_accuracy: number
  completeness: number
  coherence: number
  relevance: number
  citation_quality: number
  writing_quality: number
}

interface Evaluation {
  grade: string
  overall_score: number
  scores: Scores
  strengths: string[]
  weaknesses: string[]
  suggestions: string[]
  summary: string
  word_count: number
  citation_count: number
  image_count: number
  code_block_count: number
}

interface Props {
  visible: boolean
  evaluation: Evaluation | null
  loading: boolean
}

const props = defineProps<Props>()
defineEmits<{ (e: 'close'): void }>()

const scoreLabels: Record<string, string> = {
  factual_accuracy: '事实准确',
  completeness: '内容完整',
  coherence: '逻辑连贯',
  relevance: '主题相关',
  citation_quality: '引用质量',
  writing_quality: '写作质量',
}

const gradeColorClass = computed(() => {
  const grade = props.evaluation?.grade || ''
  if (grade === 'N/A') return 'grade-poor'
  if (grade.startsWith('A')) return 'grade-excellent'
  if (grade.startsWith('B')) return 'grade-good'
  if (grade.startsWith('C')) return 'grade-average'
  return 'grade-poor'
})
</script>

<style scoped>
.quality-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
}

.quality-dialog {
  width: 100%;
  max-width: 480px;
  max-height: 80vh;
  overflow-y: auto;
  padding: var(--space-lg);
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  font-family: var(--font-mono);
}

.quality-loading {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xl) 0;
  justify-content: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.loading-spinner {
  animation: spin 1s linear infinite;
  font-size: var(--font-size-lg);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.quality-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
}

.quality-grade {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: #fff;
}

.grade-excellent { background: #22c55e; }
.grade-good { background: #3b82f6; }
.grade-average { background: #eab308; }
.grade-poor { background: #ef4444; }

.quality-overall {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.dialog-close-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: var(--font-size-lg);
  cursor: pointer;
  padding: var(--space-xs);
  border-radius: var(--radius-sm);
  transition: var(--transition-all);
}

.dialog-close-btn:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-input);
}

/* 6 维度评分 */
.quality-scores {
  margin-bottom: var(--space-md);
}

.score-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 3px 0;
  font-size: var(--font-size-xs);
}

.score-label {
  min-width: 64px;
  color: var(--color-text-secondary);
}

.score-bar {
  flex: 1;
  height: 8px;
  background: var(--color-bg-input);
  border-radius: 4px;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.score-value {
  min-width: 36px;
  text-align: right;
  color: var(--color-text-muted);
}

/* 统计信息 */
.quality-stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-md);
  padding: var(--space-sm) 0;
  margin-bottom: var(--space-md);
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

/* 列表 */
.quality-list {
  margin-bottom: var(--space-md);
}

.list-title {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-xs);
}

.list-item {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  padding: 2px 0 2px var(--space-md);
}

.strengths .list-title { color: var(--color-success); }
.weaknesses .list-title { color: var(--color-error, #ef4444); }
.suggestions .list-title { color: var(--color-primary); }

/* 总结 */
.quality-summary {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  padding-top: var(--space-sm);
  border-top: 1px solid var(--color-border);
  line-height: var(--line-height-relaxed);
}
</style>
