<template>
  <div class="blog-detail-container" :class="{ 'dark-mode': isDark }">
    <!-- 终端风格导航栏 -->
    <nav class="terminal-nav">
      <div class="terminal-nav-left">
        <div class="terminal-dots">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
        <span class="terminal-title">$ cat ~/blog/{{ blog?.category || 'posts' }}/</span>
      </div>
      <div class="terminal-nav-right">
        <router-link to="/blog" class="nav-cmd">cd ~/blog-list</router-link>
        <router-link to="/" class="nav-cmd">cd ~/home</router-link>
        <button class="theme-toggle" @click="themeStore.toggleTheme()" title="切换主题">
          <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 2v2"></path>
            <path d="M12 20v2"></path>
            <path d="m4.93 4.93 1.41 1.41"></path>
            <path d="m17.66 17.66 1.41 1.41"></path>
            <path d="M2 12h2"></path>
            <path d="M20 12h2"></path>
            <path d="m6.34 17.66-1.41 1.41"></path>
            <path d="m19.07 4.93-1.41 1.41"></path>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>
          </svg>
        </button>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：博客内容 -->
      <div class="content-area">
        <!-- 面包屑导航 -->
        <div class="breadcrumb-bar">
          <div class="breadcrumb-inner">
            <span class="prompt">$</span>
            <span class="muted">pwd:</span>
            <nav class="breadcrumb">
              <router-link to="/" class="crumb-link">~</router-link>
              <span class="separator">/</span>
              <router-link to="/blog" class="crumb-link">blog</router-link>
              <span class="separator">/</span>
              <span class="crumb-current">{{ blog?.title || 'loading...' }}</span>
            </nav>
          </div>
        </div>

        <!-- 标题区 -->
        <div class="title-section">
          <h1 class="blog-title">
            <span class="title-highlight">{{ blog?.title }}</span>
          </h1>
          <p class="blog-description">
            <span class="comment-prefix">// </span>{{ blog?.description }}
          </p>
        </div>

        <!-- Git 统计信息 -->
        <section class="stats-section">
          <div class="stats-header">
            <div class="terminal-dots-sm">
              <span class="dot red"></span>
              <span class="dot yellow"></span>
              <span class="dot green"></span>
            </div>
            <span class="stats-title">$ git log --oneline --stat</span>
          </div>
          <div class="stats-content">
            <div class="stat-item">
              <svg class="stat-icon star" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path>
              </svg>
              <span class="stat-label">stars:</span>
              <span class="stat-value">{{ blog?.stars || 0 }}</span>
            </div>
            <div class="stat-item">
              <svg class="stat-icon fork" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="18" r="3"></circle>
                <circle cx="6" cy="6" r="3"></circle>
                <circle cx="18" cy="6" r="3"></circle>
                <path d="M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9"></path>
                <path d="M12 12v3"></path>
              </svg>
              <span class="stat-label">forks:</span>
              <span class="stat-value">{{ blog?.forks || 0 }}</span>
            </div>
            <div class="stat-item">
              <svg class="stat-icon calendar" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 2v4"></path>
                <path d="M16 2v4"></path>
                <rect width="18" height="18" x="3" y="4" rx="2"></rect>
                <path d="M3 10h18"></path>
              </svg>
              <span class="stat-label">updated:</span>
              <span class="stat-value">{{ formatDate(blog?.updatedAt) }}</span>
            </div>
          </div>
        </section>

        <!-- 博客内容区 -->
        <div class="content-card">
          <div class="content-card-header">
            <div class="header-left">
              <div class="terminal-dots-sm">
                <span class="dot red"></span>
                <span class="dot yellow"></span>
                <span class="dot green"></span>
              </div>
              <span class="file-name">README.md</span>
            </div>
            <span class="readonly-badge">readonly</span>
          </div>
          <div class="content-card-body">
            <!-- 加载状态 -->
            <div v-if="isLoading" class="loading-state">
              <div class="code-line"><span class="prompt">$</span> loading content...</div>
              <div class="spinner"></div>
            </div>
            <!-- 博客内容 -->
            <div v-else class="blog-content prose" v-html="renderedContent"></div>
          </div>
        </div>
      </div>

      <!-- 右侧：侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-sticky">
          <!-- 作者信息 -->
          <div class="sidebar-card">
            <div class="sidebar-card-header">
              <span class="card-title">package.json</span>
              <div class="header-actions">
                <button class="action-btn" title="分享">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="18" cy="5" r="3"></circle>
                    <circle cx="6" cy="12" r="3"></circle>
                    <circle cx="18" cy="19" r="3"></circle>
                    <line x1="8.59" x2="15.42" y1="13.51" y2="17.49"></line>
                    <line x1="15.41" x2="8.59" y1="6.51" y2="10.49"></line>
                  </svg>
                </button>
                <button class="action-btn favorite" :class="{ active: isFavorite }" @click="toggleFavorite" title="收藏">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path>
                  </svg>
                </button>
              </div>
            </div>
            <div class="sidebar-card-body">
              <div class="author-info">
                <img :src="blog?.authorAvatar || 'https://avatars.githubusercontent.com/u/1?v=4'" :alt="blog?.author" class="author-avatar">
                <div class="author-details">
                  <div class="json-line">
                    <span class="json-key">"author"</span>: <span class="json-value">"{{ blog?.author || 'anonymous' }}"</span>
                  </div>
                  <div class="json-line">
                    <span class="json-key">"category"</span>: <span class="json-value">"{{ blog?.category || 'general' }}"</span>
                  </div>
                </div>
              </div>
              <a :href="blog?.sourceUrl || '#'" target="_blank" class="source-link">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
                  <path d="M9 18c-4.51 2-5-2-7-2"></path>
                </svg>
                <span class="prompt">$</span> gh browse
              </a>
            </div>
          </div>

          <!-- 标签 -->
          <div class="sidebar-card">
            <div class="sidebar-card-header">
              <span class="card-title">$ tags --list</span>
            </div>
            <div class="sidebar-card-body">
              <div class="tags-list">
                <span v-for="tag in blog?.tags" :key="tag" class="tag-item">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- 博客属性 - 代码风格标签 -->
          <div class="sidebar-card stats-card">
            <div class="sidebar-card-header">
              <span class="card-title">$ stat --format blog.md</span>
            </div>
            <div class="sidebar-card-body">
              <div class="stat-tags-row">
                <span class="stat-tag type">
                  <span class="stat-tag-key">type</span>
                  <span class="stat-tag-value">{{ blog?.articleType || '短文' }}</span>
                </span>
                <span class="stat-tag sections">
                  <span class="stat-tag-key">sections</span>
                  <span class="stat-tag-value">{{ blog?.sectionsCount || 0 }}</span>
                </span>
                <span class="stat-tag images">
                  <span class="stat-tag-key">images</span>
                  <span class="stat-tag-value">{{ blog?.imagesCount || 0 }}</span>
                </span>
                <span class="stat-tag code">
                  <span class="stat-tag-key">code</span>
                  <span class="stat-tag-value">{{ blog?.codeBlocksCount || 0 }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- 下载与发布 -->
          <div class="sidebar-card download-card">
            <div class="sidebar-card-header">
              <span class="card-title">$ download --local</span>
              <a href="#" class="man-link" title="帮助">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                  <path d="M12 17h.01"></path>
                </svg>
                man
              </a>
            </div>
            <div class="sidebar-card-body">
              <button class="download-btn primary" :disabled="isDownloading" @click="downloadMarkdown">
                <svg v-if="!isDownloading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" x2="12" y1="15" y2="3"></line>
                </svg>
                <span v-if="isDownloading" class="download-spinner"></span>
                {{ isDownloading ? '下载中...' : 'wget blog.zip' }}
              </button>
              <button class="download-btn secondary" @click="openPublishModal">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                  <polyline points="16 6 12 2 8 6"></polyline>
                  <line x1="12" x2="12" y1="2" y2="15"></line>
                </svg>
                发布到 CSDN
              </button>
              <div class="download-hint">
                <span class="hint-tag">[HINT]</span> 下载完整的博客 ZIP 包（含 Markdown 和图片），或一键发布到 CSDN 平台
              </div>
            </div>
          </div>

          <!-- 封面视频预览 -->
          <div v-if="blog?.coverVideo" class="sidebar-card video-card">
            <div class="sidebar-card-header">
              <span class="card-title">$ ffplay cover.mp4</span>
              <span class="video-badge">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                VIDEO
              </span>
            </div>
            <div class="sidebar-card-body video-body">
              <div class="video-container">
                <video 
                  :src="blog.coverVideo" 
                  controls 
                  loop 
                  muted 
                  autoplay
                  playsinline
                  class="cover-video"
                >
                  您的浏览器不支持视频播放
                </video>
              </div>
              <div class="video-actions">
                <a :href="blog.coverVideo" download class="video-download-btn">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" x2="12" y1="15" y2="3"></line>
                  </svg>
                  下载视频
                </a>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Toast 通知 -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      <svg v-if="toast.type === 'success'" class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <polyline points="20 6 9 17 4 12"></polyline>
      </svg>
      <svg v-else-if="toast.type === 'error'" class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <line x1="18" x2="6" y1="6" y2="18"></line>
        <line x1="6" x2="18" y1="6" y2="18"></line>
      </svg>
      <svg v-else class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 16v-4"></path>
        <path d="M12 8h.01"></path>
      </svg>
      {{ toast.message }}
    </div>

    <!-- 发布弹窗 -->
    <div v-if="showPublishModal" class="publish-modal-overlay" @click.self="closePublishModal">
      <div class="publish-modal">
        <div class="publish-modal-header">
          <h3>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" style="display: inline; vertical-align: middle; margin-right: 8px;">
              <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
              <polyline points="16 6 12 2 8 6"></polyline>
              <line x1="12" x2="12" y1="2" y2="15"></line>
            </svg>
            发布到平台
          </h3>
          <button class="modal-close-btn" @click="closePublishModal">×</button>
        </div>
        
        <div class="publish-modal-body">
          <div class="form-group">
            <label>选择平台</label>
            <select v-model="publishPlatform" class="form-select">
              <option value="csdn">CSDN</option>
              <option value="zhihu">知乎</option>
              <option value="juejin">掘金</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>
              Cookie
              <a href="javascript:void(0)" class="help-link" @click="showCookieHelp = !showCookieHelp">如何获取？</a>
            </label>
            <textarea 
              v-model="publishCookie" 
              class="form-textarea"
              placeholder="直接粘贴浏览器复制的 Cookie，如：name=value; name2=value2; ..."
            ></textarea>
            <div class="cookie-warning">
              ⚠️ <strong>安全提示：</strong>服务端不会存储您的 Cookie，仅用于本次发布。
            </div>
          </div>
          
          <div v-if="showCookieHelp" class="cookie-help">
            <strong>获取 Cookie 步骤：</strong><br>
            1. 在浏览器登录目标平台（如 CSDN）<br>
            2. 按 F12 打开开发者工具<br>
            3. 切换到 Application → Cookies<br>
            4. 选择对应域名，复制所有 Cookie<br>
            5. 或安装 "EditThisCookie" 扩展一键导出 JSON
          </div>
          
          <button 
            class="publish-submit-btn" 
            :disabled="isPublishing"
            @click="doPublish"
          >
            <span v-if="isPublishing" class="download-spinner"></span>
            <svg v-if="!isPublishing" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14" style="margin-right: 6px;">
              <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
              <polyline points="16 6 12 2 8 6"></polyline>
              <line x1="12" x2="12" y1="2" y2="15"></line>
            </svg>
            {{ isPublishing ? '发布中...' : '立即发布' }}
          </button>
          
          <div v-if="publishStatus.show" class="publish-status" :class="{ success: publishStatus.success }">
            {{ publishStatus.message }}
            <a v-if="publishStatus.url" :href="publishStatus.url" target="_blank" class="view-link">查看文章</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import mermaid from 'mermaid'
import { useThemeStore } from '../stores/theme'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const isDark = computed(() => themeStore.isDark)
const isLoading = ref(true)
const isFavorite = ref(false)
const showPublishModal = ref(false)
const publishPlatform = ref('csdn')
const publishCookie = ref('')
const isPublishing = ref(false)
const publishStatus = ref({ show: false, success: false, message: '', url: '' })
const showCookieHelp = ref(false)

interface Blog {
  id: string
  title: string
  description: string
  content: string
  category: string
  theme: string
  tags: string[]
  author: string
  authorAvatar: string
  sourceUrl: string
  stars: number
  forks: number
  createdAt: string
  updatedAt: string
  // 博客属性
  articleType: string
  sectionsCount: number
  imagesCount: number
  codeBlocksCount: number
  wordCount: number
  // 封面视频
  coverVideo?: string
}

const blog = ref<Blog | null>(null)

const toast = ref({ show: false, message: '', type: 'info' })

const showToast = (message: string, type = 'info') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatWordCount = (count: number) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + ' 万字'
  } else if (count >= 1000) {
    return (count / 1000).toFixed(1) + ' 千字'
  }
  return count + ' 字'
}

const renderedContent = computed(() => {
  if (!blog.value?.content) return ''
  return marked(blog.value.content)
})

const toggleFavorite = () => {
  isFavorite.value = !isFavorite.value
  showToast(isFavorite.value ? '已添加到收藏' : '已取消收藏', 'success')
}

const isDownloading = ref(false)

const downloadMarkdown = async () => {
  if (!blog.value?.content) {
    showToast('没有可下载的内容', 'error')
    return
  }
  
  if (isDownloading.value) return
  isDownloading.value = true
  
  const title = blog.value.title || 'blog'
  const safeTitle = title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]/g, '_').substring(0, 50)
  
  try {
    // 调用后端 API 导出包含图片的 Markdown ZIP
    const response = await fetch('/api/export/markdown', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        markdown: blog.value.content,
        title: title
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || '导出失败')
    }
    
    // 获取 ZIP 文件
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    
    // 下载 ZIP 文件
    const a = document.createElement('a')
    a.href = url
    a.download = `${safeTitle}_${new Date().toISOString().slice(0, 10)}.zip`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    showToast('ZIP 文件已下载', 'success')
  } catch (error: any) {
    showToast('下载失败: ' + error.message, 'error')
  } finally {
    isDownloading.value = false
  }
}

const openPublishModal = () => {
  if (!blog.value?.content) {
    showToast('没有可发布的内容', 'error')
    return
  }
  showPublishModal.value = true
  publishStatus.value = { show: false, success: false, message: '', url: '' }
}

const closePublishModal = () => {
  showPublishModal.value = false
  publishCookie.value = ''
  showCookieHelp.value = false
}

const parseCookieString = (cookieStr: string, platform: string) => {
  const domainMap: Record<string, string> = {
    'csdn': '.csdn.net',
    'zhihu': '.zhihu.com',
    'juejin': '.juejin.cn'
  }
  const domain = domainMap[platform] || '.csdn.net'
  
  const cookies: { name: string; value: string; domain: string }[] = []
  const pairs = cookieStr.split(';')
  for (const pair of pairs) {
    const trimmed = pair.trim()
    if (!trimmed) continue
    
    const eqIndex = trimmed.indexOf('=')
    if (eqIndex === -1) continue
    
    const name = trimmed.substring(0, eqIndex).trim()
    const value = trimmed.substring(eqIndex + 1).trim()
    
    if (name) {
      cookies.push({ name, value, domain })
    }
  }
  return cookies
}

const doPublish = async () => {
  if (!publishCookie.value.trim()) {
    showToast('请输入 Cookie', 'error')
    return
  }
  
  if (isPublishing.value) return
  isPublishing.value = true
  
  // 解析 Cookie
  let cookies
  try {
    cookies = JSON.parse(publishCookie.value)
    if (!Array.isArray(cookies)) {
      throw new Error('not array')
    }
  } catch (e) {
    cookies = parseCookieString(publishCookie.value, publishPlatform.value)
    if (cookies.length === 0) {
      showToast('Cookie 格式错误，请检查输入', 'error')
      isPublishing.value = false
      return
    }
  }
  
  const title = blog.value?.title || '未命名博客'
  const content = blog.value?.content || ''
  
  publishStatus.value = { show: true, success: false, message: '⏳ 正在发布，请稍候...（约 30-60 秒）', url: '' }
  
  try {
    const response = await fetch('/api/publish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        platform: publishPlatform.value,
        cookies,
        title,
        content
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      publishStatus.value = {
        show: true,
        success: true,
        message: '✅ 发布成功！',
        url: data.url || ''
      }
    } else {
      publishStatus.value = {
        show: true,
        success: false,
        message: '❌ ' + (data.error || '发布失败'),
        url: ''
      }
    }
  } catch (error: any) {
    publishStatus.value = {
      show: true,
      success: false,
      message: '❌ 发布失败: ' + error.message,
      url: ''
    }
  } finally {
    isPublishing.value = false
  }
}

const loadBlog = async (id: string) => {
  isLoading.value = true
  try {
    // 使用历史记录 API
    const response = await fetch(`/api/history/${id}`)
    const result = await response.json()
    
    if (result.success && result.record) {
      const record = result.record
      // 解析 outline 获取标签
      let outline: any = {}
      try { outline = JSON.parse(record.outline || '{}') } catch (e) {}
      
      // 从 outline 或 markdown 中提取标题
      let blogTitle = outline.title || ''
      if (!blogTitle && record.markdown_content) {
        // 从 markdown 内容中提取第一个 # 标题
        const titleMatch = record.markdown_content.match(/^#\s+(.+)$/m)
        if (titleMatch) {
          blogTitle = titleMatch[1].trim()
        }
      }
      // 如果还没有标题，截取 topic 前 50 个字符
      if (!blogTitle) {
        blogTitle = (record.topic || '未命名博客').slice(0, 50)
        if (record.topic && record.topic.length > 50) {
          blogTitle += '...'
        }
      }
      
      // 计算字数
      const wordCount = (record.markdown_content || '').length
      
      // 计算图片数量
      const imageMatches = (record.markdown_content || '').match(/!\[.*?\]\(.*?\)/g)
      const imagesCount = imageMatches ? imageMatches.length : (record.images_count || 0)
      
      // 计算代码块数量
      const codeMatches = (record.markdown_content || '').match(/```[\s\S]*?```/g)
      const codeBlocksCount = codeMatches ? codeMatches.length : (record.code_blocks_count || 0)
      
      // 文章类型映射
      const articleTypeMap: Record<string, string> = {
        'mini': 'Mini',
        'short': '短文',
        'medium': '中等',
        'long': '长文',
        'custom': '自定义'
      }
      
      blog.value = {
        id: record.id,
        title: blogTitle,
        description: outline.summary || '',
        content: record.markdown_content || '',
        category: record.content_type || 'blog',
        theme: 'ai',
        tags: outline.keywords || [],
        author: 'vibe-blog',
        authorAvatar: 'https://avatars.githubusercontent.com/u/1?v=4',
        sourceUrl: '',
        stars: Math.floor(Math.random() * 1000) + 100,
        forks: Math.floor(Math.random() * 500) + 50,
        createdAt: record.created_at,
        updatedAt: record.created_at,
        // 博客属性
        articleType: articleTypeMap[record.article_type] || record.article_type || '短文',
        sectionsCount: record.sections_count || outline.sections?.length || 0,
        imagesCount: imagesCount,
        codeBlocksCount: codeBlocksCount,
        wordCount: wordCount,
        // 封面视频
        coverVideo: record.cover_video || ''
      }
    } else {
      showToast('加载失败: ' + (result.error || '记录不存在'), 'error')
      router.push('/')
    }
  } catch (e: any) {
    showToast('加载失败: ' + e.message, 'error')
    router.push('/')
  } finally {
    isLoading.value = false
  }
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    loadBlog(newId as string)
  }
})

// 初始化 Mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  flowchart: {
    htmlLabels: true,
    useMaxWidth: true,
    curve: 'basis'
  }
})

// 渲染 Mermaid 图表
const renderMermaid = async () => {
  await nextTick()
  
  const container = document.querySelector('.blog-content')
  if (!container) return
  
  const mermaidBlocks = container.querySelectorAll('pre code.language-mermaid')
  if (mermaidBlocks.length === 0) return
  
  for (let i = 0; i < mermaidBlocks.length; i++) {
    const block = mermaidBlocks[i] as HTMLElement
    let code = block.textContent || ''
    
    // 预处理 Mermaid 代码
    code = code.replace(/[""'']/g, '"')
    code = code.replace(/（/g, '(').replace(/）/g, ')')
    code = code.replace(/【/g, '[').replace(/】/g, ']')
    code = code.replace(/：/g, ':')
    code = code.replace(/；/g, ';')
    code = code.replace(/，/g, ',')
    
    // 修复空标签问题
    code = code.replace(/(\bsubgraph\s+\w+)\[""\]/g, '$1[" "]')
    code = code.replace(/(\w+)\[""\]/g, '$1[" "]')
    
    // 处理节点文本中的特殊字符
    code = code.replace(/\[([^\]]+)\]/g, (match, content) => {
      if (content.startsWith('"') && content.endsWith('"')) return match
      if (/[\\\/\n·•–—\(\)="]/.test(content) || content.includes('\\n')) {
        let fixed = content.replace(/\\n/g, '<br/>')
        fixed = fixed.replace(/"/g, '#quot;')
        return '["' + fixed + '"]'
      }
      return match
    })
    
    const div = document.createElement('div')
    div.className = 'mermaid-container'
    div.id = 'mermaid-' + i
    
    try {
      const { svg } = await mermaid.render('mermaid-graph-' + i + '-' + Date.now(), code)
      div.innerHTML = svg
      block.parentElement?.replaceWith(div)
    } catch (e: any) {
      console.warn('Mermaid 图表渲染失败:', e.message)
      div.innerHTML = '<pre class="mermaid-error"><code>' + code + '</code></pre><p class="mermaid-error-msg">⚠️ 图表渲染失败</p>'
      block.parentElement?.replaceWith(div)
    }
  }
}

// 监听内容变化，渲染 Mermaid
watch(() => blog.value?.content, () => {
  setTimeout(renderMermaid, 100)
})

onMounted(() => {
  const id = route.params.id as string
  if (id) {
    loadBlog(id)
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

.blog-detail-container {
  --bg: #ffffff;
  --surface: #f8fafc;
  --surface-hover: #f1f5f9;
  --border: #e2e8f0;
  --text: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --primary: #8b5cf6;
  --primary-light: rgba(139, 92, 246, 0.1);
  --keyword: #8b5cf6;
  --string: #22c55e;
  --number: #f59e0b;
  --comment: #64748b;
  --function: #3b82f6;
  --variable: #ec4899;
  --star: #eab308;
  --fork: #3b82f6;
  --calendar: #22c55e;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
  --glass-bg: rgba(255, 255, 255, 0.8);
  --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  
  min-height: 100vh;
  font-family: 'JetBrains Mono', monospace;
  background: linear-gradient(135deg, var(--surface) 0%, #f1f5f9 50%, #dbeafe 100%);
  color: var(--text);
}

.blog-detail-container.dark-mode {
  --bg: #0f172a;
  --surface: #1e293b;
  --surface-hover: #334155;
  --border: #334155;
  --text: #f1f5f9;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --keyword: #a78bfa;
  --string: #4ade80;
  --number: #fbbf24;
  --function: #60a5fa;
  --variable: #f472b6;
  --glass-bg: rgba(15, 23, 42, 0.85);
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #172554 100%);
}

/* 导航栏 */
.terminal-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 28px;
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.terminal-nav-left, .terminal-nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.terminal-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform var(--transition);
}

.dot:hover { transform: scale(1.2); }
.dot.red { background: linear-gradient(135deg, #ef4444, #dc2626); }
.dot.yellow { background: linear-gradient(135deg, #eab308, #ca8a04); }
.dot.green { background: linear-gradient(135deg, #22c55e, #16a34a); }

.terminal-dots-sm { display: flex; gap: 6px; }
.terminal-dots-sm .dot { width: 10px; height: 10px; }

.terminal-title {
  font-size: 13px;
  color: var(--text-secondary);
}

.nav-cmd {
  font-size: 13px;
  color: var(--function);
  text-decoration: none;
  padding: 8px 16px;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all var(--transition);
}

.nav-cmd:hover {
  background: var(--surface-hover);
  border-color: var(--function);
  transform: translateY(-1px);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface);
  border: 1px solid var(--border);
  cursor: pointer;
  padding: 10px;
  border-radius: 8px;
  transition: all 0.2s ease;
  color: var(--text-secondary);
}

.theme-toggle:hover {
  background: var(--surface-hover);
  color: var(--primary);
  border-color: var(--primary);
  transform: scale(1.05);
}

.theme-toggle svg {
  transition: transform 0.2s ease;
}

.theme-toggle:hover svg {
  transform: rotate(15deg);
}

/* 主内容区 */
.main-content {
  display: flex;
  gap: 32px;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.content-area {
  flex: 1;
  min-width: 0;
}

/* 面包屑 */
.breadcrumb-bar {
  margin-bottom: 24px;
}

.breadcrumb-inner {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--glass-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
}

.prompt { color: var(--string); font-weight: 600; }
.muted { color: var(--text-muted); }

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
}

.crumb-link {
  color: var(--function);
  text-decoration: none;
  transition: color var(--transition);
}

.crumb-link:hover { color: var(--primary); }
.separator { color: var(--text-muted); }
.crumb-current { color: var(--text); font-weight: 500; }

/* 标题区 */
.title-section {
  margin-bottom: 24px;
}

.blog-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.title-highlight {
  background: linear-gradient(135deg, var(--text) 0%, var(--primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.blog-description {
  font-size: 14px;
  color: var(--text-secondary);
}

.comment-prefix {
  color: var(--string);
}

/* 统计信息 */
.stats-section {
  margin-bottom: 24px;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--glass-bg);
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  color: var(--text-muted);
}

.stats-content {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  padding: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.stat-icon {
  width: 14px;
  height: 14px;
}

.stat-icon.star { color: var(--star); }
.stat-icon.fork { color: var(--fork); }
.stat-icon.calendar { color: var(--calendar); }

.stat-label { color: var(--text-muted); }
.stat-value { color: var(--text); font-weight: 600; }

/* 内容卡片 */
.content-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--glass-bg);
}

.content-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-name {
  font-size: 12px;
  color: var(--text-muted);
}

.readonly-badge {
  font-size: 12px;
  color: var(--text-muted);
}

.content-card-body {
  padding: 24px 32px;
}

/* 博客内容样式 */
.blog-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text);
}

.blog-content :deep(h1),
.blog-content :deep(h2),
.blog-content :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  color: var(--text);
}

.blog-content :deep(h1) { font-size: 1.75rem; }
.blog-content :deep(h2) { font-size: 1.5rem; }
.blog-content :deep(h3) { font-size: 1.25rem; }

.blog-content :deep(p) {
  margin-bottom: 16px;
}

.blog-content :deep(code) {
  background: var(--surface);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  color: var(--variable);
}

.blog-content :deep(pre) {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.blog-content :deep(pre code) {
  background: transparent;
  padding: 0;
}

.blog-content :deep(ul),
.blog-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 24px;
}

.blog-content :deep(li) {
  margin-bottom: 8px;
}

.blog-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
  display: block;
  object-fit: contain;
}

/* Mermaid 图表样式 */
.blog-content :deep(.mermaid-container) {
  background: var(--surface);
  border-radius: 10px;
  padding: 20px;
  margin: 16px 0;
  text-align: center;
  overflow: visible;
}

.blog-content :deep(.mermaid-container svg) {
  max-width: 100%;
  height: auto;
  overflow: visible;
}

.blog-content :deep(.mermaid-error) {
  background: #fff3cd;
  padding: 10px;
  border-radius: 5px;
  text-align: left;
  overflow-x: auto;
}

.blog-content :deep(.mermaid-error-msg) {
  color: #856404;
  font-size: 12px;
  margin-top: 8px;
}

.blog-content :deep(a) {
  color: var(--function);
  text-decoration: none;
}

.blog-content :deep(a:hover) {
  text-decoration: underline;
}

/* 侧边栏 */
.sidebar {
  width: 350px;
  flex-shrink: 0;
}

.sidebar-sticky {
  position: sticky;
  top: 88px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 112px);
  overflow-y: auto;
}

.sidebar-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--glass-bg);
}

.sidebar-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.card-title {
  font-size: 12px;
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  background: transparent;
  border: none;
  padding: 6px;
  cursor: pointer;
  border-radius: 6px;
  color: var(--text-muted);
  transition: all var(--transition);
}

.action-btn:hover {
  background: var(--surface-hover);
  color: var(--text);
}

.action-btn.favorite:hover,
.action-btn.favorite.active {
  color: #ef4444;
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

.sidebar-card-body {
  padding: 16px;
}

/* 作者信息 */
.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid var(--border);
}

.author-details {
  flex: 1;
  min-width: 0;
}

.json-line {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.json-key { color: var(--function); }
.json-value { color: var(--string); }

.source-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  text-decoration: none;
  font-size: 13px;
  transition: all var(--transition);
}

.source-link:hover {
  background: var(--surface-hover);
  border-color: var(--primary);
}

.source-link svg {
  width: 16px;
  height: 16px;
}

/* 标签 */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 4px 10px;
  background: var(--primary-light);
  border-radius: 6px;
  font-size: 11px;
  color: var(--primary);
  font-weight: 500;
}

/* 相关文章 */
.related-comment {
  margin-bottom: 12px;
  font-size: 12px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.related-item {
  text-decoration: none;
}

.related-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  transition: all var(--transition);
}

.related-card:hover {
  border-color: var(--primary);
  background: var(--surface-hover);
}

.related-header {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.related-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid var(--border);
  flex-shrink: 0;
}

.related-info {
  flex: 1;
  min-width: 0;
}

.related-title {
  margin-bottom: 2px;
}

.import-keyword {
  color: var(--function);
  font-size: 12px;
}

.import-name {
  color: var(--text);
  font-size: 12px;
  font-weight: 600;
  margin-left: 4px;
}

.import-path {
  color: var(--string);
  font-size: 12px;
  margin-left: 4px;
}

.related-stars {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.star-icon {
  width: 10px;
  height: 10px;
  fill: var(--star);
}

/* 下载与发布卡片 */
.download-card .sidebar-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.man-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--string);
  text-decoration: none;
  transition: opacity 0.2s;
}

.man-link:hover {
  opacity: 0.8;
}

.download-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  margin-bottom: 10px;
  font-family: 'JetBrains Mono', monospace;
}

.download-btn.primary {
  background: linear-gradient(135deg, #cc8b4e, #b87a3d);
  color: #fff;
}

.download-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(204, 139, 78, 0.4);
}

.download-btn.secondary {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
}

.download-btn.secondary:hover {
  background: var(--surface-hover);
  border-color: var(--primary);
}

.download-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.download-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.download-hint {
  font-size: 11px;
  color: var(--text-muted);
  line-height: 1.5;
  margin-top: 4px;
}

.hint-tag {
  color: var(--string);
  font-weight: 600;
}

/* 封面视频卡片 */
.video-card .sidebar-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--number);
  background: rgba(245, 158, 11, 0.15);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.video-body {
  padding: 0 !important;
}

.video-container {
  position: relative;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

.cover-video {
  width: 100%;
  display: block;
  max-height: 200px;
  object-fit: contain;
  transition: opacity 0.2s ease;
}

.cover-video:hover {
  opacity: 0.95;
}

.video-actions {
  padding: 12px;
  display: flex;
  justify-content: center;
  background: var(--surface);
  border-top: 1px solid var(--border);
}

.video-download-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text);
  font-size: 12px;
  text-decoration: none;
  transition: all 0.2s ease;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
}

.video-download-btn:hover {
  background: var(--surface-hover);
  border-color: var(--number);
  color: var(--number);
  transform: translateY(-1px);
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 40px;
}

.code-line {
  margin-bottom: 16px;
  font-size: 14px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  padding: 14px 24px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
  z-index: 1001;
  box-shadow: var(--shadow-lg);
  animation: toastIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes toastIn {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.toast.success {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.3);
  color: #16a34a;
}

.toast.error {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.3);
  color: #dc2626;
}

.toast-icon { 
  margin-right: 10px;
  flex-shrink: 0;
}

/* 发布弹窗样式 */
.publish-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.publish-modal {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.publish-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}

.publish-modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text);
}

.modal-close-btn {
  width: 32px;
  height: 32px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 20px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: var(--surface-hover);
  color: #ef4444;
}

.publish-modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.help-link {
  color: var(--primary);
  margin-left: 8px;
  text-decoration: none;
}

.help-link:hover {
  text-decoration: underline;
}

.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
}

.form-textarea {
  width: 100%;
  height: 120px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  background: var(--surface);
  color: var(--text);
  resize: vertical;
}

.form-textarea::placeholder {
  color: var(--text-muted);
}

.cookie-warning {
  margin-top: 8px;
  padding: 10px 12px;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 6px;
  font-size: 11px;
  color: var(--text-secondary);
}

.cookie-help {
  background: var(--surface);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.publish-submit-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.publish-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.publish-submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.publish-status {
  margin-top: 12px;
  padding: 12px;
  background: var(--surface);
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
  color: var(--text-secondary);
}

.publish-status.success {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
}

.view-link {
  color: var(--primary);
  margin-left: 8px;
}

/* 博客属性样式 - 代码风格标签 */
.stat-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stat-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  transition: all 0.15s ease;
  cursor: default;
}

.stat-tag:hover {
  border-color: var(--primary);
  background: var(--surface-hover);
}

.stat-tag-key {
  color: var(--function);
  font-weight: 500;
}

.stat-tag-value {
  color: var(--text);
  font-weight: 600;
}

/* 不同类型的标签颜色 */
.stat-tag.type .stat-tag-value {
  color: var(--primary);
  background: var(--primary-light);
  padding: 2px 6px;
  border-radius: 4px;
}

.stat-tag.sections .stat-tag-key { color: var(--string); }
.stat-tag.images .stat-tag-key { color: var(--number); }
.stat-tag.code .stat-tag-key { color: var(--function); }

/* 响应式 */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
  }
  
  .sidebar-sticky {
    position: static;
    max-height: none;
  }
}

@media (max-width: 768px) {
  .terminal-nav {
    flex-direction: column;
    gap: 12px;
    padding: 12px 16px;
  }
  
  .terminal-nav-right {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .content-card-body {
    padding: 16px;
  }
  
  .blog-title {
    font-size: 1.5rem;
  }
  
  .stats-content {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
