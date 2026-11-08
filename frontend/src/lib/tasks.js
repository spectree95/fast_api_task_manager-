export function filterTasks(tasks, { query = '', status = 'all', sort = 'newest' } = {}) {
  const search = query.trim().toLocaleLowerCase('ru')
  return tasks.filter((task) => {
    const matches = `${task.title} ${task.description || ''}`.toLocaleLowerCase('ru').includes(search)
    return matches && (status === 'all' || task.completed === (status === 'completed'))
  }).sort((a, b) => {
    if (sort === 'title') return a.title.localeCompare(b.title, 'ru')
    if (sort === 'oldest') return new Date(a.created_at) - new Date(b.created_at) || a.id - b.id
    return new Date(b.created_at) - new Date(a.created_at) || b.id - a.id
  })
}

export function taskStats(tasks) {
  const total = tasks.length
  const completed = tasks.filter((task) => task.completed).length
  return { total, completed, active: total - completed, percent: total ? Math.round(completed / total * 100) : 0 }
}

export function formatDate(value, options = {}) {
  return new Intl.DateTimeFormat('ru-RU', { day: 'numeric', month: 'short', ...options }).format(new Date(value))
}

export function demoTasks() {
  const rows = [
    ['Собрать идеи для нового проекта', 'Выписать первые мысли, найти вдохновение и определить, с чего хочется начать.', false],
    ['Продумать структуру приложения', 'Определить основные экраны и путь пользователя. Главное — простота и удобство.', false],
    ['Навести порядок в рабочем пространстве', 'Закрыть лишние вкладки, разобрать заметки и освободить место для новых идей.', false],
    ['Прочитать главу книги', 'Выделить полчаса без уведомлений. Сохранить интересные мысли в заметки.', false],
    ['Составить план на неделю', 'Выбрать три главные цели и оставить время для себя.', true],
    ['Подготовить рабочее окружение', 'Настроить редактор, создать репозиторий и запустить проект.', true],
    ['Разобрать входящие', 'Ответить на важные сообщения и сохранить то, к чему нужно вернуться.', true],
    ['Записать цели месяца', 'Подумать, что действительно важно, и превратить идеи в конкретные шаги.', true],
  ]
  return rows.map(([title, description, completed], index) => {
    const date = new Date()
    date.setDate(date.getDate() - Math.floor(index / 2))
    return { id: index + 1, title, description, completed, created_at: date.toISOString(), updated_at: date.toISOString(), owner_id: 0 }
  })
}
