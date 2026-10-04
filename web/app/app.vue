<template>
  <div class="site-shell">
    <div class="demo-banner" role="note">
      <span class="demo-dot" aria-hidden="true" />
      Démonstration — données fictives
    </div>
    <header class="site-header">
      <StudioBrand />
      <a class="repository-link" href="https://github.com/Yanis1650/lotimap" target="_blank" rel="noopener noreferrer">
        Voir le code <span aria-hidden="true">→</span>
      </a>
    </header>
    <NuxtPage />
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-identity"><StudioBrand inverted /><p class="footer-kicker">Géomatique et développement web</p></div>
        <div class="footer-content">
          <p>lotimap · Démonstrateur conçu par Drekky Studio · Aucun lot proposé à la vente</p>
          <p>
        Fond : <a href="https://cartes.gouv.fr/aide/fr/guides-utilisateur/utiliser-les-services-de-la-geoplateforme/diffusion/wmts/" target="_blank" rel="noopener noreferrer">© IGN, Géoplateforme WMTS</a>
        · Licence Ouverte · service consulté le 30 septembre 2026.
          </p>
          <p>GPU, Géorisques et DVF : indicateurs ouverts pré-calculés. <NuxtLink to="/#territorial-context">Sources et dates de consultation</NuxtLink>.</p>
        </div>
      </div>
    </footer>
  </div>
</template>
