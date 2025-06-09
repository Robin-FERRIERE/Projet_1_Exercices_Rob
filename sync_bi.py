import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# === CHARGEMENT DES VARIABLES D'ENVIRONNEMENT ===
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "Projet_1_Exercices_Rob"
GITHUB_OWNER = "Robin-FERRIERE"
GITHUB_PROJECT_ID = os.getenv("GITHUB_PROJECT_ID")
EXERCICES_FILE = "exercices_with_updatedAt.json"

HEADERS = {"Authorization": f"bearer {GITHUB_TOKEN}"}

# === UTILS ===
def parse_iso_date(iso_str):
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

def load_local_exercices():
    with open(EXERCICES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_local_exercices(exercices):
    with open(EXERCICES_FILE, "w", encoding="utf-8") as f:
        json.dump(exercices, f, indent=2, ensure_ascii=False)

# === RÉCUPÉRATION DES DONNÉES GITHUB ===
def get_project_issues_with_metadata():
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              updatedAt
              content {
                ... on Issue {
                  id
                  number
                  title
                  updatedAt
                }
              }
              fieldValues(first: 10) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field {
                      ... on ProjectV2SingleSelectField {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"projectId": GITHUB_PROJECT_ID}
    response = requests.post("https://api.github.com/graphql", headers=HEADERS, json={"query": query, "variables": variables})
    data = response.json()

    if "errors" in data:
        print("❌ Erreur lors de la récupération du projet GitHub :", data["errors"])
        return []

    items = data["data"]["node"]["items"]["nodes"]
    results = []

    for item in items:
        content = item.get("content")
        if not content:
            continue

        fields = {
            f["field"]["name"]: f["name"]
            for f in item["fieldValues"]["nodes"]
            if f.get("field")
        }

        results.append({
            "card_id": item["id"],
            "issue_id": content["id"],
            "number": content["number"],
            "title": content["title"],
            "updatedAt": item["updatedAt"],  # ← c’est la carte, pas l’issue !
            "statut": fields.get("Statut"),
            "priorite": fields.get("Priorité"),
        })

    return results

def get_custom_fields_and_options(project_id):
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 50) {
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
    response = requests.post("https://api.github.com/graphql", headers=HEADERS, json={"query": query, "variables": {"projectId": project_id}})
    data = response.json()

    if "errors" in data:
        print("❌ Erreur récupération des champs personnalisés :", data["errors"])
        return {}

    fields = {}
    for field in data["data"]["node"]["fields"]["nodes"]:
        if "options" in field and "name" in field:
            field_name = field["name"]
            field_id = field["id"]
            options = {opt["name"]: opt["id"] for opt in field["options"]}
            fields[field_name] = {
                "id": field_id,
                "options": options
            }

    return fields
# === COMPARAISON ===
def compare_and_sync(local_exercices, github_issues):
    local_map = {e["issue_node_id"]: e for e in local_exercices if "issue_node_id" in e}
    github_map = {g["issue_id"]: g for g in github_issues}

    updates_from_local = []
    updates_from_github = []

    for issue_id, local in local_map.items():
        github = github_map.get(issue_id)
        if not github:
            continue
        local_date = parse_iso_date(local.get("updatedAt", "2000-01-01T00:00:00Z"))
        github_date = parse_iso_date(github.get("updatedAt", "2000-01-01T00:00:00Z"))

        if local_date > github_date:
            updates_from_local.append((local, github))
        elif github_date > local_date:
            updates_from_github.append((github, local))

    return updates_from_local, updates_from_github

# === MISE À JOUR ===
def update_local_from_github(local_exercices, updates_from_github):
    id_map = {e["issue_node_id"]: e for e in local_exercices}
    updated_count = 0

    for github, _ in updates_from_github:
        local_exo = id_map.get(github["issue_id"])
        if not local_exo:
            print(f"❌ Exercice local avec issue_node_id {github['issue_id']} introuvable.")
            continue

        print(f"✏️ Mise à jour de l'exercice {local_exo['id']} depuis GitHub")
        local_exo["statut"] = github.get("statut", local_exo.get("statut"))
        local_exo["priorite"] = github.get("priorite", local_exo.get("priorite"))
        local_exo["updatedAt"] = github["updatedAt"]
        updated_count += 1

    print(f"\n✅ {updated_count} exercices mis à jour localement.")
    return local_exercices

def update_github_field(project_id, item_id, field_id, value_id):
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $valueId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $valueId }
      }) {
        projectV2Item {
          id
        }
      }
    }
    """
    variables = {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "valueId": value_id
    }
    response = requests.post("https://api.github.com/graphql", headers=HEADERS, json={"query": mutation, "variables": variables})
    result = response.json()
    if "errors" in result:
        print(f"❌ Erreur mise à jour GitHub : {result['errors']}")
    else:
        print(f"✅ Mise à jour réussie pour l’item {item_id}")

def update_github_from_local(updates_from_local, custom_fields):
    statut_field_id = custom_fields["Status"]["id"]
    statut_options = custom_fields["Status"]["options"]
    priorite_field_id = custom_fields["Priority"]["id"]
    priorite_options = custom_fields["Priority"]["options"]

    updated_count = 0
    for local, github in updates_from_local:
        card_id = github["card_id"]
        local_statut = local.get("status")
        if local_statut != github.get("status"):
            value_id = statut_options.get(local_statut)
            if value_id:
                update_github_field(GITHUB_PROJECT_ID, card_id, statut_field_id, value_id)
                updated_count += 1
                
        if local.get("priorite") != github.get("priorite"):
            value_id = priorite_options.get(local["priorite"])
            if value_id:
                update_github_field(GITHUB_PROJECT_ID, card_id, priorite_field_id, value_id)
                updated_count += 1

    print(f"\n🚀 {updated_count} mises à jour effectuées sur GitHub.")

# === MAIN ===
def main():
    print("🔄 Synchronisation bidirectionnelle en cours...")
    local_exercices = load_local_exercices()
    print(f"📁 {len(local_exercices)} exercices trouvés dans le fichier local.")

    github_issues = get_project_issues_with_metadata()
    print(f"🐙 {len(github_issues)} issues récupérées depuis GitHub.")
    with open("github_issues.json", "w", encoding="utf-8") as f:
      json.dump(github_issues, f, indent=2, ensure_ascii=False)
    print("💾 Export GitHub enregistré dans github_issues.json")

    custom_fields = get_custom_fields_and_options(GITHUB_PROJECT_ID)
    updates_from_local, updates_from_github = compare_and_sync(local_exercices, github_issues)

    print("\n📤 À envoyer vers GitHub :")
    for local, _ in updates_from_local:
        print(f"- {local['id']} (local plus récent)")

    print("\n📥 À mettre à jour localement :")
    for github, _ in updates_from_github:
        print(f"- {github['title']} (GitHub plus récent)")

    if updates_from_github:
        local_exercices = update_local_from_github(local_exercices, updates_from_github)
        save_local_exercices(local_exercices)
        print("💾 Fichier exercices.json mis à jour.")

    if updates_from_local:
        update_github_from_local(updates_from_local, custom_fields)

if __name__ == "__main__":
    main()
