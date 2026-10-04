<script setup lang="ts">
const props = withDefaults(defineProps<{ inverted?: boolean }>(), { inverted: false })
const variant = computed(() => props.inverted ? 'creme' : 'ardoise')
</script>

<template>
  <NuxtLink class="studio-brand" to="/" aria-label="Drekky Studio, accueil lotimap">
    <img :src="`/branding/drekky-symbole-${variant}.svg`" class="brand-symbol" width="42" height="42" alt="">
    <span class="brand-wordmark">
      <img :src="`/branding/drekky-mot-${variant}.svg`" width="100" height="31" alt="">
      <span>Studio</span>
    </span>
  </NuxtLink>
</template>
