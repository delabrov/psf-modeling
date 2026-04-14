# psf-modeling

Simulation pédagogique de PSF (Point Spread Function) en optique de Fourier à partir de pupilles télescope.

Le projet montre comment la géométrie de pupille (segments, obstruction, spiders) transforme une source ponctuelle en structure de diffraction dans le plan image.

## Objectif actuel

- Générer une pupille JWST simplifiée (18 segments + spiders).
- Calculer la PSF normalisée par FFT 2D.
- Visualiser pupille et PSF en échelle log.
- Fournir une base propre et modulaire pour enrichissements scientifiques ultérieurs.

Note: dans cette version, le scope est volontairement centré sur JWST uniquement (pas de comparaison HST).

## Hypothèses scientifiques explicites

- Régime de Fraunhofer (champ lointain).
- Modèle monochromatique et sans aberrations de phase.
- Pupille binaire (transmission 0/1).
- PSF calculée comme `|FFT(pupil)|^2`, puis normalisée à flux total unité.

## Structure du dépôt

- `src/psf_modeling/pupil.py` : génération de pupilles (JWST, cercle, hexagone), spiders, I/O.
- `src/psf_modeling/psf.py` : calcul PSF et log10(PSF).
- `src/psf_modeling/plotting.py` : visualisation standard pupille + PSF.
- `PSF_JWST.py` : script principal (génère pupille JWST, PSF et figure).
- `view_PSF.py` : recharge une pupille sauvegardée et affiche la PSF.
- `others_PSF.py` : exemples de pupilles alternatives.
- `scripts/` : scripts utilitaires pour génération/sauvegarde automatisée.
- `tests/` : tests unitaires de base.
- `figures/` : figures générées.

## Installation

### Option pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Option conda

```bash
conda env create -f environment.yml
conda activate psf-modeling
```

## Usage rapide

Générer la pupille JWST + PSF + figure:

```bash
python PSF_JWST.py --no-show
```

Afficher la PSF à partir d'une pupille sauvegardée:

```bash
python view_PSF.py --no-show
```

Tester des pupilles alternatives:

```bash
python others_PSF.py --pupil hexagon --with-spiders --no-show
```

## Résultats générés

- Pupille texte compatible historique: `pupil_JWST.dat`
- Figure principale: `figures/jwst_pupil_psf.png`

## Validation rapide

```bash
pytest -q
```

## Prochaines extensions (hors scope actuel)

- Échelle physique (`lambda/D`, arcsec).
- Profils radiaux et énergie encerclée.
- Aberrations de phase et polychromatisme.
