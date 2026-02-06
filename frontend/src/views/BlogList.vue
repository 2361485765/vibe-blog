<template>
  <div class="min-h-screen" :style="{ backgroundColor: 'var(--color-background)', color: 'var(--color-foreground)' }">
    <!-- Fixed Top Navigation -->
    <header class="fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b" :style="{ backgroundColor: 'var(--color-card)', borderColor: 'var(--color-border)' }">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center gap-3 group">
            <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg border" :style="{ backgroundColor: 'var(--color-primary-light)', borderColor: 'var(--color-primary-light)' }">
              <div class="w-2 h-2 rounded-full animate-pulse" :style="{ backgroundColor: 'var(--color-primary)' }"></div>
              <span class="text-xs font-mono font-semibold" :style="{ color: 'var(--color-primary)' }">ONLINE</span>
            </div>
            <div class="font-sans text-lg flex items-center font-bold">
              <span :style="{ color: 'var(--color-primary)' }">~/</span>
              <span class="ml-1" :style="{ color: 'var(--color-foreground)' }">vibe-blog</span>
              <span class="inline-block w-2 h-5 ml-1 animate-blink" :style="{ backgroundColor: 'var(--color-primary)' }"></span>
            </div>
          </router-link>

          <!-- Navigation -->
          <nav class="hidden md:flex items-center gap-2">
            <a href="#" class="nav-link px-4 py-2 rounded-lg font-mono text-sm transition-all cursor-pointer">
              <span class="syntax-comment">$</span>
              <span class="syntax-function ml-2">cd</span>
              <span class="ml-2">/categories</span>
            </a>
            <a href="#" class="nav-link-active px-4 py-2 rounded-lg font-mono text-sm border transition-all cursor-pointer">
              <span class="syntax-comment">$</span>
              <span class="font-semibold ml-2">ai</span>
              <span class="ml-2">--search</span>
            </a>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto">
        <!-- Search Section -->
        <section class="mb-8">
          <div class="terminal-card rounded-xl overflow-hidden shadow-card border">
            <!-- Terminal Header -->
            <div class="terminal-header flex items-center justify-between px-4 py-3 border-b">
              <div class="flex items-center gap-3">
                <div class="flex items-center gap-2">
                  <div class="terminal-dot terminal-dot-red"></div>
                  <div class="terminal-dot terminal-dot-yellow"></div>
                  <div class="terminal-dot terminal-dot-green"></div>
                </div>
                <span class="text-xs font-mono text-muted-fg">search.sh</span>
              </div>
              <button
                @click="searchQuery = ''"
                class="text-xs font-mono text-muted-fg hover-primary transition-colors cursor-pointer"
              >
                [clear]
              </button>
            </div>
            <!-- Terminal Body -->
            <div class="p-5">
              <div class="flex items-center gap-3 font-mono text-sm">
                <span class="syntax-comment text-base">❯</span>
                <span class="syntax-keyword font-semibold">find</span>
                <input
                  v-model="searchQuery"
                  type="text"
                  :placeholder="`搜索 ${mockBlogs.length} 篇博客...`"
                  class="flex-1 bg-transparent outline-none border-none"
                  :style="{ color: 'var(--color-foreground)' }"
                />
              </div>
            </div>
          </div>
        </section>

        <!-- Stats Bar -->
        <section class="mb-8">
          <div class="stats-bar flex items-center justify-between flex-wrap gap-4 rounded-xl p-4 border">
            <div class="flex items-center gap-3 font-mono text-sm">
              <span class="syntax-comment">❯</span>
              <span class="text-muted-fg">count:</span>
              <span class="text-lg font-bold" :style="{ color: 'var(--color-primary)' }">{{ filteredBlogs.length }}</span>
              <span class="text-secondary-fg">篇博客</span>
              <span class="text-muted-fg ml-2">--sort-by</span>
            </div>
            <div class="flex items-center gap-2">
              <button
                v-for="sort in sortOptions"
                :key="sort.value"
                @click="currentSort = sort.value"
                :class="[
                  'px-4 py-2 rounded-lg font-mono text-sm transition-all duration-200 cursor-pointer',
                  currentSort === sort.value
                    ? 'sort-btn-active'
                    : 'sort-btn'
                ]"
              >
                <span class="mr-2">{{ sort.icon }}</span>
                {{ sort.label }}
              </button>
            </div>
          </div>
        </section>

        <!-- Blog Cards Grid -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="blog in filteredBlogs"
            :key="blog.id"
            class="group cursor-pointer animate-fade-up"
          >
            <div class="blog-card rounded-xl overflow-hidden shadow-card hover:shadow-card-hover hover:-translate-y-1 transition-all duration-300 border h-full flex flex-col">
              <!-- Terminal Header -->
              <div class="terminal-header flex items-center justify-between px-4 py-2.5 border-b">
                <div class="flex items-center gap-3">
                  <div class="flex items-center gap-1.5">
                    <div class="terminal-dot-sm terminal-dot-red"></div>
                    <div class="terminal-dot-sm terminal-dot-yellow"></div>
                    <div class="terminal-dot-sm terminal-dot-green"></div>
                  </div>
                  <span class="text-xs font-mono text-muted-fg">{{ blog.filename }}</span>
                </div>
                <div class="flex items-center gap-1">
                  <span v-for="i in blog.stars" :key="i" class="text-xs">⭐</span>
                </div>
              </div>

              <!-- Card Content -->
              <div class="p-5 flex-1 flex flex-col">
                <div class="font-mono text-sm space-y-2.5 mb-4">
                  <!-- Line 1: export -->
                  <div class="flex items-start gap-3">
                    <span class="line-number select-none w-6 text-right flex-shrink-0">1</span>
                    <div class="flex-1 leading-relaxed">
                      <span class="syntax-keyword font-semibold">export</span>
                      <span class="ml-2 font-semibold" :style="{ color: 'var(--color-foreground)' }">{{ blog.title }}</span>
                    </div>
                  </div>
                  <!-- Line 2: comment -->
                  <div class="flex items-start gap-3">
                    <span class="line-number select-none w-6 text-right flex-shrink-0">2</span>
                    <div class="flex-1 leading-relaxed">
                      <span class="syntax-comment">// {{ blog.description }}</span>
                    </div>
                  </div>
                  <!-- Line 3: from author -->
                  <div class="flex items-start gap-3">
                    <span class="line-number select-none w-6 text-right flex-shrink-0">3</span>
                    <div class="flex-1 leading-relaxed">
                      <span class="syntax-import font-semibold">from</span>
                      <span class="syntax-string ml-2">"{{ blog.author }}"</span>
                    </div>
                  </div>
                  <!-- Line 4: empty -->
                  <div class="flex items-start gap-3">
                    <span class="line-number select-none w-6 text-right flex-shrink-0">4</span>
                    <div class="flex-1 h-4"></div>
                  </div>
                </div>

                <!-- Tags -->
                <div class="flex flex-wrap gap-2 mb-4">
                  <span
                    v-for="tag in blog.tags"
                    :key="tag"
                    class="tag-chip px-2.5 py-1 text-xs font-mono rounded border transition-all cursor-pointer"
                  >
                    #{{ tag }}
                  </span>
                </div>

                <!-- Footer -->
                <div class="mt-auto pt-4 border-t flex items-center justify-between" :style="{ borderColor: 'var(--color-border)' }">
                  <div class="flex items-center gap-2">
                    <div class="avatar-circle w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold">
                      {{ blog.author[0] }}
                    </div>
                    <span class="text-xs font-mono text-secondary-fg">{{ blog.author }}</span>
                  </div>
                  <div class="flex items-center gap-2 group-hover:translate-x-1 transition-transform" :style="{ color: 'var(--color-primary)' }">
                    <span class="text-sm">→</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="filteredBlogs.length === 0" class="mt-12">
          <div class="terminal-card rounded-xl overflow-hidden shadow-card border max-w-2xl mx-auto" style="border-color: var(--color-error)">
            <div class="terminal-header flex items-center gap-3 px-4 py-3 border-b" style="border-color: var(--color-error)">
              <div class="flex items-center gap-2">
                <div class="terminal-dot terminal-dot-red"></div>
                <div class="terminal-dot terminal-dot-yellow"></div>
                <div class="terminal-dot terminal-dot-green"></div>
              </div>
              <span class="text-xs font-mono text-muted-fg">error.log</span>
            </div>
            <div class="p-8 text-center">
              <div class="font-mono text-sm space-y-3">
                <p class="text-lg font-bold" :style="{ color: 'var(--color-error)' }">❌ Error: No blogs found</p>
                <p class="syntax-comment">// 没有找到匹配的博客</p>
                <p class="text-muted-fg">// 尝试调整搜索关键词或清除筛选条件</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const searchQuery = ref('')
const currentSort = ref('stars')

const sortOptions = [
  { value: 'stars', label: '热门', icon: '⭐' },
  { value: 'recent', label: '最新', icon: '🕐' }
]

const mockBlogs = [
  {
    id: 1,
    title: 'ModernWebDev',
    description: '现代 Web 开发完整指南',
    author: 'Alice Chen',
    filename: 'modern-web.ts',
    stars: 5,
    tags: ['react', 'typescript', 'vite'],
    date: '2026-02-05'
  },
  {
    id: 2,
    title: 'Vue3Mastery',
    description: 'Vue 3 组合式 API 深度解析',
    author: 'Bob Zhang',
    filename: 'vue3-guide.vue',
    stars: 5,
    tags: ['vue', 'composition-api', 'pinia'],
    date: '2026-02-04'
  },
  {
    id: 3,
    title: 'AIIntegration',
    description: '将 AI 集成到你的应用中',
    author: 'Carol Liu',
    filename: 'ai-integration.md',
    stars: 4,
    tags: ['ai', 'openai', 'langchain'],
    date: '2026-02-03'
  },
  {
    id: 4,
    title: 'TailwindPro',
    description: 'Tailwind CSS 专业实践',
    author: 'David Wang',
    filename: 'tailwind-pro.css',
    stars: 4,
    tags: ['tailwind', 'css', 'design'],
    date: '2026-02-02'
  },
  {
    id: 5,
    title: 'TypeScriptPatterns',
    description: 'TypeScript 高级设计模式',
    author: 'Eve Li',
    filename: 'ts-patterns.ts',
    stars: 5,
    tags: ['typescript', 'patterns', 'advanced'],
    date: '2026-01-01'
  },
  {
    id: 6,
    title: 'PerformanceOpt',
    description: 'Web 应用性能优化实战',
    author: 'Frank Zhou',
    filename: 'performance.js',
    stars: 4,
    tags: ['performance', 'optimization', 'web-vitals'],
    date: '2026-01-31'
  }
]

const filteredBlogs = computed(() => {
  let blogs = mockBlogs

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    blogs = blogs.filter(blog =>
      blog.title.toLowerCase().includes(query) ||
      blog.description.toLowerCase().includes(query) ||
      blog.author.toLowerCase().includes(query) ||
      blog.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  if (currentSort.value === 'stars') {
    blogs = [...blogs].sort((a, b) => b.stars - a.stars)
  } else if (currentSort.value === 'recent') {
    blogs = [...blogs].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
  }

  return blogs
})
</script>

<style scoped>
/* Terminal card */
.terminal-card {
  background-color: var(--color-card);
  border-color: var(--color-border);
}

.terminal-header {
  background-color: var(--color-muted);
  border-color: var(--color-border);
}

/* Terminal dots */
.terminal-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.terminal-dot-sm {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.terminal-dot-red { background-color: var(--color-dot-red); }
.terminal-dot-yellow { background-color: var(--color-dot-yellow); }
.terminal-dot-green { background-color: var(--color-dot-green); }

.group:hover .terminal-dot-red { background-color: var(--color-dot-red-hover, #ef4444); }
.group:hover .terminal-dot-yellow { background-color: var(--color-dot-yellow-hover, #eab308); }
.group:hover .terminal-dot-green { background-color: var(--color-dot-green-hover, #22c55e); }

/* Blog card */
.blog-card {
  background-color: var(--color-card);
  border-color: var(--color-border);
}

.blog-card:hover {
  border-color: var(--color-primary);
}

/* Stats bar */
.stats-bar {
  background-color: var(--color-muted);
  border-color: var(--color-border);
}

/* Sort buttons */
.sort-btn-active {
  background-color: var(--color-primary);
  color: var(--color-primary-foreground);
  box-shadow: var(--shadow-primary);
}

.sort-btn {
  background-color: var(--color-secondary);
  color: var(--color-secondary-foreground);
  border: 1px solid var(--color-border);
}

.sort-btn:hover {
  background-color: var(--color-bg-hover);
  color: var(--color-foreground);
  border-color: var(--color-border-hover);
}

/* Syntax highlight classes */
.syntax-keyword { color: var(--color-syntax-keyword); }
.syntax-comment { color: var(--color-syntax-comment); }
.syntax-function { color: var(--color-syntax-function); }
.syntax-import { color: var(--color-syntax-import); }
.syntax-string { color: var(--color-syntax-string); }
.syntax-number { color: var(--color-syntax-number); }
.syntax-tag { color: var(--color-syntax-tag); }

/* Text color helpers */
.text-muted-fg { color: var(--color-muted-foreground); }
.text-secondary-fg { color: var(--color-text-secondary); }
.line-number { color: var(--color-muted-foreground); }

/* Hover helpers */
.hover-primary:hover { color: var(--color-primary); }

/* Navigation links */
.nav-link {
  color: var(--color-text-secondary);
}

.nav-link:hover {
  color: var(--color-foreground);
  background-color: var(--color-muted);
}

.nav-link-active {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary-light);
}

.nav-link-active:hover {
  background-color: var(--color-primary-glow);
}

/* Tag chips */
.tag-chip {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary-light);
}

.tag-chip:hover {
  background-color: var(--color-primary-glow);
  border-color: var(--color-primary);
}

/* Avatar */
.avatar-circle {
  background: linear-gradient(135deg, var(--color-primary), var(--color-syntax-keyword));
  color: var(--color-primary-foreground);
}

/* Input placeholder */
input::placeholder {
  color: var(--color-muted-foreground);
}
</style>
