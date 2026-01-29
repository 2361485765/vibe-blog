<template>
  <div class="blog-list-container">
    <!-- 导航栏 -->
    <nav class="navbar">
      <a href="https://github.com/datawhalechina/vibe-blog" target="_blank" rel="noopener noreferrer" class="logo" title="GitHub - vibe-blog">> vibe-blog</a>
      <div class="nav-links">
        <a href="#about">$ about</a>
        <a href="#features">$ features</a>
        <a href="/blog" class="active">$ blog-list</a>
      </div>
    </nav>

    <!-- 主容器 -->
    <div class="main-container">
      <!-- 搜索栏 -->
      <div class="search-section">
        <div class="terminal-header">
          <div class="terminal-dots">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot green"></span>
          </div>
          <span>search --ai $ find Search blogs with AI</span>
        </div>
        <div class="search-input">
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Search blogs..."
          >
        </div>
      </div>

      <!-- 统计和排序 -->
      <div class="stats-bar">
        <span>$ count: <strong>{{ blogs.length }}</strong> blogs available</span>
        <div class="sort-buttons">
          <button 
            v-for="sort in sortOptions"
            :key="sort"
            :class="['sort-btn', { active: currentSort === sort }]"
            @click="currentSort = sort"
          >
            {{ sort }}
          </button>
        </div>
      </div>

      <!-- 博客卡片网格 -->
      <div class="blogs-grid">
        <div 
          v-for="blog in filteredBlogs"
          :key="blog.id"
          class="blog-card"
          :data-theme="blog.theme"
          @click="openBlog(blog.id)"
          role="button"
          tabindex="0"
          @keydown.enter="openBlog(blog.id)"
        >
          <div class="card-header">
            <div class="folder-tag">
              <span class="icon">📁</span>
              <span>{{ blog.category }}</span>
            </div>
            <span class="status">● module</span>
          </div>

          <div class="card-content">
            <h3>{{ blog.title }}</h3>
            <p>{{ blog.description }}</p>
          </div>

          <div class="card-tags">
            <span 
              v-for="tag in blog.tags"
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>

          <div class="card-footer">
            <span class="date">{{ formatDate(blog.date) }}</span>
            <a href="#" class="read-more">→</a>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredBlogs.length === 0" class="empty-state">
        <p>$ No blogs found</p>
      </div>
    </div>

    <!-- 底部备案信息 -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBlogStore } from '../stores/blog'
import Footer from '../components/Footer.vue'

const router = useRouter()

const blogStore = useBlogStore()
const searchQuery = ref('')
const currentSort = ref('⭐ stars')
const sortOptions = ['⭐ stars', '🕐 recent']

const blogs = ref([
  {
    id: 1,
    title: 'LangGraph 入门教程',
    description: '从零开始学习 LangGraph，构建 AI Agent',
    category: 'ai-tutorials',
    theme: 'ai',
    tags: ['AI', 'LLM', 'LangGraph'],
    date: new Date('2024-01-15')
  },
  {
    id: 2,
    title: 'React 19 新特性',
    description: 'Server Components, Actions 等新功能详解',
    category: 'web-development',
    theme: 'web',
    tags: ['Web', 'React', '前端'],
    date: new Date('2024-01-12')
  },
  {
    id: 3,
    title: 'Redis 性能优化',
    description: '深入理解 Redis 内存管理和性能优化',
    category: 'database',
    theme: 'data',
    tags: ['Data', 'Redis', '性能'],
    date: new Date('2024-01-10')
  }
])

const filteredBlogs = computed(() => {
  let result = blogs.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(blog =>
      blog.title.toLowerCase().includes(query) ||
      blog.description.toLowerCase().includes(query)
    )
  }

  if (currentSort.value === '🕐 recent') {
    result.sort((a, b) => b.date.getTime() - a.date.getTime())
  }

  return result
})

const formatDate = (date: Date) => {
  return date.toISOString().split('T')[0]
}

const openBlog = (blogId: number) => {
  router.push(`/blog/${blogId}`)
}
</script>

<style scoped>
.blog-list-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  font-family: 'JetBrains Mono', monospace;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #8b5cf6;
  letter-spacing: 2px;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 30px;
}

.nav-links a {
  color: #64748b;
  text-decoration: none;
  font-size: 13px;
  transition: all 0.3s;
}

.nav-links a:hover,
.nav-links a.active {
  color: #1e293b;
  text-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
}

.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.search-section {
  margin-bottom: 24px;
}

.terminal-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
  border-radius: 8px 8px 0 0;
  font-size: 12px;
  color: #64748b;
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

.search-input {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #e2e8f0;
  border-top: none;
  border-radius: 0 0 8px 8px;
  padding: 16px;
}

.search-input input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  color: #1e293b;
}

.search-input input::placeholder {
  color: #cbd5e1;
}

.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: #64748b;
}

.sort-buttons {
  display: flex;
  gap: 8px;
}

.sort-btn {
  padding: 6px 12px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 4px;
  color: #64748b;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.sort-btn:hover {
  background: rgba(139, 92, 246, 0.2);
  color: #8b5cf6;
}

.sort-btn.active {
  background: #8b5cf6;
  border-color: #8b5cf6;
  color: white;
}

.blogs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.blog-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
  cursor: pointer;
}

.blog-card:hover {
  border-color: #8b5cf6;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.folder-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

.status {
  font-size: 12px;
  color: #22c55e;
}

.card-content {
  margin-bottom: 12px;
}

.card-content h3 {
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 6px;
}

.card-content p {
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.tag {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 4px;
  font-size: 11px;
  color: #8b5cf6;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
  font-size: 12px;
  color: #94a3b8;
}

.read-more {
  color: #8b5cf6;
  text-decoration: none;
  transition: all 0.3s;
}

.read-more:hover {
  transform: translateX(4px);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
  font-size: 14px;
}

@media (max-width: 768px) {
  .navbar {
    flex-direction: column;
    gap: 15px;
    padding: 15px 20px;
  }

  .nav-links {
    gap: 15px;
    flex-wrap: wrap;
    justify-content: center;
  }

  .stats-bar {
    flex-direction: column;
    gap: 12px;
  }

  .blogs-grid {
    grid-template-columns: 1fr;
  }
}
</style>
