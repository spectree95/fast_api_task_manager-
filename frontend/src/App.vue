<script setup>
import { RouterView } from 'vue-router'
import { useWorkspace } from './composables/useWorkspace'
const { notice } = useWorkspace()
</script>

<template>
  <RouterView />
  <Transition name="toast">
    <div v-if="notice" class="toast" role="status"><span class="toast-dot"></span>{{ notice }}</div>
  </Transition>
</template>
