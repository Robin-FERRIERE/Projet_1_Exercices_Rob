import json
import requests
from dotenv import load_dotenv
import os

# === CHARGER LES VARIABLES D'ENVIRONNEMENT ===
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "Projet_1_Exercices_Rob"
GITHUB_OWNER = "Robin-FERRIERE"
EXERCICES_FILE = "exercices.json"
GITHUB_PROJECT_ID = os.getenv("GITHUB_PROJECT_ID")
print(f"Token chargé : {'OK' if GITHUB_TOKEN else 'NON TROUVÉ'}")
print(f"Project ID chargé : {'OK' if GITHUB_PROJECT_ID else 'NON TROUVÉ'}")

# === SESSION GITHUB ===
session = requests.Session()
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# === CHARGEMENT DU JSON ===
with open(EXERCICES_FILE, "r", encoding="utf-8") as f:
    exercices = json.load(f)

# === FONCTION : vérifier si une issue existe déjà ===
def issue_exists_by_id(session, repo, owner, token, exo_id):
    query = """
    query($repo: String!, $owner: String!) {
      repository(name: $repo, owner: $owner) {
        issues(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes {
            number
            body
          }
        }
      }
    }
    """
    variables = {"repo": repo, "owner": owner}
    headers = {"Authorization": f"bearer {token}"}
    response = session.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    data = response.json()
    issues = data["data"]["repository"]["issues"]["nodes"]
    return any(f"<!-- EXO-ID: {exo_id} -->" in issue["body"] for issue in issues)

# === FONCTION : créer une nouvelle issue ===
def create_issue(session, repo, owner, token, title, body):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    payload = {"title": title, "body": body}
    headers = {"Authorization": f"token {token}"}
    response = session.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print(f"Issue créée : {title}")
    else:
        print(f"Erreur création issue : {response.text}")

# === FONCTION : récupérer l'ID de l'issue ===
def get_issue_node_id(session, repo, owner, token, issue_number):
    query = """
    query($repo: String!, $owner: String!, $issue: Int!) {
      repository(name: $repo, owner: $owner) {
        issue(number: $issue) {
          id
        }
      }
    }
    """
    variables = {"repo": repo, "owner": owner, "issue": issue_number}
    headers = {"Authorization": f"bearer {token}"}
    response = session.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    return response.json()["data"]["repository"]["issue"]["id"]

# === FONCTION : ajouter une issue au projet ===
def add_issue_to_project(session, token, project_id, issue_node_id):
    query = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item { id }
      }
    }
    """
    variables = {"projectId": project_id, "contentId": issue_node_id}
    headers = {"Authorization": f"bearer {token}"}
    response = session.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    if "errors" in response.json():
        print("Erreur ajout au projet :", response.json()["errors"])
    else:
        print("✔️  Issue ajoutée au projet")

# === FONCTION : récupérer l'ID de l'item lié à une issue dans le projet ===
def get_project_item_id(issue_number, project_id, headers):
    query = """
    query($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          projectItems(first: 10) {
            nodes {
              id
              project { id }
            }
          }
        }
      }
    }
    """
    variables = {
        "owner": GITHUB_OWNER,
        "repo": GITHUB_REPO,
        "issueNumber": issue_number
    }
    response = requests.post("https://api.github.com/graphql", headers=headers, json={"query": query, "variables": variables})
    data = response.json()
    try:
        items = data["data"]["repository"]["issue"]["projectItems"]["nodes"]
        for item in items:
            if item["project"]["id"] == project_id:
                return item["id"]
    except:
        return None

# === FONCTION : récupérer les options du champ 'Statut' ===
def get_status_field_and_options(session, token, project_id):
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"projectId": project_id}
    headers = {"Authorization": f"bearer {token}"}
    response = session.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=headers
    )

    print("=== RAW GitHub response ===")
    print(response.status_code)
    print(response.text)

    try:
        data = response.json()
        fields = data["data"]["node"]["fields"]["nodes"]
        for field in fields:
            if "status" in field.get("name", "").lower():
                return field["id"], {opt["name"]: opt["id"] for opt in field["options"]}
        print("Champ 'Statut' non trouvé.")
        return None, {}
    except Exception as e:
        print("Erreur lors de la récupération du champ Statut :", e)
        return None, {}

# === FONCTION : mettre à jour le champ 'Statut' ===
def update_project_status(session, token, project_id, item_id, status_field_id, status_option_id):
    query = """
    mutation($input: UpdateProjectV2ItemFieldValueInput!) {
      updateProjectV2ItemFieldValue(input: $input) {
        projectV2Item { id }
      }
    }
    """
    variables = {
        "input": {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": status_field_id,
            "value": { "singleSelectOptionId": status_option_id }
        }
    }
    headers = {"Authorization": f"bearer {token}"}
    response = session.post("https://api.github.com/graphql", json={"query": query, "variables": variables}, headers=headers)
    if "errors" in response.json():
        print("❌ Erreur mise à jour statut :", response.json()["errors"])
    else:
        print("✅ Statut mis à jour")

# === TRAITEMENT DE CHAQUE EXERCICE ===
for ex in exercices:
    ex_id = ex.get("id")
    titre = f"{ex_id} – {ex['thematique']}"
    corps = f"""**Objectif pédagogique :** {ex['valeur_pedagogique']}

Langage : {ex['langage']}
Outils : {', '.join(ex['outil'])}

<!-- EXO-ID: {ex_id} -->
"""

    if not issue_exists_by_id(session, GITHUB_REPO, GITHUB_OWNER, GITHUB_TOKEN, ex_id):
        create_issue(session, GITHUB_REPO, GITHUB_OWNER, GITHUB_TOKEN, titre, corps)
        print(f"Issue créée pour : {ex_id}")
    else:
        print(f"Issue déjà existante pour : {ex_id}")

    try:
        issue_number = int(titre.split("–")[0].split("-")[-1])
        issue_node_id = get_issue_node_id(session, GITHUB_REPO, GITHUB_OWNER, GITHUB_TOKEN, issue_number)
        add_issue_to_project(session, GITHUB_TOKEN, GITHUB_PROJECT_ID, issue_node_id)

        item_id = get_project_item_id(issue_number, GITHUB_PROJECT_ID, headers)
        if not item_id:
            print(f"❌ Pas d'item trouvé pour {ex_id}")
            continue

        status_field_id, options = get_status_field_and_options(session, GITHUB_TOKEN, GITHUB_PROJECT_ID)

        STATUT_MAPPING = {
            "À faire": "Todo",
            "En cours": "In Progress",
            "Fait": "Done"
        }

        statut_fr = ex.get("statut", "À faire")
        statut = STATUT_MAPPING.get(statut_fr, "Todo")
        option_id = options.get(statut)

        if not option_id:
            print(f"❌ Statut non reconnu : {statut}")
            continue

        update_project_status(session, GITHUB_TOKEN, GITHUB_PROJECT_ID, item_id, status_field_id, option_id)
    except Exception as e:
        print(f"❌ Erreur générale pour {ex_id} : {e}")