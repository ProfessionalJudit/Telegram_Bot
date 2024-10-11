#AAFMTYxC0uw434Sc3oUGf48vvb6sdapcbdo

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, Job
import speech_recognition as sr
import io
import soundfile as sf
import datetime

date_keywords = ["avui","d'avui","dema","passat"]
hour_keywords = ["una","dos","tres","quatre","cinc","sis","set","vuit","nou","deu","onze","dotze",
                "tretze","catorze","quinze","setze","diset","divuit","dinou","vint","vint-i-un","vint-i-dos",
                "vint-i-tres","vint-i-quatre","dues","un"]
min_keywords = ["deu","vint","trenta","quaranta","cinquanta"]
min_keywords_eleven_to_twentynine = ["onze","dotze",
                "tretze","catorze","quinze","setze","diset","divuit","dinou","vint","vint-i-un","vint-i-dos",
                "vint-i-tres","vint-i-quatre","vint-i-cinc","vint-i-sis","vint-i-set","vint-i-vuit","vint-i-nou"]
moment_keywords = ["matinada","mati","migdia","tarda","vespre","nit"]
day_keywords = ["dilluns","dimarts","dimecres","dijous","divendres","dissabte","diumenje"]


async def reminder(context):
    job = context.job
    print(job.data)
    await context.bot.send_message(job.chat_id,text="Recordatori: \""+' '.join( job.data["Message"])+"\"")
    
def process_text(text):
    word_array = text.split()
    reminder_date = []
    reminder_hour = []   
    reminder_moment = [] 
    reminder_message = ""
    reminder_day = []
    last_date_element = 0
    count = 0
    for i in word_array:
        if i in day_keywords:
            reminder_day.append(i)
            last_date_element = count
        if i in date_keywords:
            reminder_date.append(i)
            last_date_element = count
        if i in hour_keywords or i in min_keywords_eleven_to_twentynine:
            reminder_hour.append(i)
            last_date_element = count
        if i.split("-")[0] in min_keywords:
            reminder_hour.append(i.split("-")[0])
            if i.split("-").__len__() > 1:
                reminder_hour.append(i.split("-")[1])
            last_date_element = count            
        if i in moment_keywords:
            reminder_moment.append(i)
            last_date_element = count
        count+=1
    word_array += "."
    reminder_message = word_array[last_date_element+1:]
    
    #Day: 1..7 = Dilluns a diumenje, 0..-2 = Avui, dema, dema passat
    #Hour: 24h format
    #Minute: 60m
    final_date = {
        "Day":  -1,
        "Hour": 8,
        "Minute": 0,
        "Message": reminder_message
    }
    
    #Set day
    if "avui" in reminder_date:
        final_date["Day"] = 0
        final_date["Hour"] = datetime.datetime.now().hour + 1
        final_date["Minute"] = 0
    elif "dema" in reminder_date:
        final_date["Hour"] = 8
        final_date["Minute"] = 0
        if "passat" in reminder_date:
            final_date["Day"] = -2
        else:
            final_date["Day"] = -1
    else:
        if "dilluns" in reminder_day:
            final_date["Day"] = 1
        elif "dimarts" in reminder_day:
            final_date["Day"] = 2
        elif "dimecres" in reminder_day:
            final_date["Day"] = 3
        elif "dijous" in reminder_day:
            final_date["Day"] = 4
        elif "divendres" in reminder_day:
            final_date["Day"] = 5
        elif "dissabte" in reminder_day:
            final_date["Day"] = 6
        elif "diumenje" in reminder_day:
            final_date["Day"] = 7
    
    #Set Hour (Prepare to get one and two numbers)
    hour = -1
    if reminder_hour.__len__() > 0:
        try:
            hour = hour_keywords.index(reminder_hour[0])
            hour += 1
        except ValueError as ve:
            hour = -1
        if hour == 25:
            hour = 2
        if hour == 26:
            hour = 1
        if hour == 24:
            hour = 0
    
    if reminder_moment.__len__() > 0:
        for i in range(12):
            if reminder_moment[0] == "mati":
                if hour == -1:
                    final_date["Hour"] = 8
                else:
                    if hour > 13:
                        hour -= 12
                    final_date["Hour"] = hour
                    
            elif reminder_moment[0] == "migdia":
                if hour == -1:
                    final_date["Hour"] = 12
                else:
                    if hour < 5:
                        hour += 12
                    final_date["Hour"] = hour
                    
            elif reminder_moment[0] == "tarda":
                if hour == -1:
                    final_date["Hour"] = 16
                else:
                    if hour < 14:
                        hour += 12
                    final_date["Hour"] = hour
                    
            elif reminder_moment[0] == "nit":
                if hour == -1:
                    final_date["Hour"] = 23
                else:
                    if hour < 23 and hour > 7:
                        hour += 12
                    final_date["Hour"] = hour
                    
            elif reminder_moment[0] == "vespre":
                if hour == -1:
                    final_date["Hour"] = 20
                else:
                    if hour < 18:
                        hour += 12
                    final_date["Hour"] = hour
            elif reminder_moment[0] == "matinada":
                if hour == -1:
                    final_date["Hour"] = 5
                else:
                    if hour > 8:
                        hour = 3
                    final_date["Hour"] = hour
    elif reminder_moment.__len__() == 0:
        final_date["Hour"] = hour
        
    
    #Unitats
    minute_u = -1
    if reminder_hour.__len__() > 2:
        #Del 1 al nou aprofitant l'array de les hores
        if minute_u == -1:
            try:
                minute_u = hour_keywords.index(reminder_hour[2])
                #Començem al 11, so +1 per que els index començen al 0 i +10 per anar a l'onze
                minute_u += 1
                
            except ValueError as ve:
                minute_u = -1
                
    #Decimes
    minute_dec = -1
    if reminder_hour.__len__() > 1:
        try:
            minute_dec = min_keywords.index(reminder_hour[1])
            if minute_dec == 0:
                minute_u = -1
            if minute_u > 9:
                minute_u = -1
            
            minute_dec += 1
            minute_dec *= 10
            
        except ValueError as ve:
            minute_dec = -1
        #Del onze al vint-i-nou
        if minute_dec == -1:
            try:
                minute_dec = min_keywords_eleven_to_twentynine.index(reminder_hour[1])
                #Començem al 11, so +1 per que els index començen al 0 i +10 per anar a l'onze
                minute_dec += 11
                minute_u = -1
            except ValueError as ve:
                minute_dec = -1
        #Del 1 al nou aprofitant l'array de les hores
        if minute_dec == -1:
            try:
                minute_dec = hour_keywords[:9].index(reminder_hour[1])
                #Començem al 11, so +1 per que els index començen al 0 i +10 per anar a l'onze
                minute_dec += 1
                minute_u = -1
            except ValueError as ve:
                minute_dec = -1
    
    if minute_u != -1:
        final_date["Minute"] = minute_u
        
    if minute_dec != -1:
        final_date["Minute"] += minute_dec

    print(reminder_date," ", reminder_hour," ",text)
    #print(minute_dec,":",minute_u,final_date,end="\n")
    return final_date
    


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Heya!\n /list per mostrar els recordatoris pendents\n /delete ID per eleminar un recordator\nTira un audio per començar!"
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
    

    

    #Speech to text
    r = sr.Recognizer()
    with sr.AudioFile(converted_audio) as source:
        # listen for the data (load audio to memory)
        audio_data = r.record(source)
        # recognize (convert from speech to text)
        text = r.recognize_google(audio_data,language="ca")
    
    #We be printin
    final_date = process_text(text)
    print(final_date)
    #Day: 1..7 = Dilluns a dimecres, 0..-2 = Avui, dema, dema passat
    chat_id = update.message.chat_id
    seconds = 0
    seconds_until_eod = (24*3600 - (datetime.datetime.today().hour +1) * 3600)
    seconds_until_eod += datetime.datetime.today().minute * 60
    
    if final_date["Day"] > 0:
        seconds += seconds_until_eod
        if (datetime.datetime.today().weekday() + 1) < final_date["Day"]:
            seconds += ((datetime.datetime.today().weekday() + 1) - final_date["Day"]) * 86400 
        elif (datetime.datetime.today().weekday() + 1) > final_date["Day"]:
            seconds += 6 * 86400
            s_difference = ((datetime.datetime.today().weekday() + 1) - final_date["Day"]) 
            seconds -= s_difference * 86400
    elif final_date["Day"] < 0:
        if final_date["Day"] == -1:
            seconds += seconds_until_eod
        if final_date["Day"] == -2:
            seconds += seconds_until_eod
            seconds += (24 * 3600)
    else:
        if seconds == 0:
            seconds += 3600
    
    seconds += (final_date["Minute"]) * 60
    seconds += (final_date["Hour"]) * 3600
    

    context.job_queue.run_once(reminder,seconds,chat_id=context._chat_id,data=final_date,name="Job "+str(context.job_queue.jobs().__len__()))

async def list_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        list_str = ""
        for i in context.job_queue.jobs():
            list_str += i.name + ": " + str(i.data["Message"]) + "\n"
        if context.job_queue.jobs().__len__() == 0:
            list_str = "No reminders active!"
        await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=list_str
    )

async def delete_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if context.args.__len__() > 0:
            current_jobs = context.job_queue.get_jobs_by_name("Job "+context.args[0])[0].schedule_removal()
            
            await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Job deleted!")
        else:
            await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error! Could not delete")
        

    

if __name__ == '__main__':
    application = ApplicationBuilder().token('7582572736:AAFMTYxC0uw434Sc3oUGf48vvb6sdapcbdo').build()
    start_handler = CommandHandler('start',start)
    application.add_handler(start_handler)  
    application.add_handler(MessageHandler(filters.VOICE, audio_recieved))
    application.add_handler(CommandHandler('delete', delete_jobs))
    application.add_handler(CommandHandler('list', list_jobs))
    application.run_polling()