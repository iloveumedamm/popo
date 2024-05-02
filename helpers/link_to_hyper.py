import re

async def link_to_hyperlink(string):
    """
    > It takes a string, finds all the links in it, and replaces them with a markdown link
    
    :param string: The string to be converted to hyperlink
    :return: A string with the links replaced with a hyperlink.
    """
    http_links = await extract_link(string)
    for link in http_links:
        string = string.replace(link, f"[👉 Click Here 🔗]({link})")
    return string



async def extract_link(string):
    """
    It takes a string and returns a list of all the URLs in that string
    
    :param string: The string to search for links in
    :return: A list of urls
    """
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', string)
    return urls