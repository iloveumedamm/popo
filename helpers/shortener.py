from shortzy import Shortzy
from helpers.link_to_hyper import link_to_hyperlink

from config import SHORTENER_API, SHORTENER_WEBSITE



async def mdisk_droplink_convertor(text, shortener_domain, shortener_api):
    
    if shortener_api and shortener_domain:
        text1 = await replace_link(text, shortener_api, shortener_domain)
        text =  await link_to_hyperlink(text1)
    return text

async def replace_link(text, shortener_api, shortener_domain):
    shortzy = Shortzy(shortener_api, shortener_domain) 
    return await shortzy.convert_from_text(text)
