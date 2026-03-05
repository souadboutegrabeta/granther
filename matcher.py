from anthropic import Anthropic
from dotenv import load_dotenv
import json

load_dotenv(dotenv_path="../.env")

client = Anthropic()

def charger_grants():
    with open("grants.json", "r", encoding="utf-8") as f:
        return json.load(f)

def matcher_grants(profil_association):
    """Analyse le profil d'une association et trouve les grants correspondants"""
    
    grants = charger_grants()
    
    reponse = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system="""Tu es un expert en financement d'associations féministes. 
        Tu analyses le profil d'une association et tu calcules un score de matching avec chaque grant disponible.
        Réponds UNIQUEMENT avec un JSON valide, sans texte avant ou après.""",
        messages=[
            {"role": "user", "content": f"""
            Voici le profil de l'association :
            {json.dumps(profil_association, ensure_ascii=False)}
            
            Voici les grants disponibles :
            {json.dumps(grants, ensure_ascii=False)}
            
            Pour chaque grant, calcule un score de matching entre 0 et 100 basé sur :
            - La correspondance entre la mission de l'association et les critères du grant
            - La zone géographique
            - La taille de l'association et les montants proposés
            
            Retourne UNIQUEMENT ce JSON :
            [
                {{
                    "grant_id": 1,
                    "nom": "nom du grant",
                    "organisme": "organisme",
                    "montant_min": 5000,
                    "montant_max": 50000,
                    "score": 85,
                    "raison": "Explication courte du matching en 1-2 phrases",
                    "deadline": "date",
                    "url": "lien"
                }}
            ]
            Trie par score décroissant et inclus uniquement les grants avec un score supérieur à 40.
            """}
        ]
    )
    
    try:
        texte = reponse.content[0].text.strip()
        # Nettoyer le JSON si besoin
        texte = texte.replace("```json", "").replace("```", "").strip()
        resultats = json.loads(texte)
        return resultats
    except Exception as e:
        # Essayer de corriger le JSON malformé
        try:
            import re
            texte = reponse.content[0].text.strip()
            texte = re.sub(r',\s*]', ']', texte)
            texte = re.sub(r',\s*}', '}', texte)
            resultats = json.loads(texte)
            return resultats
        except:
            print("Erreur parsing JSON:", e)
            return []

if __name__ == "__main__":
    # Test avec DesCodeuses
    profil_test = {
        "nom": "DesCodeuses",
        "mission": "Former des femmes aux métiers du numérique",
        "activites": ["formation", "inclusion numérique", "empowerment féminin"],
        "zone": "France",
        "taille": "petite association",
        "budget_annuel": 50000
    }
    
    print("🔍 Recherche de grants pour DesCodeuses...")
    resultats = matcher_grants(profil_test)
    
    print(f"\n🎉 {len(resultats)} grants trouvés !\n")
    for r in resultats:
        print(f"✅ {r['score']}% - {r['nom']} | {r['organisme']}")
        print(f"   💰 {r['montant_min']}€ - {r['montant_max']}€")
        print(f"   📝 {r['raison']}")
        print(f"   📅 {r['deadline']}\n")