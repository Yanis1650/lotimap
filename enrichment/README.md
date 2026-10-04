# Enrichissement pré-calculé

Ce module associe des données ouvertes au **plan fictif** avant de lancer le site. Il réutilise les dépendances Python 3.12 de `importer/` ; aucune nouvelle bibliothèque ni base de données n'est nécessaire. Le serveur web lit seulement le résultat JSON et n'interroge pas les API d'enrichissement.

## Produire le résultat

Depuis la racine du dépôt, avec [uv](https://docs.astral.sh/uv/) :

```sh
uv --directory importer sync --locked --python 3.12 --group dev
uv run --project importer --locked python -m enrichment.build
```

Le résultat est écrit dans `data/demo/enrichment.json`. Les paramètres suivants permettent d'adapter le calcul :

- `--plan` : GeoJSON WGS84 issu du convertisseur ;
- `--output` : chemin du JSON d'enrichissement ;
- `--commune-code` / `--commune-name` : code INSEE et nom de la commune, par défaut `50025` / `Avranches` ;
- `--area-crs` : `EPSG:3949` par défaut, ou `EPSG:2154` pour les intersections et surfaces ;
- `--start-year` / `--end-year` : période DVF inclusive de un à cinq ans, par défaut **2021–2025**.

La commune doit correspondre à l'emprise choisie : elle est fournie explicitement et n'est pas déduite du plan. La période de cinq ans donne un échantillon plus fourni pour cette démonstration ; elle ne décrit pas uniquement le marché récent. Une année non publiée, une erreur réseau ou une réponse inexploitable interrompt le calcul avant l'écriture du résultat, en conservant le précédent fichier.

Le fichier inclut la version du format, les dates de consultation, les sources et l'empreinte SHA256 du GeoJSON. **Toute modification du fichier du plan**, même sa mise en forme, invalide l'enrichissement : l'application masque alors le contexte et affiche une zone PLU non disponible. Recalculer l'enrichissement après avoir régénéré ou remplacé le plan.

## Méthode et limites

### Zonage GPU

Une requête [API Carto / GPU](https://apicarto.ign.fr/api/doc/gpu) récupère les zones intersectant la limite d'opération, ou l'union des lots si cette limite est absente. Les lots sont croisés localement avec les polygones dans la projection métrique choisie. Seules les zones en production, ou sans statut explicite, sont retenues.

Les polygones de même code sont réunis. Chaque code couvrant au moins **1 %** du lot est conservé, par surface décroissante. Le lot doit être couvert à au moins **95 %** par l'union des zones pour recevoir un code ; sinon la zone reste non disponible. Un lot à cheval sur plusieurs zones affiche plusieurs codes. Ces seuils réduisent les effets de petits écarts géométriques ; ils ne remplacent pas la lecture du règlement. Un code PLU seul ne permet pas de conclure à la constructibilité.

La date `datvalid` fournie par le GPU est conservée distinctement de la date de consultation. L'emprise reste provisoire : le zonage sera recalculé lors du choix de la vraie zone.

### Risques Géorisques

L'[API Géorisques](https://www.data.gouv.fr/dataservices/api-georisques), endpoint GASPAR `risques`, fournit les familles recensées pour la commune. Les codes de famille à deux chiffres évitent de compter séparément leurs sous-types. L'interface indique explicitement cette **échelle communale** ; elle n'attribue aucun risque à un lot particulier et ne produit pas d'état des risques réglementaire.

### Médiane DVF

Les [CSV géolocalisés Etalab / DVF](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees) de la commune sont téléchargés en mémoire, année par année. Le calcul retient uniquement les mutations libellées **« Vente terrain à bâtir »**, sans local bâti déclaré.

- Regroupement par `id_mutation` pour compter une vente une seule fois, y compris avec plusieurs dispositions ou parcelles.
- Valeur foncière positive et identique sur les lignes de la mutation ; surfaces positives et identifiants de parcelles présents. Les groupes incomplets ou incohérents sont exclus.
- Déduplication des surfaces par parcelle, nature de culture, culture spéciale et surface, puis somme des surfaces. La valeur foncière n'est utilisée qu'une fois.
- Calcul du ratio valeur / surface totale pour chaque mutation, puis médiane **non pondérée** de ces ratios, arrondie à l'euro.
- Médiane masquée en dessous de **cinq mutations** ; taille d'échantillon et période toujours affichées. Ce seuil est un choix de présentation de la démo, pas un seuil réglementaire.

Les exports communaux ne permettent pas de vérifier si une mutation contient aussi des parcelles dans une autre commune. Des subdivisions de même parcelle ayant exactement les mêmes attributs peuvent également être confondues lors de la déduplication. Le filtre exclut des terrains constructibles enregistrés sous une autre nature de mutation. Aucun contrôle automatique des ventes atypiques n'est ajouté. L'indicateur est donc un repère illustratif, pas une estimation du prix d'un lot.

**Aucun CSV brut, adresse, identifiant de mutation ou référence cadastrale n'est enregistré dans le résultat.** Le JSON publié contient uniquement les codes PLU des lots fictifs, les familles de risques communales et les agrégats DVF.

## Jeu de démonstration et attribution

Sources consultées et résultat recalculé le **1er octobre 2026** pour l'emprise provisoire du Clos du Verger :

- IGN, API Carto / Géoportail de l'urbanisme : **20 lots en zone Uh**, « Zone urbaine à dominante habitat », date portée par le document : **27 février 2020**. [Source et licence](https://www.data.gouv.fr/dataservices/api-carto-module-geoportail-de-lurbanisme-gpu).
- Géorisques, Ministère / BRGM, GASPAR : **sept familles communales**. [Description de GASPAR](https://www.georisques.gouv.fr/donnees/bases-de-donnees/procedures-administratives-relatives-aux-risques), [conditions d'utilisation](https://www.georisques.gouv.fr/cgu).
- DGFiP, traitement Etalab / DVF : **80 €/m²**, **12 mutations**, **2021–2025**. [Données sources](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres), [exports géolocalisés](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees).

Ces sources sont diffusées sous [Licence Ouverte 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/). Les conditions DVF interdisent la réidentification et l'indexation externe : les résultats sont agrégés, toutes les pages portent `noindex`, et `robots.txt` bloque l'exploration. Les prix commerciaux du plan restent entièrement fictifs.

## Vérification

```sh
uv run --project importer --locked python -m pytest -q importer/tests enrichment/tests
uv --directory importer run --locked ruff check src tests ../samples ../enrichment
uv --directory importer run --locked ruff format --check src tests ../samples ../enrichment
```

Les tests d'enrichissement utilisent des données synthétiques sans réseau : ventes sur plusieurs dispositions et parcelles, doublons de surfaces, exclusion du bâti, échantillon insuffisant, zonage multiple ou incomplet, zones superposées et familles de risques. Le test web vérifie également le retrait du contexte en cas de date invalide ou de changement de plan.
