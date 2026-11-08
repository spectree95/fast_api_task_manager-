<script setup>
defineProps({ name: { type: String, default: 'grid' }, size: { type: [Number, String], default: 20 } })
const paths = {
  grid: 'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  tasks: 'M9 5h12 M9 12h12 M9 19h12 M3 5l1 1 2-2 M3 12l1 1 2-2 M3 19l1 1 2-2',
  check: 'M5 12l4 4L19 6',
  circle: 'M22 11.1V12a10 10 0 1 1-5.9-9.1 M22 4 12 14.01l-3-3',
  sliders: 'M4 7h9 M17 7h3 M4 17h3 M11 17h9 M13 4v6 M7 14v6',
  search: 'M21 21l-5-5 M10.5 3a7.5 7.5 0 1 0 0 15 7.5 7.5 0 0 0 0-15',
  plus: 'M12 5v14 M5 12h14',
  arrow: 'M5 12h14 M13 6l6 6-6 6',
  chevron: 'm9 5 7 7-7 7',
  down: 'm6 9 6 6 6-6',
  close: 'm6 6 12 12 M6 18 18 6',
  calendar: 'M5 5h14a2 2 0 0 1 2 2v13H3V7a2 2 0 0 1 2-2 M7 3v4 M17 3v4 M3 11h18 M7 15h2 M13 15h2',
  clock: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M12 7v5l3 2',
  trend: 'm3 17 6-6 4 4 8-10 M15 5h6v6',
  sparkles: 'm12 3 2.4 6.6L21 12l-6.6 2.4L12 21l-2.4-6.6L3 12l6.6-2.4L12 3 M20 2v4 M18 4h4',
  logout: 'M9 4H4v16h5 M9 12h12 M17 8l4 4-4 4',
  list: 'M8 6h13 M8 12h13 M8 18h13 M3 6h.01 M3 12h.01 M3 18h.01',
  board: 'M3 4h7v16H3z M14 4h7v16h-7z',
  edit: 'm16 3 5 5-12 12H4v-5L16 3 M13 6l5 5',
  trash: 'M3 6h18 M9 6V3h6v3 M5 6l1 15h12l1-15 M10 10v7 M14 10v7',
  refresh: 'M20 7a9 9 0 1 0 1 8 M20 3v5h-5',
  sun: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8 M12 2v2 M12 20v2 M2 12h2 M20 12h2 M5 5l1.5 1.5 M17.5 17.5l1.5 1.5 M5 19l1.5-1.5 M17.5 6.5 19 5',
  menu: 'M4 6h16 M4 12h16 M4 18h16',
  leaf: 'M20 3C4 1 1 10 6 17c7 5 16 2 14-14 M5 20 16 9',
  eye: 'M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12 M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6',
  lock: 'M5 10h14v11H5z M8 10V6a4 4 0 0 1 8 0v4',
  download: 'M12 3v12 M7 10l5 5 5-5 M4 16v5h16v-5',
}
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="paths[name] || paths.grid" /></svg>
</template>
