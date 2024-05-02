import re
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests

from config import *
import requests


async def advantage_spell_chok(msg, q):
  txt = await msg.reply("`Processing....`")
  try:
    query = f"{q} movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
      await txt.delete()
      return False, False
    regex = re.compile(r".*(imdb|wikipedia).*",
                       re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [
      re.sub(
        r"\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)",
        "",
        i,
        flags=re.IGNORECASE,
      ) for i in gs
    ]
    if not gs_parsed:
      reg = re.compile(
        r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
        re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
      for mv in g_s:
        if match := reg.match(mv):
          gs_parsed.append(match[1])
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(
      gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
      gs_parsed = gs_parsed[:3]
    if gs_parsed:
      for mov in gs_parsed:
        title, _, _, _, _ = await search_movie(
          mov.strip(), )  # searching each keyword in imdb
        if imdb_s:
          movielist += [
            title,
          ]
    movielist += [(re.sub(r"(\-|\(|\)|_)", "", i,
                          flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
      await txt.delete()
      return False, False
    btn = [[
        InlineKeyboardButton(
            text=f"{movie.strip()[:25]}.."
            if len(movie.strip()) > 75 else movie.strip(),
            callback_data=
            f"spolling#{user}#{f'{movie.strip()[:25]}..' if len(movie.strip()) > 25 else movie.strip()}",
        )
    ] for movie in movielist]
    btn.append([InlineKeyboardButton(text="Close", callback_data="close")])
    await txt.delete()
    return True, InlineKeyboardMarkup(btn)

  except Exception as e:
    print(e)
    await txt.delete()
    return False, False


async def search_gagala(text):
  usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
        }
  text = text.replace(" ", '+')
  url = f'https://www.google.com/search?q={text}'
  response = requests.get(url, headers=usr_agent)
  response.raise_for_status()
  soup = BeautifulSoup(response.text, 'html.parser')
  titles = soup.find_all( 'h3' )
  return [title.getText() for title in titles]

async def search_movie(query: str):
  if not query:
    return None

  query = re.sub(
    r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|@[a-zA-Z0-9_-]{3,16}|aya(k)*(um(o)*)?|hindi|dubbed|\b(?:1080p|720p|360p|480p|240p)\b|full\smovie|_|any(one)|with\ssubtitle(s)?)",
    "",
    query.lower(),
    flags=re.IGNORECASE,
  )  # plis contribute some common words

  title = extract_title(query)
  year = re.findall(r"[1-2]\d{3}$", query, re.IGNORECASE)
  if year:
    year = list_to_str(year[:1])
    title = (query.replace(year, "")).strip()
  else:
    year = None

  movieid = get_response(title.lower(), results=10)
  if not movieid:
    return (None, None, None, None, None)

  if year:
    filtered = list(filter(lambda k: str(k.get("year")) == str(year), movieid))
    if not filtered:
      filtered = movieid
  else:
    filtered = movieid
  movieid = list(
    filter(lambda k: k.get("kind") in ["movie", "tv series"], filtered))
  if not movieid:
    movieid = filtered

  movieid = movieid[0].get("imdbID")
  movie = get_moive_by_id(movieid)

  date = movie.get("Released") or movie.get("Year") or movie.get("N/A")

  return (
    movie.get("Title"),
    movie.get("Type"),
    date,
    movie.get("Language"),
    movie.get("Poster"),
  )


def get_response(title, results: int = 10):
  title = title.strip()
  # Set the API endpoint and API key
  api_key = OMDB_API
  endpoint = f"https://www.omdbapi.com/?apikey={api_key}&s={title}&results={results}"
  # Make the API request
  response = requests.get(endpoint)
  # print(response.url)
  # Check the status code of the response
  return (response.json()["Search"] if response.status_code == 200
          and response.json()["Response"] == "True" else [])


def get_moive_by_id(id):
  # Set the API endpoint and API key
  endpoint = "http://www.omdbapi.com/"
  api_key = OMDB_API

  # Set the search parameters
  params = {
    "apikey": api_key,
    "i": id,
  }

  # Make the API request
  response = requests.get(endpoint, params=params)

  # Check the status code of the response
  return response.json() if response.status_code == 200 else []


def list_to_str(k):
  if not k:
    return "N/A"
  elif len(k) == 1:
    return str(k[0])
  else:
    return " ".join(f"{elem}, " for elem in k)


def extract_title(string):
  # Compile the regular expression
  pattern = re.compile(r"([^(]*)")
  return match.group(1) if (match := pattern.search(string)) else ""
