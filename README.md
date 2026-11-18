# GTA VI — The Ultimate Guide

Site statique de fans, principalement en français, consacré aux sources officielles, aux reviews et aux outils communautaires autour de GTA VI. Le site n’est ni affilié ni sponsorisé par Rockstar Games ou Take-Two Interactive.

## État du projet

- 54 fichiers HTML au total actuellement : une page d’accueil, 51 pages de contenu et deux pages légales en attente des vraies coordonnées du responsable.
- Aucune compilation ou dépendance npm nécessaire pour servir le site.
- Les 53 visuels locaux sont des illustrations éditoriales générées en JPEG haute résolution (1672×941 pour la majorité, portraits 1024×1536); aucun PNG/SVG ni capture Rockstar/presse n’est conservé comme image du site. Ils ne sont jamais présentés comme des captures du jeu.
- Les listes de guides tiers, avis de presse, rapports Reddit/X et données de cartes communautaires sont étiquetés par provenance et niveau de preuve.
- Les outils de progression et le quiz enregistrent leurs données dans le `localStorage` du navigateur; ils ne transmettent pas ces données à un compte ou serveur applicatif.
- Le trailer YouTube ne se charge qu’après activation volontaire. Les polices sont système/locales; les vignettes Hypebeast ont été remplacées par des liens vers la page source.

## Prévisualisation locale

```bash
npm run dev
# ou
python3 -m http.server 8080 --bind 0.0.0.0
```

Puis ouvrir `http://localhost:8080/`. Le site est autonome et utilise des chemins relatifs afin de fonctionner à la racine d’un domaine ou sous un chemin de projet.

## Contrôles avant publication

```bash
npm run audit
npm run check:js
```

L’audit vérifie les métadonnées, alt d’images, liens et fragments locaux, couverture du sitemap, cibles de recherche, JPEG, URL canoniques et l’absence d’images sourcées non générées. Il échoue aussi volontairement tant que les champs légaux contiennent des valeurs à remplir. En local, le domaine `gta6-ultimate-guide.example.com` reste un placeholder; le workflow GitHub Pages le remplace automatiquement dans le build CI.

### Publication sur GitHub Pages

Le workflow `.github/workflows/pages.yml` configure l’origine à partir de l’URL effective du site renvoyée par GitHub Pages, puis réécrit canonicals, Open Graph, sitemap et robots avant l’audit et le déploiement. Il prend donc en charge automatiquement les URL de type `https://votre-compte.github.io/nom-du-depot` sans avoir à connaître à l’avance le nom du dépôt. Dans les réglages GitHub du dépôt, sélectionnez **Settings → Pages → Build and deployment → GitHub Actions**, puis poussez la branche `main` ou lancez le workflow manuellement. Vérifiez le premier run et l’URL publique avant de soumettre le sitemap.

Pour un test manuel/local après que l’URL soit connue, exécuter :

```bash
python3 scripts/set_site_origin.py https://votre-compte.github.io/nom-du-depot --apply
npm run audit
npm run check:js
```

Les coordonnées éditoriales communiquées par l’éditeur (CIM, association loi 1901, 49 avenue d’Italie, 75013 Paris; contact `gta6guide@gmail.com`; directeur de publication Peter Slogan; responsable du traitement Peter Slogan) sont renseignées dans les pages légales. Avant l’ouverture publique, l’éditeur doit vérifier l’exactitude de ces mentions et les obligations applicables à sa situation. Ne publiez pas de valeurs inventées.

## Hébergement statique

Le dépôt peut être servi sans build par GitHub Pages, Netlify ou Vercel. Un workflow GitHub Pages et des exemples Netlify/Vercel sont fournis; choisir et configurer un seul fournisseur, ajouter le domaine personnalisé si nécessaire, activer HTTPS et vérifier le sitemap/canonicals avec l’URL publique.

## Provenance et droits

- Les marques, noms, personnages et captures GTA VI appartiennent à leurs titulaires respectifs. Le guide est indépendant.
- `assets/images/official/` et `assets/images/press/` ne contiennent aucune image tierce locale; leurs README ne sont conservés que comme notes de provenance et indiquent l’absence de captures utilisées. Les 53 images référencées sont des illustrations génériques originales et non canoniques.
- Les reviews, guides et médias externes cités dans les pages restent crédités par des liens textuels; aucune image de presse ou capture Rockstar n’est intégrée.
- Réviser les droits/conditions des médias, de la musique et des embeds avant toute exploitation commerciale. Les sons locaux ont leur propre registre `assets/audio/README.md`.

## Notes de publication

Le workspace local conserve un domaine canonique de test; le build GitHub Pages remplace automatiquement les URL canoniques, Open Graph, du sitemap et de robots.txt par l’URL retournée par `configure-pages`. Toutes les images sourcées ont été retirées et les 53 visuels sont des JPG générés. Le workflow restera bloqué jusqu’à la saisie des informations légales réelles de l’éditeur et à la vérification finale des obligations applicables.
