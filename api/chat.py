from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from google import genai
from google.genai.types import Content

# ****************
# ***** API KEY YAHAN DALO *****
# VERCEL DEPLOYMENT KE LIYE, KEY KO VERCEL KE SECRETS MEIN DALNA HOTA HAI.
# Lekin abhi testing ke liye, aap use yahan hardcode kar sakte hain ya os.environ se le sakte hain.
# Best practice: Environment variable use karein!
import os
API_KEY = os.environ.get("GEMINI_API_KEY", "YAHAN_API_KEY_DALO")
# ****************

client = None
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    # Agar key galat hai toh client None rahega
    print(f"Gemini API Client failed to initialize: {e}")


def handler(request):
    """Vercel Serverless Function ka main handler."""
    
    if client is None or API_KEY == "YAHAN_API_KEY_DALO":
        return json_response(500, {"error": "Configuration Error: Gemini API Key set nahi hai."})

    try:
        # Request body se JSON data nikalna
        data = json.loads(request.body)
        user_query = data.get("user_input")
        history_dicts = data.get("chat_history_data", [])
        
    except Exception:
        return json_response(400, {"error": "Invalid request body."})

    if not user_query:
        return json_response(400, {"error": "Kripya sawal type karein."})

    # History data ko Content objects mein badalna
    try:
        history_data = [Content.from_dict(h) for h in history_dicts]
    except Exception:
        # Agar conversion fail ho toh history khali rakho
        history_data = []

    assistant_response = ""

    # Chat session banana
    try:
        temp_chat = client.chats.create(model='gemini-2.5-flash', history=history_data)
    except Exception as e:
        return json_response(500, {"error": f"Chat session error: {e}"})

    # --- FEATURE LOGIC (Yahi logic pehle wala hai) ---
    # ... (SCORE CHECK, PIC CHECK, NORMAL CHAT) ...

    # A. SCORE CHECK
    if any(keyword in user_query.lower() for keyword in ["score", "cricket", "livescore", "kitna bana"]):
        score_search_reply = temp_chat.send_message(
            f"User ne kaha hai: '{user_query}'. Tum is sawal ka jawab dene ke liye ek perfect Google search query (sawaal) banao, jisse user ko turant live score mil jaaye. Jawab sirf ek line ka hona chahiye jismein woh search query ho."
        )
        search_query = score_search_reply.text.strip()
        google_link = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        assistant_response = (
            "Main khud *real-time score* nahi dekh sakta, lekin main aapko turant score dhoondhne mein madad karta hoon. "
            "Aap niche diye gaye link par *turant click* karke score dekh sakte hain:<br><br>"
            f"<a href='{google_link}' target='_blank' style='background-color:#4CAF50; color:white; padding:8px 15px; text-decoration:none; border-radius:5px; font-weight:bold;'>🏏 Turant Live Score Dekhein 🏏</a>"
        )

    # B. PIC CHECK
    elif any(keyword in user_query.lower() for keyword in ["pic banao", "tasveer banao", "image banao"]):
        smart_reply = temp_chat.send_message(
            f"User ne kaha hai: '{user_query}'. Tum is sawal ka jawab dene ke liye ek perfect, *high-quality image prompt* banao jise user *Microsoft Copilot* jaise free tool mein use kar sake. Jawab mein *pehli line* sirf woh *prompt* honi chahiye."
        )
        prompt_text = smart_reply.text.split('\n')[0]
        
        assistant_response = (
            "Main aapke liye *tasveer* nahi bana sakta, lekin main aapko *free AI tool* ke liye *perfect prompt* bana sakta hoon.<br><br>"
            "Aap is *Prompt* ko *Microsoft Copilot* mein paste karein:<br>"
            f"👉 *<span style='color: #4A90E2;'>{prompt_text}</span>*<br><br>"
            "Iske baad aapko apni tasveer mil jaayegi!"
        )
        
    # C. NORMAL CHAT
    else:
        try:
            gemini_response = temp_chat.send_message(user_query)
            assistant_response = gemini_response.text
        except Exception:
            assistant_response = "Maaf karna, baat-cheet mein koi gadbad ho gayi."

    # Chat History ko update karna
    new_history_dicts = [h.model_dump() for h in temp_chat.get_history()]
    
    # Final JSON response
    return json_response(200, {
        "response": assistant_response,
        "new_history": new_history_dicts
    })


def json_response(status, data):
    """JSON response banane ka utility function."""
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }

# Flask ki jagah, Vercel handler function ko define karna
# Vercel ko is file mein aane waali HTTP request ko handle karne ke liye naya tarika chahiye.
# Ab hum isse simple 'handler' function se replace kar rahe hain. 
# Zaroorat padne par isko aur badla ja sakta hai.
