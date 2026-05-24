import os
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types

# Cargar variables del archivo .env
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuracion de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL")
GEMINI_FALLBACK_MODELS = [
	model.strip()
	for model in os.getenv("GEMINI_FALLBACK_MODELS", "").split(",")
	if model.strip()
]
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta")
genai_client = genai.Client(
	api_key=GEMINI_API_KEY,
	http_options=types.HttpOptions(apiVersion=GEMINI_API_VERSION),
)