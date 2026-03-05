from anthropic import Anthropic
from dotenv import load_dotenv
import json
import re

load_dotenv(dotenv_path="../.env")
client = Anthropic()

reponse = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=8192,
    system="Tu es un expert en financements pour associations féministes mondiales. Réponds UNIQUEMENT avec un JSON valide, sans texte avant ou après, sans balises markdown.",
    messages=[{"role": "user", "content": """Génère une base de 20 grants réels et internationaux pour associations féministes, droits des femmes, égalité des genres.
    Inclus des sources : France, Europe, USA, Afrique, ONU, fondations privées mondiales comme Ford Foundation, Global Fund for Women, Mama Cash, Open Society Foundations.
    
    Format JSON strict :
    [
        {
            "id": 1,
            "nom": "nom du grant",
            "organisme": "qui finance",
            "montant_min": 1000,
            "montant_max": 50000,
            "description": "description courte",
            "criteres": ["critère 1", "critère 2"],
            "zones_geographiques": ["France", "International"],
            "deadline": "date ou cycle",
            "url": "site web",
            "langue": "français ou anglais"
        }
    ]"""}]
)

texte = reponse.content[0].text.strip()
texte = re.sub(r'```json', '', texte)
texte = re.sub(r'```', '', texte)
texte = re.sub(r',\s*]', ']', texte)
texte = re.sub(r',\s*}', '}', texte)
texte = texte.strip()

try:
    grants = json.loads(texte)
    with open("grants.json", "w", encoding="utf-8") as f:
        json.dump(grants, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(grants)} grants générés et sauvegardés !")
    for g in grants:
        print(f"- {g['nom']} | {g['organisme']}")
except Exception as e:
    print(f"Erreur : {e}")
    print(texte[:500])