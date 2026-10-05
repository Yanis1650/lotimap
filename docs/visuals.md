# Plan paysager et perspectives fictives

## Périmètre

Ajout du 5 octobre 2026, après validation : un plan 2D paysager interactif et deux perspectives d'ambiance, adaptés au téléphone et à l'ordinateur. La palette et les composants suivent la charte Drekky Studio. La [vue 3D légère](3d.md) est ajoutée lors de la phase suivante.

## Plan 2D

Le plan paysager est le fond initial ; un bouton permet de revenir à l'orthophoto IGN sans recréer la carte. Les statuts, filtres et fiches utilisent les mêmes lots dans les deux modes.

`web/app/utils/landscape.ts` construit une couche d'illustration à partir des quadrilatères convexes du GeoJSON fictif. Le côté le plus proche de la voirie sert de façade ; une interpolation dans chaque quadrilatère place maison, terrasse, accès, haies et trois arbres. Les trous et contours non convexes sont ignorés ; sans voirie, aucune implantation n'est ajoutée.

Les coordonnées, surfaces et numéros du plan source ne sont pas modifiés. Les implantations sont illustratives : elles ne vérifient pas les règles du PLU, les retraits, les réseaux ou la faisabilité d'une construction. Ce module ne fait pas partie du convertisseur générique.

Trois tests contrôlent le maintien des éléments dans les lots et l'absence de mutation du plan, le filtrage, puis les formes non prises en charge.

## Images et provenance

Deux images ont été créées avec l'outil intégré **Imagegen**, le **5 octobre 2026**, sans photographie réelle ni donnée personnelle en entrée :

- `web/public/images/verger-rue.webp` : « Les allées du verger » ;
- `web/public/images/verger-jardin.webp` : « Côté jardin ».

Ce sont des perspectives d'ambiance générées par IA, sans correspondance avec un lot particulier, le site réel ou l'implantation du plan 2D. Chaque image porte la mention visible **« Illustration fictive · IA »** et un texte alternatif descriptif. Elles ne constituent pas des photographies d'une opération existante.

Les originaux 1 536 × 1 024 ont été encodés en WebP avec Sharp, qualité 82, et déclinés en 768 × 512 sans modification du contenu. Les versions 768 px pèsent environ 108 et 128 ko ; les versions 1 536 px environ 368 et 435 ko. `srcset`, les dimensions explicites et le chargement différé limitent le poids et les décalages de mise en page.

## Prompts exacts

### Les allées du verger

```text
Use case: photorealistic-natural. Asset type: website gallery landscape architectural visualization, 1536 x 1024. Create one photorealistic CGI architectural perspective of a completely fictional small housing development named Le Clos du Verger, inspired by rural Manche near Avranches in Normandy, France. Street-level view along a calm narrow residential lane, modest contemporary detached houses with cream mineral render, local pale stone accents, charcoal slate pitched roofs, restrained timber detailing. Low hedges, apple trees, soft grass and realistic young planted trees, simple permeable pedestrian edges. Two or three houses visible, believable human scale, understated French residential landscaping, warm overcast afternoon light with natural soft shadows, finely detailed materials, editorial architecture photography quality, 35mm lens, not luxury villa advertising. Composition: wide image with road entering foreground, architecture middle distance, generous sky and foliage, no people, no readable signs, no text, no logo, no watermark. This is a conceptual fictional architectural illustration, not documentation of a real existing property. Avoid tropical plants, swimming pools, mountains, American streets, dramatic lens flare, extreme saturation, artificial glossy surfaces.
```

### Côté jardin

```text
Use case: photorealistic-natural. Asset type: website gallery landscape architectural visualization, 1536 x 1024. Create one photorealistic CGI architecture photograph of the garden side of a completely fictional modest detached house in Le Clos du Verger, an imagined housing development inspired by the rural Manche near Avranches, Normandy, France. Maintain the architectural language of cream mineral render, charcoal slate pitched roof, pale local stone accents and restrained natural timber. A simple timber terrace, a lawn, an apple tree, flowering native borders and low mixed hedges provide a calm, believable garden, with a second similar house partially visible beyond the hedge. Soft late afternoon daylight, subtle realistic shadows, natural material imperfections, high quality architecture editorial photography, restrained cream, green and slate palette. Composition: wide image of house and garden, eye-level viewpoint from the garden, no people, no text, no logos, no watermark. Fictional conceptual visualization, not a real site photograph. Avoid swimming pools, tropical plants, giant glass mansions, hot Mediterranean sunshine, oversized garden, excessive decoration, oversaturated colors.
```

## Vérification visuelle

L'affichage est contrôlé en 1 280 × 900 et 390 × 844 : changement de fond, filtres combinés, ouverture de fiche, galerie et absence de débordement horizontal. Les captures sont conservées dans `docs/images/`.
