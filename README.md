# psf-modeling

Simulation pédagogique de fonctions d’étalement du point (PSF) en optique de Fourier, avec un focus sur une pupille **JWST simplifiée** et sur d’autres géométries de pupille (circulaire, hexagonale, pupille obscurée).

## Objectif du projet

Ce dépôt montre comment la géométrie d’une pupille télescope (segments, obstruction centrale, spiders) se traduit dans le plan image par une PSF structurée (cœur, anneaux, aigrettes de diffraction).

L’objectif est double :
- fournir une base de simulation simple et reproductible ;
- proposer une lecture physique intuitive des figures obtenues.

## Hypothèses physiques

Le modèle utilisé est volontairement simple :
- régime de **Fraunhofer** (champ lointain) ;
- modèle **monochromatique** ;
- pupille **binaire** (transmission 0/1) ;
- pas d’aberrations de phase instrumentales.

Ces hypothèses suffisent pour reproduire les signatures de diffraction principales attendues.

## Méthode : de la pupille à la PSF

1. Construction d’une carte de pupille 2D (JWST simplifié ou géométrie alternative).  
2. Calcul du champ image complexe par transformée de Fourier 2D :  
   \(E \propto \mathcal{F}\{P\}\).  
3. Calcul de la PSF intensité :  
   \(\mathrm{PSF} = |E|^2\).  
4. Normalisation à flux total unité.  
5. Visualisation en échelle logarithmique pour voir cœur + structures faibles.

## Figures principales

### 1) JWST : pupille et PSF
Fichier : `figures/jwst_pupil_psf.png`

- À gauche : pupille segmentée (18 segments) avec spiders.  
- À droite : PSF correspondante.  
- Interprétation : on retrouve les signatures attendues d’un miroir segmenté et de ses supports (aigrettes marquées + structures secondaires liées à la segmentation).

### 2) Pupille alternative : exemple synthétique
Fichier : `figures/other_pupil_psf.png`

- Exemple de pupille non-JWST (selon les options du script).  
- La PSF montre bien comment un changement de géométrie modifie la distribution d’énergie (forme du cœur, anneaux, directionnalité des aigrettes).

## Utilisation rapide

```bash
python PSF_JWST.py --no-show
python view_PSF.py --no-show
python others_PSF.py --no-show
```

## Structure minimale

- `PSF_JWST.py` : génération pupille JWST simplifiée + PSF + figure.
- `view_PSF.py` : lecture d’une pupille sauvegardée et affichage de la PSF.
- `others_PSF.py` : essais sur d’autres pupilles.
- `src/psf_modeling/` : fonctions modulaires (pupilles, PSF, plotting).
- `figures/` : figures générées.
- `tests/` : tests unitaires.

## Limites actuelles

Le projet ne modélise pas encore les effets polychromatiques, les aberrations de phase ni la calibration en unités angulaires instrumentales (arcsec, λ/D).
