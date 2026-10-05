# Identité Drekky Studio dans lotimap

La charte graphique v1 de septembre 2026 et les SVG ont été fournis par le porteur du projet le **4 octobre 2026**. Le document sert de référence visuelle ; ses exemples de prestations et de tarifs ne décrivent pas lotimap.

## Application

- Fond `paper` **#F7F2E6**, cartes de contexte `paper-dim` **#EFE6D1**, texte `ink` **#1C2523**.
- Ardoise `accent` **#3C565D** pour les boutons, le bandeau de démonstration et le pied de page ; touches terracotta **#BC6A4A**, version texte **#A0553F**.
- Space Grotesk pour les titres, IBM Plex Sans pour le texte et IBM Plex Mono pour les étiquettes. Les capitales sont appliquées en CSS.
- Contenu centré sur 1 152 px, gouttières de 20 px sur téléphone puis 32 px ; cartes, champs et boutons arrondis à 3 px.
- Navigation : symbole et mot côte à côte, avec « Studio » composé en texte dessous. Le lockup vertical est réservé aux grands formats.
- Logos ardoise sur crème, crème sur ardoise, favicon fourni. Les SVG sont copiés sans modification.

Les quatre couleurs de statut sont conservées comme informations cartographiques, accompagnées de libellés. Le bandeau **« Démonstration · données fictives »** conserve le texte demandé pour le projet. La carte et sa fiche restent prioritaires dans la disposition mobile.

## Polices hébergées avec le site

Les fichiers WOFF2 latins et latins étendus sont téléchargés sans modification depuis **Google Fonts**, le 4 octobre 2026 :

- [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk), version de diffusion v22 ;
- [IBM Plex Sans](https://fonts.google.com/specimen/IBM+Plex+Sans), v23 ;
- [IBM Plex Mono](https://fonts.google.com/specimen/IBM+Plex+Mono), v20.

Space Grotesk et IBM Plex Sans sont des fichiers variables ; IBM Plex Mono utilise la graisse 400. `font-display: swap` conserve le texte lisible pendant leur chargement. Le navigateur n'appelle pas Google Fonts à la consultation du site.

Les licences originales viennent du [dépôt Google Fonts](https://github.com/google/fonts/tree/main/ofl) et sont livrées dans `web/public/fonts/`. Voir [NOTICE.md](../NOTICE.md) pour les droits des logos, du code et des données.
