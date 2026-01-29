<template>
  <div class="xhs-container" :class="{ 'dark-mode': isDark }">
    <!-- 终端风格导航栏 -->
    <nav class="terminal-nav">
      <div class="terminal-nav-left">
        <div class="terminal-dots">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
        <span class="terminal-title">$ xhs-creator --generate</span>
      </div>
      <div class="terminal-nav-right">
        <a href="https://github.com/datawhalechina/vibe-blog" target="_blank" rel="noopener noreferrer" class="nav-cmd" title="GitHub - vibe-blog">GitHub</a>
        <router-link to="/" class="nav-cmd">cd ~/blog</router-link>
        <button class="theme-toggle" @click="isDark = !isDark">{{ isDark ? '☀️' : '🌙' }}</button>
      </div>
    </nav>

    <!-- 页面标题 -->
    <div class="container">
      <div class="page-title">
        <h1>> 小红书创作助手_</h1>
        <p class="code-comment">// 输入主题，一键生成小红书风格信息图系列</p>
      </div>

    <!-- 主卡片 -->
    <div class="main-card">
      <div class="form-group">
        <label>📌 输入主题</label>
        <textarea 
          v-model="topic" 
          class="text-input" 
          placeholder="例如：RAG技术入门、Redis缓存原理、Python装饰器详解..."
        ></textarea>
      </div>

      <div class="options-row">
        <div class="option-group">
          <label>📄 页面数量</label>
          <select v-model="pageCount">
            <option value="3">3 页</option>
            <option value="4">4 页</option>
            <option value="5">5 页</option>
            <option value="6">6 页</option>
          </select>
        </div>
        <div class="option-group">
          <label>🎨 视觉风格</label>
          <select v-model="visualStyle">
            <option value="hand_drawn">温暖手绘风</option>
            <option value="claymation">黏土动画风</option>
            <option value="ghibli_summer">🌻 宫崎骏的夏天（漫画分镜）</option>
          </select>
        </div>
        <div class="option-group">
          <label>🎬 动画封面</label>
          <select v-model="generateVideo">
            <option value="false">仅静态图</option>
            <option value="true">生成动画</option>
          </select>
        </div>
      </div>

      <button class="generate-btn" :disabled="isLoading || !topic.trim()" @click="handleGenerate">
        ✨ 开始生成
      </button>

      <div v-if="errorMsg" class="error-msg show">{{ errorMsg }}</div>

      <!-- SSE 进度条组件 -->
      <div v-if="showProgress" class="progress-container show">
        <div class="progress-header">
          <span class="progress-title">{{ progressTitle }}</span>
          <button class="cancel-btn" @click="cancelGeneration">取消生成</button>
        </div>
        
        <div class="main-progress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }">
              <div class="progress-glow"></div>
            </div>
          </div>
          <span class="progress-percent">{{ progressPercent }}%</span>
        </div>
        
        <div class="stage-indicators">
          <template v-for="(stage, index) in stages" :key="stage.id">
            <div 
              class="stage-item" 
              :class="getStageClass(stage.id)"
              :data-stage="stage.id"
              @mouseenter="hoveredStage = stage.id"
              @mouseleave="hoveredStage = null"
            >
              <div class="stage-icon">{{ stage.icon }}</div>
              <div class="stage-name">{{ stage.name }}</div>
              <div class="stage-status">{{ getStageStatus(stage.id) }}</div>
              <div v-if="stage.id === 'images' && imageSubProgress" class="stage-sub-progress">
                ({{ imageSubProgress.current }}/{{ imageSubProgress.total }})
              </div>
              <div v-if="hoveredStage === stage.id && stageDetails[stage.id]" class="stage-detail">
                {{ stageDetails[stage.id] }}
              </div>
            </div>
            <div v-if="index < stages.length - 1" class="stage-arrow">→</div>
          </template>
        </div>
        
        <div class="progress-info">
          <span class="current-stage">{{ currentStageText }}</span>
          <span class="time-estimate">{{ timeEstimate }}</span>
        </div>
      </div>

      <!-- 结果区域 -->
      <div v-if="showResult" class="result-section show">
        <h2 class="result-title">🎉 生成完成</h2>
        
        <h3 style="margin-bottom: 12px;">📷 信息图预览</h3>
        <div class="images-grid">
          <div 
            v-for="(img, index) in imageSlots" 
            :key="index" 
            class="image-card"
            :class="{ loading: img.loading }"
            :id="`image-slot-${index}`"
            @mouseenter="img.showTooltip = true"
            @mouseleave="img.showTooltip = false"
          >
            <template v-if="img.loading">
              <div class="placeholder">
                <div class="mini-spinner"></div>
                <span>{{ img.statusText || `第 ${index + 1} 页` }}</span>
              </div>
            </template>
            <template v-else>
              <img :src="img.url" :alt="`第${index + 1}张`">
              <div class="caption">第 {{ index + 1 }} 页{{ index === 0 ? ' (封面)' : '' }}</div>
              <!-- 分镜提示浮窗 -->
              <div v-if="img.showTooltip && img.prompt" class="prompt-tooltip">
                <div class="tooltip-header">
                  <span>🎨 第 {{ index + 1 }} 页视觉指令</span>
                  <button @click.stop="copyImagePrompt(index)">复制</button>
                </div>
                <pre>{{ img.prompt }}</pre>
              </div>
            </template>
          </div>
        </div>

        <div class="copy-section">
          <h3>📝 推荐标题</h3>
          <div class="titles-list">
            <div 
              v-for="(title, i) in currentResult?.titles || []" 
              :key="i" 
              class="title-item"
              :class="{ primary: i === 0 }"
            >
              {{ i === 0 ? '⭐ ' : '' }}{{ title }}
            </div>
          </div>
          
          <h3>📄 文案内容</h3>
          <div class="copy-content">{{ currentResult?.copywriting || '' }}</div>
          
          <h3 style="margin-top: 16px;">🏷️ 推荐标签</h3>
          <div class="tags-list">
            <span v-for="tag in currentResult?.tags || []" :key="tag" class="tag">#{{ tag }}</span>
          </div>
        </div>
        
        <!-- 讲解视频生成区域 -->
        <div class="explanation-video-section">
          <h3 style="margin-bottom: 12px; color: #333;">🎬 生成讲解视频</h3>
          <p style="color: #666; font-size: 14px; margin-bottom: 16px;">
            将所有图片合成为一个完整的动画讲解视频，适合发布到小红书、抖音等平台
          </p>
          <div class="video-options">
            <select v-model="videoModel">
              <option value="sora2">🎬 Sora2 (推荐)</option>
              <option value="veo3">🎥 Veo3</option>
            </select>
            <select v-model="videoStyle">
              <option value="ghibli_summer">🌻 宫崎骏夏日风</option>
              <option value="cartoon">🎨 卡通活泼风</option>
              <option value="scientific">🔬 科普专业风</option>
            </select>
            <select v-model="videoDuration">
              <option value="30">30 秒</option>
              <option value="60">60 秒</option>
              <option value="90">90 秒</option>
              <option value="120">2 分钟</option>
            </select>
            <button class="explanation-video-btn" :disabled="isGeneratingVideo" @click="generateExplanationVideo">
              🎬 {{ isGeneratingVideo ? '生成中...' : '生成讲解视频' }}
            </button>
          </div>
          
          <!-- 视频生成进度 -->
          <div v-if="showVideoProgress" class="video-progress-container show">
            <div class="video-progress-bar">
              <div class="video-progress-fill" :style="{ width: videoProgressPercent + '%' }"></div>
            </div>
            <div class="video-progress-text">{{ videoProgressText }}</div>
          </div>
          
          <!-- 视频结果展示 -->
          <div v-if="explanationVideoUrl" class="video-result-container show">
            <h4 style="margin-bottom: 12px; color: #333;">✅ 讲解视频已生成</h4>
            <video :src="explanationVideoUrl" controls autoplay loop muted playsinline></video>
            <div class="video-actions">
              <button @click="downloadExplanationVideo">📥 下载视频</button>
              <button @click="copyVideoUrl">📋 复制链接</button>
            </div>
          </div>
        </div>
        
        <!-- 发布按钮区域 -->
        <div class="publish-section">
          <h3>🚀 发布到小红书</h3>
          <p style="color: #666; font-size: 14px; margin-bottom: 16px;">
            请先在浏览器登录小红书创作者中心，然后使用浏览器扩展导出 Cookie
          </p>
          <div class="publish-buttons">
            <button class="publish-btn outline" @click="copyToClipboard">📋 复制文案</button>
            <button class="publish-btn outline" @click="downloadImages">📥 下载图片</button>
            <button class="publish-btn primary" @click="openPublishDialog">🚀 一键发布</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 发布弹窗 -->
    <div v-if="showPublishModal" class="publish-modal" @click.self="closePublishDialog">
      <div class="publish-modal-content">
        <h3>🔐 输入小红书 Cookie</h3>
        <p>在浏览器开发者工具 → Network → 任意请求 → Headers → Cookie，复制粘贴即可：</p>
        <textarea 
          v-model="cookieInput" 
          placeholder="直接粘贴 Cookie 字符串，如: a1=xxx; webId=yyy; web_session=zzz"
        ></textarea>
        <div class="modal-actions">
          <button class="cancel" @click="closePublishDialog">取消</button>
          <button class="confirm" @click="publishToXHS">确认发布</button>
        </div>
      </div>
    </div>

    <!-- 分镜详情面板 -->
    <div v-if="showStoryboardPanel" class="side-panel storyboard-panel">
      <div class="panel-header storyboard">
        <h3>🎨 分镜视觉指令</h3>
        <button @click="showStoryboardPanel = false">×</button>
      </div>
      <div class="panel-content">
        <div 
          v-for="(p, i) in storyboardPrompts" 
          :key="i" 
          class="prompt-card"
          :class="getPageTypeClass(p.page_type)"
        >
          <div class="prompt-header">
            <span>第 {{ p.index + 1 }} 页 ({{ p.page_type }})</span>
            <button @click="copyPrompt(i)">复制</button>
          </div>
          <pre>{{ p.prompt }}</pre>
        </div>
      </div>
    </div>

    <!-- 大纲详情面板 -->
    <div v-if="showOutlinePanel" class="side-panel outline-panel">
      <div class="panel-header outline">
        <h3>📋 完整大纲</h3>
        <button @click="showOutlinePanel = false">×</button>
      </div>
      <div class="panel-content">
        <div v-if="outlineData?.outline" class="outline-section">
          <div class="section-header">
            <span>📝 完整大纲</span>
            <button @click="copyOutline">复制</button>
          </div>
          <pre>{{ outlineData.outline }}</pre>
        </div>
        <div v-if="outlineData?.pages?.length" class="pages-section">
          <h4>📄 各页内容</h4>
          <div 
            v-for="(p, i) in outlineData.pages" 
            :key="i" 
            class="page-card"
            :class="getPageTypeClass(p.page_type)"
          >
            <div class="page-header">
              <span>第 {{ p.index + 1 }} 页 <span class="page-type-badge">{{ p.page_type }}</span></span>
            </div>
            <div class="page-content">{{ p.content || '暂无内容' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部备案信息 -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import * as api from '../services/api'
import { parseCookies } from '../utils/helpers'
import Footer from '../components/Footer.vue'

const route = useRoute()
const isDark = ref(false)

// ========== 输入状态 ==========
const topic = ref('')
const pageCount = ref('4')
const visualStyle = ref('hand_drawn')
const generateVideo = ref('false')

// ========== 生成状态 ==========
const isLoading = ref(false)
const showProgress = ref(false)
const showResult = ref(false)
const errorMsg = ref('')
const currentTaskId = ref<string | null>(null)
let eventSource: EventSource | null = null
let startTime: number | null = null

// ========== 进度状态 ==========
const progressTitle = ref('🚀 小红书内容生成中...')
const progressPercent = ref(0)
const currentStageText = ref('准备中...')
const timeEstimate = ref('预计剩余: --')
const hoveredStage = ref<string | null>(null)
const imageSubProgress = ref<{ current: number; total: number } | null>(null)

// ========== 阶段定义 ==========
const stages = [
  { id: 'search', icon: '🔍', name: '搜索' },
  { id: 'outline', icon: '📋', name: '大纲' },
  { id: 'content', icon: '📝', name: '文案' },
  { id: 'storyboard', icon: '🎨', name: '分镜' },
  { id: 'images', icon: '🖼️', name: '图片' },
  { id: 'video', icon: '🎬', name: '视频' }
]
const stageStatuses = reactive<Record<string, string>>({})
const stageDetails = reactive<Record<string, string>>({})

// ========== 结果数据 ==========
interface XhsResult {
  id?: string
  topic?: string
  image_urls?: string[]
  video_url?: string
  titles?: string[]
  copywriting?: string
  tags?: string[]
  pages?: Array<{ content?: string; page_type?: string }>
}
const currentResult = ref<XhsResult | null>(null)

// ========== 图片槽位 ==========
interface ImageSlot {
  loading: boolean
  url: string
  prompt: string
  statusText: string
  showTooltip: boolean
}
const imageSlots = ref<ImageSlot[]>([])

// ========== 分镜和大纲面板 ==========
const showStoryboardPanel = ref(false)
const showOutlinePanel = ref(false)
const storyboardPrompts = ref<Array<{ index: number; page_type: string; prompt: string }>>([])
const outlineData = ref<{ outline?: string; pages?: Array<{ index: number; page_type: string; content: string }> } | null>(null)

// ========== 讲解视频 ==========
const videoModel = ref('sora2')
const videoStyle = ref('ghibli_summer')
const videoDuration = ref('60')
const isGeneratingVideo = ref(false)
const showVideoProgress = ref(false)
const videoProgressPercent = ref(0)
const videoProgressText = ref('准备中...')
const explanationVideoUrl = ref('')

// ========== 发布弹窗 ==========
const showPublishModal = ref(false)
const cookieInput = ref('')

// ========== 工具函数 ==========
const getStageClass = (stageId: string) => {
  const status = stageStatuses[stageId]
  if (status === 'completed') return 'completed'
  if (status === 'active') return 'active'
  return 'waiting'
}

const getStageStatus = (stageId: string) => {
  const status = stageStatuses[stageId]
  if (status === 'completed') return '已完成'
  if (status === 'active') return '进行中'
  return '等待中'
}

const getPageTypeClass = (pageType: string) => {
  if (pageType === 'cover') return 'type-cover'
  if (pageType === 'summary') return 'type-summary'
  return 'type-content'
}

const initImagePlaceholders = (count: number) => {
  imageSlots.value = Array.from({ length: count }, (_, i) => ({
    loading: true,
    url: '',
    prompt: '',
    statusText: `第 ${i + 1} 页`,
    showTooltip: false
  }))
  showResult.value = true
}

const resetProgress = () => {
  progressPercent.value = 0
  currentStageText.value = '准备中...'
  timeEstimate.value = '预计剩余: --'
  progressTitle.value = '🚀 小红书内容生成中...'
  imageSubProgress.value = null
  
  stages.forEach(s => {
    stageStatuses[s.id] = 'waiting'
    stageDetails[s.id] = ''
  })
}

const updateTimeEstimate = (progress: number) => {
  if (!startTime || progress <= 0) return
  const elapsed = (Date.now() - startTime) / 1000
  const estimated = (elapsed / progress) * (100 - progress)
  
  if (estimated > 60) {
    timeEstimate.value = `预计剩余: ${Math.ceil(estimated / 60)} 分钟`
  } else {
    timeEstimate.value = `预计剩余: ${Math.ceil(estimated)} 秒`
  }
}

// ========== 生成小红书 ==========
const handleGenerate = async () => {
  if (!topic.value.trim() || isLoading.value) return
  
  errorMsg.value = ''
  isLoading.value = true
  showProgress.value = true
  showResult.value = false
  resetProgress()
  initImagePlaceholders(parseInt(pageCount.value))
  
  try {
    const response = await fetch('/api/xhs/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic.value,
        count: parseInt(pageCount.value),
        style: visualStyle.value,
        generate_video: generateVideo.value === 'true'
      })
    })
    
    const result = await response.json()
    
    if (!result.success) {
      throw new Error(result.error || '任务创建失败')
    }
    
    currentTaskId.value = result.task_id
    startTime = Date.now()
    connectSSE(result.task_id)
    
  } catch (error: any) {
    errorMsg.value = '❌ ' + error.message
    showProgress.value = false
    isLoading.value = false
  }
}

// ========== SSE 连接 ==========
const connectSSE = (taskId: string) => {
  if (eventSource) eventSource.close()
  
  eventSource = new EventSource(`/api/xhs/stream/${taskId}`)
  
  eventSource.addEventListener('progress', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    progressPercent.value = data.progress
    currentStageText.value = data.message
    updateStageIndicators(data.stage, data.sub_progress)
    updateTimeEstimate(data.progress)
  })
  
  eventSource.addEventListener('search', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    stageDetails['search'] = `${data.results_count} 条结果\n来源: ${data.sources?.join(', ') || '通用'}`
  })
  
  eventSource.addEventListener('outline', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    stageDetails['outline'] = `${data.summary || ''}\n点击查看完整大纲`
    outlineData.value = data
  })
  
  eventSource.addEventListener('content', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    stageDetails['content'] = `标题: ${data.titles?.[0] || ''}\n标签: ${data.tags?.slice(0, 3).join(', ') || ''}`
    renderContent(data)
  })
  
  eventSource.addEventListener('storyboard', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    stageDetails['storyboard'] = `共 ${data.total} 个分镜\n悬浮图片查看视觉指令`
    storyboardPrompts.value = data.prompts || []
    
    // 将 prompt 存入图片槽位
    if (data.prompts) {
      data.prompts.forEach((p: any) => {
        if (imageSlots.value[p.index]) {
          imageSlots.value[p.index].prompt = p.prompt || ''
        }
      })
    }
  })
  
  eventSource.addEventListener('image_progress', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    if (imageSlots.value[data.index]) {
      if (data.status === 'generating') {
        imageSlots.value[data.index].statusText = `第 ${data.index + 1} 页 生成中...`
      } else if (data.status === 'failed') {
        imageSlots.value[data.index].statusText = `第 ${data.index + 1} 页 失败`
      }
    }
  })
  
  eventSource.addEventListener('image', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    if (imageSlots.value[data.index]) {
      imageSlots.value[data.index].loading = false
      imageSlots.value[data.index].url = data.url
    }
  })
  
  eventSource.addEventListener('video', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    stageDetails['video'] = '动画封面已生成'
    if (currentResult.value) {
      currentResult.value.video_url = data.url
    }
  })
  
  eventSource.addEventListener('complete', (e: MessageEvent) => {
    const data = JSON.parse(e.data)
    eventSource?.close()
    eventSource = null
    onGenerationComplete(data)
  })
  
  eventSource.addEventListener('error', (e: MessageEvent) => {
    if (e.data) {
      const data = JSON.parse(e.data)
      eventSource?.close()
      eventSource = null
      onGenerationError(data.message)
    }
  })
  
  eventSource.addEventListener('cancelled', () => {
    eventSource?.close()
    eventSource = null
    onGenerationCancelled()
  })
  
  eventSource.onerror = () => {
    if (eventSource?.readyState === EventSource.CLOSED) {
      console.log('SSE 连接已关闭')
    }
  }
}

const updateStageIndicators = (currentStage: string, subProgress?: { current: number; total: number }) => {
  const stageIds = stages.map(s => s.id)
  let stageIndex = stageIds.indexOf(currentStage)
  const isComplete = currentStage === 'complete'
  if (isComplete) stageIndex = stageIds.length
  
  stageIds.forEach((id, index) => {
    if (index < stageIndex || isComplete) {
      stageStatuses[id] = 'completed'
    } else if (index === stageIndex) {
      stageStatuses[id] = 'active'
      if (id === 'images' && subProgress) {
        imageSubProgress.value = subProgress
      }
    } else {
      stageStatuses[id] = 'waiting'
    }
  })
}

const renderContent = (data: any) => {
  currentResult.value = {
    ...currentResult.value,
    titles: data.titles,
    copywriting: data.copywriting,
    tags: data.tags
  }
}

// ========== 完成/错误/取消处理 ==========
const onGenerationComplete = (data: any) => {
  currentResult.value = {
    ...currentResult.value,
    ...data,
    image_urls: data.image_urls
  }
  
  progressPercent.value = 100
  progressTitle.value = '🎉 生成完成！'
  currentStageText.value = '全部完成'
  
  const elapsed = Math.ceil((Date.now() - (startTime || Date.now())) / 1000)
  timeEstimate.value = `总耗时: ${elapsed} 秒`
  
  stages.forEach(s => stageStatuses[s.id] = 'completed')
  
  // 确保所有图片都渲染
  if (data.image_urls) {
    data.image_urls.forEach((url: string, index: number) => {
      if (imageSlots.value[index]?.loading) {
        imageSlots.value[index].loading = false
        imageSlots.value[index].url = url
      }
    })
  }
  
  isLoading.value = false
  
  setTimeout(() => {
    showProgress.value = false
  }, 3000)
}

const onGenerationError = (message: string) => {
  progressTitle.value = '❌ 生成失败'
  currentStageText.value = message
  errorMsg.value = '❌ ' + message
  isLoading.value = false
  
  setTimeout(() => {
    showProgress.value = false
  }, 5000)
}

const onGenerationCancelled = () => {
  progressTitle.value = '⚠️ 已取消生成'
  currentStageText.value = '任务已被用户取消'
  isLoading.value = false
  
  setTimeout(() => {
    showProgress.value = false
  }, 3000)
}

// ========== 取消生成 ==========
const cancelGeneration = async () => {
  if (!currentTaskId.value) return
  
  try {
    await fetch(`/api/xhs/tasks/${currentTaskId.value}/cancel`, { method: 'POST' })
  } catch (e) {
    console.error('取消请求失败:', e)
  }
  
  eventSource?.close()
  eventSource = null
  onGenerationCancelled()
}

// ========== 复制和下载 ==========
const copyToClipboard = () => {
  if (!currentResult.value) {
    alert('请先生成内容')
    return
  }
  
  const title = currentResult.value.titles?.[0] || ''
  const copy = currentResult.value.copywriting || ''
  const tags = (currentResult.value.tags || []).map(t => '#' + t).join(' ')
  const fullText = `${title}\n\n${copy}\n\n${tags}`
  
  navigator.clipboard.writeText(fullText).then(() => {
    alert('✅ 文案已复制到剪贴板')
  }).catch(() => {
    alert('复制失败，请手动复制')
  })
}

const downloadImages = async () => {
  const urls = currentResult.value?.image_urls
  if (!urls || urls.length === 0) {
    alert('没有可下载的图片')
    return
  }
  
  alert(`开始下载 ${urls.length} 张图片`)
  
  for (let i = 0; i < urls.length; i++) {
    try {
      const response = await fetch(urls[i])
      const blob = await response.blob()
      const blobUrl = URL.createObjectURL(blob)
      
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = `xhs_${i + 1}.jpg`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      
      await new Promise(r => setTimeout(r, 200))
      URL.revokeObjectURL(blobUrl)
      
      if (i < urls.length - 1) {
        await new Promise(r => setTimeout(r, 3000))
      }
    } catch (e) {
      console.error(`下载第 ${i + 1} 张图片失败:`, e)
      window.open(urls[i], '_blank')
    }
  }
  
  alert(`✓ 所有 ${urls.length} 张图片下载完成`)
}

const copyImagePrompt = (index: number) => {
  const prompt = imageSlots.value[index]?.prompt
  if (prompt) {
    navigator.clipboard.writeText(prompt).then(() => alert('已复制到剪贴板'))
  }
}

const copyPrompt = (index: number) => {
  const prompt = storyboardPrompts.value[index]?.prompt
  if (prompt) {
    navigator.clipboard.writeText(prompt).then(() => alert('已复制到剪贴板'))
  }
}

const copyOutline = () => {
  if (outlineData.value?.outline) {
    navigator.clipboard.writeText(outlineData.value.outline).then(() => alert('已复制到剪贴板'))
  }
}

// ========== 发布功能 ==========
const openPublishDialog = () => {
  if (!currentResult.value) {
    alert('请先生成内容')
    return
  }
  showPublishModal.value = true
}

const closePublishDialog = () => {
  showPublishModal.value = false
}

const publishToXHS = async () => {
  if (!cookieInput.value.trim()) {
    alert('请输入 Cookie')
    return
  }
  
  const cookies = parseCookies(cookieInput.value)
  if (!cookies || cookies.length === 0) {
    alert('Cookie 解析失败，请检查格式')
    return
  }
  
  if (!currentResult.value?.image_urls?.length) {
    alert('没有可发布的图片')
    return
  }
  
  closePublishDialog()
  showProgress.value = true
  progressTitle.value = '📤 正在发布到小红书...'
  currentStageText.value = '准备发布...'
  
  try {
    const response = await fetch('/api/xhs/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        cookies,
        title: currentResult.value.titles?.[0] || currentResult.value.topic || '',
        content: currentResult.value.copywriting || '',
        tags: currentResult.value.tags || [],
        images: currentResult.value.image_urls || []
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      alert('🎉 发布成功！' + (result.url ? '\n笔记链接: ' + result.url : ''))
    } else {
      alert('❌ 发布失败: ' + (result.message || result.error || '未知错误'))
    }
  } catch (error: any) {
    alert('❌ 发布失败: ' + error.message)
  } finally {
    showProgress.value = false
  }
}

// ========== 讲解视频生成 ==========
const generateExplanationVideo = async () => {
  const urls = currentResult.value?.image_urls
  if (!urls || urls.length === 0) {
    alert('请先生成小红书图片')
    return
  }
  
  // 获取每张图片对应的文案
  const scripts: string[] = []
  if (outlineData.value?.pages) {
    outlineData.value.pages.forEach(p => scripts.push(p.content || ''))
  } else if (currentResult.value?.pages) {
    currentResult.value.pages.forEach(p => scripts.push(p.content || ''))
  }
  while (scripts.length < urls.length) scripts.push('')
  
  isGeneratingVideo.value = true
  showVideoProgress.value = true
  videoProgressPercent.value = 0
  videoProgressText.value = '准备生成讲解视频...'
  explanationVideoUrl.value = ''
  
  // 模拟进度
  let progress = 0
  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 5
      videoProgressPercent.value = Math.min(progress, 90)
      
      if (progress < 20) videoProgressText.value = '创建时间线...'
      else if (progress < 40) videoProgressText.value = '生成动画指令...'
      else if (progress < 80) videoProgressText.value = `生成视频片段 (${Math.floor(progress / 20)}/${urls.length})...`
      else videoProgressText.value = '合成最终视频...'
    }
  }, 2000)
  
  try {
    const response = await fetch('/api/xhs/explanation-video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        images: urls,
        scripts,
        style: videoStyle.value,
        target_duration: parseInt(videoDuration.value),
        video_model: videoModel.value
      })
    })
    
    clearInterval(progressInterval)
    const result = await response.json()
    
    if (result.success && result.video_url) {
      explanationVideoUrl.value = result.video_url
      videoProgressPercent.value = 100
      videoProgressText.value = '✅ 视频生成完成！'
      
      setTimeout(() => {
        showVideoProgress.value = false
      }, 2000)
    } else {
      throw new Error(result.error || '视频生成失败')
    }
  } catch (error: any) {
    clearInterval(progressInterval)
    videoProgressPercent.value = 100
    videoProgressText.value = '❌ 生成失败: ' + error.message
    
    setTimeout(() => {
      showVideoProgress.value = false
    }, 5000)
  } finally {
    isGeneratingVideo.value = false
  }
}

const downloadExplanationVideo = () => {
  if (!explanationVideoUrl.value) {
    alert('没有可下载的视频')
    return
  }
  
  const a = document.createElement('a')
  a.href = explanationVideoUrl.value
  a.download = 'explanation_video.mp4'
  a.target = '_blank'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const copyVideoUrl = () => {
  if (!explanationVideoUrl.value) {
    alert('没有可复制的链接')
    return
  }
  
  navigator.clipboard.writeText(explanationVideoUrl.value).then(() => {
    alert('✅ 视频链接已复制到剪贴板')
  }).catch(() => {
    prompt('请手动复制视频链接:', explanationVideoUrl.value)
  })
}

// ========== 加载历史记录 ==========
const loadXhsHistory = async (historyId: string) => {
  try {
    const data = await api.getHistoryRecord(historyId)
    
    if (data.success && data.record) {
      const record = data.record as any
      topic.value = record.topic || ''
      
      let imageUrls: string[] = []
      try { imageUrls = JSON.parse(record.xhs_image_urls || '[]') } catch (e) {}
      
      let tags: string[] = []
      try { tags = JSON.parse(record.xhs_hashtags || '[]') } catch (e) {}
      
      currentResult.value = {
        id: record.id,
        topic: record.topic,
        image_urls: imageUrls,
        video_url: record.cover_video || '',
        titles: [record.topic],
        copywriting: record.xhs_copy_text || '',
        tags
      }
      
      // 显示结果
      imageSlots.value = imageUrls.map((url, i) => ({
        loading: false,
        url,
        prompt: '',
        statusText: `第 ${i + 1} 页`,
        showTooltip: false
      }))
      showResult.value = true
    }
  } catch (error) {
    console.error('加载小红书历史详情失败:', error)
    alert('加载历史记录失败')
  }
}

// ========== 初始化 ==========
onMounted(() => {
  const urlTopic = route.query.topic as string
  const sourceId = route.query.source_id as string
  const historyId = route.query.history_id as string
  
  if (urlTopic) topic.value = urlTopic
  if (sourceId) (window as any).xhsSourceId = sourceId
  if (historyId) loadXhsHistory(historyId)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* CSS 变量 */
.xhs-container {
  --code-bg: #ffffff;
  --code-surface: #f8fafc;
  --code-surface-hover: #f1f5f9;
  --code-border: #e2e8f0;
  --code-text: #1e293b;
  --code-text-secondary: #64748b;
  --code-text-muted: #94a3b8;
  --code-keyword: #8b5cf6;
  --code-string: #22c55e;
  --code-number: #f59e0b;
  --code-comment: #64748b;
  --code-function: #3b82f6;
  --code-variable: #ec4899;
  --code-operator: #6b7280;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
  --glass-bg: rgba(255, 255, 255, 0.85);
  --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
  font-family: 'JetBrains Mono', monospace;
  background: linear-gradient(135deg, var(--code-surface) 0%, #fdf4ff 50%, #fce7f3 100%);
  color: var(--code-text);
}

/* 深色模式 */
.xhs-container.dark-mode {
  --code-bg: #0f172a;
  --code-surface: #1e293b;
  --code-surface-hover: #334155;
  --code-border: #334155;
  --code-text: #f1f5f9;
  --code-text-secondary: #94a3b8;
  --code-text-muted: #64748b;
  --code-keyword: #a78bfa;
  --code-string: #4ade80;
  --code-number: #fbbf24;
  --code-function: #60a5fa;
  --code-variable: #f472b6;
  --glass-bg: rgba(15, 23, 42, 0.9);
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #4a1d6a 100%);
}

/* 终端导航栏 */
.terminal-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 28px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--code-border);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all var(--transition-normal);
}
.terminal-nav-left, .terminal-nav-right { display: flex; align-items: center; gap: 16px; }
.terminal-dots { display: flex; gap: 8px; }
.dot { 
  width: 12px; height: 12px; border-radius: 50%; 
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  cursor: pointer;
}
.dot:hover { transform: scale(1.2); }
.dot.red { background: linear-gradient(135deg, #ef4444, #dc2626); box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
.dot.yellow { background: linear-gradient(135deg, #eab308, #ca8a04); box-shadow: 0 0 8px rgba(234, 179, 8, 0.4); }
.dot.green { background: linear-gradient(135deg, #22c55e, #16a34a); box-shadow: 0 0 8px rgba(34, 197, 94, 0.4); }
.terminal-title { font-size: 13px; color: var(--code-text-secondary); letter-spacing: 0.3px; }
.nav-cmd { 
  font-size: 13px; color: var(--code-function); text-decoration: none; 
  padding: 8px 16px; background: var(--code-surface); border-radius: 8px;
  border: 1px solid transparent;
  transition: all var(--transition-fast);
}
.nav-cmd:hover { 
  background: var(--code-surface-hover); 
  border-color: var(--code-function);
  transform: translateY(-1px);
}
.theme-toggle { 
  background: var(--code-surface); border: 1px solid var(--code-border); 
  font-size: 16px; cursor: pointer; padding: 8px; border-radius: 8px;
  transition: all var(--transition-fast);
}
.theme-toggle:hover { 
  background: var(--code-surface-hover); 
  transform: rotate(15deg) scale(1.1);
}

/* 容器 */
.container { max-width: 900px; margin: 0 auto; padding: 24px; }

/* 页面标题 */
.page-title { margin-bottom: 32px; }
.page-title h1 { 
  font-size: 32px; font-weight: 700; 
  background: linear-gradient(135deg, var(--code-text) 0%, var(--code-variable) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}
.code-comment { color: var(--code-comment); font-style: italic; font-size: 14px; margin-top: 10px; opacity: 0.8; }

/* 主卡片 */
.main-card {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--code-border);
  border-radius: 20px;
  padding: 28px;
  box-shadow: var(--shadow-lg);
  transition: all var(--transition-normal);
}
.main-card:hover { box-shadow: var(--shadow-xl); }

/* 表单 */
.form-group { margin-bottom: 24px; }
.form-group label {
  display: block; margin-bottom: 10px;
  font-weight: 600; color: var(--code-text); font-size: 13px;
  display: flex; align-items: center; gap: 8px;
}
.text-input {
  width: 100%; padding: 16px;
  border: 1px solid var(--code-border);
  border-radius: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  resize: vertical;
  min-height: 100px;
  background: var(--code-surface);
  color: var(--code-text);
  transition: all var(--transition-fast);
}
.text-input:focus {
  outline: none;
  border-color: var(--code-keyword);
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.12);
  background: var(--code-bg);
}

/* 选项行 */
.options-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.option-group { flex: 1; min-width: 140px; }
.option-group label { display: block; margin-bottom: 8px; font-size: 12px; color: var(--code-text-secondary); font-weight: 500; }
.option-group select {
  width: 100%; padding: 12px 14px;
  border: 1px solid var(--code-border);
  border-radius: 10px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  background: var(--code-surface);
  color: var(--code-text);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.option-group select:hover { border-color: var(--code-keyword); }
.option-group select:focus { 
  outline: none; border-color: var(--code-keyword); 
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

/* 生成按钮 */
.generate-btn {
  width: 100%; padding: 16px;
  background: linear-gradient(135deg, var(--code-keyword), #7c3aed, var(--code-variable));
  background-size: 200% 200%;
  border: none; border-radius: 12px;
  color: white; font-family: 'JetBrains Mono', monospace;
  font-size: 14px; font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.35);
  position: relative;
  overflow: hidden;
}
.generate-btn::before {
  content: '';
  position: absolute;
  top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;
}
.generate-btn:hover:not(:disabled)::before { left: 100%; }
.generate-btn:hover:not(:disabled) { 
  transform: translateY(-2px); 
  box-shadow: 0 8px 25px rgba(139, 92, 246, 0.45);
  background-position: 100% 0;
}
.generate-btn:active { transform: translateY(0); }
.generate-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }

/* 错误消息 */
.error-msg {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 16px;
  font-size: 13px;
}

/* SSE 进度条 */
.progress-container {
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--code-border);
  border-radius: 16px;
  padding: 24px;
  margin-top: 24px;
  box-shadow: var(--shadow-md);
  animation: slideDown 0.3s ease;
}
@keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
.progress-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.progress-title { font-size: 14px; font-weight: 600; color: var(--code-text); }
.cancel-btn {
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  transition: all var(--transition-fast);
}
.cancel-btn:hover { 
  background: rgba(239, 68, 68, 0.2); 
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.main-progress { display: flex; align-items: center; gap: 14px; margin-bottom: 24px; }
.progress-bar {
  flex: 1; height: 10px;
  background: var(--code-border);
  border-radius: 5px;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--code-keyword), #7c3aed, var(--code-variable));
  background-size: 200% 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
  position: relative;
  animation: shimmer 2s infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
.progress-glow { display: none; }
.progress-percent {
  font-size: 14px; font-weight: 700; color: var(--code-keyword);
  min-width: 50px; text-align: right;
}

/* 阶段指示器 */
.stage-indicators {
  display: flex; justify-content: center; align-items: center;
  gap: 6px; margin-bottom: 16px; flex-wrap: wrap;
}
.stage-item {
  display: flex; flex-direction: column; align-items: center;
  padding: 12px 14px;
  background: var(--code-surface);
  border: 1px solid var(--code-border);
  border-radius: 10px;
  min-width: 65px;
  transition: all var(--transition-fast);
  position: relative;
  cursor: pointer;
}
.stage-item:hover { transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.stage-item.waiting { color: var(--code-text-muted); }
.stage-item.active {
  background: rgba(139, 92, 246, 0.12);
  border-color: var(--code-keyword);
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.2);
}
.stage-item.active .stage-icon { animation: pulse 1s ease infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
.stage-item.completed {
  background: rgba(34, 197, 94, 0.12);
  border-color: var(--code-string);
}
.stage-item.completed::after {
  content: '✓'; position: absolute; top: -8px; right: -8px;
  width: 18px; height: 18px;
  background: linear-gradient(135deg, var(--code-string), #16a34a); color: white; border-radius: 50%;
  font-size: 10px; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4);
}
.stage-icon { font-size: 18px; margin-bottom: 6px; }
.stage-name { font-size: 10px; font-weight: 600; color: var(--code-text); }
.stage-status { font-size: 9px; color: var(--code-text-muted); margin-top: 3px; }
.stage-item.active .stage-status { color: var(--code-keyword); font-weight: 500; }
.stage-item.completed .stage-status { color: var(--code-string); font-weight: 500; }
.stage-sub-progress { font-size: 9px; color: var(--code-keyword); font-weight: 700; margin-top: 3px; }
.stage-arrow { color: var(--code-text-muted); font-size: 12px; opacity: 0.5; }

/* 阶段详情悬浮 */
.stage-detail {
  position: absolute; bottom: 100%; left: 50%;
  transform: translateX(-50%);
  background: var(--code-text); color: var(--code-bg);
  padding: 8px 12px; border-radius: 6px;
  font-size: 11px; white-space: pre-line;
  min-width: 180px; max-width: 280px;
  z-index: 100; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  margin-bottom: 8px; line-height: 1.5;
}
.stage-detail::after {
  content: ''; position: absolute; top: 100%; left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent; border-top-color: #333;
}

.progress-info {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 12px; border-top: 1px solid var(--code-border);
}
.current-stage { font-size: 12px; color: var(--code-text-secondary); }
.time-estimate { font-size: 11px; color: var(--code-text-muted); }

/* 结果区域 */
.result-section {
  margin-top: 28px; padding-top: 28px;
  border-top: 2px solid var(--code-border);
  animation: fadeIn 0.4s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.result-title { 
  font-size: 18px; font-weight: 700; margin-bottom: 20px; 
  color: var(--code-text);
  display: flex; align-items: center; gap: 10px;
}
.result-title::before { content: '🎨'; }

/* 图片网格 */
.images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.image-card {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--code-border);
  background: var(--code-bg);
  position: relative;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}
.image-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--shadow-lg);
  border-color: var(--code-variable);
}
.image-card img {
  width: 100%;
  aspect-ratio: 3/4;
  object-fit: cover;
  transition: transform var(--transition-normal);
}
.image-card:hover img { transform: scale(1.05); }
.image-card .caption {
  padding: 10px;
  font-size: 11px;
  color: var(--code-text-secondary);
  text-align: center;
  background: linear-gradient(0deg, var(--code-surface) 0%, transparent 100%);
  position: absolute;
  bottom: 0; left: 0; right: 0;
}
.image-card.loading {
  background: var(--code-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 3/4;
}
.image-card.loading .placeholder { text-align: center; color: var(--code-text-muted); font-size: 12px; }
.mini-spinner {
  width: 24px; height: 24px;
  border: 2px solid var(--code-border);
  border-top-color: var(--code-keyword);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 图片提示浮窗 */
.prompt-tooltip {
  position: absolute; top: 0; left: 105%;
  width: 320px; max-height: 350px;
  background: var(--code-bg); border-radius: 8px;
  border: 1px solid var(--code-border);
  box-shadow: var(--shadow-lg);
  z-index: 100; overflow: hidden;
}
.tooltip-header {
  background: var(--code-surface);
  color: var(--code-text); padding: 10px 12px;
  font-weight: 500; font-size: 12px;
  display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid var(--code-border);
}
.tooltip-header button {
  background: var(--code-keyword);
  border: none; color: white;
  padding: 4px 8px; border-radius: 4px;
  cursor: pointer; font-size: 10px;
  font-family: 'JetBrains Mono', monospace;
}
.prompt-tooltip pre {
  padding: 12px; font-size: 11px; line-height: 1.5;
  white-space: pre-wrap; word-break: break-word;
  margin: 0; max-height: 280px; overflow-y: auto;
  background: var(--code-bg);
  color: var(--code-text-secondary);
}

/* 文案区域 */
.copy-section {
  background: var(--glass-bg);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid var(--code-border);
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  transition: all var(--transition-normal);
}
.copy-section:hover { box-shadow: var(--shadow-md); }
.copy-section h3 { font-size: 15px; margin-bottom: 14px; color: var(--code-text); font-weight: 600; }
.titles-list { margin-bottom: 14px; }
.title-item {
  padding: 10px 14px; background: var(--code-bg);
  border: 1px solid var(--code-border);
  border-radius: 8px; margin-bottom: 8px;
  font-size: 12px; color: var(--code-text-secondary);
  transition: all var(--transition-fast);
  cursor: pointer;
}
.title-item:hover { border-color: var(--code-keyword); background: rgba(139, 92, 246, 0.05); }
.title-item.primary {
  background: rgba(139, 92, 246, 0.12);
  border-color: var(--code-keyword);
  color: var(--code-keyword);
  font-weight: 500;
}
.copy-content {
  background: var(--code-bg);
  border: 1px solid var(--code-border);
  border-radius: 10px;
  padding: 14px;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  color: var(--code-text-secondary);
}
.tags-list { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.tag {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 11px;
  color: var(--code-keyword);
  transition: all var(--transition-fast);
  cursor: pointer;
}
.tag:hover { background: rgba(139, 92, 246, 0.2); transform: scale(1.05); }

/* 讲解视频区域 */
.explanation-video-section {
  margin-top: 20px; padding: 16px;
  background: var(--code-surface);
  border: 1px solid var(--code-border);
  border-radius: 8px;
}
.video-options { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.video-options select {
  padding: 8px 12px;
  border: 1px solid var(--code-border);
  border-radius: 6px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  background: var(--code-bg);
  color: var(--code-text);
}
.explanation-video-btn {
  padding: 10px 20px;
  background: var(--code-string);
  border: none; border-radius: 6px;
  color: white; font-size: 12px; font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
  transition: all 0.2s;
}
.explanation-video-btn:hover:not(:disabled) { opacity: 0.9; }
.explanation-video-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.video-progress-container {
  margin-top: 12px; padding: 12px;
  background: var(--code-bg); border-radius: 6px;
  border: 1px solid var(--code-border);
}
.video-progress-bar {
  height: 6px; background: var(--code-border);
  border-radius: 3px; overflow: hidden; margin-bottom: 8px;
}
.video-progress-fill {
  height: 100%;
  background: var(--code-string);
  border-radius: 3px;
  transition: width 0.5s ease;
}
.video-progress-text { font-size: 11px; color: var(--code-text-muted); text-align: center; }

.video-result-container { margin-top: 12px; }
.video-result-container video {
  width: 100%; max-width: 350px;
  border-radius: 8px;
  border: 1px solid var(--code-border);
}
.video-actions { margin-top: 10px; display: flex; gap: 10px; }
.video-actions button {
  padding: 8px 16px;
  background: var(--code-bg);
  border: 1px solid var(--code-string);
  border-radius: 6px;
  color: var(--code-string);
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
}

/* 发布区域 */
.publish-section {
  margin-top: 20px; padding-top: 16px;
  border-top: 1px solid var(--code-border);
}
.publish-section h3 { margin-bottom: 10px; font-size: 14px; color: var(--code-text); }
.publish-buttons { display: flex; gap: 10px; flex-wrap: wrap; }
.publish-btn {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
}
.publish-btn.outline {
  background: var(--code-bg);
  border: 1px solid var(--code-keyword);
  color: var(--code-keyword);
}
.publish-btn.primary {
  background: var(--code-keyword);
  border: none;
  color: white;
  font-weight: 600;
}

/* 发布弹窗 */
.publish-modal {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 1000;
  display: flex; align-items: center; justify-content: center;
}
.publish-modal-content {
  background: var(--code-bg); border-radius: 12px; padding: 20px;
  max-width: 480px; width: 90%; max-height: 80vh; overflow-y: auto;
  border: 1px solid var(--code-border);
}
.publish-modal-content h3 { margin-bottom: 12px; font-size: 14px; color: var(--code-text); }
.publish-modal-content p { color: var(--code-text-secondary); font-size: 12px; margin-bottom: 10px; }
.publish-modal-content textarea {
  width: 100%; height: 120px; padding: 10px;
  border: 1px solid var(--code-border); border-radius: 6px;
  font-family: 'JetBrains Mono', monospace; font-size: 11px; resize: vertical;
  background: var(--code-surface); color: var(--code-text);
}
.modal-actions { display: flex; gap: 10px; margin-top: 14px; justify-content: flex-end; }
.modal-actions button {
  padding: 8px 16px; border-radius: 6px; cursor: pointer;
  font-family: 'JetBrains Mono', monospace; font-size: 12px;
}
.modal-actions .cancel { background: var(--code-surface); border: 1px solid var(--code-border); color: var(--code-text-secondary); }
.modal-actions .confirm {
  background: var(--code-keyword);
  border: none; color: white; font-weight: 600;
}

/* 侧边面板 */
.side-panel {
  position: fixed; top: 0; right: 0;
  width: 400px; height: 100vh;
  background: var(--code-bg);
  border-left: 1px solid var(--code-border);
  z-index: 1000; overflow-y: auto;
}
.panel-header {
  position: sticky; top: 0;
  padding: 14px 16px;
  display: flex; justify-content: space-between; align-items: center;
  background: var(--code-surface);
  border-bottom: 1px solid var(--code-border);
}
.panel-header.storyboard { border-left: 4px solid var(--code-variable); }
.panel-header.outline { border-left: 4px solid var(--code-string); }
.panel-header h3 { margin: 0; font-size: 13px; color: var(--code-text); }
.panel-header button {
  background: var(--code-surface-hover);
  border: 1px solid var(--code-border);
  width: 28px; height: 28px; border-radius: 6px;
  cursor: pointer; font-size: 14px; color: var(--code-text-secondary);
}
.panel-content { padding: 14px; }

.prompt-card, .page-card {
  background: var(--code-surface); border-radius: 8px;
  padding: 12px; margin-bottom: 12px;
  border: 1px solid var(--code-border);
}
.prompt-card.type-cover, .page-card.type-cover { border-left: 3px solid var(--code-variable); }
.prompt-card.type-summary, .page-card.type-summary { border-left: 3px solid var(--code-string); }
.prompt-card.type-content, .page-card.type-content { border-left: 3px solid var(--code-number); }

.prompt-header, .page-header, .section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px;
}
.prompt-header span, .page-header span, .section-header span { font-weight: 500; color: var(--code-text); font-size: 12px; }
.prompt-header button, .section-header button {
  background: var(--code-bg); border: 1px solid var(--code-border);
  padding: 4px 10px; border-radius: 4px;
  cursor: pointer; font-size: 10px; color: var(--code-text-secondary);
  font-family: 'JetBrains Mono', monospace;
}
.prompt-card pre, .outline-section pre {
  background: var(--code-bg); padding: 10px; border-radius: 6px;
  font-size: 11px; line-height: 1.5;
  white-space: pre-wrap; word-break: break-word;
  margin: 0; max-height: 250px; overflow-y: auto;
  border: 1px solid var(--code-border);
  color: var(--code-text-secondary);
}
.page-type-badge {
  background: var(--code-keyword); color: white;
  padding: 2px 6px; border-radius: 3px;
  font-size: 10px; margin-left: 6px;
}
.page-content {
  background: var(--code-bg); padding: 10px; border-radius: 6px;
  font-size: 12px; line-height: 1.5;
  border: 1px solid var(--code-border);
  color: var(--code-text-secondary);
}
.pages-section h4 { margin: 14px 0 10px; color: var(--code-text); font-size: 12px; }

/* 响应式 */
@media (max-width: 768px) {
  .terminal-nav { padding: 12px 16px; }
  .terminal-title { display: none; }
  .container { padding: 16px; }
  .options-row { flex-direction: column; }
  .side-panel { width: 100%; }
  .prompt-tooltip { left: 0; width: 100%; }
}
</style>
