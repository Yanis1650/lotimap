<script setup lang="ts">
defineProps<{ volume: boolean }>()
const emit = defineEmits<{ rotate: [direction: -1 | 1]; reset: [] }>()
</script>

<template>
  <div class="map-view-controls" role="group" aria-label="Orientation de la carte">
    <button v-if="volume" type="button" aria-label="Tourner la vue à gauche" title="Tourner à gauche" @click="emit('rotate', -1)">↶</button>
    <button type="button" @click="emit('reset')">Recentrer</button>
    <button v-if="volume" type="button" aria-label="Tourner la vue à droite" title="Tourner à droite" @click="emit('rotate', 1)">↷</button>
  </div>
</template>
