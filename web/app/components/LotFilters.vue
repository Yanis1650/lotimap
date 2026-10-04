<script setup lang="ts">
defineProps<{ budgetMax: number; surfaceMin: number }>()
const emit = defineEmits<{
  'update:budgetMax': [value: number]
  'update:surfaceMin': [value: number]
}>()

function selectedNumber(event: Event): number {
  return Number((event.target as HTMLSelectElement).value)
}
</script>

<template>
  <section class="filters" aria-labelledby="filters-title">
    <div class="section-heading">
      <h2 id="filters-title">Affiner la recherche</h2>
    </div>
    <div class="filter-fields">
      <label class="filter-field">
        <span>Budget maximum</span>
        <select :value="budgetMax" @change="emit('update:budgetMax', selectedNumber($event))">
          <option :value="0">Sans limite</option>
          <option :value="70000">70 000 €</option>
          <option :value="80000">80 000 €</option>
          <option :value="90000">90 000 €</option>
          <option :value="100000">100 000 €</option>
        </select>
      </label>
      <label class="filter-field">
        <span>Surface minimale</span>
        <select :value="surfaceMin" @change="emit('update:surfaceMin', selectedNumber($event))">
          <option :value="0">Sans limite</option>
          <option :value="700">700 m²</option>
          <option :value="800">800 m²</option>
          <option :value="900">900 m²</option>
          <option :value="1000">1 000 m²</option>
        </select>
      </label>
    </div>
  </section>
</template>
