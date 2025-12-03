import os
import json
from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import math
import re
import unicodedata
from pathlib import Path 

# Chemin vers le dossier "data"
BASE_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_PATH, "..", "data")  # remonte d'un dossier puis entre dans "data"

# Définir les chemins complets vers les fichiers JSON
SYMPTOMES_PATH = os.path.join(DATA_PATH, "symptomes.json")
MALADIES_PATH = os.path.join(DATA_PATH, "maladies.json")
LIEUX_PATH = os.path.join(DATA_PATH, "lieu.json")

# Fonction pour charger un fichier JSON
def charger_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

MAX_MESSAGES = 100

# ========== Limite de messages ==========
class ActionVerifierLimiteMessages(Action):
    def name(self) -> Text:
        return "action_verifier_limite_messages"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nb_messages = tracker.get_slot("nb_messages") or 0
        if nb_messages >= MAX_MESSAGES:
            dispatcher.utter_message(response="utter_attente")
            return []
        return []

class ActionIncrementerMessages(Action):
    def name(self) -> Text:
        return "action_incrementer_messages"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nb_messages = tracker.get_slot("nb_messages") or 0
        return [SlotSet("nb_messages", nb_messages + 1)]

# ========== Diagnostic à partir des symptômes ==========
class ActionDiagnostiquerMaladie(Action):
    def name(self) -> Text:
        return "action_diagnostiquer_maladie"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Récupérer les symptômes que l'utilisateur a écrits
        symptomes_utilisateur = tracker.latest_message.get('text', '').lower()

        if not symptomes_utilisateur:
            dispatcher.utter_message(text="Je n'ai pas bien compris vos symptômes. Pouvez-vous les reformuler ?")
            return []

        try:
            with open('data/symptomes.json', 'r', encoding='utf-8') as f:
                data_symptomes = json.load(f)
        except Exception as e:
            dispatcher.utter_message(text=f"Erreur lors du chargement des données médicales : {str(e)}")
            return []

        # Initialisation
        maladie_probable = None
        max_symptomes_trouves = 0

        # Vérification des correspondances
        for maladie, liste_symptomes in data_symptomes.items():
            correspondance = sum(1 for symptome in liste_symptomes if symptome.lower() in symptomes_utilisateur)
            if correspondance > max_symptomes_trouves:
                max_symptomes_trouves = correspondance
                maladie_probable = maladie

        if maladie_probable and max_symptomes_trouves > 0:
            dispatcher.utter_message(text=f"Selon les symptômes que vous avez décrits, vous pourriez souffrir de {maladie_probable}.")
            return [
                SlotSet("symptomes", symptomes_utilisateur),
                SlotSet("maladie", maladie_probable),
                SlotSet("diagnostic", maladie_probable)
            ]
        else:
            dispatcher.utter_message(text="Je ne peux pas déterminer la maladie à partir des symptômes donnés. Veuillez vérifier ou ajouter plus de détails.")
            return []

class ActionHopitalProcheParLieu(Action):
    def name(self) -> Text:
        return "action_hopital_proche_par_lieu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get("text").lower()
        lieux_dict = charger_json(LIEUX_PATH)

        # Nettoyage message (sans ponctuation)
        message_clean = re.sub(r"[^\w\s]", "", message.lower())

        lieu_trouve = None

        for lieu in lieux_dict:
            # Nettoyage du nom du lieu pour comparaison
            lieu_clean = lieu.lower().replace("-", " ").replace("_", " ")
            if lieu_clean in message_clean:
                lieu_trouve = lieu
                hopitaux = lieux_dict[lieu]
                liste_hopitaux = ", ".join(hopitaux)
                dispatcher.utter_message(text=f"À {lieu}, vous pouvez aller à : {liste_hopitaux}")
                return [SlotSet("lieu", lieu)]

        dispatcher.utter_message(text="Je n’ai pas trouvé d’hôpital correspondant à ce lieu. Veuillez préciser le nom du village, de la ville ou du quartier.")
        return []

# --- utilitaires ---
def normalize(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^\w\s]", " ", s)
    s = s.replace("-", " ").replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def charger_json(path: str) -> dict:
    import json
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def creer_index_maladies(data: dict) -> dict:
    """Retourne {nom_normalisé: nom_original}"""
    idx = {}
    for nom in data.keys():
        nom_norm = normalize(nom)
        idx[nom_norm] = nom
    return idx

class ActionFournirMedicamentsEtConseilsMaladie(Action):
    def name(self) -> Text:
        return "action_fournir_medicaments_et_conseils_maladie"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        message = tracker.latest_message.get("text", "") or ""
        msg_norm = normalize(message)

        maladies_dict = charger_json(MALADIES_PATH)
        slot_maladie = tracker.get_slot("maladie")
        events: List[Dict[Text, Any]] = []

        # --- Détecter directement la maladie dans le message ---
        maladie_trouvee = None
        for mal in maladies_dict:
            mal_norm = normalize(mal)
            # recherche mot entier, insensible aux accents/majuscules/tirets
            if re.search(rf"\b{re.escape(mal_norm)}\b", msg_norm):
                maladie_trouvee = mal
                break

        # --- Si la maladie est trouvée directement ---
        if maladie_trouvee:
            obj = maladies_dict[maladie_trouvee]
            meds = obj.get("Médicaments") or obj.get("Medicaments") or []
            conseils = obj.get("Conseils") or []
            if meds:
                texte = f"Pour traiter {maladie_trouvee}, vous pouvez prendre : {', '.join(meds)}."
                if conseils:
                    texte += "\nVoici aussi quelques conseils pratiques :\n- " + "\n- ".join(conseils[:3])
                dispatcher.utter_message(text=texte)
            else:
                dispatcher.utter_message(text=f"Désolé, je n’ai pas de médicaments enregistrés pour {maladie_trouvee}.")
            # mettre à jour le slot
            events.append(SlotSet("maladie", maladie_trouvee))
            return events

        # --- Si le slot maladie est déjà rempli ---
        if slot_maladie:
            obj = maladies_dict.get(slot_maladie)
            if obj:
                meds = obj.get("Médicaments") or obj.get("Medicaments") or []
                conseils = obj.get("Conseils") or []
                if meds:
                    texte = f"Pour traiter {slot_maladie}, vous pouvez prendre : {', '.join(meds)}."
                    if conseils:
                        texte += "\nVoici aussi quelques conseils pratiques :\n- " + "\n- ".join(conseils[:3])
                    dispatcher.utter_message(text=texte)
                else:
                    dispatcher.utter_message(text=f"Désolé, je n’ai pas de médicaments enregistrés pour {slot_maladie}.")
                return events

        # --- Sinon demander la maladie à l'utilisateur ---
        dispatcher.utter_message(text="Pour quelle maladie souhaitez-vous connaître les médicaments ?")
        return events