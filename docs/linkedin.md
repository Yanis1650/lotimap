# Post LinkedIn — brouillon à valider

Préparé le 5 octobre 2026, puis actualisé avec les liens de la démo publiée et du dépôt. Publication LinkedIn à effectuer après validation du texte et des visuels.

## Texte

Du plan de géomètre à la carte web interactive.

J’ai développé lotimap, une démonstration open source à la croisée de la géomatique et du développement web, sous l’identité Drekky Studio.

Le point de départ : un plan DXF avec des calques, des contours et des numéros de lots. L’objectif : obtenir des données géographiques contrôlées, puis les rendre faciles à explorer sur téléphone et ordinateur.

La pièce centrale est le convertisseur Python : mapping des calques configurable, prise en charge de Lambert 93 et CC49, surfaces calculées dans la projection source, association des numéros aux polygones et rapport d’anomalies. Les tests utilisent aussi des plans volontairement défectueux.

La carte ajoute des filtres budget/surface, des fiches de lots, une vue 2D, des volumes 3D illustratifs et un contexte issu des données ouvertes françaises : IGN/GPU, Géorisques et DVF en agrégé.

Le scénario du Clos du Verger est entièrement fictif. Les volumes et les perspectives d’ambiance sont illustratifs ; ces dernières sont générées par IA. Aucune donnée de propriétaire ni collecte de contacts.

Python, Nuxt/Vue, TypeScript, MapLibre, SQLite et Docker. Le dépôt documente les choix, les tests et les limites.

Découvrir la démo : [lotimap.drekky.fr](https://lotimap.drekky.fr).

Le code est disponible sous licence MIT : [github.com/Yanis1650/lotimap](https://github.com/Yanis1650/lotimap).

Géomaticiens, développeurs, professionnels de l’aménagement : vos retours sur la conversion DXF et le parcours de consultation sont les bienvenus.

#Géomatique #Python #OpenSource #DéveloppementWeb

## Visuels proposés

- En premier : la [vue 3D sur ordinateur](images/lotimap-3d-desktop.png), avec le bandeau de démonstration et les commandes de la carte visibles.
- En second : le [retour à la carte sur téléphone dans la démo publiée](images/lotimap-live-mobile.png), après sélection d'un lot depuis la liste.
- Conserver les mentions de fiction sur les captures. Les perspectives IA peuvent accompagner une publication ultérieure centrée sur la présentation visuelle.

La démo publiée est accessible en HTTPS. Le lien GitHub utilise l'adresse web du dépôt, adaptée aux lecteurs du post. L'adresse SSH de clonage n'est pas un lien de consultation.
