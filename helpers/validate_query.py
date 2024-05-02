import re
async def validate_q(q):
    query = q
            # Checking if the length of the query is less than 2. If it is, it returns.
    if len(query) < 2:
        return False
   
    # Checking if the message contains any of the following:
    #         1. /
    #         2. ,
    #         3. .
    #         4. Emojis
    #         If it does, it will return.
    if re.findall(r"((^\/|^,|^:|^\.|^[\U0001F600-\U000E007F]).*)", query):
        return False
    
    # Checking if the message contains a link.
    if ("https://" or "http://") in query:
        return False

    # It removes the year from the search query.
    query = re.sub(r"[1-2]\d{3}", "", query)
    query = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|hd|movie|-|hindi|in|dubbed|\(|\)|dedo|print|full|bhai|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)", "", query.lower(), flags=re.IGNORECASE)

    return query.strip()