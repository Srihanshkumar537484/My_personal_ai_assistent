from google import genai
import os

# ****************
# ***** YAHAN DHAMAKA POINT HAI *****
# Apni API Key ko in quotes (' ') ke andar daalo (Single quotes ' ' zaroori hain)
API_KEY = 'AIzaSyDiLqs8runrwcv_Sf5H1ASOYIM5GepCNHE' 
# ****************


# Assistant ko chabi de kar taiyar karte hain
try:
    client = genai.Client(api_key=API_KEY)
    
    # Chat session shuru karte hain jismein memory hogi
    # Model: gemini-2.5-flash tez hai aur smart bhi
    chat = client.chats.create(model='gemini-2.5-flash')
    
    print("AI Assistant ka connection successful ho gaya hai! Ready to Chat.")

except Exception as e:
    # Agar key galat hui ya internet nahi mila toh yahin ruk jaayega
    print("\n🚨 GADBAD! CONNECTION FAIL HO GAYA. 🚨")
    print("Kripya API Key check karein, ya internet connection dekhein.")
    # Agar error hai toh program yahin ruk jaayega
    exit()


# ***** ASISTANT KA MAIN LOOP ****
print("\nHello! Main tumhara Personal AI Assistant hoon.")
print("Mujhe baatein yaad hain, main sawalon ke jawab de sakta hoon, aur pic/score search mein madad kar sakta hoon.")
print("Type 'stop' ya 'exit' to band karne ke liye.")

while True:
    # User se sawal lena
    user_input = input("Tum: ")

    # Exit condition
    if user_input.lower() in ["exit", "quit", "band karo", "stop"]:
        print("\nAssistant: Alvida! Phir milenge.")
        break
    
    
    # *** 1. LIVE SCORE CHECK ***
    # Agar user score ya match ka haal pooche
    if any(keyword in user_input.lower() for keyword in ["score", "cricket", "match ka haal", "livescore", "kitna bana"]):
        
        print("Assistant: Live score ke liye main aapki madad karta hoon...")
        
        # Gemini se perfect search query maangte hain
        score_search_reply = chat.send_message(
            f"User ne kaha hai: '{user_input}'. Tum is sawal ka jawab dene ke liye ek perfect Google search query (sawaal) banao, jisse user ko turant live score mil jaaye. Jawab sirf ek line ka hona chahiye jismein woh search query ho."
        )
        
        search_query = score_search_reply.text.strip()
        
        response_text = f"Main khud *real-time score* nahi dekh sakta, lekin main aapko turant score dhoondhne mein madad karta hoon.\n\nGoogle mein yeh search karo:\n👉 *{search_query}*\n\nIsse aapko taaza (live) score mil jaayega."

    
    # *** 2. PIC CHECK (SMART, FREE SOLUTION) ***
    # Agar user pic banane ko kahe
    elif any(keyword in user_input.lower() for keyword in ["pic banao", "tasveer banao", "image banao", "picture banao"]):
        
        print("Assistant: Soch Raha Hai...")
        
        # Gemini se smart reply maangte hain
        smart_reply = chat.send_message(
            f"User ne kaha hai: '{user_input}'. Main seedhe image nahi bana sakta. Use batao ki woh *Microsoft Copilot/Designer* ya *Google Imagen's AI Studio* jaise *free tools* use karein. Aur yeh bhi batao ki main (Gemini) us tool ke liye *perfect prompt* bana sakta hoon (Agar user us tool ka naam bataye). Poora jawab achhi Hindi mein do."
        )
        
        response_text = smart_reply.text
    
    
    # *** 3. NORMAL CHAT (MEMORY KE SAATH) ***
    else:
        # Simple chat continue karein
        print("Assistant Soch Raha Hai...")
        try:
            response = chat.send_message(user_input)
            response_text = response.text
        except Exception:
            response_text = "Maaf karna, baat-cheet mein koi gadbad ho gayi."
        
    # Jawab print karna
    print(f"Assistant: {response_text}\n")           
