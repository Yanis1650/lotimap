<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { PlanCollection, LotFeature } from '#shared/lot'
import { isLotFeature } from '#shared/lot'
import type { MapMode } from '~/utils/landscape-layers'

const { data, error, pending, refresh } = await useFetch<PlanCollection>('/api/lots')
const budgetMax = ref(0)
const surfaceMin = ref(0)
const selectedId = ref<string | null>(null)
const mapMode = ref<MapMode>('landscape')
const mapSection = ref<HTMLElement | null>(null)

async function selectFromList(id: string) {
  selectedId.value = id
  await nextTick()
  mapSection.value?.focus({ preventScroll: true })
  mapSection.value?.scrollIntoView({
    block: 'start',
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
  })
}

const allLots = computed(() => data.value?.features.filter(isLotFeature) ?? [])
const filteredLots = computed(() => allLots.value.filter((lot) => {
  const priceOk = budgetMax.value === 0 || lot.properties.price_eur <= budgetMax.value
  return priceOk && lot.properties.area_m2 >= surfaceMin.value
}))
const availableCount = computed(() => filteredLots.value.filter(lot => lot.properties.status === 'available').length)
const selectedLot = computed<LotFeature | null>(() => filteredLots.value.find(lot => lot.id === selectedId.value) ?? null)
const visiblePlan = computed<PlanCollection>(() => ({
  type: 'FeatureCollection',
  features: [
    ...(data.value?.features.filter(feature => !isLotFeature(feature)) ?? []),
    ...filteredLots.value,
  ],
}))
watch(filteredLots, (lots) => {
  if (selectedId.value && !lots.some(lot => lot.id === selectedId.value)) selectedId.value = null
})
</script>

<template>
  <main class="page-container">
    <header class="hero">
      <div>
        <p class="eyebrow">lotimap / Démonstration géomatique</p>
        <h1>Le Clos <em>du Verger</em></h1>
        <p class="hero-description">Un plan fictif pour explorer les lots, leurs surfaces et leurs disponibilités.</p>
        <p class="hero-location">Avranches, Manche · Emprise provisoire illustrative</p>
      </div>
      <div class="hero-count" aria-live="polite">
        <strong>{{ availableCount }}</strong>
        <span>lots disponibles<br>sur {{ allLots.length }} lots fictifs</span>
      </div>
    </header>

    <div v-if="pending" class="page-message" role="status">Chargement du plan…</div>
    <div v-else-if="error" class="page-message" role="alert">
      Le plan est momentanément indisponible.
      <button type="button" @click="refresh()">Réessayer</button>
    </div>
    <div v-else class="explorer">
      <aside class="explorer-sidebar">
        <LotFilters v-model:budget-max="budgetMax" v-model:surface-min="surfaceMin" />
        <div class="legend" aria-label="Légende des statuts">
          <span><i data-status="available" />Disponible</span>
          <span><i data-status="option" />Option</span>
          <span><i data-status="reserved" />Réservé</span>
          <span><i data-status="sold" />Vendu</span>
        </div>
        <LotList :lots="filteredLots" :selected-id="selectedId" @select="selectFromList" />
      </aside>
      <section ref="mapSection" class="map-section" tabindex="-1" aria-label="Carte interactive des lots">
        <div class="map-toolbar">
          <div class="map-mode-switch" role="group" aria-label="Fond du plan">
            <button type="button" :aria-pressed="mapMode === 'landscape'" @click="mapMode = 'landscape'">Plan 2D</button>
            <button type="button" :aria-pressed="mapMode === 'volume'" @click="mapMode = 'volume'">Vue 3D</button>
            <button type="button" :aria-pressed="mapMode === 'orthophoto'" @click="mapMode = 'orthophoto'">Orthophoto IGN</button>
          </div>
          <span>{{ mapMode === 'orthophoto' ? 'Emprise provisoire' : mapMode === 'volume' ? 'Volumes fictifs' : 'Vue 2D illustrative' }}</span>
        </div>
        <ClientOnly>
          <LotMap :collection="visiblePlan" :selected-id="selectedId" :mode="mapMode" @select="selectedId = $event" />
          <template #fallback><div class="map-loading">Chargement de la carte…</div></template>
        </ClientOnly>
        <div class="map-footnote">
          <template v-if="mapMode === 'orthophoto'">Localisation et emprise fictives</template>
          <template v-else-if="mapMode === 'volume'">Volumes et hauteurs fictifs · Terrain plat</template>
          <template v-else>Maisons et plantations illustratives · Contours issus du plan fictif</template>
          · Cliquez sur un lot pour voir sa fiche
        </div>
        <LotDetails v-if="selectedLot" :lot="selectedLot" @close="selectedId = null" />
      </section>
    </div>
    <ProjectGallery />
    <OpenDataPanel v-if="data?.context" :context="data.context" />
  </main>
</template>
