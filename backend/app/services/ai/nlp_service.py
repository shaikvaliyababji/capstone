import re
import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Device alias dictionaries for natural language mapping across English, Hindi, Telugu, Spanish, French
DEVICE_ALIASES = {
    "bedroom_light": [
        # English
        "bedroom light", "bed room light", "light in bedroom", "bedroom lamp",
        "bedroom lights", "lights in the bedroom", "bedroom bulb",
        # Hindi (Devanagari & Hinglish)
        "बेडरूम लाइट", "बेडरूम की लाइट", "बेडरूम का बल्ब", "bedroom ki light", "bedroom light",
        # Telugu (Telugu script & Teluglish)
        "బెడ్ రూమ్ లైట్", "బెడ్ రూమ్ లైటు", "బెడ్రూమ్ లైట్", "bedroom light", "bedroom lo light",
        # Spanish
        "luz de la recámara", "luz de la habitación", "luz del dormitorio", "luz del cuarto",
        # French
        "lumière de la chambre", "lampe de la chambre"
    ],
    "living_room_light": [
        # English
        "living room light", "hall light", "living light", "living room lamp",
        "living room lights", "hallway light", "lounge light", "drawing room light",
        # Hindi
        "लिविंग रूम लाइट", "हॉल लाइट", "लिविंग रूम की लाइट", "बैठक की लाइट", "हॉल की लाइट", "hall ki light",
        # Telugu
        "లివింగ్ రూమ్ లైట్", "హాల్ లైట్", "హాలు లైటు", "హాల్ లో లైట్", "hall lo light",
        # Spanish
        "luz de la sala", "luz del salón", "luz de la sala de estar",
        # French
        "lumière du salon", "lumière de la salle de séjour"
    ],
    "kitchen_light": [
        # English
        "kitchen light", "light in kitchen", "kitchen lamp", "kitchen lights", "kitchen bulb",
        # Hindi
        "किचन लाइट", "रसोई की लाइट", "रसोईघर की लाइट", "kitchen ki light", "rasoi ki light",
        # Telugu
        "కిచెన్ లైట్", "వంటగది లైట్", "వంట గది లైట్", "kitchen lo light", "vantagadi light",
        # Spanish
        "luz de la cocina", "foco de la cocina",
        # French
        "lumière de la cuisine"
    ],
    "fan": [
        # English
        "fan", "living room fan", "ceiling fan", "the fan", "room fan",
        # Hindi
        "पंखा", "पंखे", "हॉल का पंखा", "pankha", "pankhe",
        # Telugu
        "ఫ్యాన్", "విసనకర్ర", "సీలింగ్ ఫ్యాన్", "fan", "phyan",
        # Spanish
        "ventilador", "abanico",
        # French
        "ventilateur"
    ],
    "ac": [
        # English
        "ac", "a/c", "air conditioner", "air condition", "air conditioning",
        "bedroom ac", "cooler", "climate control",
        # Hindi
        "एसी", "एयर कंडीशनर", "कूलर", "ac", "a/c",
        # Telugu
        "ఏసీ", "ఎయిర్ కండీషనర్", "కూలర్", "ac", "a/c",
        # Spanish
        "aire acondicionado", "el aire", "clima",
        # French
        "climatiseur", "la clim", "climatisation"
    ],
    "door": [
        # English
        "door", "front door", "main door", "entrance door", "lock", "entry door",
        # Hindi
        "दरवाजा", "मुख्य दरवाजा", "मेन गेट", "दरवाजे", "कपाट", "darwaza", "darwaje", "main door",
        # Telugu
        "డోర్", "తలుపు", "ప్రధాన ద్వారం", "ముందు తలుపు", "talupu", "door",
        # Spanish
        "puerta", "puerta principal", "cerradura",
        # French
        "porte", "porte d'entrée", "serrure"
    ],
    "curtains": [
        # English
        "curtain", "curtains", "living room curtains", "blinds", "window curtains",
        "window blind", "shades",
        # Hindi
        "पर्दा", "पर्दे", "खिड़की का पर्दा", "parda", "parde", "curtain", "curtains",
        # Telugu
        "కర్టెన్లు", "తెరలు", "కిటికీ తెరలు", "curtains", "teralu",
        # Spanish
        "cortinas", "persianas",
        # French
        "rideaux", "stores"
    ]
}

# Pre-configured Smart Scenes with Multilingual Triggers and Responses
SMART_SCENES = {
    "good_night": {
        "id": "good_night",
        "name": "Good Night",
        "description": "Turns off all lights, closes curtains, and securely locks the front door.",
        "icon": "Moon",
        "example_phrases": [
            "Good night", "शुभ रात्रि (Hindi)", "శుభరాత్రి (Telugu)", "Buenas noches (Spanish)"
        ],
        "triggers": [
            # English
            "good night", "bedtime", "going to sleep", "sleep mode", "night mode", "sleep now",
            # Hindi
            "शुभ रात्रि", "shubh ratri", "सोने जा रहा", "सोने का समय", "गुड नाईट", "सुला दो",
            # Telugu
            "శుభరాత్రి", "shubharatri", "పడుకోబోతున్నా", "పడుకునే సమయం", "గుడ్ నైట్",
            # Spanish
            "buenas noches", "hora de dormir", "modo noche", "me voy a dormir",
            # French
            "bonne nuit", "l'heure de dormir", "mode nuit", "je vais dormir"
        ],
        "actions": [
            {"device": "bedroom_light", "action": "off"},
            {"device": "living_room_light", "action": "off"},
            {"device": "kitchen_light", "action": "off"},
            {"device": "curtains", "action": "off"},  # CLOSED
            {"device": "door", "action": "off"}       # LOCKED
        ],
        "responses": {
            "en": "Good night! I've turned off all the lights, closed the curtains, and locked the front door. Sleep well!",
            "hi": "शुभ रात्रि! मैंने सभी लाइटें बंद कर दी हैं, पर्दे गिरा दिए हैं और मुख्य दरवाजा लॉक कर दिया है। आराम से सोइए!",
            "te": "శుభరాత్రి! నేను అన్ని లైట్లను ఆఫ్ చేశాను, కర్టెన్లు మూసివేశాను మరియు ప్రధాన ద్వారం లాక్ చేశాను. శుభ నిద్ర!",
            "es": "¡Buenas noches! He apagado todas las luces, cerrado las cortinas y asegurado la puerta principal. ¡Que descanses!",
            "fr": "Bonne nuit ! J'ai éteint toutes les lumières, fermé les rideaux et verrouillé la porte d'entrée. Dormez bien !"
        }
    },
    "good_morning": {
        "id": "good_morning",
        "name": "Good Morning",
        "description": "Opens living room curtains and illuminates kitchen & bedroom lights.",
        "icon": "Sun",
        "example_phrases": [
            "Good morning", "सुप्रभात (Hindi)", "శుభోదయం (Telugu)", "Buenos días (Spanish)"
        ],
        "triggers": [
            # English
            "good morning", "wake up", "start my day", "morning routine", "morning mode",
            # Hindi
            "सुप्रभात", "subh prabhat", "shubh prabhat", "सुबह हो गई", "गुड मॉर्निंग", "जगा दो",
            # Telugu
            "శుభోదయం", "shubhodhayam", "తెల్లవారింది", "మేల్కొలుపు", "గుడ్ మార్నింగ్",
            # Spanish
            "buenos días", "despierta", "modo mañana", "rutina de la mañana",
            # French
            "bonjour", "réveil", "mode matin"
        ],
        "actions": [
            {"device": "curtains", "action": "on"},  # OPEN
            {"device": "bedroom_light", "action": "on"},
            {"device": "kitchen_light", "action": "on"}
        ],
        "responses": {
            "en": "Good morning! I've opened the curtains and turned on the bedroom and kitchen lights. Have a great day!",
            "hi": "सुप्रभात! पर्दे खोल दिए गए हैं और बेडरूम तथा किचन की लाइटें जला दी गई हैं। आपका दिन शुभ हो!",
            "te": "శుభోదయం! కర్టెన్లు తెరవబడ్డాయి మరియు బెడ్ రూమ్, కిచెన్ లైట్లు ఆన్ చేయబడ్డాయి. ఈ రోజు మీకు శుభప్రదం!",
            "es": "¡Buenos días! He abierto las cortinas y encendido las luces del dormitorio y la cocina. ¡Que tengas un excelente día!",
            "fr": "Bonjour ! J'ai ouvert les rideaux et allumé les lumières de la chambre et de la cuisine. Passez une excellente journée !"
        }
    },
    "movie_mode": {
        "id": "movie_mode",
        "name": "Movie Night",
        "description": "Dims living room lights, draws curtains closed, and starts air conditioning.",
        "icon": "Film",
        "example_phrases": ["Movie mode", "मूवी टाइम (Hindi)", "సినిమా మోడ్ (Telugu)", "Modo película"],
        "triggers": [
            "movie mode", "movie night", "watch movie", "cinema mode", "film mode",
            "मूवी मोड", "मूवी टाइम", "फिल्म देखना", "సినిమా మోడ్", "మూవీ మోడ్",
            "modo película", "modo cine", "mode film", "mode cinéma"
        ],
        "actions": [
            {"device": "living_room_light", "action": "off"},
            {"device": "curtains", "action": "off"},  # CLOSED
            {"device": "ac", "action": "on"}
        ],
        "responses": {
            "en": "Movie night mode activated! Living room lights are off, curtains drawn closed, and the AC is running.",
            "hi": "मूवी नाइट मोड सक्रिय! लिविंग रूम की लाइट बंद कर दी गई है, पर्दे गिरा दिए गए हैं और एसी चालू है।",
            "te": "మూవీ నైట్ మోడ్ ఆన్ చేయబడింది! లివింగ్ రూమ్ లైట్లు ఆఫ్ చేయబడ్డాయి, కర్టెన్లు మూయబడ్డాయి మరియు ఏసీ ఆన్ చేయబడింది.",
            "es": "¡Modo película activado! Luces de la sala apagadas, cortinas cerradas y aire acondicionado encendido.",
            "fr": "Mode cinéma activé ! Lumières du salon éteintes, rideaux fermés et climatisation en marche."
        }
    },
    "away_mode": {
        "id": "away_mode",
        "name": "Leaving Home",
        "description": "Powers off all lights and appliances, and locks the front door.",
        "icon": "LogOut",
        "example_phrases": ["Leaving home", "घर से बाहर (Hindi)", "బయటకు వెళ్తున్నా (Telugu)", "Salgo de casa"],
        "triggers": [
            "leaving home", "i am leaving", "away mode", "goodbye", "bye", "turn everything off",
            "turn off everything", "घर से बाहर", "बाहर जा रहा", "सब बंद करो", "अलविदा",
            "బయటకు వెళ్తున్నా", "అన్నీ ఆఫ్ చేయి", "బయటికి వెళ్తున్నాను",
            "salir de casa", "modo fuera", "apagar todo", "adiós",
            "je sors", "mode absence", "éteindre tout", "au revoir"
        ],
        "actions": [
            {"device": "bedroom_light", "action": "off"},
            {"device": "living_room_light", "action": "off"},
            {"device": "kitchen_light", "action": "off"},
            {"device": "fan", "action": "off"},
            {"device": "ac", "action": "off"},
            {"device": "door", "action": "off"}  # LOCKED
        ],
        "responses": {
            "en": "Away mode activated. All appliances and lights are switched off, and the front door is securely locked.",
            "hi": "अवे मोड सक्रिय। सभी उपकरण और लाइटें बंद कर दी गई हैं, और मुख्य दरवाजा सुरक्षित रूप से लॉक कर दिया गया है।",
            "te": "అవే మోడ్ సక్రియం చేయబడింది. అన్ని పరికరాలు మరియు లైట్లు ఆఫ్ చేయబడ్డాయి, ముందు తలుపు సురక్షితంగా లాక్ చేయబడింది.",
            "es": "Modo fuera activado. Todos los electrodomésticos y luces están apagados, y la puerta principal está bloqueada.",
            "fr": "Mode absence activé. Tous les appareils et lumières sont éteints, et la porte d'entrée est verrouillée."
        }
    },
    "welcome_home": {
        "id": "welcome_home",
        "name": "Welcome Home",
        "description": "Unlocks front door, turns on living room light and air conditioner.",
        "icon": "Home",
        "example_phrases": ["Welcome home", "घर आ गया (Hindi)", "ఇంటికి వచ్చాను (Telugu)", "Llegué a casa"],
        "triggers": [
            "welcome home", "i'm home", "im home", "arrived home", "i am back", "i'm back",
            "घर आ गया", "घर पहुँच गया", "मैं घर हूँ", "घर आया",
            "ఇంటికి వచ్చాను", "నేను వచ్చాను", "ఇంటికి చేరుకున్నాను",
            "bienvenido a casa", "llegué a casa", "estoy en casa",
            "bienvenue à la maison", "je suis rentré", "de retour"
        ],
        "actions": [
            {"device": "door", "action": "on"},  # UNLOCKED
            {"device": "living_room_light", "action": "on"},
            {"device": "ac", "action": "on"}
        ],
        "responses": {
            "en": "Welcome back home! Unlocked the front door, turned on the living room light, and started the AC.",
            "hi": "घर वापसी पर स्वागत है! मुख्य दरवाजा अनलॉक कर दिया गया है, लिविंग रूम की लाइट और एसी चालू कर दिए गए हैं।",
            "te": "ఇంటికి స్వాగతం! ప్రధాన ద్వారం అన్‌లాక్ చేయబడింది, లివింగ్ రూమ్ లైట్ మరియు ఏసీ ఆన్ చేయబడ్డాయి.",
            "es": "¡Bienvenido a casa! Puerta principal abierta, luz de la sala encendida y aire acondicionado activado.",
            "fr": "Bienvenue à la maison ! Porte déverrouillée, lumière du salon allumée et climatisation activée."
        }
    },
    "party_mode": {
        "id": "party_mode",
        "name": "Party Mode",
        "description": "Powers on all home lights and starts the fan.",
        "icon": "PartyPopper",
        "example_phrases": ["Party mode", "पार्टी मोड (Hindi)", "పార్టీ మోడ్ (Telugu)", "Modo fiesta"],
        "triggers": [
            "party mode", "party time", "पार्टी मोड", "पार्टी टाइम", "పార్టీ మోడ్",
            "modo fiesta", "fiesta", "mode fête"
        ],
        "actions": [
            {"device": "living_room_light", "action": "on"},
            {"device": "bedroom_light", "action": "on"},
            {"device": "kitchen_light", "action": "on"},
            {"device": "fan", "action": "on"}
        ],
        "responses": {
            "en": "Party mode activated! All home lights and cooling fans are now turned on.",
            "hi": "पार्टी मोड चालू! घर की सभी लाइटें और पंखा चालू कर दिए गए हैं।",
            "te": "పార్టీ మోడ్ ఆన్ చేయబడింది! అన్ని లైట్లు మరియు ఫ్యాన్ ఆన్ చేయబడ్డాయి.",
            "es": "¡Modo fiesta activado! Todas las luces y el ventilador están encendidos.",
            "fr": "Mode fête activé ! Toutes les lumières et le ventilateur sont allumés."
        }
    }
}

# Multilingual ON keywords
ON_KEYWORDS = [
    # English
    "turn on", "switch on", "power on", "activate", "start", "enable", "unlock", "open", "on",
    # Hindi (Devanagari & Hinglish)
    "चालू करो", "चालू कर", "चालू", "ऑन करो", "ऑन कर", "ऑन", "खोलो", "खोल दो", "खोल", "जलाओ", "जला दो",
    "on karo", "chalu karo", "kholo", "jalao",
    # Telugu (Telugu script & Teluglish)
    "ఆన్ చేయి", "ఆన్ చెయ్", "ఆన్", "వెలిగించు", "తెరువు", "తెరవు", "తీయి", "ప్రారంభించు",
    "on cheyi", "chalu cheyi", "teruvu", "tiyi", "veliginchu",
    # Spanish
    "encender", "enciende", "prender", "prende", "activar", "activa", "abrir", "abre", "desbloquear",
    # French
    "allumer", "allume", "ouvrir", "ouvre", "déverrouiller", "activer", "active"
]

# Multilingual OFF keywords
OFF_KEYWORDS = [
    # English
    "turn off", "switch off", "power off", "shut down", "deactivate", "stop", "disable", "lock", "close", "shut", "off",
    # Hindi (Devanagari & Hinglish)
    "बंद करो", "बंद कर", "बंद", "ऑफ करो", "ऑफ कर", "ऑफ", "बुझाओ", "बुझा दो", "लॉक करो", "रोको",
    "off karo", "band karo", "bujhao", "lock karo", "roko",
    # Telugu (Telugu script & Teluglish)
    "ఆఫ్ చేయి", "ఆఫ్ చెయ్", "ఆఫ్", "ఆపు", "వేయి", "మూయి", "మూసివేయి", "లాక్ చేయి",
    "off cheyi", "aapu", "mooyi", "veyi", "lock cheyi",
    # Spanish
    "apagar", "apaga", "desactivar", "desactiva", "cerrar", "cierra", "bloquear", "bloquea", "detener",
    # French
    "éteindre", "éteins", "fermer", "ferme", "verrouiller", "verrouille", "désactiver", "désactive"
]


class NLPService:
    """
    Multilingual Natural Language Processing Service for AI-SmartHome.
    Supports English, Hindi, Telugu, Spanish, French with automatic script and keyword detection.
    """

    @classmethod
    def get_scenes(cls) -> List[Dict[str, Any]]:
        """Return list of available smart scene presets."""
        return [
            {
                "id": scene["id"],
                "name": scene["name"],
                "description": scene["description"],
                "icon": scene["icon"],
                "example_phrases": scene["example_phrases"]
            }
            for scene in SMART_SCENES.values()
        ]

    @classmethod
    def _normalize_lang(cls, raw: Optional[str]) -> str:
        """Normalize any locale or language string to 2-letter ISO code."""
        if not raw:
            return "en"
        clean = raw.strip().lower()
        if clean.startswith("te") or "telugu" in clean:
            return "te"
        if clean.startswith("hi") or "hindi" in clean:
            return "hi"
        if clean.startswith("es") or "spanish" in clean:
            return "es"
        if clean.startswith("fr") or "french" in clean:
            return "fr"
        if clean.startswith("en") or "english" in clean:
            return "en"
        return clean[:2] if len(clean) >= 2 else "en"

    @classmethod
    def detect_language(cls, text: str, hinted_lang: Optional[str] = None) -> str:
        """
        Detect primary language from Unicode characters, hinted locale, or language patterns.
        Returns: 'en', 'hi', 'te', 'es', or 'fr'.
        """
        if not text:
            return cls._normalize_lang(hinted_lang or "en")

        # Check explicit Devanagari (Hindi) script: U+0900 to U+097F
        if re.search(r'[\u0900-\u097F]', text):
            return "hi"

        # Check explicit Telugu script: U+0C00 to U+0C7F
        if re.search(r'[\u0C00-\u0C7F]', text):
            return "te"

        # If user explicitly selected a regional language, give it strong priority
        if hinted_lang and hinted_lang != "auto":
            norm_hint = cls._normalize_lang(hinted_lang)
            if norm_hint in ["te", "hi", "es", "fr"]:
                return norm_hint

        lower = text.lower()
        # Hinglish patterns
        if any(w in lower for w in ["karo", "band", "chalu", "shubh ratri", "pankha", "darwaza", "khol", "kholo", "jalao"]):
            return "hi"
        # Teluglish patterns
        if any(w in lower for w in ["cheyi", "cheyyi", "shubharatri", "talupu", "teruvu", "aapu", "veyi", "on cheyi", "off cheyi", "mooyi"]):
            return "te"
        # Spanish patterns
        if any(w in lower for w in ["enciende", "apaga", "puerta", "luces", "habitacion", "sala", "buenas noches"]):
            return "es"
        # French patterns
        if any(w in lower for w in ["allume", "éteins", "lumière", "porte", "chambre", "bonne nuit"]):
            return "fr"

        return "en"

    @classmethod
    def process_command(
        cls, 
        query: str, 
        current_devices: List[Dict[str, Any]], 
        language: Optional[str] = "en"
    ) -> Dict[str, Any]:
        """
        Process a natural language query in any supported language against current devices.
        Returns parsed intent, target actions, language code, and conversational response.
        """
        cleaned_query = query.strip()
        lang_code = cls.detect_language(cleaned_query, language)

        if not cleaned_query:
            fallback_msg = {
                "en": "I didn't catch that. Try saying 'Turn on living room light' or 'Good night'.",
                "hi": "मुझे समझ नहीं आया। 'लिविंग रूम लाइट चालू करो' या 'शुभ रात्रि' बोलकर देखें।",
                "te": "నాకు అర్థం కాలేదు. 'లివింగ్ రూమ్ లైట్ ఆన్ చేయి' లేదా 'శుభరాత్రి' అని చెప్పి చూడండి.",
                "es": "No pude entenderlo. Intenta decir 'Enciende la luz de la sala' o 'Buenas noches'.",
                "fr": "Je n'ai pas compris. Essayez de dire « Allume la lumière du salon » ou « Bonne nuit »."
            }.get(lang_code, "I didn't catch that.")

            return {
                "query": query,
                "intent": "unknown",
                "language": lang_code,
                "response": fallback_msg,
                "actions": []
            }

        # Check for Gemini API key
        gemini_api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                gemini_result = cls._process_with_gemini(cleaned_query, current_devices, gemini_api_key, lang_code)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                logger.warning(f"Gemini API invocation failed ({e}), falling back to local multilingual NLP.")

        # Default / Fallback: Local Multilingual Engine
        return cls._process_locally(cleaned_query, current_devices, lang_code)

    @classmethod
    def _process_locally(cls, query: str, current_devices: List[Dict[str, Any]], lang: str) -> Dict[str, Any]:
        """
        Local deterministic intent extraction supporting multiple languages.
        """
        lower = query.lower()

        # 1. Greetings
        greeting_words = [
            "hello", "hi", "hey", "नमस्ते", "नमस्कार", "namaste", "నమస్కారం", "హలో", "namaskaram",
            "hola", "buenos días", "salut", "bonjour"
        ]
        if any(w in lower for w in greeting_words) and len(lower.split()) <= 3:
            active_count = sum(1 for d in current_devices if d.get("status") in ["ON", "UNLOCKED", "OPEN"])
            resp = {
                "en": f"Hello! Your AI Smart Home is running smoothly. Currently, {active_count} device{'s are' if active_count != 1 else ' is'} active. How can I help you?",
                "hi": f"नमस्ते! आपका AI स्मार्ट होम सुचारू रूप से चल रहा है। अभी {active_count} उपकरण सक्रिय हैं। मैं आपकी क्या सहायता कर सकता हूँ?",
                "te": f"నమస్కారం! మీ AI స్మార్ట్ హోమ్ సజావుగా పనిచేస్తోంది. ప్రస్తుతం {active_count} పరికరాలు యాక్టివ్‌గా ఉన్నాయి. నేను మీకు ఎలా సహాయపడగలను?",
                "es": f"¡Hola! Tu casa inteligente funciona perfectamente. Actualmente hay {active_count} dispositivo(s) activo(s). ¿En qué puedo ayudarte?",
                "fr": f"Bonjour ! Votre maison intelligente fonctionne parfaitement. Actuellement, {active_count} appareil(s) est/sont actif(s). Comment puis-je vous aider ?"
            }.get(lang, f"Hello! {active_count} devices active.")

            return {
                "query": query,
                "intent": "general_qa",
                "language": lang,
                "response": resp,
                "actions": []
            }

        # 2. Smart Scenes
        for scene_key, scene_data in SMART_SCENES.items():
            for trigger in scene_data["triggers"]:
                if trigger in lower:
                    response_text = scene_data["responses"].get(lang, scene_data["responses"]["en"])
                    return {
                        "query": query,
                        "intent": "scene_control",
                        "language": lang,
                        "response": response_text,
                        "actions": scene_data["actions"]
                    }

        # 3. Status Queries
        status_triggers = [
            "what is on", "what's on", "what devices are on", "which devices are on",
            "is anything on", "status", "how many devices", "what is active", "check devices",
            "is the door locked", "are the lights on", "are lights on",
            # Hindi
            "क्या चालू है", "क्या ऑन है", "क्या कुछ चालू है", "दरवाजा लॉक है", "लाइट चालू है",
            "kya chalu hai", "kya on hai",
            # Telugu
            "ఏమి ఆన్ లో ఉంది", "ఏ పరికరాలు ఆన్ లో ఉన్నాయి", "డోర్ లాక్ అయిందా", "లైట్లు ఆన్ లో ఉన్నాయా",
            "emi on lo undi", "talupu lock ayinda",
            # Spanish
            "qué está encendido", "cuántos dispositivos", "está la puerta cerrada",
            # French
            "qu'est-ce qui est allumé", "la porte est verrouillée", "état"
        ]
        if any(st in lower for st in status_triggers):
            return cls._handle_status_query(query, lower, current_devices, lang)

        # 4. Group Commands: Bulk lights
        all_lights_triggers_off = [
            "all lights off", "turn off all lights", "switch off all lights", "turn off the lights",
            "सब लाइटें बंद", "सारी लाइटें बंद", "सभी लाइटें बंद", "sab light band karo",
            "అన్ని లైట్లు ఆఫ్ చేయి", "లైట్లన్నీ ఆఫ్ చేయి", "లైట్లన్నీ ఆపు", "anni lights off cheyi",
            "apaga todas las luces", "apagar todas las luces",
            "éteins toutes les lumières", "éteindre toutes les lumières"
        ]
        all_lights_triggers_on = [
            "all lights on", "turn on all lights", "switch on all lights",
            "सब लाइटें चालू", "सारी लाइटें ऑन", "सभी लाइटें चालू करो", "sab light on karo",
            "అన్ని లైట్లు ఆన్ చేయి", "లైట్లన్నీ వెలిగించు", "anni lights on cheyi",
            "enciende todas las luces", "encender todas las luces",
            "allume toutes les lumières", "allumer toutes les lumières"
        ]

        if any(tr in lower for tr in all_lights_triggers_off):
            light_devices = [d["name"] for d in current_devices if d.get("category") == "light"]
            actions = [{"device": d, "action": "off"} for d in light_devices]
            resp = {
                "en": f"Turned off all {len(light_devices)} lights in the home.",
                "hi": f"घर की सभी {len(light_devices)} लाइटें बंद कर दी गई हैं।",
                "te": f"ఇంట్లోని మొత్తం {len(light_devices)} లైట్లు ఆఫ్ చేయబడ్డాయి.",
                "es": f"Se apagaron las {len(light_devices)} luces de la casa.",
                "fr": f"Les {len(light_devices)} lumières de la maison ont été éteintes."
            }.get(lang, "All lights turned off.")
            return {"query": query, "intent": "group_control", "language": lang, "response": resp, "actions": actions}

        if any(tr in lower for tr in all_lights_triggers_on):
            light_devices = [d["name"] for d in current_devices if d.get("category") == "light"]
            actions = [{"device": d, "action": "on"} for d in light_devices]
            resp = {
                "en": f"Turned on all {len(light_devices)} lights in the home.",
                "hi": f"घर की सभी {len(light_devices)} लाइटें चालू कर दी गई हैं।",
                "te": f"ఇంట్లోని మొత్తం {len(light_devices)} లైట్లు ఆన్ చేయబడ్డాయి.",
                "es": f"Se encendieron las {len(light_devices)} luces de la casa.",
                "fr": f"Les {len(light_devices)} lumières de la maison ont été allumées."
            }.get(lang, "All lights turned on.")
            return {"query": query, "intent": "group_control", "language": lang, "response": resp, "actions": actions}

        # 5. Individual Device Control
        is_turn_off = any(w in lower for w in OFF_KEYWORDS)
        is_turn_on = any(w in lower for w in ON_KEYWORDS)

        if is_turn_off or is_turn_on:
            action = "off" if is_turn_off else "on"
            matched_device = cls._match_device(lower, current_devices)

            if matched_device:
                dev_name = matched_device["name"]
                dev_cat = matched_device.get("category", "")
                label = cls._format_label(dev_name)

                # Format multilingual response
                resp = cls._build_action_response(label, dev_cat, action, lang)
                return {
                    "query": query,
                    "intent": "device_control",
                    "language": lang,
                    "response": resp,
                    "actions": [{"device": dev_name, "action": action}]
                }

        # 6. Fallback Unhandled Command
        fallback_responses = {
            "en": f"I couldn't quite match '{query}' to a device or scene. Try saying 'Turn on living room light', 'Turn off all lights', or 'Good night'.",
            "hi": f"मुझे '{query}' के लिए कोई उपकरण या सीन नहीं मिला। कृपया 'लिविंग रूम लाइट चालू करो' या 'शुभ रात्रि' बोलें।",
            "te": f"'{query}' కోసం పరికరం లేదా సీన్ దొరకలేదు. 'లివింగ్ రూమ్ లైట్ ఆన్ చేయి' లేదా 'శుభరాత్రి' అని ప్రయత్నించండి.",
            "es": f"No pude asociar '{query}' a un dispositivo o escena. Prueba diciendo 'Enciende la luz de la sala' o 'Buenas noches'.",
            "fr": f"Je n'ai pas pu associer « {query} » à un appareil. Essayez de dire « Allume la lumière du salon » ou « Bonne nuit »."
        }
        return {
            "query": query,
            "intent": "unknown",
            "language": lang,
            "response": fallback_responses.get(lang, fallback_responses["en"]),
            "actions": []
        }

    @classmethod
    def _match_device(cls, lower: str, current_devices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find matching device using multilingual aliases and fuzzy tokens."""
        # 1. Registered aliases across all languages
        for dev_name, aliases in DEVICE_ALIASES.items():
            for alias in aliases:
                if alias in lower:
                    for d in current_devices:
                        if d["name"] == dev_name:
                            return d

        # 2. Exact database names or spaced names
        for d in current_devices:
            name = d["name"]
            spaced = name.replace("_", " ")
            if spaced in lower or name in lower:
                return d

        # 3. Category + Room matching
        for d in current_devices:
            cat = d.get("category", "").lower()
            room = d.get("room", "").replace("_", " ").lower()
            if cat in lower and room in lower:
                return d

        # 4. Fallback category matching
        for cat in ["fan", "ac", "door", "curtains"]:
            if cat in lower or (cat == "ac" and ("air conditioner" in lower or "cooler" in lower)):
                for d in current_devices:
                    if d.get("category") == cat or d["name"] == cat:
                        return d

        return None

    @classmethod
    def _build_action_response(cls, label: str, category: str, action: str, lang: str) -> str:
        """Construct a grammatically natural response in the selected language."""
        if lang == "hi":
            if category == "security":
                return f"{label} {'लॉक' if action == 'off' else 'अनलॉक'} कर दिया गया है।"
            elif category == "comfort":
                return f"{label} {'बंद' if action == 'off' else 'खोल'} दिए गए हैं।"
            else:
                return f"{label} {'बंद' if action == 'off' else 'चालू'} कर दी गई है।"

        elif lang == "te":
            if category == "security":
                return f"{label} {'లాక్' if action == 'off' else 'అన్‌లాక్'} చేయబడింది."
            elif category == "comfort":
                return f"{label} {'మూసివేయబడింది' if action == 'off' else 'తెరవబడింది'}."
            else:
                return f"{label} {'ఆఫ్' if action == 'off' else 'ఆన్'} చేయబడింది."

        elif lang == "es":
            if category == "security":
                return f"{label} {'bloqueada' if action == 'off' else 'desbloqueada'}."
            elif category == "comfort":
                return f"{label} {'cerradas' if action == 'off' else 'abiertas'}."
            else:
                return f"{label} {'apagado' if action == 'off' else 'encendido'}."

        elif lang == "fr":
            if category == "security":
                return f"{label} {'verrouillée' if action == 'off' else 'déverrouillée'}."
            elif category == "comfort":
                return f"{label} {'fermés' if action == 'off' else 'ouverts'}."
            else:
                return f"{label} {'éteint' if action == 'off' else 'allumé'}."

        # Default English
        if category == "security":
            return f"{'Locked' if action == 'off' else 'Unlocked'} {label}."
        elif category == "comfort":
            return f"{'Closed' if action == 'off' else 'Opened'} {label}."
        else:
            return f"Turned {'OFF' if action == 'off' else 'ON'} {label}."

    @classmethod
    def _handle_status_query(
        cls, query: str, lower: str, current_devices: List[Dict[str, Any]], lang: str
    ) -> Dict[str, Any]:
        """Format an accurate, conversational status response in the user's language."""
        # Check specific door
        if any(w in lower for w in ["door", "दरवाजा", "తలుపు", "puerta", "porte"]):
            door_dev = next((d for d in current_devices if d["name"] == "door"), None)
            if door_dev:
                status = door_dev.get("status", "LOCKED")
                if lang == "hi":
                    resp = f"मुख्य दरवाजा अभी {status} है।"
                elif lang == "te":
                    resp = f"ప్రధాన తలుపు ప్రస్తుతం {status} గా ఉంది."
                elif lang == "es":
                    resp = f"La puerta principal está actualmente {status}."
                elif lang == "fr":
                    resp = f"La porte d'entrée est actuellement {status}."
                else:
                    resp = f"The front door is currently {status.upper()}."
                return {"query": query, "intent": "status_query", "language": lang, "response": resp, "actions": []}

        # Check active devices list
        active_devices = [
            cls._format_label(d["name"])
            for d in current_devices
            if d.get("status") in ["ON", "UNLOCKED", "OPEN"]
        ]

        count = len(active_devices)
        if count == 0:
            resp = {
                "en": "All smart home devices are currently idle or turned off.",
                "hi": "स्मार्ट होम के सभी उपकरण अभी बंद या शांत हैं।",
                "te": "అన్ని స్మార్ట్ హోమ్ పరికరాలు ప్రస్తుతం ఆఫ్ చేయబడి ఉన్నాయి.",
                "es": "Todos los dispositivos del hogar inteligente están apagados.",
                "fr": "Tous les appareils de la maison intelligente sont actuellement éteints."
            }.get(lang, "All devices are off.")
            return {"query": query, "intent": "status_query", "language": lang, "response": resp, "actions": []}

        if lang == "hi":
            resp = f"अभी {count} उपकरण चालू हैं: {', '.join(active_devices)}।"
        elif lang == "te":
            resp = f"ప్రస్తుతం {count} పరికరాలు ఆన్‌లో ఉన్నాయి: {', '.join(active_devices)}."
        elif lang == "es":
            resp = f"Actualmente hay {count} dispositivo(s) encendido(s): {', '.join(active_devices)}."
        elif lang == "fr":
            resp = f"Actuellement, {count} appareil(s) est/sont allumé(s) : {', '.join(active_devices)}."
        else:
            if count == 1:
                resp = f"1 device is currently active: {active_devices[0]}."
            else:
                resp = f"There are {count} devices currently active: {', '.join(active_devices[:-1])} and {active_devices[-1]}."

        return {"query": query, "intent": "status_query", "language": lang, "response": resp, "actions": []}

    @classmethod
    def _process_with_gemini(
        cls, query: str, current_devices: List[Dict[str, Any]], api_key: str, lang: str
    ) -> Optional[Dict[str, Any]]:
        """Query Google Gemini with multilingual instruction."""
        import httpx

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
        device_summary = [
            {"name": d["name"], "room": d["room"], "category": d["category"], "status": d["status"]}
            for d in current_devices
        ]

        system_instruction = (
            "You are an AI Smart Home Assistant. The home has the following devices:\n"
            f"{json.dumps(device_summary, indent=2)}\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Accurately detect the language the user is speaking in (e.g. English, Hindi, Telugu, Tamil, Spanish, French, German, Hinglish, Teluglish, etc.).\n"
            "2. Determine the user's smart home intent and any target device actions (on/off).\n"
            "3. Generate a natural, conversational spoken response STRICTLY in the EXACT SAME LANGUAGE the user used.\n"
            "   - If the user speaks Telugu, formulate your response in fluent Telugu.\n"
            "   - If the user speaks Hindi, formulate your response in fluent Hindi.\n"
            "   - If the user speaks Spanish, formulate your response in Spanish.\n"
            "   - If the user speaks French, formulate your response in French.\n"
            "   - If the user speaks English, formulate your response in English.\n"
            "   - If the user speaks Hinglish or Teluglish, formulate your response in natural conversational Hindi or Telugu.\n"
            "Return strictly valid JSON:\n"
            "{\n"
            '  "detected_language": "en" | "hi" | "te" | "es" | "fr",\n'
            '  "intent": "device_control" | "scene_control" | "status_query" | "general_qa" | "unknown",\n'
            '  "response": "Spoken reply strictly in the exact language the user used",\n'
            '  "actions": [{"device": "device_name", "action": "on" | "off"}]\n'
            "}"
        )

        target_norm = cls._normalize_lang(lang)
        if target_norm in ["te", "hi", "es", "fr"]:
            system_instruction += (
                f"\n\nUSER PREFERRED LANGUAGE: The user's requested language is '{target_norm.upper()}'. "
                f"You MUST formulate your conversational response in fluent, natural {target_norm.upper()} "
                f"and set 'detected_language' to '{target_norm}'."
            )

        payload = {
            "contents": [{"parts": [{"text": f"{system_instruction}\n\nUser command: {query}"}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1}
        }

        with httpx.Client(timeout=6.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    return None
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "text" in part:
                        try:
                            raw_text = part["text"].strip()
                            if raw_text.startswith("```"):
                                raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
                                raw_text = re.sub(r"\n?```$", "", raw_text).strip()
                            parsed = json.loads(raw_text)
                            detected = cls._normalize_lang(parsed.get("detected_language") or lang)
                            if not detected or detected == "en":
                                detected = cls.detect_language(query, lang)
                            return {
                                "query": query,
                                "intent": parsed.get("intent", "device_control"),
                                "language": detected,
                                "response": parsed.get("response", "Command processed."),
                                "actions": parsed.get("actions", [])
                            }
                        except Exception as parse_err:
                            logger.warning(f"Error parsing Gemini JSON: {parse_err}")
            return None

    @staticmethod
    def _format_label(name: str) -> str:
        """Convert snake_case device name into Title Case string."""
        return " ".join(word.capitalize() for word in name.split("_"))
