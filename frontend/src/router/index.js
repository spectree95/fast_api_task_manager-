import { createRouter, createWebHistory } from 'vue-router'
import { useWorkspace } from '../composables/useWorkspace'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: () => import('../views/AuthView.vue'), meta: { title: 'Вход' } },
    {
      path: '/', component: () => import('../components/AppLayout.vue'),
      children: [
        { path: '', name: 'overview', component: () => import('../views/WorkspaceView.vue'), meta: { title: 'Обзор' } },
        { path: 'tasks', name: 'tasks', component: () => import('../views/WorkspaceView.vue'), meta: { title: 'Мои задачи' } },
        { path: 'completed', name: 'completed', component: () => import('../views/WorkspaceView.vue'), meta: { title: 'Завершённые' } },
        { path: 'settings', name: 'settings', component: () => import('../views/ProfileView.vue'), meta: { title: 'Настройки' } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  const workspace = useWorkspace()
  await workspace.restore()
  if (!workspace.user.value && to.name !== 'login') return { name: 'login' }
  if (workspace.user.value && to.name === 'login') return { name: 'overview' }
  document.title = `${to.meta.title || 'Задачи'} — Flow`
})

export default router
