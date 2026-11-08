import { computed, ref } from 'vue'
import { request, tokenStore } from '../lib/api'
import { demoTasks, taskStats } from '../lib/tasks'

const user = ref(null)
const tasks = ref([])
const isDemo = ref(false)
const loading = ref(false)
const error = ref('')
const notice = ref('')
const pending = ref(new Set())
let restoration
let noticeTimer
let sessionVersion = 0
const DEMO_KEY = 'flow.demo.v1'

function notify(message) {
  notice.value = message
  clearTimeout(noticeTimer)
  noticeTimer = setTimeout(() => { notice.value = '' }, 4000)
}

function persistDemo() {
  try { localStorage.setItem(DEMO_KEY, JSON.stringify({ user: user.value, tasks: tasks.value })) }
  catch { notify('Хранилище браузера недоступно. Изменения сохранятся только до закрытия страницы.') }
}

function logout() {
  sessionVersion++
  tokenStore.clear()
  sessionStorage.removeItem('flow.demo-active')
  user.value = null
  tasks.value = []
  isDemo.value = false
  error.value = ''
  loading.value = false
  pending.value = new Set()
}

async function restore() {
  if (restoration) return restoration
  restoration = (async () => {
    if (sessionStorage.getItem('flow.demo-active')) { startDemo(); return }
    if (tokenStore.get()) {
      try { user.value = await request('/users/me') }
      catch (err) {
        if (err.status === 401) tokenStore.clear()
        error.value = err.message
      }
    }
  })()
  return restoration
}

function startDemo() {
  logout()
  let saved
  try { saved = JSON.parse(localStorage.getItem(DEMO_KEY)) } catch { /* Invalid storage starts a fresh demo. */ }
  isDemo.value = true
  user.value = saved?.user || { id: 0, first_name: 'Александр', last_name: '', username: 'demo', email: 'demo@example.com' }
  tasks.value = Array.isArray(saved?.tasks) && saved.tasks.every((t) => typeof t.title === 'string' && typeof t.completed === 'boolean' && Number.isFinite(t.id) && !Number.isNaN(Date.parse(t.created_at))) ? saved.tasks : demoTasks()
  sessionStorage.setItem('flow.demo-active', '1')
  persistDemo()
}

async function login(credentials) {
  logout()
  const data = await request('/users/login', { method: 'POST', body: credentials, form: true })
  tokenStore.set(data.access_token)
  try { user.value = await request('/users/me') }
  catch (err) { tokenStore.clear(); throw err }
}

async function register(values) {
  await request('/users/', { method: 'POST', body: values })
  try { await login({ username: values.username, password: values.password }) }
  catch { throw new Error('Аккаунт создан. Теперь войдите с вашим логином и паролем.') }
}

async function loadTasks() {
  if (isDemo.value || loading.value || !user.value) return
  const version = sessionVersion
  loading.value = true
  error.value = ''
  try {
    const result = []
    let total = 0
    do {
      const page = await request(`/tasks?skip=${result.length}&limit=100&sort=created_at&order=desc`)
      if (version !== sessionVersion) return
      total = page.total
      result.push(...page.items)
      if (!page.items.length) break
    } while (result.length < total)
    tasks.value = [...new Map(result.map((task) => [task.id, task])).values()]
  } catch (err) { if (version === sessionVersion) error.value = err.message }
  finally { if (version === sessionVersion) loading.value = false }
}

async function saveTask(values, id = null) {
  const payload = { title: values.title.trim(), description: values.description.trim() }
  if (!payload.title) throw new Error('Введите название задачи.')
  let task
  if (isDemo.value) {
    const existing = tasks.value.find((item) => item.id === id)
    task = { ...existing, ...payload, id: id ?? Math.max(0, ...tasks.value.map((item) => item.id)) + 1, completed: existing?.completed ?? false, created_at: existing?.created_at || new Date().toISOString(), updated_at: new Date().toISOString(), owner_id: 0 }
  } else {
    task = await request(id === null ? '/tasks/create' : `/tasks/${id}`, { method: id === null ? 'POST' : 'PATCH', body: payload })
  }
  tasks.value = id === null ? [task, ...tasks.value] : tasks.value.map((item) => item.id === id ? task : item)
  if (isDemo.value) persistDemo()
  notify(id === null ? 'Задача добавлена. Первый шаг сделан!' : 'Изменения сохранены')
}

async function toggleTask(task) {
  if (pending.value.has(task.id)) return
  pending.value.add(task.id)
  try {
    const updated = isDemo.value ? { ...task, completed: !task.completed, updated_at: new Date().toISOString() } : await request(`/tasks/${task.id}`, { method: 'PATCH', body: { completed: !task.completed } })
    tasks.value = tasks.value.map((item) => item.id === task.id ? updated : item)
    if (isDemo.value) persistDemo()
    notify(updated.completed ? 'Ещё одно дело сделано. Отличная работа!' : 'Задача снова в работе')
  } catch (err) { notify(err.message) }
  finally { pending.value.delete(task.id) }
}

async function deleteTask(id) {
  if (!isDemo.value) await request(`/tasks/${id}`, { method: 'DELETE' })
  tasks.value = tasks.value.filter((task) => task.id !== id)
  if (isDemo.value) persistDemo()
  notify('Задача удалена')
}

async function updateProfile(values) {
  const payload = { first_name: values.first_name.trim(), last_name: values.last_name.trim() }
  if (values.username.trim() !== user.value.username) payload.username = values.username.trim()
  user.value = isDemo.value ? { ...user.value, ...payload } : await request('/users/', { method: 'PATCH', body: payload })
  if (isDemo.value) persistDemo()
  notify('Профиль обновлён')
}

export function useWorkspace() {
  return { user, tasks, isDemo, loading, error, notice, pending, stats: computed(() => taskStats(tasks.value)), restore, startDemo, login, register, logout, loadTasks, saveTask, toggleTask, deleteTask, updateProfile, notify }
}
