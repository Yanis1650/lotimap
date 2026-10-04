# Application lotimap

La carte présente les 20 lots fictifs du Clos du Verger sur l'orthophoto IGN. Elle lit le GeoJSON généré par le convertisseur ; une base SQLite locale fournit les prix et statuts de démonstration.

## Lancer en local

Depuis `web/`, avec Node.js 22.22.2 ou plus récent dans la branche 22 :

```powershell
npx --yes npm@12.2.0 ci
npm run dev
```

Ouvrir `http://127.0.0.1:3000`. Pour contrôler le code et la compilation :

```powershell
npm run typecheck
npm run lint
npm test
```

La commande d'installation utilise npm 12.2.0 sans modifier le npm global. Les scripts des versions verrouillées d'esbuild et du résolveur ESLint sont autorisés dans `package.json`. SQLite utilise ses binaires fournis ; la recompilation automatique est désactivée, car npm 10 la déclenche à tort sous Windows. Les autres branches Node compatibles sont indiquées dans `engines`.

Par défaut, l'application lit `../data/demo/geojson/clos_du_verger.geojson`, charge `../data/demo/enrichment.json` et crée `.data/lotimap.sqlite`. Elle doit être lancée depuis `web/`. Un fichier `.env` local peut définir `LOTIMAP_GEOJSON_PATH`, `LOTIMAP_ENRICHMENT_PATH` et `LOTIMAP_DB_PATH` ; voir `.env.example`. La base est initialisée à la première lecture : 14 lots disponibles, 2 en option, 2 réservés et 2 vendus, avec des prix fictifs de 65 000 à 87 500 €. Les valeurs déjà présentes en base sont conservées.

## Fonctionnement

- `/api/lots` associe les polygones du GeoJSON aux prix et statuts SQLite.
- Le navigateur affiche l'orthophoto IGN par WMTS, les lots colorés et les numéros, puis permet de filtrer par budget et surface.
- La fiche indique le numéro, la surface, le prix, le prix au m² et le zonage PLU issu du GPU, avec sa description lorsqu'une seule zone est retenue.
- Sous la carte, le contexte territorial présente les sources datées, les familles de risques à l'échelle communale et la médiane DVF agrégée. La disposition passe d'une colonne sur téléphone à trois sur ordinateur.
- Le bouton « Je suis intéressé » affiche un message local ; aucune donnée n'est envoyée ni collectée.
- Le bandeau « Démonstration — données fictives » est permanent. Les pages portent une balise `noindex` et un en-tête `X-Robots-Tag` ; `robots.txt` interdit l'exploration.

## Enrichissement

Le fichier fourni a été calculé le **1er octobre 2026** : zone Uh pour les 20 lots de l'emprise provisoire, sept familles de risques communaux et médiane DVF de 80 €/m² sur 12 mutations de 2021 à 2025. Les prix des lots affichés par SQLite restent fictifs.

Le serveur vérifie le format et l'empreinte SHA256 du GeoJSON. Si le fichier d'enrichissement manque, est invalide ou ne correspond plus au plan, la carte fonctionne avec des zones PLU « Non disponible » et sans panneau territorial. Recalculer le fichier après toute modification du plan. Aucun appel GPU, Géorisques ou DVF n'est effectué lors de la consultation du site. Voir [la méthode et ses limites](../enrichment/README.md).

## Administration

La route `/admin` permet de changer le statut et le prix indicatif des lots fictifs. Pour l'activer, définir dans `web/.env` (ignoré par Git) :

- `LOTIMAP_ADMIN_PASSWORD` : mot de passe choisi pour la démo ;
- `LOTIMAP_SESSION_SECRET` : secret aléatoire d'au moins 32 caractères.

La commande `node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))"` génère un secret local. Sans ces deux variables, `/admin` affiche « accès non configuré » et les modifications sont désactivées. La session dure 8 h ; le cookie est `HttpOnly` et `SameSite=Strict`. Le mot de passe n'est ni écrit dans la base ni envoyé à l'API publique. Cinq échecs de connexion depuis une même adresse bloquent les tentatives pendant 15 minutes (compteur en mémoire du processus).

L'API de modification exige une origine identique à celle du site et valide le statut, le prix entier positif et l'existence du lot. Derrière un proxy HTTPS, définir aussi `LOTIMAP_PUBLIC_ORIGIN` à l'origine visible par le navigateur, sans barre finale (exemple : `https://lotimap.example`). Le proxy doit transmettre HTTPS de façon fiable et ne pas exposer directement le serveur Node. Les fichiers Compose et labels Traefik sont dans [deploy/README.md](../deploy/README.md).

L'identité **Drekky Studio** reprend la charte v1 fournie : fond crème, ardoise, touches terracotta, arrondis de 3 px et les trois polices prévues. Les logos SVG et les polices WOFF2 sont servis localement. Voir [les choix et les sources](../docs/branding.md) et [les licences](../NOTICE.md).

L'orthophoto est fournie par l'IGN Géoplateforme, Licence Ouverte, service consulté le 30 septembre 2026. Le zonage GPU, les risques Géorisques et les agrégats DGFiP / Etalab / DVF sont attribués avec leur date de consultation et la Licence Ouverte 2.0 dans le panneau public et [la documentation d'enrichissement](../enrichment/README.md).
