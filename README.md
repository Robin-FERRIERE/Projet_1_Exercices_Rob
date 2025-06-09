# Projet 1 – Suivi des exercices Rob

Ce dépôt contient les scripts et les données permettant d’automatiser le suivi des exercices d’apprentissage de Robin via GitHub Projects.

## 🔧 Fonctionnalités principales

- Lecture d’un fichier `exercices.json` structurant les exercices.
- Génération automatique des issues GitHub pour chaque exercice.
- Ajout de chaque issue dans le GitHub Project.
- Mise à jour automatique du champ **Statut** dans le kanban GitHub.

## 📁 Structure des fichiers

- `main.py` : script principal d’automatisation.
- `exercices.json` : base de données des exercices (format JSON).
- `.env` : variables d’environnement (token GitHub, ID projet).
- `README.md` : ce fichier !

## 🚀 Pour exécuter le projet

1. Cloner le dépôt :
```bash
git clone https://github.com/Robin-FERRIERE/Projet_1_Exercices_Rob.git
cd Projet_1_Exercices_Rob
```

2. Créer un fichier `.env` avec les informations suivantes :
```
GITHUB_TOKEN=ghp_...
GITHUB_PROJECT_ID=PVT_...
```

3. Lancer le script :
```bash
python3 main.py
```

## 🧠 Remarques

- Le script vérifie si une issue existe déjà (via un identifiant unique dans le corps).
- Il utilise l’API GraphQL de GitHub.
- Le champ `statut` dans le fichier JSON peut être : `À faire`, `En cours`, `Fait`.


✅ Processus de suivi d’un nouvel exercice
1. 💡 Une idée d’exercice émerge
Par exemple : "Faire un script Hello World en Python"
Tu peux me la dicter à l’écrit ou simplement dire :

“Je veux ajouter un exercice Hello World.”

2. 🧠 Tu m’indiques de l’ajouter à ton suivi
Je prends cette idée et je l’ajoute dans la source officielle des exercices : le fichier exercices.json.
Ce fichier est la base de référence.

3. 🔄 Génération automatique du tableau
Tu exécutes un script Python (generer_markdown.py) qui :

lit le fichier exercices.json,

génère automatiquement un tableau Markdown bien structuré,

le sauvegarde dans suivi_exercices_rob.md.

👉 Ce tableau sert de vue synthétique de ton suivi.

4. ⬆️ Mise à jour du dépôt GitHub
Tu commits & push le projet (y compris le .md) vers ton dépôt GitHub.

5. 📌 (Optionnel) Synchronisation avec ton Kanban GitHub
Tu peux ajouter chaque exercice comme une carte dans ton Kanban GitHub Projects, soit :

