<script setup>
import { nextTick, reactive, ref } from 'vue'
import AppIcon from './AppIcon.vue'
import { useWorkspace } from '../composables/useWorkspace'
const { saveTask, deleteTask } = useWorkspace()
const dialog = ref(null)
const form = reactive({ title: '', description: '' })
const selected = ref(null)
const mode = ref('edit')
const busy = ref(false)
const error = ref('')

async function open(task = null, action = 'edit') {
  selected.value = task
  mode.value = action
  form.title = task?.title || ''
  form.description = task?.description || ''
  error.value = ''
  await nextTick()
  dialog.value.showModal()
}
function close() { if (!busy.value) dialog.value.close() }
async function submit() {
  busy.value = true
  error.value = ''
  try {
    if (mode.value === 'delete') await deleteTask(selected.value.id)
    else await saveTask(form, selected.value?.id ?? null)
    dialog.value.close()
  } catch (err) { error.value = err.message }
  finally { busy.value = false }
}
defineExpose({ open })
</script>

<template>
  <dialog ref="dialog" class="modal" aria-labelledby="editor-title" @cancel="busy && $event.preventDefault()" @click="($event.target === dialog) && close()">
    <form @submit.prevent="submit">
      <div class="modal-heading"><div class="icon-tile" :class="{ red: mode === 'delete' }"><AppIcon :name="mode === 'delete' ? 'trash' : 'edit'" /></div><button type="button" class="icon-button" aria-label="Закрыть" :disabled="busy" @click="close"><AppIcon name="close" /></button></div>
      <h2 id="editor-title">{{ mode === 'delete' ? 'Удалить задачу?' : selected ? 'Редактировать задачу' : 'Маленький шаг к большой цели' }}</h2>
      <p class="muted modal-description">{{ mode === 'delete' ? `«${selected?.title}» будет удалена. Отменить это действие нельзя.` : 'Освободите мысли. Всё важное останется здесь.' }}</p>
      <template v-if="mode !== 'delete'">
        <label class="field">Название задачи <span class="required">*</span><input v-model="form.title" placeholder="Что хотите сделать?" required maxlength="255" autofocus :disabled="busy"></label>
        <label class="field">Описание <span class="optional">необязательно</span><textarea v-model="form.description" placeholder="Детали, идеи или первый шаг…" rows="5" maxlength="1000" :disabled="busy"></textarea><span class="char-count">{{ form.description.length }} / 1000</span></label>
      </template>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <div class="modal-actions"><button type="button" class="button secondary" :disabled="busy" @click="close">Отмена</button><button class="button" :class="mode === 'delete' ? 'danger' : 'primary'" :disabled="busy || (mode !== 'delete' && !form.title.trim())"><span v-if="busy" class="spinner"></span>{{ busy ? 'Сохраняем…' : mode === 'delete' ? 'Удалить задачу' : selected ? 'Сохранить изменения' : 'Создать задачу' }}<AppIcon v-if="!busy && mode !== 'delete'" name="arrow" :size="17" /></button></div>
    </form>
  </dialog>
</template>
