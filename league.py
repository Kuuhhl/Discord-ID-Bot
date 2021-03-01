import discord
import requests
import config
import os


def get_links():
    text = requests.get(
        "https://raw.communitydragon.org/latest/cdragon/files.exported.txt"
    ).text.splitlines()
    save = []
    for line in text:
        line = line.strip()
        if line.startswith(
            "plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/"
        ):
            save.append(line)
        elif (
            line.startswith(
                "plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/"
            )
            and "uncentered" not in line
            and ".jpg" in line
        ):
            save.append(line)
    return save


def compare_links(allstuff, savefilepath):
    oldstuff = []
    with open(savefilepath, "r") as f:
        text = f.readlines()
    for line in text:
        oldstuff.append(line.strip())
    newstuff = []
    for link in allstuff:
        if link in oldstuff:
            continue
        newstuff.append(link)
    for link in newstuff:
        with open(savefilepath, "a") as f:
            f.write(link + "\n")
    return newstuff


def parse_info():
    newstuff = compare_links(get_links(), os.path.join(os.getcwd(), "savefile.txt"))
    backgrounds = []
    icons = []
    for link in newstuff:
        if link.startswith(
            "plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/"
        ):
            combined = {}
            linkid = (
                link.split(
                    "plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/"
                )[1]
                .split("/")[1]
                .split(".")[0]
            )
            folderid = link.split(
                "plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/"
            )[1].split("/")[0]
            combined["folderid"] = folderid
            combined["linkid"] = linkid
            backgrounds.append(combined)
        if link.startswith(
            "plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/"
        ):
            link = link.split(
                "plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/"
            )[1].split(".")[0]
            icons.append(link)
    return backgrounds, icons


def discord_bot():
    client = discord.Client()

    @client.event
    async def on_ready():
        print("We have logged in as {0.user}".format(client))
        idchannel = client.get_channel(int(config.channel_id))
        parsed = parse_info()
        icons = parsed[1]
        backgrounds = parsed[0]
        if icons == [] and backgrounds == []:
            pass
        else:
            print("Posting into channel: #" + str(idchannel))
            for background in backgrounds:
                folderid = background["folderid"]
                linkid = background["linkid"]
                imageurl = (
                    "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-splashes/"
                    + str(folderid)
                    + "/"
                    + str(linkid)
                    + ".jpg"
                )
                embedVar = discord.Embed(
                    title="ID: " + str(linkid),
                    description="Profile Background",
                    color=0xE88DAF,
                )
                embedVar.set_image(url=imageurl)
                embedVar.add_field(
                    name="Custom Request:",
                    value="""
                **API-Endpoint:** `/lol-summoner/v1/current-summoner/summoner-profile`
                **Method:** `POST`
                **Body:**
                ```{
"key": "backgroundSkinId",
"value": """
                    + str(linkid)
                    + """
}```""",
                    inline=False,
                )
                await idchannel.send(embed=embedVar)
            for icon in icons:
                imageurl = (
                    "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/"
                    + str(icon)
                    + ".jpg"
                )
                embedVar = discord.Embed(
                    title="ID: " + str(icon), description="Icon", color=0x00FF00
                )
                embedVar.set_image(url=imageurl)
                embedVar.add_field(
                    name="Custom Request:",
                    value="""
                **API-Endpoint:** `/lol-chat/v1/me`
                **Method:** `PUT`
                **Body:**
                ```{
"icon": """
                    + str(icon)
                    + """
}```""",
                    inline=False,
                )
                await idchannel.send(embed=embedVar)
        print("Finished task. Closing...")
        await client.logout()
        return

    client.run(config.bot_token)


discord_bot()
