<script setup>
import { reactive, ref } from 'vue'
import AppIcon from '../components/AppIcon.vue'
import { useWorkspace } from '../composables/useWorkspace'
const { user, isDemo, tasks, updateProfile, notify } = useWorkspace()
const form = reactive({ first_name: user.value.first_name, last_name: user.value.last_name, username: user.value.username })
const busy = ref(false)
const error = ref('')
async function save() {
  busy.value = true
  error.value = ''
  try { await updateProfile(form) } catch (err) { error.value = err.message } finally { busy.value = false }
}
function exportTasks() {
  const blob = new Blob([JSON.stringify({ exported_at: new Date().toISOString(), tasks: tasks.value }, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `flow-tasks-${new Date().toISOString().slice(0, 10)}.json`
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
  notify('Задачи экспортированы')
}
</script>

<template>
  <div class="page-heading"><div><p class="page-eyebrow">ПРОСТРАНСТВО, В КОТОРОМ ВЫ — ЭТО ВЫ</p><h1>Настройки<span class="green-text">.</span></h1><p class="muted">Немного личного. Всё по-вашему.</p></div></div>
  <div class="settings-grid"><section class="panel profile-panel"><div class="section-heading"><div><h2>Личный профиль</h2><p class="muted">Так мы будем обращаться к вам.</p></div><span class="avatar large">{{ (user.first_name || user.username).slice(0, 1).toUpperCase() }}</span></div><form @submit.prevent="save"><fieldset :disabled="busy"><div class="form-grid"><label class="field">Имя<input v-model="form.first_name" autocomplete="given-name" required maxlength="100" pattern=".*\S.*"></label><label class="field">Фамилия<input v-model="form.last_name" autocomplete="family-name" maxlength="100"></label></div><label class="field">Логин<input v-model="form.username" autocomplete="username" required maxlength="100" pattern=".*\S.*"></label><label class="field">Email<input :value="user.email" type="email" disabled><small class="muted">Email привязан к вашему аккаунту и не редактируется.</small></label><p v-if="error" class="form-error" role="alert">{{ error }}</p><button class="button primary" :disabled="busy"><span v-if="busy" class="spinner"></span>{{ busy ? 'Сохраняем…' : 'Сохранить изменения' }}</button></fieldset></form></section><div class="settings-aside"><section class="panel data-panel"><span class="icon-tile"><AppIcon name="download" /></span><h2>Ваши задачи — с вами</h2><p class="muted">Скачайте все задачи в формате JSON, чтобы сохранить личную копию.</p><button class="button secondary" @click="exportTasks"><AppIcon name="download" :size="17" />Экспортировать задачи</button></section><section class="settings-note"><AppIcon name="lock" :size="19" /><div><strong>{{ isDemo ? 'Вы в деморежиме' : 'Личное остаётся личным' }}</strong><p>{{ isDemo ? 'Данные этого пространства хранятся только в вашем браузере. Для синхронизации создайте аккаунт.' : 'Задачи доступны только после входа в ваш аккаунт. После работы на общем компьютере не забудьте выйти.' }}</p></div></section></div></div>
</template>
