import os
import requests
from dotenv import load_dotenv

# ----------------------------------------
# Carrega o token do Telegram e a chave da API do clima
# ----------------------------------------
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_KEY = os.getenv("OPENWEATHER_KEY")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# ----------------------------------------
# Comunicação com o Telegram
# ----------------------------------------
def get_updates(offset=None):
    """Obtém mensagens enviadas ao bot"""
    url = f"{BASE_URL}/getUpdates"
    if offset:
        url += f"?offset={offset}"
    response = requests.get(url)
    return response.json()

def send_message(chat_id, text):
    """Envia mensagem de resposta"""
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

# ----------------------------------------
# Clima atual
# ----------------------------------------
def get_weather(city):
    """Consulta o clima atual da cidade"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric&lang=pt_br"
        data = requests.get(url).json()

        if data.get("cod") != 200:
            return "❌ Cidade não encontrada. Tente algo como: clima São Paulo ou clima Lisboa,PT"

        nome = data["name"]
        temp = data["main"]["temp"]
        sens = data["main"]["feels_like"]
        umid = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()

        return (f"🌤️ Clima em {nome}:\n"
                f"{desc}\n"
                f"🌡️ Temperatura: {temp:.1f}°C\n"
                f"🤔 Sensação térmica: {sens:.1f}°C\n"
                f"💧 Umidade: {umid}%")

    except Exception as e:
        return f"⚠️ Erro ao obter clima: {e}"

# ----------------------------------------
# Previsão do tempo (3 dias)
# ----------------------------------------
def get_forecast(city):
    """Consulta a previsão dos próximos 3 dias"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_KEY}&units=metric&lang=pt_br"
        data = requests.get(url).json()

        if data.get("cod") != "200":
            return "❌ Cidade não encontrada. Tente algo como: previsão São Paulo ou previsão Lisboa,PT"

        nome = data["city"]["name"]
        previsoes = data["list"]

        texto = f"📅 Previsão para {nome} (próximos 3 dias):\n"
        texto += "---------------------------------\n"

        dias_mostrados = []
        for item in previsoes:
            dt_txt = item["dt_txt"]
            data_dia = dt_txt.split(" ")[0]
            hora = dt_txt.split(" ")[1][:5]

            # Mostra só 1 previsão por dia (meio-dia)
            if "12:00" in hora and data_dia not in dias_mostrados:
                desc = item["weather"][0]["description"].capitalize()
                temp = item["main"]["temp"]
                sens = item["main"]["feels_like"]
                texto += (f"📆 {data_dia}\n"
                          f"☁️ {desc}\n"
                          f"🌡️ {temp:.1f}°C (Sensação {sens:.1f}°C)\n"
                          "---------------------------------\n")
                dias_mostrados.append(data_dia)

            if len(dias_mostrados) >= 3:
                break

        return texto.strip()

    except Exception as e:
        return f"⚠️ Erro ao obter previsão: {e}"

# ----------------------------------------
# Processa mensagens recebidas
# ----------------------------------------
def process_message(text):
    text = text.strip().lower()

    if text.startswith("clima"):
        cidade = text.replace("clima", "").strip()
        if not cidade:
            return "🌍 Diga o nome de uma cidade. Exemplo: clima São Paulo"
        return get_weather(cidade)

    elif text.startswith("previsão") or text.startswith("previsao"):
        cidade = text.replace("previsão", "").replace("previsao", "").strip()
        if not cidade:
            return "📅 Diga o nome de uma cidade. Exemplo: previsão Recife"
        return get_forecast(cidade)

    elif text in ["oi", "olá", "ola"]:
        return "👋 Olá! Eu posso te dizer o clima e a previsão.\n\nEnvie:\n🌤️ clima + cidade\n📅 previsão + cidade"

    else:
        return ("❓ Não entendi. Use:\n"
                "🌤️ clima + cidade → clima atual\n"
                "📅 previsão + cidade → próximos 3 dias\n\n"
                "Exemplo: previsão Rio de Janeiro")

# ----------------------------------------
# Loop principal do bot
# ----------------------------------------
def main():
    print("✅ Bot de clima rodando...")
    update_id = None

    while True:
        updates = get_updates(update_id)
        results = updates.get("result", [])

        if results:
            for update in results:
                update_id = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text")

                if text:
                    resposta = process_message(text)
                    send_message(chat_id, resposta)

if __name__ == "__main__":
    main()
