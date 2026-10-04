<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { LotFeature, LotStatus } from '#shared/lot'

const props = defineProps<{ lot: LotFeature }>()
const emit = defineEmits<{ saved: []; unauthorized: [] }>()
const status = ref<LotStatus>(props.lot.properties.status)
const price = ref(props.lot.properties.price_eur)
const busy = ref(false)
const message = ref('')
const changed = computed(() => status.value !== props.lot.properties.status
  || price.value !== props.lot.properties.price_eur)

watch(() => props.lot, (lot) => {
  status.value = lot.properties.status
  price.value = lot.properties.price_eur
})

async function save() {
  if (!changed.value || busy.value) return
  busy.value = true
  message.value = ''
  try {
    await $fetch(`/api/admin/lots/${encodeURIComponent(props.lot.id)}`, {
      method: 'PATCH',
      body: { status: status.value, price_eur: price.value },
    })
    emit('saved')
  } catch (error) {
    const code = error && typeof error === 'object' && 'statusCode' in error
      ? Number(error.statusCode) : 0
    message.value = code === 401 ? 'Session expirée. Reconnectez-vous.' : 'Enregistrement impossible.'
    if (code === 401) emit('unauthorized')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <article class="admin-lot-card" :data-status="lot.properties.status">
    <header class="admin-card-head">
      <div>
        <span class="admin-card-kicker">Lot {{ lot.properties.number ?? '—' }}</span>
        <h2>{{ lot.properties.area_m2.toLocaleString('fr-FR') }} m²</h2>
      </div>
    </header>
    <form class="admin-card-form" @submit.prevent="save">
      <label>
        <span>Statut</span>
        <select v-model="status">
          <option value="available">Disponible</option>
          <option value="option">En option</option>
          <option value="reserved">Réservé</option>
          <option value="sold">Vendu</option>
        </select>
      </label>
      <label>
        <span>Prix indicatif (€)</span>
        <input v-model.number="price" type="number" min="1" step="1" inputmode="numeric" required>
      </label>
      <button type="submit" :disabled="!changed || busy">
        {{ busy ? 'Enregistrement…' : 'Enregistrer' }}
      </button>
    </form>
    <p v-if="message" class="admin-card-message" role="status">{{ message }}</p>
  </article>
</template>
