#AAFMTYxC0uw434Sc3oUGf48vvb6sdapcbdo
from email import message
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import speech_recognition as sr
import io
import soundfile as sf
import datetime

date_keywords = ["avui","d'avui","dema","passat"]
hour_keywords = ["una","dues","dos","tres","quatre","cinc","sis","set","vuit","nou","deu","onze","dotze"]
moment_keywords = ["mati","migdia","tarda","vespre","nit"]


def process_text(text):
    word_array = text.split()
    reminder_date = []
    reminder_hour = []    
    reminder_message = ""
    
    last_date_element = 0
    count = 0
    for i in word_array:
        if i in date_keywords:
            reminder_date.append(i)
            last_date_element = count
        if i in hour_keywords:
            reminder_hour.append(i)
            last_date_element = count
        count+=1
    
    word_array += "."
    reminder_message = word_array[last_date_element+1:]
    print(text)
    print(reminder_date)
    print(reminder_hour)
    print(reminder_message)
    
    #Day: 1..7 = Dilluns a dimecres, 0..-2 = Avui, dema, dema passat
    #Hour: 24h format
    #Minute: 60m
    final_date = {
        "Day":  -1,
        "Hour": 8,
        "Minute": 0
    }
    
    #Set day
    if "avui" in reminder_date:
        final_date["Day"] = 0
        final_date["Hour"] = datetime.datetime.now().hour
        final_date["Minute"] = datetime.datetime.now().minute
    elif "dema" in reminder_date:
        final_date["Hour"] = 8
        final_date["Minute"] = 0
        if "passat" in reminder_date:
            final_date["Day"] = -2
        else:
            final_date["Day"] = -1
    else:
        if "dilluns" in reminder_date:
            final_date["Day"] = 1
        elif "dimarts" in reminder_date:
            final_date["Day"] = 2
        elif "dimecres" in reminder_date:
            final_date["Day"] = 3
        elif "dijous" in reminder_date:
            final_date["Day"] = 4
        elif "divendres" in reminder_date:
            final_date["Day"] = 5
        elif "dissabte" in reminder_date:
            final_date["Day"] = 6
        elif "diumenje" in reminder_date:
            final_date["Day"] = 7
    #Set Hour (Prepare to get one and two numbers)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Heya! Use /help to view all commands. \nSend an audio to create a new entry"
    )   

async def audio_recieved(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await context.bot.get_file(update.message.voice.file_id)
    
    #Get audio file as a byte array
    audio_bytearray = await file.download_as_bytearray()

    #Convert it to a buffer
    bytes_content = io.BytesIO(bytes(audio_bytearray))

    #Convert it to wav format and shove it into a buffer
    data, samplerate = sf.read(bytes_content)
    converted_audio = io.BytesIO()
    sf.write(converted_audio, data, samplerate,format="WAV",subtype="PCM_16")
    converted_audio.seek(0)
    
    #Detect Language
    idioma = ""
    if update.effective_user.language_code == "es":
        idioma = "es-ES"
    if update.effective_user.language_code == "en":
        idioma = "en-US"
    if update.effective_user.language_code == "ca":
        idioma = "ca-ES"
        
    

    #Speech to text
    r = sr.Recognizer()
    with sr.AudioFile(converted_audio) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data,language=idioma)
    
    process_text(text)
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )

if __name__ == '__main__':
    application = ApplicationBuilder().token('7582572736:AAFMTYxC0uw434Sc3oUGf48vvb6sdapcbdo').build()
    start_handler = CommandHandler('start',start)
    application.add_handler(start_handler)  
    application.add_handler(MessageHandler(filters.VOICE, audio_recieved))
    
    application.run_polling()