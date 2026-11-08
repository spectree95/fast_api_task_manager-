const TOKEN_KEY = 'flow.access-token'
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')

export const tokenStore = {
  get: () => sessionStorage.getItem(TOKEN_KEY),
  set: (token) => sessionStorage.setItem(TOKEN_KEY, token),
  clear: () => sessionStorage.removeItem(TOKEN_KEY),
}

const messages = {
  'Invalid username or password.': 'Неверный логин или пароль.',
  'Username already exists.': 'Этот логин уже занят.',
  'This email address is already in use.': 'Этот email уже зарегистрирован.',
  'Task not found': 'Задача не найдена. Обновите список.',
}

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status }
}

export async function request(path, { method = 'GET', body, form = false } = {}) {
  const headers = { Accept: 'application/json' }
  const token = tokenStore.get()
  if (token) headers.Authorization = `Bearer ${token}`
  if (body) headers['Content-Type'] = form ? 'application/x-www-form-urlencoded' : 'application/json'
  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method, headers, signal: AbortSignal.timeout(15000),
      body: body ? (form ? new URLSearchParams(body) : JSON.stringify(body)) : undefined,
    })
  } catch {
    throw new ApiError('Не удалось связаться с сервером. Проверьте подключение и попробуйте снова.', 0)
  }
  if (response.status === 204) return null
  const data = await response.json().catch(() => null)
  if (!response.ok) {
    let message = messages[data?.detail] || (typeof data?.detail === 'string' ? data.detail : '')
    if (response.status >= 500) message = 'Сервер временно недоступен. Попробуйте ещё раз.'
    if (response.status === 422) message = 'Проверьте введённые данные и заполните обязательные поля.'
    if (response.status === 401 && path !== '/users/login') {
      window.dispatchEvent(new Event('flow:unauthorized'))
      message = 'Сессия истекла. Войдите в аккаунт снова.'
    }
    throw new ApiError(message || 'Не удалось выполнить действие. Попробуйте снова.', response.status)
  }
  return data
}
