<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
import { useWorkspace } from '../composables/useWorkspace'
const { login, register, startDemo, error: sessionError } = useWorkspace()
const router = useRouter()
const registering = ref(false)
const busy = ref(false)
const showPassword = ref(false)
const error = ref(sessionError.value)
const form = reactive({ username: '', password: '', email: '', first_name: '', last_name: '' })
async function submit() {
  busy.value = true
  error.value = ''
  try {
    if (registering.value) await register({ ...form, username: form.username.trim(), email: form.email.trim(), first_name: form.first_name.trim(), last_name: form.last_name.trim() })
    else await login({ username: form.username.trim(), password: form.password })
    router.replace('/')
  } catch (err) { error.value = err.message }
  finally { busy.value = false }
}
function demo() { startDemo(); router.replace('/') }
function switchMode() { registering.value = !registering.value; error.value = ''; form.password = '' }
</script>

<template>
  <div class="auth-page">
    <section class="auth-story"><a href="/" class="brand"><img src="/favicon.svg" width="38" height="38" alt=""><span>flow.</span></a><div class="auth-story-content"><span class="eyebrow"><span class="live-dot"></span>МЕСТО ДЛЯ ВАЖНОГО</span><h1>Освободите мысли.<br>Поймайте свой<br><em>поток.</em></h1><p>Задачи, идеи и маленькие победы —<br>в одном спокойном пространстве.</p><div class="auth-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="art-leaf leaf-one"></div><div class="art-leaf leaf-two"></div><div class="floating-note"><span class="note-check"><AppIcon name="check" :size="16" /></span><div><strong>Начать с малого</strong><span>Первый шаг уже сделан</span></div><span class="note-star">✦</span></div><div class="art-circle"><AppIcon name="leaf" :size="64" /></div><div class="floating-tag"><AppIcon name="sparkles" :size="16" /> В своём ритме</div><span class="art-plus">+</span></div></div><p class="auth-bottom">Меньше шума. Больше смысла.</p></section>
    <section class="auth-form-side"><div class="auth-top-note">{{ registering ? 'Уже с нами?' : 'Впервые здесь?' }} <button :disabled="busy" @click="switchMode">{{ registering ? 'Войти' : 'Создать аккаунт' }} <AppIcon name="arrow" :size="15" /></button></div><div class="auth-form-wrap"><span class="auth-welcome-icon"><AppIcon :name="registering ? 'leaf' : 'sun'" :size="26" /></span><h2>{{ registering ? 'Начните свою историю' : 'С возвращением' }}<span class="green-text">.</span></h2><p class="muted">{{ registering ? 'Немного о вас — и можно перейти к важному.' : 'Ваши планы на месте. Продолжим?' }}</p><form class="auth-form" @submit.prevent="submit"><fieldset :disabled="busy"><div v-if="registering" class="form-grid"><label class="field">Имя<input v-model="form.first_name" autocomplete="given-name" placeholder="Александр" maxlength="100" required></label><label class="field">Фамилия<input v-model="form.last_name" autocomplete="family-name" placeholder="Иванов" maxlength="100" required></label></div><label class="field">Логин<input v-model="form.username" autocomplete="username" placeholder="Ваш логин" maxlength="100" pattern=".*\S.*" required></label><label v-if="registering" class="field">Email<input v-model="form.email" type="email" autocomplete="email" placeholder="you@example.com" required maxlength="254"></label><label class="field">Пароль<span class="password-field"><input v-model="form.password" :type="showPassword ? 'text' : 'password'" :autocomplete="registering ? 'new-password' : 'current-password'" placeholder="Введите пароль" :minlength="registering ? 8 : 1" maxlength="128" required><button type="button" class="icon-button" :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'" :aria-pressed="showPassword" @click="showPassword = !showPassword"><AppIcon name="eye" :size="18" /></button></span><small v-if="registering" class="muted">Не менее 8 символов</small></label><p v-if="error" class="form-error" role="alert">{{ error }}</p><button class="button primary auth-submit" :disabled="busy"><span v-if="busy" class="spinner"></span>{{ busy ? 'Подождите…' : registering ? 'Создать аккаунт' : 'Войти в пространство' }}<AppIcon v-if="!busy" name="arrow" :size="18" /></button></fieldset></form><div class="auth-divider"><span>или сначала познакомимся</span></div><button class="button secondary demo-button" :disabled="busy" @click="demo"><AppIcon name="sparkles" :size="18" />Посмотреть демо</button><p class="auth-reassurance"><AppIcon name="lock" :size="13" />Ваши задачи видны только вам</p></div><div class="auth-footer">FLOW — ВАШ ЛИЧНЫЙ РИТМ</div></section>
  </div>
</template>
