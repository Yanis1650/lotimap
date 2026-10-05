<script setup lang="ts">
const illustrations = [
  {
    src: '/images/verger-rue.webp', title: 'Les allées du verger',
    description: 'Une rue calme, des haies et des matières inspirées de la Normandie.',
    alt: 'Perspective fictive d’une rue bordée de maisons aux façades crème et toits en ardoise, avec des plantations.',
  },
  {
    src: '/images/verger-jardin.webp', title: 'Côté jardin',
    description: 'Une terrasse, un pommier et un jardin à l’abri des haies.',
    alt: 'Perspective fictive d’une maison au toit en ardoise donnant sur une terrasse et un jardin planté d’un pommier.',
  },
]
</script>

<template>
  <section class="project-gallery" aria-labelledby="gallery-title">
    <div class="gallery-intro">
      <div>
        <p class="eyebrow">Le projet en images</p>
        <h2 id="gallery-title">Imaginer le quotidien.</h2>
      </div>
      <p>Deux perspectives d’ambiance pour ce scénario fictif. Elles ne représentent ni le site réel ni l’implantation exacte des lots.</p>
    </div>
    <div class="gallery-grid">
      <figure v-for="image in illustrations" :key="image.src" class="gallery-figure">
        <div class="gallery-image">
          <img
            :src="image.src" :srcset="`${image.src.replace('.webp', '-768.webp')} 768w, ${image.src} 1536w`"
            sizes="(max-width: 639px) calc(100vw - 40px), (max-width: 1152px) calc((100vw - 88px) / 2), 532px"
            :alt="image.alt" width="1536" height="1024" loading="lazy" decoding="async"
          >
          <span>Illustration fictive · IA</span>
        </div>
        <figcaption>
          <h3>{{ image.title }}</h3>
          <p>{{ image.description }}</p>
        </figcaption>
      </figure>
    </div>
  </section>
</template>
