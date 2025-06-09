import os
import requests
import json
from dotenv import load_dotenv

# Charger le token depuis le fichier .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = "Robin-FERRIERE"
REPO_NAME = "Projet_1_Exercices_Rob"
PROJECT_NUMBER = 2

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github+json"
}

# Étape 1 : Obtenir l'ID du projet
def get_project_id():
    query = """
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          id
        }
      }
    }
    """
    variables = {
        "login": GITHUB_USERNAME,
        "number": PROJECT_NUMBER
    }
    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": query, "variables": variables}
    )
    return response.json()["data"]["user"]["projectV2"]["id"]

# Étape 2 : Créer une issue GitHub
def create_issue(title, body=""):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/issues"
    payload = {
        "title": title,
        "body": body
    }
    response = requests.post(url, headers=headers, json=payload)
    issue_data = response.json()
    return issue_data["node_id"]

# Étape 3 : Ajouter l’issue au projet
def add_issue_to_project(project_id, issue_node_id):
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {
        projectId: $projectId,
        contentId: $contentId
      }) {
        item {
          id
        }
      }
    }
    """
    variables = {
        "projectId": project_id,
        "contentId": issue_node_id
    }
    response = requests.post(
        "https://api.github.com/graphql",
        headers=headers,
        json={"query": mutation, "variables": variables}
    )
    return response.json()

if __name__ == "__main__":
    project_id = get_project_id()
    print(f"✅ Projet GitHub trouvé : {project_id}")

    title = "Hello World en Python"
    issue_node_id = create_issue(title)
    print(f"🐛 Issue créée (node_id) : {issue_node_id}")

    result = add_issue_to_project(project_id, issue_node_id)
    print("📌 Résultat de l'ajout au Kanban :", json.dumps(result, indent=2))
