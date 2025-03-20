import requests
import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import textwrap
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


# Detect OS and set paths
if os.name == "nt":  # Windows
    font_path = r"C:\Users\ThinkPad\Downloads\gd botto\font_thingy.otf"
    bg_path = r"C:\Users\ThinkPad\Downloads\gd botto\bg.png"
else:  # Linux (VPS)
    font_path = "/home/fire/gd-botto/font_thingy.otf"
    bg_path = "/home/fire/gd-botto/bg.png"
    

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync slash commands properly
    print(f'Bot is logged in as {bot.user}')

def get_level_info(level_id):
    url = f"https://gdbrowser.com/api/level/{level_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()


def create_level_image(level_data):



    bg = Image.open(bg_path)
    draw = ImageDraw.Draw(bg)

    # Get difficulty and check for demon type
    difficulty = level_data.get('difficulty', 'unrated').lower()

    # Determine difficulty type and size multiplier
    size_multiplier = 2
    if level_data.get('mythic', 0) == 1 or level_data.get('legendary', 0) == 1:
        size_multiplier = 2
    elif level_data.get('epic', 0) == 1:
        size_multiplier = 2
    elif level_data.get('featured', 0) == 1:
        size_multiplier = 2

    # Check if it's a demon level
    if "demon" in difficulty:
        demon_types = ["easy", "medium", "hard", "insane", "extreme"]
        demon_type = next((d for d in demon_types if d in difficulty), "")

        if level_data.get('mythic', 0) == 1:
            difficulty_name = f"demon-{demon_type}-mythic" if demon_type else "demon-mythic"
        elif level_data.get('legendary', 0) == 1:
            difficulty_name = f"demon-{demon_type}-legendary" if demon_type else "demon-legendary"
        elif level_data.get('featured', 0) == 1:
            difficulty_name = f"demon-{demon_type}-featured" if demon_type else "demon-featured"
        elif level_data.get('epic', 0) == 1:
            difficulty_name = f"demon-{demon_type}-epic" if demon_type else "demon-epic"
        else:
            difficulty_name = f"demon-{demon_type}" if demon_type else "demon"
    else:
        if level_data.get('mythic', 0) == 1:
            difficulty_name = f"{difficulty}-mythic"
        elif level_data.get('legendary', 0) == 1:
            difficulty_name = f"{difficulty}-legendary"
        elif level_data.get('epic', 0) == 1:
            difficulty_name = f"{difficulty}-epic"
        elif level_data.get('featured', 0) == 1:
            difficulty_name = f"{difficulty}-featured"
        else:
            difficulty_name = difficulty

    # Fetch difficulty image
    difficulty_url = f"https://gdbrowser.com/assets/difficulties/{difficulty_name}.png"
    response = requests.get(difficulty_url)

    if response.status_code == 200:
        difficulty_img = Image.open(BytesIO(response.content))
        width, height = difficulty_img.size
        new_size = (int(width * size_multiplier), int(height * size_multiplier))
        difficulty_img = difficulty_img.resize(new_size)

        # Calculate center placement at (300, 270)
        x_pos = 330 - new_size[0] // 2
        y_pos = 320 - new_size[1] // 2
        bg.paste(difficulty_img, (x_pos, y_pos), difficulty_img)

    # Load custom font

    font_big = ImageFont.truetype(font_path, 160)
    font_large = ImageFont.truetype(font_path, 130)
    font_medium = ImageFont.truetype(font_path, 90)
    font_desc = ImageFont.truetype(font_path, 80)
    font_small = ImageFont.truetype(font_path, 60)

    # Menampilkan Stars hanya jika level Featured
    if level_data.get('featured', 0) == 1:
        star_text = f"{level_data.get('stars', 0)}"
        draw.text((280, 650), star_text, font=font_medium, fill="white",stroke_width=5, stroke_fill="black")

        # Fetch star icon from URL
        star_url = "https://gdbrowser.com/assets/star.png"
        response = requests.get(star_url)

        if response.status_code == 200:
            star_icon = Image.open(BytesIO(response.content)).convert("RGBA")

            # Resize icon (1.5x bigger)
            original_size = star_icon.size
            new_size = (int(original_size[0] * 1.5), int(original_size[1] * 1.5))
            star_icon = star_icon.resize(new_size)

            # Position image to the right of the text (330 + text width + padding)
            text_width = draw.textbbox((0, 0), star_text, font=font_medium)[2]
            star_x = 300 + text_width + 2  # 10px padding from text

            bg.paste(star_icon, (star_x, 620), star_icon)

    downloads = "{:,}".format(level_data.get('downloads', 0))
    likes = "{:,}".format(level_data.get('likes', 0))
    # Ambil jumlah objek dari level data
    object_count =  level_data.get('coins', 'Tidak Diketahui')

    object_text = f"{object_count}"

    # Hitung lebar teks untuk menentukan titik tengah
    text_width = draw.textbbox((0, 0), object_text, font=font_small)[2]
    x_objects = 2720 - (text_width // 2)  # Hitung posisi agar teks berada di tengah

    # Menentukan posisi vertikal
    # Menambahkan teks ke gambar
    text = level_data.get('name', 'Tidak Diketahui')
    image_width, _ = bg.size  # Ambil lebar gambar
    text_width = draw.textbbox((0, 0), text, font=font_big)[2]  # Ambil lebar teks
    x_position = (image_width - text_width) // 2  # Hitung posisi tengah

    text2 = level_data.get('author', 'Tidak Diketahui')
    text_width = draw.textbbox((0, 0), text2, font=font_medium)[2]  # Ambil lebar teks
    x_position2 = (bg.width - text_width) // 2  # Hitung posisi tengah

    text4 = downloads

    text3 = f"Description"
    image_width, _ = bg.size  # Ambil lebar gambar
    text_width = draw.textbbox((0, 0), text, font=font_medium)[2]  # Ambil lebar teks
    x_position3 = (image_width - text_width) // 2  # Hitung posisi tengah

    text5 = f"{level_data.get('songName', 'Tidak Diketahui')} / {level_data.get('songID', 'Tidak Diketahui')}"
    image_width, _ = bg.size  # Ambil lebar gambar
    text_width = draw.textbbox((0, 0), text5, font=font_small)[2]  # Ambil lebar teks
    x_position5 = (image_width - text_width) // 2  # Hitung posisi tengah

    # Calculate centered position for "Length" text (middle point at 300)
    length_text = f"{level_data.get('length', 'Tidak Diketahui')}"
    text_width = draw.textbbox((0, 0), length_text, font=font_large)[2]
    x_position_length = 335 - (text_width // 2)  # Centering logic

    draw.text((x_position, 170), text, font=font_big, fill="white", stroke_width=10, stroke_fill="black")
    draw.text((x_position2, 300), text2, font=font_medium, fill="#fec932", stroke_width=5, stroke_fill="black")
    draw.text((x_position3, 450), text3 , font=font_desc, fill="white",stroke_width=5, stroke_fill="black")
    draw.text((2400, 950), f"ID: {level_data.get('id', 'Tidak Diketahui')}", font=font_small, fill="white", stroke_width=5, stroke_fill="black")
    draw.text((x_position_length, 500), length_text, font=font_large, fill="white", stroke_width=5, stroke_fill="black")
    draw.text((305, 930), downloads , font=font_small, fill="white", stroke_width=5, stroke_fill="black")
    draw.text((855, 930), likes, font=font_small, fill="white", stroke_width=5, stroke_fill="black")
    draw.text((x_position5, 770), text5, font=font_small, fill="#27d2ff", stroke_width=5, stroke_fill="black")
    draw.text((x_objects, 605), object_text, font=font_small, fill="#c2723e", stroke_width=5, stroke_fill="black")

    # Menampilkan deskripsi level dengan wrap agar tidak terlalu panjang di satu baris
    description_text = level_data.get("description", "Tidak ada deskripsi.")
    if len(description_text) < 50:
        text_width = draw.textbbox((0, 0), description_text, font=font_small)[2]
        x_desc = (bg.width - text_width) // 2
        draw.text((x_desc, 560), description_text, font=font_small, fill="white", stroke_width=5, stroke_fill="black")
    else:
        # Ambil 50 huruf pertama untuk menentukan lebar teks
        preview_text = description_text[:50]
        text_width = draw.textbbox((0, 0), preview_text, font=font_small)[2]
        x_desc = (bg.width - text_width) // 2
        wrapped_text = "\n".join(textwrap.wrap(description_text, width=50))
        draw.text((x_desc, 560), wrapped_text, font=font_small, fill="white", stroke_width=5, stroke_fill="black")
    # Simpan gambar sementara
    image_path = "level_info.png"
    bg.save(image_path)
    return image_path

@bot.tree.command(name="level", description="Get Geometry Dash level info")
async def level(interaction: discord.Interaction, level_id: int):
    await interaction.response.defer()  # Memberi tahu Discord bahwa bot butuh waktu lebih lama

    level_data = get_level_info(level_id)
    if level_data is None:
        await interaction.followup.send("Gagal mengambil data dari GD Browser.")
        return

    image_path = create_level_image(level_data)
    await interaction.followup.send(file=discord.File(image_path))

def get_user_info(username):
    url = f"https://gdbrowser.com/api/profile/{username}"
    response = requests.get(url)

    if response.status_code != 200:
        return "Gagal mengambil data pengguna dari GD Browser."

    data = response.json()

    info = (f"**Nama Pengguna:** {data.get('username', 'Tidak Diketahui')}\n"
            f"**ID Pengguna:** {data.get('playerID', 'Tidak Diketahui')}\n"
            f"**Bintang:** {data.get('stars', 0)}\n"
            f"**Demons:** {data.get('demons', 0)}\n"
            f"**Coins:** {data.get('coins', 0)}\n"
            f"**User Coins:** {data.get('userCoins', 0)}\n"
            f"**Diamonds:** {data.get('diamonds', 0)}\n"
            f"**CP:** {data.get('creatorPoints', 0)}\n"
            f"**Tautan Profil:** https://gdbrowser.com/u/{username}")

    return info

@bot.tree.command(name="username", description="get geometrydash user info but im lazy so no pictures")
async def level(interaction: discord.Interaction, username: str):
    info = get_user_info(username)
    await ctx.send(info)

bot.run(TOKEN)
