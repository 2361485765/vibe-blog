<template>
  <div class="home-container" :class="{ 'dark-mode': isDarkMode }">
    <div class="bg-animation"></div>

    <!-- 导航栏 -->
    <AppNavbar :app-config="appConfig" />

    <!-- Hero 区域 -->
    <HeroSection />

    <!-- 博客卡片容器 -->
    <div class="code-cards-container">
      <!-- 主输入框 - 终端风格搜索栏 -->
      <BlogInputCard
        v-model:topic="topic"
        v-model:show-advanced-options="showAdvancedOptions"
        :uploaded-documents="uploadedDocuments"
        :is-loading="isLoading"
        @generate="handleGenerate"
        @file-upload="handleFileUpload"
        @remove-document="removeDocument"
      />

      <!-- 高级选项面板 -->
      <AdvancedOptionsPanel
        v-if="showAdvancedOptions"
        v-model:article-type="articleType"
        v-model:target-length="targetLength"
        v-model:audience-adaptation="audienceAdaptation"
        v-model:image-style="imageStyle"
        v-model:generate-cover-video="generateCoverVideo"
        v-model:video-aspect-ratio="videoAspectRatio"
        v-model:custom-config="customConfig"
        :image-styles="imageStyles"
        :app-config="appConfig"
      />

      <!-- 进度面板 -->
      <ProgressDrawer
        :visible="showProgress"
        :expanded="terminalExpanded"
        :is-loading="isLoading"
        :status-badge="statusBadge"
        :progress-text="progressText"
        :progress-items="progressItems"
        :article-type="articleType"
        :target-length="targetLength"
        :task-id="currentTaskId"
        @toggle="toggleTerminal"
        @close="closeProgress"
        @stop="stopGeneration"
      />

      <!-- 博客列表 -->
      <BlogHistoryList
        :show-list="showBlogList"
        :current-tab="currentHistoryTab"
        :content-type="historyContentType"
        v-model:show-cover-preview="showCoverPreview"
        :records="historyRecords"
        :total="historyTotal"
        :current-page="historyCurrentPage"
        :total-pages="historyTotalPages"
        :content-type-filters="contentTypeFilters"
        @toggle-list="showBlogList = !showBlogList"
        @switch-tab="switchHistoryTab"
        @filter-content-type="filterByContentType"
        @load-detail="loadHistoryDetail"
        @load-page="loadHistory"
      />
    </div>

    <!-- 发布弹窗 -->
    <PublishModal
      :visible="showPublishModal"
      v-model:platform="publishPlatform"
      v-model:cookie="publishCookie"
      :is-publishing="isPublishing"
      :status="publishStatus"
      :status-type="publishStatusType"
      @close="showPublishModal = false"
      @publish="doPublish"
    />

    <!-- 底部备案信息 -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '../stores/theme'
import * as api from '../services/api'
import { isSpinningStatus } from '../utils/helpers'

// Components
import AppNavbar from '../components/home/AppNavbar.vue'
import HeroSection from '../components/home/HeroSection.vue'
import BlogInputCard from '../components/home/BlogInputCard.vue'
import AdvancedOptionsPanel from '../components/home/AdvancedOptionsPanel.vue'
import ProgressDrawer from '../components/home/ProgressDrawer.vue'
import BlogHistoryList from '../components/home/BlogHistoryList.vue'
import PublishModal from '../components/home/PublishModal.vue'
import Footer from '../components/Footer.vue'

const router = useRouter()
const themeStore = useThemeStore()

// ========== 应用配置 ==========
const appConfig = reactive<{ features: Record<string, boolean> }>({ features: {} })
const isDarkMode = computed(() => themeStore.isDark)

// ========== 输入状态 ==========
const topic = ref('')
const showAdvancedOptions = ref(false)

// ========== 高级选项 ==========
const articleType = ref('tutorial')
const targetLength = ref('mini')
const audienceAdaptation = ref('default')
const imageStyle = ref('cartoon')
const generateCoverVideo = ref(false)
const videoAspectRatio = ref('16:9')
const imageStyles = ref<Array<{ id: string; name: string; icon: string }>>([
  { id: 'cartoon', name: '默认风格', icon: '🎨' }
])
const customConfig = reactive({
  sectionsCount: 4,
  imagesCount: 4,
  codeBlocksCount: 2,
  targetWordCount: 3500
})

// ========== 文档上传 ==========
interface UploadedDocument {
  id: string
  filename: string
  status: string
  fileSize?: number
  wordCount?: number
  errorMessage?: string
}
const uploadedDocuments = ref<UploadedDocument[]>([])

// ========== 生成状态 ==========
const isLoading = ref(false)
const showProgress = ref(false)
const terminalExpanded = ref(true)
const currentTaskId = ref<string | null>(null)
let eventSource: EventSource | null = null

// ========== 进度面板 ==========
interface ProgressItem {
  time: string
  message: string
  type: string
  detail?: string
}
const progressItems = ref<ProgressItem[]>([])
const statusBadge = ref('准备中')
const progressText = ref('等待开始')

// ========== 历史记录 ==========
const showBlogList = ref(true)
const currentHistoryTab = ref('blogs')
const historyContentType = ref('all')
const showCoverPreview = ref(false)
const historyRecords = ref<api.HistoryRecord[]>([])
const historyTotal = ref(0)
const historyCurrentPage = ref(1)
const historyTotalPages = ref(1)
const contentTypeFilters = ref([
  { label: '全部', value: 'all' },
  { label: '博客', value: 'blog' },
  { label: '小红书', value: 'xhs' }
])

// ========== 发布 ==========
const showPublishModal = ref(false)
const publishPlatform = ref('csdn')
const publishCookie = ref('')
const isPublishing = ref(false)
const publishStatus = ref('')
const publishStatusType = ref('')

// ========== 文件上传 ==========
const handleFileUpload = async (files: FileList) => {
  for (const file of Array.from(files)) {
    await uploadDocument(file)
  }
}

const uploadDocument = async (file: File) => {
  const tempId = 'temp_' + Date.now()
  uploadedDocuments.value.push({
    id: tempId,
    filename: file.name,
    status: 'uploading',
    fileSize: file.size
  })

  try {
    const data = await api.uploadDocument(file)
    uploadedDocuments.value = uploadedDocuments.value.filter(d => d.id !== tempId)

    if (data.success && data.document_id) {
      uploadedDocuments.value.push({
        id: data.document_id,
        filename: data.filename || file.name,
        status: data.status || 'pending',
        fileSize: file.size
      })
      pollDocumentStatus(data.document_id)
    } else {
      alert('上传失败: ' + (data.error || '未知错误'))
    }
  } catch (error: any) {
    uploadedDocuments.value = uploadedDocuments.value.filter(d => d.id !== tempId)
    alert('上传失败: ' + error.message)
  }
}

const pollDocumentStatus = async (docId: string) => {
  let attempts = 0
  const maxAttempts = 60

  const poll = async () => {
    if (attempts >= maxAttempts) {
      updateDocStatus(docId, 'timeout')
      return
    }

    try {
      const data = await api.getDocumentStatus(docId)
      if (data.success) {
        updateDocStatus(docId, data.status || 'pending', data.markdown_length, data.error_message)
        if (data.status === 'ready' || data.status === 'error') return
      }
    } catch (error) {
      console.error('Poll document status error:', error)
    }

    attempts++
    setTimeout(poll, 2000)
  }

  poll()
}

const updateDocStatus = (docId: string, status: string, wordCount?: number, errorMessage?: string) => {
  const doc = uploadedDocuments.value.find(d => d.id === docId)
  if (doc) {
    doc.status = status
    if (wordCount) doc.wordCount = wordCount
    if (errorMessage) doc.errorMessage = errorMessage
  }
}

const removeDocument = (docId: string) => {
  uploadedDocuments.value = uploadedDocuments.value.filter(d => d.id !== docId)
}

const getReadyDocumentIds = () => {
  return uploadedDocuments.value.filter(d => d.status === 'ready').map(d => d.id)
}

// ========== 生成博客 ==========
const handleGenerate = async () => {
  if (!topic.value.trim() || isLoading.value) return

  isLoading.value = true
  showProgress.value = true
  progressItems.value = []
  statusBadge.value = '准备中'

  const isStorybook = articleType.value === 'storybook'
  const isMini = targetLength.value === 'mini'
  const taskName = isStorybook ? '科普绘本' : (isMini ? 'Mini 博客' : '博客')
  progressText.value = `正在创建${taskName}生成任务...`

  try {
    let data: { success: boolean; task_id?: string; error?: string }

    if (isStorybook) {
      data = await api.createStorybookTask({
        content: topic.value,
        page_count: targetLength.value === 'short' ? 5 : (targetLength.value === 'medium' ? 8 : 12),
        target_audience: '技术小白',
        style: '可爱卡通风',
        generate_images: true
      })
    } else if (isMini) {
      data = await api.createMiniBlogTask({
        topic: topic.value,
        article_type: articleType.value,
        audience_adaptation: audienceAdaptation.value,
        image_style: imageStyle.value,
        document_ids: getReadyDocumentIds()
      })
    } else {
      const params: api.BlogGenerateParams = {
        topic: topic.value,
        article_type: articleType.value,
        target_length: targetLength.value,
        audience_adaptation: audienceAdaptation.value,
        document_ids: getReadyDocumentIds(),
        image_style: imageStyle.value,
        generate_cover_video: generateCoverVideo.value,
        video_aspect_ratio: videoAspectRatio.value
      }

      if (targetLength.value === 'custom') {
        params.custom_config = {
          sections_count: customConfig.sectionsCount,
          images_count: customConfig.imagesCount,
          code_blocks_count: customConfig.codeBlocksCount,
          target_word_count: customConfig.targetWordCount
        }
      }

      data = await api.createBlogTask(params)
    }

    if (data.success && data.task_id) {
      currentTaskId.value = data.task_id
      addProgressItem(`✓ 任务创建成功 (ID: ${data.task_id})`, 'success')
      connectSSE(data.task_id)
    } else {
      addProgressItem(`✗ 任务创建失败: ${data.error || '未知错误'}`, 'error')
      statusBadge.value = '错误'
      isLoading.value = false
    }
  } catch (error: any) {
    addProgressItem(`✗ 请求失败: ${error.message}`, 'error')
    statusBadge.value = '错误'
    isLoading.value = false
  }
}

const connectSSE = (taskId: string) => {
  const url = `/api/blog/stream/${taskId}`
  eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      handleSSEMessage(data)
    } catch (error) {
      console.error('Parse SSE message error:', error)
    }
  }

  eventSource.onerror = () => {
    eventSource?.close()
    if (isLoading.value) {
      addProgressItem('✗ 连接中断', 'error')
      statusBadge.value = '错误'
      isLoading.value = false
    }
  }
}

const handleSSEMessage = (data: any) => {
  if (data.type === 'progress') {
    addProgressItem(data.message, 'info')
    progressText.value = data.message
    statusBadge.value = '运行中'
  } else if (data.type === 'complete') {
    addProgressItem('✓ 生成完成', 'success')
    statusBadge.value = '已完成'
    progressText.value = '生成完成'
    isLoading.value = false
    eventSource?.close()
    loadHistory(1)
  } else if (data.type === 'error') {
    addProgressItem(`✗ ${data.message}`, 'error')
    statusBadge.value = '错误'
    isLoading.value = false
    eventSource?.close()
  }
}

const addProgressItem = (message: string, type: string) => {
  progressItems.value.push({
    time: new Date().toLocaleTimeString(),
    message,
    type
  })
}

const toggleTerminal = () => {
  terminalExpanded.value = !terminalExpanded.value
}

const closeProgress = () => {
  showProgress.value = false
  eventSource?.close()
  eventSource = null
}

const stopGeneration = async () => {
  if (currentTaskId.value) {
    try {
      const data = await api.cancelTask(currentTaskId.value)
      if (data.success) {
        addProgressItem('⏹️ 任务已取消', 'error')
      } else {
        addProgressItem(`⚠️ 取消失败: ${data.error}`, 'error')
      }
    } catch (e: any) {
      addProgressItem('⚠️ 取消请求失败', 'error')
    }
  }

  eventSource?.close()
  eventSource = null
  statusBadge.value = '已停止'
  isLoading.value = false
}

// ========== 历史记录 ==========
const loadHistory = async (page: number = 1) => {
  try {
    const data = await api.getHistory({
      page,
      page_size: 12,
      content_type: historyContentType.value === 'all' ? undefined : historyContentType.value
    })

    if (data.success) {
      historyRecords.value = data.records
      historyTotal.value = data.total
      historyCurrentPage.value = data.page
      historyTotalPages.value = data.total_pages
    }
  } catch (error) {
    console.error('Load history error:', error)
  }
}

const switchHistoryTab = (tab: string) => {
  currentHistoryTab.value = tab
  if (tab === 'blogs') {
    loadHistory(1)
  }
}

const filterByContentType = (type: string) => {
  historyContentType.value = type
  loadHistory(1)
}

const loadHistoryDetail = async (historyId: string) => {
  try {
    const data = await api.getHistoryRecord(historyId)
    if (data.success && data.record) {
      const record = data.record

      if (record.content_type === 'xhs') {
        router.push(`/xhs?history_id=${historyId}`)
        return
      }

      router.push(`/blog/${historyId}`)
    }
  } catch (error) {
    console.error('Load history detail error:', error)
  }
}

// ========== 发布 ==========
const doPublish = async () => {
  if (!publishCookie.value.trim() || isPublishing.value) return

  isPublishing.value = true
  publishStatus.value = '发布中...'
  publishStatusType.value = 'info'

  try {
    // Implement publish logic here
    await new Promise(resolve => setTimeout(resolve, 2000))
    publishStatus.value = '发布成功！'
    publishStatusType.value = 'success'
  } catch (error: any) {
    publishStatus.value = `发布失败: ${error.message}`
    publishStatusType.value = 'error'
  } finally {
    isPublishing.value = false
  }
}

// ========== 初始化 ==========
onMounted(async () => {
  // Load app config
  try {
    const data = await api.getAppConfig()
    if (data.success) {
      appConfig.features = data.features || {}
    }
  } catch (error) {
    console.error('Load app config error:', error)
  }

  // Load image styles
  try {
    const data = await api.getImageStyles()
    if (data.success && data.styles) {
      imageStyles.value = data.styles
    }
  } catch (error) {
    console.error('Load image styles error:', error)
  }

  // Load history
  loadHistory(1)
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: var(--color-bg-base);
  position: relative;
  padding-top: 60px;
  transition: var(--transition-colors);
}

/* Background Animation */
.bg-animation {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-animation::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
  background: radial-gradient(circle, var(--color-primary-light) 1px, transparent 1px);
  background-size: 50px 50px;
  animation: bg-scroll 60s linear infinite;
}

@keyframes bg-scroll {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(50px, 50px);
  }
}

.code-cards-container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-xl) var(--space-lg);
}

/* Dark Mode */
.dark-mode {
  background: var(--color-bg-base);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .home-container {
    padding-top: 56px;
  }

  .code-cards-container {
    padding: var(--space-lg) var(--space-md);
  }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  .code-cards-container {
    padding: var(--space-xl) var(--space-lg);
  }
}

/* Large Desktop */
@media (min-width: 1440px) {
  .code-cards-container {
    max-width: 1400px;
  }
}

/* Reduce motion */
@media (prefers-reduced-motion: reduce) {
  .bg-animation::before {
    animation: none;
  }
}
</style>
