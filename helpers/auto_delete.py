import asyncio
import config

async def auto_delete(txt=None, m=None):
    try:
        if config.AUTO_DELETE is not False:

            async def delete_message():
                await asyncio.sleep(config.AUTO_DELETE_TIME)
                await m.delete() if m else None
                await txt.delete() if txt else None
                
            asyncio.create_task(delete_message())

    except Exception as e:
        print(e)


