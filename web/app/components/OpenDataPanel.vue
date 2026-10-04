<script setup lang="ts">
import { computed } from 'vue'
import type { OpenDataContext } from '#shared/lot'

const props = defineProps<{ context: OpenDataContext }>()
const money = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 })
const formatDate = (value: string) => new Intl.DateTimeFormat('fr-FR', {
  day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
}).format(new Date(`${value}T00:00:00Z`)).replace(/^1 /, '1er ')
const consultedOn = computed(() => formatDate(props.context.generated_on))
const documentDates = computed(() => props.context.plu_document_dates.map(value =>
  formatDate(`${value.slice(0, 4)}-${value.slice(4, 6)}-${value.slice(6, 8)}`),
).join(', '))
const period = computed(() => `${props.context.dvf.years[0]}–${props.context.dvf.years.at(-1)}`)
</script>

<template>
  <section id="territorial-context" class="territorial-context" aria-labelledby="context-title">
    <header class="context-heading">
      <p class="eyebrow">Données ouvertes / {{ context.commune_name }}</p>
      <h2 id="context-title">Le contexte du territoire.</h2>
      <p>Un éclairage sur l'emprise provisoire et sa commune, calculé avant la consultation du plan.</p>
    </header>
    <div class="context-grid">
      <article class="context-card">
        <p class="context-kicker">Urbanisme</p>
        <h3>Zonage par lot</h3>
        <p>La zone PLU issue du GPU apparaît dans la fiche de chaque lot. Les lots à cheval sur plusieurs zones peuvent présenter plusieurs codes.</p>
        <p v-if="documentDates" class="context-small">Date portée par le document : {{ documentDates }}.</p>
        <a href="https://www.data.gouv.fr/dataservices/api-carto-module-geoportail-de-lurbanisme-gpu" target="_blank" rel="noopener noreferrer">IGN · API Carto / GPU ↗</a>
      </article>
      <article class="context-card">
        <p class="context-kicker">Risques communaux</p>
        <h3>{{ context.risk_families.length }} familles recensées</h3>
        <p>Cette liste concerne {{ context.commune_name }}. Elle ne localise pas les risques sur les lots fictifs.</p>
        <details>
          <summary>Voir les familles de risques</summary>
          <ul><li v-for="family in context.risk_families" :key="family">{{ family }}</li></ul>
        </details>
        <a href="https://www.georisques.gouv.fr/donnees/bases-de-donnees/procedures-administratives-relatives-aux-risques" target="_blank" rel="noopener noreferrer">Géorisques · Ministère / BRGM ↗</a>
      </article>
      <article class="context-card">
        <p class="context-kicker">Terrains à bâtir · DVF</p>
        <h3 v-if="context.dvf.median_eur_m2 !== null">{{ money.format(context.dvf.median_eur_m2) }} <span>€/m²</span></h3>
        <h3 v-else>Échantillon insuffisant</h3>
        <p>Médiane communale · {{ context.dvf.sample_size }} mutations retenues · {{ period }}.</p>
        <p class="context-small">Ventes libellées « terrain à bâtir », sans local bâti. Indicateur de contexte ; les prix des lots restent fictifs.</p>
        <a href="https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees" target="_blank" rel="noopener noreferrer">DGFiP · Etalab / DVF ↗</a>
      </article>
    </div>
    <p class="context-attribution">
      Sources consultées le {{ consultedOn }} ·
      <a href="https://www.etalab.gouv.fr/licence-ouverte-open-licence/" target="_blank" rel="noopener noreferrer">Licence Ouverte 2.0</a>.
      Ces indicateurs ne constituent ni une estimation immobilière ni un diagnostic réglementaire.
    </p>
  </section>
</template>
