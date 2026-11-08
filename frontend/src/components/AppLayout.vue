<script setup>
import { computed, onMounted, onUnmounted, provide, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import AppIcon from './AppIcon.vue'
import TaskEditor from './TaskEditor.vue'
import { useWorkspace } from '../composables/useWorkspace'
const { user, stats, isDemo, logout, loadTasks, notify } = useWorkspace()
const route = useRoute()
const router = useRouter()
const editor = ref(null)
const mobileNav = ref(false)
const query = ref('')
const searchInput = ref(null)
const initials = computed(() => `${user.value?.first_name?.[0] || user.value?.username?.[0] || ''}${user.value?.last_name?.[0] || ''}`.toUpperCase())
const today = new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date())
const navigation = [{ name: 'overview', label: 'Обзор', icon: 'grid' }, { name: 'tasks', label: 'Мои задачи', icon: 'tasks' }, { name: 'completed', label: 'Завершённые', icon: 'circle' }]
provide('taskEditor', (task, action) => editor.value.open(task, action))
provide('searchQuery', query)
function signOut() { logout(); router.replace('/login') }
function expired() { signOut(); notify('Сессия истекла. Войдите снова.') }
function shortcuts(event) {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); searchInput.value?.focus() }
  if (event.key === 'Escape') mobileNav.value = false
}
function search() { if (route.name !== 'tasks') router.push('/tasks') }
watch(() => route.path, () => { mobileNav.value = false })
onMounted(() => { loadTasks(); window.addEventListener('flow:unauthorized', expired); window.addEventListener('keydown', shortcuts) })
onUnmounted(() => { window.removeEventListener('flow:unauthorized', expired); window.removeEventListener('keydown', shortcuts) })
</script>

<template>
  <div class="app-shell">
    <button v-if="mobileNav" class="sidebar-backdrop" aria-label="Закрыть меню" @click="mobileNav = false"></button>
    <aside class="sidebar" :class="{ 'is-open': mobileNav }">
      <RouterLink class="brand" to="/" aria-label="Flow — главная"><img src="/favicon.svg" width="36" height="36" alt=""><span>flow<span class="brand-dot">.</span></span></RouterLink>
      <div class="workspace-switch"><span class="workspace-avatar"><AppIcon name="leaf" :size="18" /></span><div><strong>Моё пространство</strong><small>Личный аккаунт</small></div><span class="workspace-dot"></span></div>
      <p class="nav-label">РАБОЧЕЕ ПРОСТРАНСТВО</p>
      <nav aria-label="Основная навигация"><RouterLink v-for="item in navigation" :key="item.name" :to="{ name: item.name }" class="nav-link" :class="{ active: route.name === item.name }"><AppIcon :name="item.icon" :size="19" /><span>{{ item.label }}</span><span v-if="item.name === 'tasks'" class="nav-count">{{ stats.active }}</span></RouterLink></nav>
      <div class="sidebar-bottom"><div class="sidebar-tip"><span class="tip-icon"><AppIcon name="sparkles" :size="20" /></span><strong>В своём ритме</strong><p>Большие цели начинаются<br>с маленьких шагов.</p><button @click="editor.open()">Сделать первый шаг <AppIcon name="arrow" :size="15" /></button></div><RouterLink to="/settings" class="nav-link" :class="{ active: route.name === 'settings' }"><AppIcon name="sliders" :size="19" /><span>Настройки</span></RouterLink><div class="sidebar-profile"><RouterLink to="/settings" class="profile-link"><span class="avatar">{{ initials }}</span><span><strong>{{ user?.first_name || user?.username }}</strong><small>{{ isDemo ? 'Демоаккаунт' : '@' + user?.username }}</small></span></RouterLink><button class="icon-button" aria-label="Выйти из аккаунта" @click="signOut"><AppIcon name="logout" :size="18" /></button></div></div>
    </aside>
    <div class="main-shell">
      <header class="topbar"><div class="breadcrumb"><button class="icon-button mobile-menu" aria-label="Открыть меню" :aria-expanded="mobileNav" @click="mobileNav = !mobileNav"><AppIcon name="menu" /></button><span>Моё пространство</span><AppIcon name="chevron" :size="13" /><strong>{{ route.meta.title }}</strong></div><div class="topbar-right"><form class="global-search" role="search" @submit.prevent="search"><AppIcon name="search" :size="17" /><input ref="searchInput" v-model="query" type="search" aria-label="Поиск задач" placeholder="Найти задачу…" @input="search"><kbd>Ctrl K</kbd></form><span class="topbar-divider"></span><RouterLink to="/settings" class="avatar small" aria-label="Открыть профиль">{{ initials }}</RouterLink></div></header>
      <div v-if="isDemo" class="demo-banner"><span><span class="live-dot"></span>Деморежим <span class="demo-description">· Изменения сохраняются в этом браузере</span></span><button @click="signOut">Войти в аккаунт <AppIcon name="arrow" :size="14" /></button></div>
      <main id="main-content" class="main-content"><RouterView /></main>
      <footer class="app-footer"><span>Меньше шума. Больше смысла.</span><span>{{ today }}</span></footer>
    </div>
    <TaskEditor ref="editor" />
  </div>
</template>
