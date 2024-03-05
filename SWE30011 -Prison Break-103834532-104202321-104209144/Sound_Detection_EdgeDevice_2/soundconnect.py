import discord
import serial
import pymysql
from discord.ext import commands
import threading
import asyncio

token = "MTEyMTM3MzQwMjAwMzk1MTY0Ng.GLCDpM.xiFT3vNDq1X87SuKWGXQz14S8snSIvOd3AcuKo"
intents = discord.Intents.default()
intents.message_content =True
intents.typing = True
intents.presences = False
client = discord.Client(intents=intents)


ser = serial.Serial('/dev/ttyS0',9600, timeout =1)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="$", intents=intents)

db_conn = pymysql.connect(host="localhost",user="admin",password="abcd1234", db="sound", port=3306)
cursor = db_conn.cursor()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user.name}")
    
@bot.command()
async def sound_data(ctx):
    try:
        cursor.execute("SELECT * FROM dbsound ORDER BY id DESC LIMIT 10")
        result = cursor.fetchall()
        data = "\n".join([f"ID: {row[0]}\nSound Level: {row[1]}" for row in result])
        await ctx.send(f"Latest data:\n{data}")
    except Exception as e:
        print("Error fetching data from the database:", str(e))


@bot.command()
async def set_soundthreshold(ctx, sound):
    try:
        threshold = int(sound)
        cursor.execute("UPDATE threshold SET value = %s", threshold)
        db_conn.commit()
        ser.write(str(threshold).encode())  # Send the threshold value to the Arduino
        await ctx.send(f"Threshold value set to: {threshold}")
    except ValueError:
        await ctx.send("Invalid threshold value. Please provide a valid integer.")
        
@bot.command()
async def get_soundthreshold(ctx):
    try:
        cursor.execute("SELECT value FROM threshold ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        threshold = result[0]
        await ctx.send(f"Current threshold value: {threshold}")
    except Exception as e:
        print("Error fetching threshold value from the database:", str(e))
        await ctx.send("Error retrieving threshold value.")
        
async def send_alert(channel):
    file = discord.File("/home/yunwei88/Desktop/undertaker.png", filename="undertaker.png")  # Replace "image.jpg" with the actual path to your image file
    await channel.send("Sound level exceeded the threshold!", file=file)
   
def process_serial_data():
    alertTriggered = False
    while True:
        data = ser.readline().decode().rstrip()
        try:
            if data:
                sensor_values = data.split(',')
                sound_level = int(sensor_values[0])

                cursor.execute("INSERT INTO dbsound(sound) VALUES (%s)", data)
                db_conn.commit()

                cursor.execute("SELECT * FROM dbsound ORDER BY id DESC LIMIT 1")
                result = cursor.fetchall()
                for row in result:
                    print(row)

                cursor.execute("SELECT value FROM threshold")
                result = cursor.fetchone()
                threshold = result[0]
                
                if sound_level > threshold and not alertTriggered:
                    alertTriggered = True
                    channel = bot.get_channel(1121371828993134684)
                    if channel:
                        asyncio.run_coroutine_threadsafe(send_alert(channel), bot.loop)
                    else:
                        print("Error: Channel not found.")
                elif sound_level <= threshold and alertTriggered:
                    alertTriggered = False

        except Exception as e:
            print("Error inserting to database:", str(e))


# Start the serial data processing in a separate thread
serial_thread = threading.Thread(target=process_serial_data)
serial_thread.start()

bot.run("MTEyMTM3MzQwMjAwMzk1MTY0Ng.GLCDpM.xiFT3vNDq1X87SuKWGXQz14S8snSIvOd3AcuKo")


