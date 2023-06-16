import random
from fastapi import FastAPI
import openai
from lyricsgenius import Genius
from fastapi.middleware.cors import CORSMiddleware
import re
from typing import Union
import os

app = FastAPI()

openai.api_key = os.environ.get('openai_api_key')
genius = Genius(os.environ['Genius_Token'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get('origins'),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Vibes = [
    "Dreamy and Surreal: The artwork should evoke a sense of wonder and bewilderment, using a vibrant and otherworldly color palette. Elements might include floating objects, bizarre landscapes, or morphed realities.",
    "Dark and Gothic: The design should exude a sense of mystery and darkness. It might include elements like old castles, full moons, shadowy figures, or ancient symbols, using a color palette of black, deep purples, and silver.",
    "Energetic and Vibrant: The artwork should feel alive and exciting, with bright, vivid colors. It could include elements like explosions, lightning, fast-moving objects, or a chaotic cityscape.",
    "Romantic and Soft: The design should convey a sense of love, softness, and warmth. It might include elements like roses, soft lights, handwritten letters, or a couple sitting under a tree, using a pastel color palette.",
    "Retro and Vintage: The artwork should feel nostalgic, possibly with an aesthetic from a particular decade or time period. Elements might include vinyl records, classic cars, vintage clothing, or old-style typography.",
    "Minimalist and Modern: The design should be sleek and simple, with a clean, uncluttered look. It might include simple shapes, a limited color palette, and plenty of white space.",
    "Psychedelic and Trippy: The artwork should be mind-bending and colorful, drawing inspiration from psychedelic art. It might include swirling patterns, abstract shapes, or surreal landscapes, with a highly saturated and vibrant color palette."
]


def Generate_Lyrics(Topic, Lyrics, Title, Vibe):
    prompt = f"""
Please rewrite the following lyrics to create a new song called "{Title}". The new song should be about {Topic}, and it should capture vibes of {Vibe}:

{Lyrics}
    """
    response = openai.Completion.create(
        model="text-davinci-003", prompt=prompt, temperature=0.7, max_tokens=1500)

    return response.choices[0].text


def Generate_Song_Title(Topic, Song_Title):
    prompt = f"""
Please rewrite the following song title to be about {Topic}. The rewritten title should reflect the mood and key aspects of {Topic}:

{Song_Title}

    """
    response = openai.Completion.create(
        model="text-davinci-003", prompt=prompt, temperature=0.7, max_tokens=10)

    return response.choices[0].text


def Generate_Album_Art(title, vibes, topic):
    prompt = f"""
    Design an album cover for the song "{title}".
    It is about {topic}.
    the vibe is {vibes}
    """
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="512x512"
    )
    return response['data'][0]['url']


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/generate/{song}/{artist}/{topic}")
async def generate(song: str, artist: str, topic: str):
    song = genius.search_song(song, artist)

    new_lyrics = song.lyrics if song else "No Lyrics Found"
    new_song_title = song.title if song else "No Song Title Found"
    new_album_art = song.song_art_image_url if song else "No Album Art Found"

    if topic != "None":
        vibe = random.choice(Vibes)
        new_song_title = Generate_Song_Title(topic, song.title) if song else "No Song Title Found"
        new_lyrics = Generate_Lyrics(topic, song.lyrics, new_song_title, vibe) if song else "No Lyrics Found"
        new_album_art = Generate_Album_Art(new_song_title, vibe, topic) if song else "No Album Art Found"

    return {"lyrics": f"{new_lyrics}", "song": f"{new_song_title}", "artist": f"{artist}", "image": f"{new_album_art}"}
