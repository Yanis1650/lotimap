# Contexte du projet — lotimap

> Document de reprise pour les prochaines conversations. État au 5 octobre 2026 : phases 0 à 7 validées. Plan paysager 2D et galerie de perspectives fictives ajoutés ; phase 8 réalisée, en attente de validation. Le déploiement réel sur le VPS reste à faire.

## Intention

**lotimap** est une démonstration open source de géomatique et de développement web, destinée à un portfolio, à GitHub et à un post LinkedIn. Un tech lead ou un recruteur doit pouvoir comprendre et évaluer les choix, la qualité du code et les limites de la démonstration. Le budget cible est d'environ **25 heures au total** ; la lisibilité prime sur le nombre de fonctionnalités.

La pièce maîtresse est un convertisseur **DXF → GeoJSON générique**. La carte de lots et l'enrichissement par données ouvertes montrent l'utilisation du résultat.

## Scénario et données

- Lotissement fictif **« Le Clos du Verger »**, porté par un lotisseur privé fictif, d'environ 20 lots.
- Emprise provisoire paramétrable près d'Avranches (Manche), centrée approximativement sur **48.684° N, 1.357° O**. Le site réel sera fourni plus tard.
- Le générateur produit un DXF synthétique en **CC49 (EPSG:3949)** avec lots, voirie, limite d'opération et numéros, ainsi que des variantes défectueuses pour les tests.
- Aucun plan réel, propriétaire ou référence cadastrale dans le dépôt ou l'interface. `data/private/` est réservé à d'éventuels fichiers locaux et ignoré par Git.

## Composants prévus

### `importer/` — conversion et contrôle

- Python 3.12, uv, ezdxf, shapely, pyproj, typer ; pytest et ruff.
- Mapping des calques en YAML pour des plans de géomètres différents.
- Projection source choisie en CLI : Lambert 93 (EPSG:2154) ou CC49 (EPSG:3949).
- Surfaces calculées dans la projection source ; GeoJSON produit en WGS84.
- Numéros `TEXT` et `MTEXT` rattachés au polygone qui les contient.
- Rapport lisible : polylignes non fermées, lots sans numéro, numéros en double, textes hors polygone, géométries invalides. Une erreur sur une entité ne doit pas interrompre l'analyse des autres.
- Tests pytest sur des DXF synthétiques, dont des cas défectueux.

### `web/` — carte publique et administration réalisées

- Vue 3, TypeScript, MapLibre GL et Nuxt 4/Nitro ; SQLite pour les prix et statuts.
- Orthophoto IGN Géoplateforme via WMTS, lots colorés : disponible, option, réservé, vendu.
- Fiche : numéro, surface, prix, prix au m², zone PLU et bouton d'intérêt factice sans collecte de données.
- Filtres budget/surface, compteur des lots disponibles, interface pensée pour mobile.
- `/admin` minimal protégé par un mot de passe fourni par variable d'environnement, permettant de changer statut et prix.

### Enrichissement pré-calculé

- Zone PLU par lot : API Carto GPU de l'IGN.
- Risques : API Géorisques.
- Prix médian au m² des terrains à bâtir à l'échelle communale : DVF, uniquement sous forme agrégée.
- Aucune interrogation de ces services pendant la consultation d'un lot ; méthode, dates et limites documentées dans `enrichment/README.md`.

### Livraison

- Docker Compose, configuration prête pour Traefik sur un VPS.
- GitHub Actions : tests, lint et vérification des types.
- Documentation finale en français (`README.md`) et en anglais (`README.en.md`).

## Contraintes non négociables

- Bandeau visible **« Démonstration — données fictives »**.
- `noindex` sur toutes les pages et `robots.txt` interdisant l'exploration.
- Aucune donnée de propriétaire ni référence cadastrale affichée.
- Attribution datée des sources IGN, Etalab/DVF, GPU et Géorisques, avec leurs licences vérifiées avant publication.
- Aucun paiement, CRM ou système d'authentification complexe.

## Décisions et réalisations validées ou proposées

- Monorepo léger : `importer/`, `samples/`, `enrichment/`, `web/`, `data/`, `deploy/`, `.github/workflows/`.
- La phase 0 a créé l'arborescence et la documentation sans implémentation métier.
- Les exemples synthétiques publiables sont préparés dans `data/demo/dxf/` pour être versionnés ; les fichiers réels éventuels iront dans `data/private/`, ignoré par Git.
- Le générateur `samples/generate.py` utilise Python 3.12, uv, ezdxf et pyproj. Il produit un plan de 20 lots en deux rangées, numérotés en `TEXT` et `MTEXT`, ainsi que cinq défauts isolés. Centre, orientation et dimensions sont paramétrables. Les profondeurs varient de 80 à 125 % de la valeur nominale (672 à 1 050 m² par défaut) pour rendre le filtre de surface pertinent. `manifest.json` enregistre les paramètres et les anomalies attendues.
- Le convertisseur prend en charge `LWPOLYLINE` et `POLYLINE` 2D fermées sans courbes ; les autres entités configurées sont signalées. Le mapping YAML permet d'adapter les calques. Les GeoJSON et rapports du plan sain sont dans `data/demo/geojson/`.
- Une règle persistante dans `.cursor/rules/code-file-length.mdc` limite chaque fichier de code écrit à la main à 200 lignes physiques ; un test pytest vérifie cette limite.
- La carte publique utilise Nuxt 4, avec une route Nitro `/api/lots` qui associe le GeoJSON synthétique aux états et prix SQLite. Le GeoJSON est lu dans `data/demo/geojson/` par défaut ; `LOTIMAP_GEOJSON_PATH` et `LOTIMAP_DB_PATH` permettent de choisir d'autres chemins.
- SQLite initialise des valeurs fictives de 65 000 à 87 500 € : 14 disponibles, 2 en option, 2 réservés, 2 vendus. Les lignes existantes sont préservées pour permettre la future édition admin.
- MapLibre GL affiche l'orthophoto IGN Géoplateforme WMTS (`ORTHOIMAGERY.ORTHOPHOTOS`, `PM_0_19`) et les polygones colorés. Son worker est empaqueté par Vite avec `?worker&url`, nécessaire avec MapLibre GL 6. La route API copie l'identifiant stable du GeoJSON dans la propriété `lot_id` pour que les clics et la surbrillance restent fiables, même si les numéros de lots sont dupliqués.
- L'interface publique est utilisable sur mobile et ordinateur, avec filtres budget/surface, compteur, liste accessible et fiche. La zone PLU et sa description viennent de l'enrichissement ; le bouton d'intérêt ne collecte rien.
- Le bandeau de démonstration, la balise `noindex`, l'en-tête `X-Robots-Tag` et le `robots.txt` bloquant sont en place. L'attribution du fond IGN est datée au 30 septembre 2026.
- L'administration est désactivée tant que `LOTIMAP_ADMIN_PASSWORD` et `LOTIMAP_SESSION_SECRET` (au moins 32 caractères) ne sont pas définis. Le mot de passe est vérifié côté serveur et les échecs de connexion sont limités par adresse IP en mémoire (5 essais / 15 min).
- Après connexion, H3 place une session signée de 8 h dans un cookie `HttpOnly`, `SameSite=Strict`, limité aux routes `/api/admin`. Les mutations contrôlent l'en-tête `Origin`, le type JSON, l'identifiant du lot, le statut et le prix entier positif. `LOTIMAP_PUBLIC_ORIGIN` permet de définir l'origine attendue derrière le futur proxy HTTPS.
- Un test d'intégration Node démarre le serveur compilé avec une base SQLite temporaire et vérifie le refus sans session, la connexion, les validations, l'édition, l'API publique et la déconnexion.
- La vue admin est pensée pour téléphone et ordinateur. Les couleurs provisoires ont été remplacées par la charte Drekky Studio fournie le 4 octobre 2026.
- `enrichment/` réutilise l'environnement Python de `importer/`. Le script `python -m enrichment.build` est lancé depuis la racine, avec plan, commune, période DVF et projection métrique paramétrables. Le JSON d'enrichissement est fourni dans `data/demo/enrichment.json` ; aucune ligne DVF brute n'est conservée.
- GPU : une requête sur la limite d'opération, puis intersections locales dans la projection métrique. Les codes couvrant au moins 1 % du lot sont conservés si les zones couvrent au moins 95 % du lot. Une zone non attribuable reste non disponible. Le code ne conclut pas à la constructibilité.
- Géorisques : familles GASPAR à l'échelle **communale**, clairement indiquées comme telles, sans attribution aux lots fictifs.
- DVF : période **2021–2025** retenue pour un échantillon plus fourni. Ventes explicitement libellées « Vente terrain à bâtir », sans local bâti, regroupées par mutation, surfaces dédupliquées et totalisées. Médiane non pondérée des ratios valeur/surface, arrondie à l'euro et masquée sous cinq mutations. Les limites des exports communaux et de la déduplication sont documentées.
- Résultat recalculé le **1er octobre 2026** : **20 lots en zone Uh**, document GPU daté du **27 février 2020**, **sept familles de risques** à Avranches (INSEE 50025), **80 €/m² sur 12 mutations** DVF. Les prix des lots restent fictifs. IGN/GPU, Géorisques et DGFiP/Etalab sont attribués sous Licence Ouverte 2.0.
- L'enrichissement est lié à l'empreinte SHA256 du fichier GeoJSON. Tout changement du fichier impose un recalcul ; un résultat absent, invalide ou périmé est masqué sans empêcher la consultation de la carte.
- Les tests d'enrichissement sont synthétiques et sans réseau. Le test web couvre aussi la lecture du contexte, une date invalide et le retrait des résultats après modification du plan. La limite de 200 lignes inclut le nouveau module.
- Vérifications de la phase 5 : 18 tests Python réussis, Ruff et formatage conformes, vérification TypeScript et compilation/test d'intégration web réussis. Affichage contrôlé en 390 × 844 et 1 280 × 900, sans débordement horizontal. L'aperçu local utilise le port 3333.
- La phase 6 ajoute une image Docker en deux étapes, sous Node 22 / Debian : construction Nuxt et binaire SQLite Linux fourni par le paquet, sortie Nitro et données de démonstration dans l'image finale. Le conteneur tourne sans root, avec un volume SQLite persistant et le reste du système de fichiers en lecture seule.
- L'installation utilise `npx --yes npm@12.2.0 ci`, avec Node 22.22.2 minimum dans la branche 22, sans modifier le npm global. npm 10 déclenchait à tort une recompilation de better-sqlite3 13 malgré ses binaires fournis. `allowScripts` autorise esbuild 0.28.2 et unrs-resolver 1.12.2 et désactive la recompilation SQLite. Cette configuration est partagée par le développement, Docker et la CI.
- `deploy/compose.yaml` ne publie aucun port. Le fichier local ajoute `127.0.0.1:3333` (port paramétrable). L'ajout Traefik utilise un réseau externe, une route HTTPS et un résolveur de certificat existant ; domaine, réseau, entrée et résolveur restent paramétrables dans un fichier `.env` ignoré.
- `deploy/README.md` documente l'administration, le VPS, les mises à jour et la sauvegarde complète de SQLite avec écritures arrêtées. Le plan et l'enrichissement sont embarqués dans l'image ; un changement de données nécessite une reconstruction.
- `.dockerignore` sélectionne les sources nécessaires et exclut secrets, bases, dépendances locales et fichiers privés. `.gitattributes` conserve les octets des GeoJSON/DXF afin que les fins de ligne Git ne cassent pas l'empreinte du plan entre Windows et Linux.
- ESLint via le module officiel Nuxt contrôle le code Vue/TypeScript/JavaScript. `npm run lint`, la vérification des types et le test web réussissent.
- GitHub Actions contient trois tâches : Python 3.12 (tests, Ruff et formatage), web Node 22 (lint, types, compilation/test), puis construction et test du conteneur. Les actions sont fixées par leur commit, les permissions limitées à la lecture et aucun déploiement automatique n'est configuré.
- Le test conteneur utilise le projet isolé `lotimap-check`, avec des identifiants factices ; il vérifie l'API, les 20 lots, le contexte, la persistance d'un prix/statut après redémarrage, le cookie `Secure` derrière un protocole HTTPS simulé, les pages `noindex` et `robots.txt`. Son volume jetable est supprimé après vérification.
- Les README français/anglais finaux et une capture réelle de la carte sont fournis. Le guide de déploiement explique les paramètres Traefik et la sauvegarde SQLite.
- Vérifications du **4 octobre 2026** après reprise : installation propre avec npm 12.2.0, lint, types, compilation et test web réussis ; 18 tests Python, Ruff/formatage et limite de 200 lignes réussis sous Linux. Image reconstruite avec npm 12, test conteneur réussi et workflow validé par actionlint. Les trois tâches du premier passage réel sur GitHub ont également réussi.
- Deux avis de sécurité sans correctif publié (`braces` et `node-forge`) remontent 11 dépendances affectées dans l'audit. Ces modules sont absents des sorties serveur Nitro Windows et Linux vérifiées ; les deux README documentent leur portée et les liens de suivi. Recontrôler avant déploiement.
- Le contrôle d'application Windows bloque le chargement local de pyproj ; la vérification Python a été effectuée dans un conteneur Linux Python 3.12. Aucune protection Windows n'a été modifiée. Après un échec temporaire de Docker Desktop, une relance officielle a rétabli le moteur ; aucune suppression manuelle de son fichier temporaire n'a été exécutée.
- L'aperçu `http://127.0.0.1:3333/` tourne dans Docker (projet `lotimap`, volume `lotimap_sales` conservé), administration désactivée. Le serveur Node temporaire a été arrêté et le projet de test `lotimap-check` avec son volume jetable a été supprimé.
- L'utilisateur a validé **MIT** pour le code le 4 octobre 2026. `LICENSE` et `NOTICE.md` distinguent le code et les exemples synthétiques des données ouvertes, polices OFL et éléments de marque.
- La charte v1 de septembre 2026 et les SVG ont été fournis le 4 octobre. L'intégration applique les couleurs exactes, Space Grotesk / IBM Plex Sans / IBM Plex Mono, arrondis de 3 px, contenu centré sur 1 152 px, symbole et mot côte à côte dans la navigation, variantes crème au pied de page et favicon original. Les six WOFF2 sont hébergés localement avec leurs licences ; les logos sont copiés sans modification. Les choix sont dans `docs/branding.md`.
- Le dépôt cible fourni et autorisé par l'utilisateur est **https://github.com/Yanis1650/lotimap**, public et initialement vide, branche par défaut `main`. Le remote SSH `origin` est configuré ; le commit initial `e73180c` a été publié le 4 octobre 2026, avec une adresse GitHub noreply. [Le premier passage CI](https://github.com/Yanis1650/lotimap/actions/runs/37219417210) a réussi pour Python, le web et le conteneur Docker.
- Vérification de l'identité le **4 octobre 2026** : vues 390 × 844 et 1 280 × 900 sans débordement horizontal ; filtres combinés à 70 000 € / 900 m² donnant deux lots disponibles, fiche du lot 13 avec zonage Uh et bouton factice sans collecte. Le bandeau reste visible pendant le défilement ; l'admin non configurée affiche son état désactivé. Les captures sont dans `docs/images/`.
- L'utilisateur a autorisé le **5 octobre 2026** une étape visuelle : plan paysager 2D et deux perspectives d'ambiance réalistes. Une couche MapLibre place maisons, terrasses, accès, haies et arbres dans les quadrilatères convexes du plan fictif, avec façade orientée vers la voirie. Aucun contour, numéro, prix ou surface source n'est modifié ; l'empreinte du GeoJSON reste identique et l'enrichissement reste applicable. La bascule vers l'orthophoto conserve filtres et sélection. Le paysage ignore les lots avec trous ou non convexes et ne vérifie aucune règle de construction.
- Les deux perspectives rue/jardin ont été créées avec Imagegen, encodées en WebP 1 536 px et 768 px, avec chargement différé. Elles restent des illustrations d'ambiance sans correspondance avec un lot ou une implantation exacte ; la mention « Illustration fictive · IA » est visible sur chaque image. La provenance et les prompts sont dans `docs/visuals.md`. La 3D interactive reste une option future.
- Vérifications de la phase 8 : lint, types, compilation et quatre tests web réussis ; limite de 200 lignes vérifiée par pytest. Docker reconstruit et aperçu sain sur le port 3333, volume existant conservé. Plan et galerie contrôlés en 1 280 × 900 et 390 × 844, sans débordement horizontal, avec changement de fond, filtres et ouverture d'une fiche depuis le plan mobile. Les captures sont dans `docs/images/lotimap-landscape-*.png` et `docs/images/lotimap-gallery-*.png`.

## Phases et règle de travail

0. Cadrage et arborescence — **validée**.
1. Générateur de DXF synthétiques — **validée**.
2. Convertisseur et tests — **validée**.
3. Carte publique — **validée**.
4. Vue admin — **validée**.
5. Enrichissement open data — **validée**.
6. Docker, CI, README final en français et en anglais — **validée**.
7. Identité Drekky Studio et publication GitHub — **validée**.
8. Plan paysager 2D et perspectives d'ambiance — **réalisée le 5 octobre 2026, en attente de validation**.

Arrêter le travail à la fin de chaque phase, résumer ce qui est fait et ce qui reste, proposer un message de commit et attendre la validation avant la suivante. Présenter les options avant de trancher un choix technique discutable.

## Questions et points à confirmer

1. **Déploiement** : domaine, réseau Traefik et méthode TLS à renseigner avant déploiement VPS, sans valeurs privées dans Git.
2. **Emprise définitive** : adapter le plan et recalculer l'enrichissement quand la vraie zone sera choisie.
3. **Communication** : préparer le post LinkedIn après validation de cette étape.
