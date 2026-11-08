<script setup>
import AppIcon from './AppIcon.vue'
import { formatDate } from '../lib/tasks'
import { useWorkspace } from '../composables/useWorkspace'
defineProps({ task: { type: Object, required: true }, board: Boolean })
defineEmits(['edit', 'delete'])
const { toggleTask, pending } = useWorkspace()
</script>

<template>
  <article class="task-row" :class="{ 'is-completed': task.completed, 'task-card': board }">
    <button class="task-check" :class="{ checked: task.completed }" :aria-label="task.completed ? `Вернуть в работу: ${task.title}` : `Завершить: ${task.title}`" :aria-pressed="task.completed" :disabled="pending.has(task.id)" @click="toggleTask(task)"><span v-if="pending.has(task.id)" class="spinner"></span><AppIcon v-else-if="task.completed" name="check" :size="14" /></button>
    <button class="task-content" @click="$emit('edit', task)"><span class="task-title">{{ task.title }}</span><span class="task-description">{{ task.description || 'Добавьте детали, чтобы было проще начать' }}</span></button>
    <span class="status-pill" :class="task.completed ? 'green' : 'amber'"><span></span>{{ task.completed ? 'Готово' : 'В работе' }}</span>
    <span class="task-date" :title="`Создана ${formatDate(task.created_at, { year: 'numeric' })}`"><AppIcon name="calendar" :size="14" />{{ formatDate(task.created_at) }}</span>
    <div class="task-actions"><button class="icon-button" aria-label="Редактировать задачу" @click="$emit('edit', task)"><AppIcon name="edit" :size="16" /></button><button class="icon-button delete-button" aria-label="Удалить задачу" @click="$emit('delete', task)"><AppIcon name="trash" :size="16" /></button></div>
  </article>
</template>
