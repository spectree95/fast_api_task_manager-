import { test } from 'node:test'
import assert from 'node:assert/strict'
import { filterTasks, taskStats } from './tasks.js'

const tasks = [
  { id: 1, title: 'Бета', description: 'План проекта', completed: false, created_at: '2026-01-01T00:00:00Z' },
  { id: 2, title: 'Альфа', description: '', completed: true, created_at: '2026-01-02T00:00:00Z' },
  { id: 3, title: 'Гамма', description: null, completed: false, created_at: '2026-01-03T00:00:00Z' },
]

test('search is case-insensitive, trims whitespace and includes description', () => {
  assert.deepEqual(filterTasks(tasks, { query: ' ПЛАН ' }).map(t => t.id), [1])
  assert.deepEqual(filterTasks(tasks, { query: 'аЛьФа' }).map(t => t.id), [2])
  assert.equal(filterTasks(tasks, { query: 'нет результата' }).length, 0)
})

test('status, search and sorting compose without mutating source', () => {
  assert.deepEqual(filterTasks(tasks, { status: 'active', sort: 'oldest' }).map(t => t.id), [1, 3])
  assert.deepEqual(filterTasks(tasks, { status: 'completed', query: 'альфа' }).map(t => t.id), [2])
  assert.deepEqual(filterTasks(tasks, { sort: 'title' }).map(t => t.id), [2, 1, 3])
  assert.deepEqual(filterTasks(tasks).map(t => t.id), [3, 2, 1])
  assert.deepEqual(tasks.map(t => t.id), [1, 2, 3])
})

test('statistics handle empty, partial and fully completed lists', () => {
  assert.deepEqual(taskStats([]), { total: 0, completed: 0, active: 0, percent: 0 })
  assert.deepEqual(taskStats(tasks), { total: 3, completed: 1, active: 2, percent: 33 })
  assert.equal(taskStats(tasks.map(t => ({ ...t, completed: true }))).percent, 100)
})
