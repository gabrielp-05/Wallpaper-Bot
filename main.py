from discord_webhook import DiscordWebhook, DiscordEmbed
from bs4 import BeautifulSoup
from keep_alive import keep_alive
import datetime
import requests
import os


PARSER = "html.parser"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

def get_image(url) -> str:
    content = requests.get(url, PARSER)
    soup = BeautifulSoup(content.text, features=PARSER)

    img = soup.find("img", attrs={"id": "previewImageMain", "class": "workshopItemPreviewImageMain"})
    if img is None:
        img = soup.find("img", attrs={"id": "previewImage", "class": "workshopItemPreviewImageEnlargeable"})

    return img["src"]

def get_title(url) -> str:
    content = requests.get(url, PARSER)
    soup = BeautifulSoup(content.text, features=PARSER)
    title = soup.find("div", attrs={"class": "workshopItemTitle"})
    return title.text

def get_name(url) -> str:
    content = requests.get(url, PARSER)
    soup = BeautifulSoup(content.text, features=PARSER)
    user = soup.find("div", attrs={"class": "friendBlockContent"})
    status = user.find('span')
    status.extract()
    return user.text.strip()

def send_wallpaper(wallpaper_url) -> None:
    url = WEBHOOK_URL
    get_image(wallpaper_url)

    webhook = DiscordWebhook(url=url)
    embed = DiscordEmbed(title="Wallpaper of the day", description=f"**{get_title(wallpaper_url)}** - **{get_name(wallpaper_url)}**", color="A020F0")
    embed.set_url(url=wallpaper_url)
    embed.set_image(url=get_image(wallpaper_url))
    webhook.add_embed(embed)
    webhook.execute()

def choose_wallpaper() -> str:
    url = "https://steamcommunity.com/workshop/browse/?appid=431960&searchtext=&childpublishedfileid=0&browsesort=trend&section=readytouseitems&requiredtags%5B%5D=Approved&excludedtags%5B%5D=Anime"
    content = requests.get(url, PARSER)
    soup = BeautifulSoup(content.text, features=PARSER)

    item = soup.find("a", attrs={"class": "ugc"})
    return(item["href"])


def scheduler():
    run = True
    while True:
        if datetime.datetime.now().hour == 6 and run:
            send_wallpaper(wallpaper_url=choose_wallpaper())
            print(f"Wallpaper successfully sent at {datetime.datetime.now()}")
            run = False
        elif datetime.datetime.now().hour != 6:
            run = True

if __name__ == "__main__":
    keep_alive()
    scheduler()
