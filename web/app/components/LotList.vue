<script setup lang="ts">
import type { LotFeature } from '#shared/lot'

defineProps<{ lots: LotFeature[]; selectedId: string | null }>()
defineEmits<{ select: [id: string] }>()

const statusLabels = {
  available: 'Disponible',
  option: 'En option',
  reserved: 'Réservé',
  sold: 'Vendu',
}
const money = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
</script>

<template>
  <section class="lot-list" aria-labelledby="lot-list-title">
    <div class="section-heading">
      <h2 id="lot-list-title">Les lots</h2>
      <span>{{ lots.length.toString().padStart(2, '0') }}</span>
    </div>
    <p v-if="!lots.length" class="empty-state">Aucun lot ne correspond à ces critères.</p>
    <div v-else class="lot-list-items">
      <button
        v-for="lot in lots"
        :key="lot.id"
        type="button"
        class="lot-row"
        :class="{ 'is-selected': selectedId === lot.id }"
        :aria-pressed="selectedId === lot.id"
        @click="$emit('select', lot.id)"
      >
        <span class="lot-row-number">{{ lot.properties.number ?? '—' }}</span>
        <span class="lot-row-main">
          <strong>Lot {{ lot.properties.number ?? 'sans numéro' }}</strong>
          <small>{{ lot.properties.area_m2.toLocaleString('fr-FR') }} m² · {{ statusLabels[lot.properties.status] }}</small>
        </span>
        <span class="lot-row-price">{{ money.format(lot.properties.price_eur) }}</span>
      </button>
    </div>
  </section>
</template>
