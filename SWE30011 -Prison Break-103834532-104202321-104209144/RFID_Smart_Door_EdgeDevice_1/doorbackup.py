import serial
import pymysql
import discord
from discord.ext import commands
import asyncio
import threading

ser = serial.Serial('/dev/ttyS0', 9600)
ser.reset_input_buffer()
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

db_conn = pymysql.connect(host="localhost", user="Aaronlrs", password="", db="entry", port=3306)
cursor = db_conn.cursor()

# Define UID-Image path mappings
image_mapping = {
    "4D6FE644": "/home/aaronlrs/Desktop/najib2.png",
    "CDDB9FEA": "/home/aaronlrs/Desktop/anwar.png",
    "73208D94": "/home/aaronlrs/Desktop/messi.png" 
    # Add more UID-image path mappings as needed
}

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user.name}")
    
    @bot.command()
    async def uid(ctx):
        try:
            cursor.execute("SELECT uid, access FROM prison ORDER BY id DESC LIMIT 3")
            result = cursor.fetchall()
            uid = "\n".join([f"UID: {row[0]}\nAccess: {row[1]}\n" for row in result])
            await ctx.send(f"The UIDs:\n{uid}\n")
        except Exception as e:
            print("Error fetching data from the database:", str(e))
        

async def send_access_granted_message(uid):
    channel_id = 1121371828993134684  # Replace with your desired channel ID
    channel = bot.get_channel(channel_id)
    if channel is not None:
        if uid in image_mapping:
            image_path = image_mapping[uid]
            file = discord.File(image_path)
            await channel.send(f"Access granted for UID: {uid}", file=file)
            print("Message Sent")
        else:
            print("No image mapping found for UID:", uid)
    else:
        print("Channel not found")

def rfid_loop():
    while True:
        
        uid = ser.readline().decode().rstrip()
        
        if not uid:
            continue

        uid = uid.replace(" ", "")
        
        cursor.execute("SELECT uid, access FROM prison WHERE uid = %s", (uid))
        result = cursor.fetchone()
        print(result)

        if result:
#             access_status = result[1]
            print("uid found")

#             if access_status == 'Granted':
                
            print("Access granted for UID:", uid)
            asyncio.run_coroutine_threadsafe(send_access_granted_message(uid), bot.loop)
            ser.write(b'o')
            print("\n o sent\n")
        
        else:
            print("Access denied for UID:", uid)
            ser.write(b'c')
            print("\n c sent\n")
            
        uid=""
#             if access_status == 'Denied':
#                
#                 print("Access denied for UID:", uid)

#             else:
#                 print("Unknown access status for UID:", uid)
#         else:
#             print("UID not found:", uid)


def start_rfid_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(rfid_loop())

try:
    rfid_thread = threading.Thread(target=start_rfid_loop)
    rfid_thread.start()
    bot.run("MTEyMTM3MzQwMjAwMzk1MTY0Ng.GLCDpM.xiFT3vNDq1X87SuKWGXQz14S8snSIvOd3AcuKo")
except pymysql.Error as e:
    print("Error connecting to the database:", str(e))
finally:
    cursor.close()
