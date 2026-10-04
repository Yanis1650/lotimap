<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { PlanCollection, LotFeature } from '#shared/lot'
import { isLotFeature } from '#shared/lot'

const { data, error, pending, refresh } = await useFetch<PlanCollection>('/api/lots')
const budgetMax = ref(0)
const surfaceMin = ref(0)
const selectedId = ref<string | null>(null)

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
        <LotList :lots="filteredLots" :selected-id="selectedId" @select="selectedId = $event" />
      </aside>
      <section class="map-section" aria-label="Carte interactive des lots">
        <div class="map-toolbar"><span>Plan interactif</span><span>Orthophoto IGN</span></div>
        <ClientOnly>
          <LotMap :collection="visiblePlan" :selected-id="selectedId" @select="selectedId = $event" />
          <template #fallback><div class="map-loading">Chargement de la carte…</div></template>
        </ClientOnly>
        <div class="map-footnote">Localisation et emprise fictives · Cliquez sur un lot pour voir sa fiche</div>
        <LotDetails v-if="selectedLot" :lot="selectedLot" @close="selectedId = null" />
      </section>
    </div>
    <OpenDataPanel v-if="data?.context" :context="data.context" />
  </main>
</template>
