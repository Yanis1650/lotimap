<script setup lang="ts">
import { computed, ref } from 'vue'
import type { PlanCollection } from '#shared/lot'
import { isLotFeature } from '#shared/lot'

useHead({ title: 'Administration | lotimap' })

interface SessionState {
  configured: boolean
  authenticated: boolean
}

const password = ref('')
const busy = ref(false)
const loginMessage = ref('')
const workspaceMessage = ref('')
const savedMessage = ref('')
const { data: session, pending: sessionPending, refresh: refreshSession } = await useFetch<SessionState>(
  '/api/admin/session', { server: false },
)
const { data: plan, pending: planPending, refresh: refreshPlan } = await useFetch<PlanCollection>(
  '/api/lots', { server: false },
)
const lots = computed(() => plan.value?.features.filter(isLotFeature) ?? [])
const availableCount = computed(() => lots.value.filter(lot => lot.properties.status === 'available').length)

async function login() {
  if (busy.value) return
  busy.value = true
  loginMessage.value = ''
  try {
    await $fetch('/api/admin/login', { method: 'POST', body: { password: password.value } })
    password.value = ''
    await refreshSession()
    await refreshPlan()
  } catch (error) {
    const code = error && typeof error === 'object' && 'statusCode' in error
      ? Number(error.statusCode) : 0
    loginMessage.value = code === 429
      ? 'Trop de tentatives. Réessayez dans quelques minutes.'
      : 'Connexion impossible. Vérifiez le mot de passe.'
  } finally {
    busy.value = false
  }
}

async function logout() {
  workspaceMessage.value = ''
  try {
    await $fetch('/api/admin/logout', { method: 'POST' })
    await refreshSession()
  } catch {
    workspaceMessage.value = 'Déconnexion impossible. Réessayez.'
  }
}

async function onSaved(number: string | null) {
  savedMessage.value = ''
  await refreshPlan()
  savedMessage.value = `Lot ${number ?? '—'} mis à jour.`
}
</script>

<template>
  <main class="admin-page">
    <header class="admin-top">
      <div>
        <p class="admin-brand">Drekky Studio / lotimap</p>
        <h1>Gestion des lots<span>.</span></h1>
        <p>Prix et disponibilités de démonstration.</p>
      </div>
      <NuxtLink class="admin-back" to="/">Voir la carte <span aria-hidden="true">↗</span></NuxtLink>
    </header>

    <section v-if="sessionPending" class="admin-panel" role="status">Chargement de l'administration…</section>
    <section v-else-if="!session?.configured" class="admin-panel">
      <p class="admin-kicker">Accès non configuré</p>
      <h2>L'administration est indisponible.</h2>
      <p>Configurez l'accès local pour modifier les lots fictifs.</p>
    </section>
    <section v-else-if="!session.authenticated" class="admin-panel admin-login">
      <p class="admin-kicker">Espace de gestion</p>
      <h2>Connexion</h2>
      <p>Entrez le mot de passe de la démonstration.</p>
      <form @submit.prevent="login">
        <label for="admin-password">Mot de passe</label>
        <input id="admin-password" v-model="password" type="password" autocomplete="current-password" required>
        <button type="submit" :disabled="busy">{{ busy ? 'Connexion…' : 'Se connecter' }}</button>
      </form>
      <p v-if="loginMessage" class="admin-form-message" role="alert">{{ loginMessage }}</p>
    </section>
    <section v-else class="admin-workspace">
      <div class="admin-overview">
        <div>
          <p class="admin-kicker">Le Clos du Verger · Données fictives</p>
          <h2>{{ availableCount }} disponibles <span>/ {{ lots.length }} lots</span></h2>
        </div>
        <button type="button" class="admin-logout" @click="logout">Se déconnecter</button>
      </div>
      <p v-if="workspaceMessage" class="admin-form-message" role="alert">{{ workspaceMessage }}</p>
      <p v-if="savedMessage" class="admin-save-message" role="status">{{ savedMessage }}</p>
      <p v-if="planPending" role="status">Chargement des lots…</p>
      <div v-else class="admin-grid">
        <AdminLotCard
          v-for="lot in lots" :key="lot.id" :lot="lot"
          @saved="onSaved(lot.properties.number)" @unauthorized="refreshSession()"
        />
      </div>
    </section>
  </main>
</template>
