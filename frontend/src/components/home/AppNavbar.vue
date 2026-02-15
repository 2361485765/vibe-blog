<template>
  <nav class="navbar">
    <a
      href="https://github.com/datawhalechina/vibe-blog"
      target="_blank"
      rel="noopener noreferrer"
      class="logo"
      title="GitHub - vibe-blog"
    >
      &lt;vibe-blog /&gt;
    </a>
    <div class="nav-actions">
      <router-link
        v-if="appConfig.features?.xhs_tab"
        to="/xhs"
        class="nav-link"
      >
        <BookOpen :size="14" />
        <span>小红书创作</span>
      </router-link>
      <router-link
        v-if="appConfig.features?.reviewer"
        to="/reviewer"
        class="nav-link"
      >
        <Search :size="14" />
        <span>教程评估</span>
      </router-link>
      <a
        href="https://github.com/datawhalechina/vibe-blog"
        target="_blank"
        rel="noopener noreferrer"
        class="theme-toggle"
        title="在 GitHub 上点赞"
      >
        <Github :size="18" />
      </a>
      <button
        class="theme-toggle"
        :title="isDarkMode ? '切换到浅色模式' : '切换到深色模式'"
        @click="toggleTheme"
      >
        <Sun v-if="isDarkMode" :size="18" />
        <Moon v-else :size="18" />
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Sun, Moon, BookOpen, Search, Github } from 'lucide-vue-next'
import { useThemeStore } from '../../stores/theme'

interface Props {
  appConfig: {
    features?: Record<string, boolean>
  }
}

const props = defineProps<Props>()
const themeStore = useThemeStore()

const isDarkMode = computed(() => themeStore.isDark)

const toggleTheme = () => {
  themeStore.toggleTheme()
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: var(--glass-bg);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-xl);
  z-index: var(--z-fixed);
  transition: var(--transition-colors);
  box-shadow: var(--shadow-sm);
}


.logo {
  font-family: var(--font-mono);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  background: var(--color-primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
  transition: var(--transition-all);
  letter-spacing: -0.5px;
  position: relative;
}

.logo::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--color-primary-gradient);
  transition: width 0.3s ease;
}

.logo:hover::after {
  width: 100%;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: var(--transition-colors);
}

.nav-link:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-input);
}

.nav-link.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-light);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: var(--transition-all);
}

.theme-toggle:hover {
  background: var(--color-bg-input);
  color: var(--color-text-primary);
  transform: rotate(15deg);
}

.theme-toggle:active {
  transform: scale(0.95);
}

/* Mobile Responsive */
@media (max-width: 767px) {
  .navbar {
    padding: 0 var(--space-md);
    height: 56px;
  }

  .logo {
    font-size: var(--font-size-lg);
  }

  .nav-actions {
    gap: var(--space-sm);
  }

  .nav-link span {
    display: none;
  }

  .nav-link {
    padding: var(--space-sm);
  }

  .theme-toggle {
    width: 32px;
    height: 32px;
  }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  .navbar {
    padding: 0 var(--space-lg);
  }
}
</style>
