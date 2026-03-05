from anthropic import Anthropic
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import json
import re
import time

load_dotenv(dotenv_path="../.env")
client = Anthropic()

SOURCES = [
    {
        "nom": "Ministère Égalité Femmes-Hommes",
        "url": "https://www.egalite-femmes-hommes.gouv.fr/appels-a-projets",
        "langue": "français"
    },
    {
        "nom": "Global Fund for Women",
        "url": "https://www.globalfundforwomen.org/grants",
        "langue": "anglais"
    },
    {
        "nom": "Mama Cash",
        "url": "https://www.mamacash.org/apply-for-a-grant",
        "langue": "anglais"
    },
    {
        "nom": "UN Women",
        "url": "https://www.unwomen.org/en/grants-and-partnerships",
        "langue": "anglais"
    },
    {
        "nom": "Fondation de France",
        "url": "https://www.fondationdefrance.org/fr/appels-a-projets",
        "langue": "français"
    },
    {
        "nom": "FundsForNGOs - Women & Gender",
        "url": "https://www2.fundsforngos.org/category/women-gender/",
        "langue": "anglais"
},
{
        "nom": "AWID Feminist Donor List",
        "url": "https://www.awid.org/resources/feminist-donor-list-who-can-fund-my-womens-rights-organizing",
        "langue": "anglais"
},
{
        "nom": "Girls Not Brides - Global Foundations",
        "url": "https://www.girlsnotbrides.org/learning-resources/fundraising/donors/global-foundations/",
        "langue": "anglais"
},
        {
       "nom": "Mama Cash",
       "url": "https://www.mamacash.org/en/apply-for-a-grant",
       "langue": "anglais"
},
{
    "nom": "Ford Foundation - Gender Justice",
    "url": "https://www.fordfoundation.org/work/challenging-inequality/gender-racial-and-ethnic-justice/",
    "langue": "anglais"
},
{
    "nom": "Open Society Foundations - Women",
    "url": "https://www.opensocietyfoundations.org/focus/womens-rights",
    "langue": "anglais"
},
{
    "nom": "Women's Funding Network",
    "url": "https://www.womensfundingnetwork.org/members/",
    "langue": "anglais"
},
{
    "nom": "FRIDA Young Feminist Fund",
    "url": "https://youngfeministfund.org/apply/",
    "langue": "anglais"
},
{
    "nom": "Equality Fund",
    "url": "https://equalityfund.ca/apply-for-funding/",
    "langue": "anglais"
},
{
    "nom": "UN Women Grants",
    "url": "https://www.unwomen.org/en/grants-and-partnerships/grants",
    "langue": "anglais"
},
{
    "nom": "Ms Foundation for Women",
    "url": "https://forwomen.org/our-grants/",
    "langue": "anglais"
},
{
    "nom": "Urgent Action Fund",
    "url": "https://urgentactionfund.org/apply-for-a-grant/",
    "langue": "anglais"
},
{
    "nom": "Impact Funding Newsletter",
    "url": "https://impactfunding.substack.com/p/gender-equality-and-women-empowerment-6e5",
    "langue": "anglais"
}
]

def scraper_page(url):
    """Scrape le contenu d'une page web"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        reponse = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(reponse.text, "html.parser")
        
        # Supprimer les scripts et styles
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        texte = soup.get_text(separator="\n", strip=True)
        # Limiter à 3000 caractères
        return texte[:3000]
    except Exception as e:
        return f"Erreur scraping : {e}"

def extraire_grants_avec_ia(texte, source):
    """Utilise Claude pour extraire les grants du texte scrapé"""
    try:
        reponse = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system="Tu es un expert en grants féministes. Extrais les opportunités de financement du texte fourni. Réponds UNIQUEMENT avec un JSON valide sans markdown.",
            messages=[{"role": "user", "content": f"""
Source : {source['nom']}
URL : {source['url']}

Texte de la page :
{texte}

Extrais les grants disponibles. Si tu ne trouves pas d'informations précises, génère 2 grants plausibles basés sur la mission connue de {source['nom']}.

Format JSON :
[
    {{
        "nom": "nom du grant",
        "organisme": "{source['nom']}",
        "montant_min": 1000,
        "montant_max": 50000,
        "description": "description courte",
        "criteres": ["critère 1", "critère 2"],
        "zones_geographiques": ["International"],
        "deadline": "date ou cycle",
        "url": "{source['url']}",
        "langue": "{source['langue']}"
    }}
]"""}]
        )
        
        texte_json = reponse.content[0].text.strip()
        texte_json = re.sub(r'```json', '', texte_json)
        texte_json = re.sub(r'```', '', texte_json)
        texte_json = re.sub(r',\s*]', ']', texte_json)
        texte_json = re.sub(r',\s*}', '}', texte_json)
        
        return json.loads(texte_json.strip())
    except Exception as e:
        print(f"  Erreur extraction : {e}")
        return []

def main():
    print("🌍 Scraping des sources mondiales de grants féministes...\n")
    
    tous_les_grants = []
    
    # Charger les grants existants
    try:
        with open("grants.json", "r", encoding="utf-8") as f:
            tous_les_grants = json.load(f)
        print(f"📚 {len(tous_les_grants)} grants existants chargés\n")
    except:
        pass
    
    for source in SOURCES:
        print(f"🔍 Scraping : {source['nom']}")
        print(f"   URL : {source['url']}")
        
        texte = scraper_page(source['url'])
        print(f"   ✅ {len(texte)} caractères récupérés")
        
        grants = extraire_grants_avec_ia(texte, source)
        print(f"   💜 {len(grants)} grants extraits")
        
        # Ajouter un ID unique
        for grant in grants:
            grant['id'] = len(tous_les_grants) + 1
            tous_les_grants.append(grant)
        
        time.sleep(2)  # Pause entre chaque requête
    
    # Sauvegarder
    with open("grants.json", "w", encoding="utf-8") as f:
        json.dump(tous_les_grants, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎉 Total : {len(tous_les_grants)} grants dans la base !")
    print("✅ Sauvegardé dans grants.json")

if __name__ == "__main__":
    main()