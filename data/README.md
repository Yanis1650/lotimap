# data

- `demo/dxf/` : six plans DXF synthétiques publiables et leur manifeste, produits par `samples/generate.py`.
- `demo/geojson/` : GeoJSON du plan sain et rapport de validation, produits par `importer/`.
- `demo/enrichment.json` : zonage GPU des lots fictifs, familles de risques communales Géorisques et médiane DVF agrégée, calculés par `enrichment/` le 1er octobre 2026.
- `private/` : espace local pour d'éventuels fichiers réels ; ce chemin est ignoré par Git. Ne jamais copier son contenu dans `demo/` sans vérification et anonymisation.

L'enrichissement contient la version du format, les dates et URL des sources, le code de commune et l'empreinte SHA256 du plan. Il ne contient aucune ligne DVF brute, adresse, référence cadastrale ou donnée de propriétaire. Les fichiers CSV sources sont traités en mémoire et ne sont pas enregistrés.

Pour l'emprise provisoire, les 20 lots sont en zone Uh ; sept familles de risques sont recensées dans la commune d'Avranches. La médiane DVF est de 80 €/m² sur 12 mutations de terrains à bâtir entre 2021 et 2025. Ces indicateurs ouverts ne changent pas les prix fictifs des lots. La provenance, la Licence Ouverte 2.0 et les limites du calcul sont détaillées dans [enrichment/README.md](../enrichment/README.md).
