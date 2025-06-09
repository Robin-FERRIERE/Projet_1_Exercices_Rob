import json
from pathlib import Path

def charger_exercices(fichier_json):
    with open(fichier_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def generer_tableau_markdown(exercices):
    lignes = []
    en_tete = "| Thématique | Langage | Outil | Valeur pédagogique | Statut | Date | Device |"
    separateur = "|------------|---------|-------|--------------------|--------|------|--------|"
    lignes.append(en_tete)
    lignes.append(separateur)

    for ex in exercices:
        ligne = f"| {ex['thematique']} | {ex['langage']} | {', '.join(ex['outil'])} | {ex['valeur_pedagogique']} | {ex['statut']} | {ex['date']} | {ex['device']} |"
        lignes.append(ligne)

    return "\n".join(lignes)

if __name__ == '__main__':
    chemin_fichier_json = 'exercices.json'
    chemin_fichier_markdown = 'suivi_exercices_rob.md'

    exercices = charger_exercices(chemin_fichier_json)

    # Supprimer les clés "titre" avant génération
    for ex in exercices:
        if "titre" in ex:
            del ex["titre"]

    tableau = generer_tableau_markdown(exercices)

    with open(chemin_fichier_markdown, 'w', encoding='utf-8') as f:
        f.write(tableau)

    print(f"✅ Tableau généré et sauvegardé dans : {chemin_fichier_markdown}")
