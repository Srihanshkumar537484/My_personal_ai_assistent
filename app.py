from flask import Flask, render_template, request
from google import genai
from google.genai.types import Content

# ****************
# ***** YAHAN API KEY DALO *****
API_KEY = 'AIzaSyANi7LygZz8Bsyt5FjDV3BmoQGbndhTHGE' 
# ****************

app = Flask(__name__)
# Secret key ki ab zaroorat nahi hai, kyunki hum session use nahi kar rahe

# Global client object
client = None
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"FATAL ERROR: Gemini API Client failed to initialize: {e}")
    client = None


@app.route("/", methods=["GET", "POST"])
def home():
    
    if client is None:
        return "<h1>Configuration Error</h1><p>Gemini API key setup mein gadbad hai. Kripya app.py file check karein.</p>", 500

    user_query = ""
    assistant_response = ""
    
    # 1. Chat History ko Hidden Form se load karna
    # Yeh JSON string ko wapas Content object mein badlega
    history_json = request.form.get("chat_history_data", "[]")
    
    # History data ko load karne ki koshish (pichhle errors ko avoid karne ke liye try-except)
    try:
        history_dicts = eval(history_json)
        # Content object create karna
        history_data = [Content.from_dict(h) for h in history_dicts]
    except Exception:
        # Agar JSON toot gaya toh history khali rakho
        history_data = []


    # 2. Jab user koi sawal bhejta hai (POST request)
    if request.method == "POST":
        user_query = request.form.get("user_input")
        
        if user_query:
            
            # History ke saath Chat session banana
            try:
                # Purani history se naya chat object banao
                temp_chat = client.chats.create(model='gemini-2.5-flash', history=history_data)
            except Exception as e:
                return f"Chat session error: {e}", 500

            # --- FEATURE LOGIC ---
            # (Logic wahi rahega)
            
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
            
            # 3. Chat History ko update karna
            # Final history ko dictionary format mein badlo
            history_dicts = [h.model_dump() for h in temp_chat.get_history()]
            

    # 4. HTML file ko render karna
    return render_template("index.html", user_input=user_query, ai_response=assistant_response, history=history_dicts)


if __name__ == '__main__':
    # Web server ko chalao
    app.run(debug=True)