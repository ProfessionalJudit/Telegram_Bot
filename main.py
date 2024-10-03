#AAFMTYxC0uw434Sc3oUGf48vvb6sdapcbdo
from email import message
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import speech_recognition as sr
import io
import soundfile as sf

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!"
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
    
    print(update.effective_user.language_code)
    
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
        print(text)

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