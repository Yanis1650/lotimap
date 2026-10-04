<script setup lang="ts">
import { ref, watch } from 'vue'
import type { LotFeature } from '#shared/lot'

const props = defineProps<{ lot: LotFeature }>()
defineEmits<{ close: [] }>()

const interestMessage = ref('')
watch(() => props.lot.id, () => { interestMessage.value = '' })

const labels = {
  available: 'Disponible',
  option: 'En option',
  reserved: 'Réservé',
  sold: 'Vendu',
}
const money = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 })
</script>

<template>
  <section class="lot-details" aria-label="Détail du lot sélectionné">
    <button type="button" class="detail-close" aria-label="Fermer la fiche" @click="$emit('close')">×</button>
    <p class="eyebrow">Le Clos du Verger · Lot {{ lot.properties.number ?? '—' }}</p>
    <h2>Le lot en détail</h2>
    <span class="status-pill" :data-status="lot.properties.status">{{ labels[lot.properties.status] }}</span>
    <dl class="detail-grid">
      <div><dt>Surface</dt><dd>{{ lot.properties.area_m2.toLocaleString('fr-FR') }} m²</dd></div>
      <div><dt>Prix indicatif</dt><dd>{{ money.format(lot.properties.price_eur) }}</dd></div>
      <div><dt>Prix au m²</dt><dd>{{ money.format(lot.properties.price_eur / lot.properties.area_m2) }}</dd></div>
      <div><dt>Zone PLU</dt><dd>{{ lot.properties.plu_zone ?? 'Non disponible' }}</dd></div>
    </dl>
    <p v-if="lot.properties.plu_description" class="plu-description">{{ lot.properties.plu_description }} · Emprise provisoire.</p>
    <button type="button" class="interest-button" @click="interestMessage = 'Démonstration uniquement : aucune donnée n’est collectée.'">
      Je suis intéressé <span aria-hidden="true">↗</span>
    </button>
    <p v-if="interestMessage" class="interest-note" role="status">{{ interestMessage }}</p>
    <p class="detail-disclaimer">Lot, prix et disponibilité fictifs. Ce plan ne représente aucune offre immobilière.</p>
  </section>
</template>
