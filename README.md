# 📚 Projet_1_Exercices_Rob

Ce dépôt contient un ensemble d'exercices pratiques visant à progresser pas à pas dans l'utilisation de :

- Git & GitHub
- Python
- APIs REST
- Fichiers JSON
- VS Code
- Obsidian
- et l'intégration avec ChatGPT

---

## 🚀 Synchronisation bidirectionnelle

Le script `sync_bi.py` permet de **synchroniser automatiquement** :

- 🗂 le fichier local `exercices_with_updatedAt.json`
- 🗃 le projet GitHub Kanban (GitHub Projects v2)

Il fonctionne **dans les deux sens** :

| Source mise à jour | Destination synchronisée               |
|--------------------|----------------------------------------|
| JSON local         | GitHub Kanban (*Status*, *Priority*)   |
| GitHub Kanban      | JSON local (*status*, *priorité*, `updatedAt`) |

---

## ✅ Prérequis

1. **Python 3.8+**
2. Un fichier `.env` local contenant :

```env
GITHUB_TOKEN=ghp_...
GITHUB_PROJECT_ID=...
💡 Ce fichier est ignoré par Git et ne sera jamais poussé.

Un fichier exercices_with_updatedAt.json avec des champs comme :

id, thematique, langage, status, priorite, updatedAt, issue_node_id, etc.

📜 Utilisation
bash
Copier
Modifier
python3 sync_bi.py
Le script :

Compare les dates updatedAt

Met à jour GitHub (Status / Priority) ou le fichier local selon la source la plus récente

Exporte un fichier github_issues.json pour debug

📁 Structure typique
pgsql
Copier
Modifier
Projet_1_Exercices_Rob/
├── .env
├── .gitignore
├── README.md
├── sync_bi.py
├── main.py
├── exercices_with_updatedAt.json
├── github_issues.json
├── scripts/
│   ├── generer_markdown.py
│   └── sync_to_kanban.py
└── Illustration_Process.png
💡 Idées à venir
Génération d’un .log.md automatique

Détection des exercices orphelins (non liés à une issue GitHub)

Intégration avec un Kanban local (Markdown ou Obsidian)

🙌 Remerciements
Ce projet est construit progressivement en binôme avec ChatGPT, dans une logique d’apprentissage guidé. (Dans les faits, c'est surtout ChatGPT qui a travaillé, et moi suivi comme un âne)