<script setup>
import {ref} from "vue"
const count = ref(0)

const name = "Nurbol"
</script>

<template>
  <h1>Task manager</h1>
  <h2>{{count}}</h2>

  <button @click="count++">
    +1
  </button>
  <p>
    Hello, {{name}}!
  </p>
</template>

<style scoped></style>
