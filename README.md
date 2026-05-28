# taupeNco

## Affichage des chemins pointillés (`J`)

Sur le plateau inférieur (roche mère), certaines cases sont marquées **`J`**.

- **`J` est un point de repère** : la case elle-même se traite comme une case classique (même rendu qu'une case normale du plateau).
- **C'est le segment entre `J` et le centre** du plateau qu'il faut afficher en **pointillés** — pas la case `J` en tant que telle.

En résumé : pour chaque marqueur `J`, tracer une ligne pointillée reliant ce point au centre de l'hexagone.
