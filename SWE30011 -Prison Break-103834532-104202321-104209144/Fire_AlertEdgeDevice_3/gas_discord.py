import serial
import pymysql
import discord
from discord.ext import commands
import threading
import asyncio

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="/", intents=intents)

db_conn = pymysql.connect("localhost", "admin", "", "fire")
cursor = db_conn.cursor()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user.name}")


@bot.command()
async def data(ctx):
    try:
        cursor.execute("SELECT * FROM gas ORDER BY id DESC LIMIT 10")
        result = cursor.fetchall()
        data = "\n".join([f"ID: {row[0]}\nSmoke Level: {row[1]}" for row in result])
        await ctx.send(f"Latest data:\n{data}")
    except Exception as e:
        print("Error fetching data from the database:", str(e))
        
        
@bot.command()
async def set_threshold(ctx, gas):
    try:
        threshold = int(gas)
        cursor.execute("UPDATE thresholds SET value = %s", threshold)
        db_conn.commit()
        ser.write(f"threshold:{threshold}\n".encode())  # Send the threshold value to the Arduino
        await ctx.send(f"Threshold value set to: {threshold}")
    except ValueError:
        await ctx.send("Invalid threshold value. Please provide a valid integer.")
        
@bot.command()
async def get_threshold(ctx):
    try:
        cursor.execute("SELECT value FROM thresholds ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        threshold = result[0]
        await ctx.send(f"Current threshold value: {threshold}")
    except Exception as e:
        print("Error fetching threshold value from the database:", str(e))
        await ctx.send("Error retrieving threshold value.")
        
async def send_alert(channel):
    file = discord.File("/home/admin/Desktop/ghostrider.gif", filename="ghostrider.gif")  
    await channel.send("URGENT! FIRE BREAKOUT IN PRISON", file=file)
    
@bot.command()
async def stop_alert(ctx):
    global alertTriggered
    if alertTriggered:
        alertTriggered = False
        ser.write(b"stop\n")  # Send command to Arduino to turn off the water pump
        await ctx.send("Alert has been turned off.")
    else:
        await ctx.send("No alert is currently active.")

        
def process_serial_data():
    global alertTriggered
    alertTriggered = False  # Set initial value to False
    while True:
        data = ser.readline().decode().rstrip()
        try:
            if data:
                sensor_values = data.split(',')
                smoke_level = int(sensor_values[0])

                cursor.execute("INSERT INTO gas(smoke_level) VALUES (%s)", data)
                db_conn.commit()

                cursor.execute("SELECT * FROM gas ORDER BY id DESC LIMIT 1")
                result = cursor.fetchall()
                for row in result:
                    print(row)

                cursor.execute("SELECT value FROM thresholds")
                result = cursor.fetchone()
                threshold = result[0]
                
                if smoke_level > threshold and not alertTriggered:
                    alertTriggered = True
                    channel = bot.get_channel(1121371828993134684)
                    if channel:
                        asyncio.run_coroutine_threadsafe(send_alert(channel), bot.loop)
                    else:
                        print("Error: Channel not found.")
                elif smoke_level <= threshold and alertTriggered:
                    alertTriggered = False

        except Exception as e:
            print("Error inserting to database:", str(e))


# Start the serial data processing in a separate thread
serial_thread = threading.Thread(target=process_serial_data)
serial_thread.start()

bot.run("MTEyMTM3MzQwMjAwMzk1MTY0Ng.GLCDpM.xiFT3vNDq1X87SuKWGXQz14S8snSIvOd3AcuKo")