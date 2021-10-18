from discord_webhook import DiscordWebhook, DiscordEmbed
from bs4 import BeautifulSoup
from utils.keep_alive import keep_alive
import datetime
import requests
import os

PARSER = "html.parser"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")


def get_image(content) -> str:
    """Returns the media link to the main review image of the wallpaper"""
    soup = BeautifulSoup(content.text, features=PARSER)

    img = soup.find("img", attrs={"id": "previewImageMain", "class": "workshopItemPreviewImageMain"})
    if img is None:
        img = soup.find("img", attrs={"id": "previewImage", "class": "workshopItemPreviewImageEnlargeable"})

    return img["src"]

def get_title(content) -> str:
    """returns the title of the wallpaper"""
    soup = BeautifulSoup(content.text, features=PARSER)
    title = soup.find("div", attrs={"class": "workshopItemTitle"})
    return title.text

def get_name(content) -> str:
    """Returns the name of the creator of the wallpaper"""
    soup = BeautifulSoup(content.text, features=PARSER)
    user = soup.find("div", attrs={"class": "friendBlockContent"})
    status = user.find('span')
    status.extract()
    return user.text.strip()

def send_wallpaper(wallpaper_url) -> None:
    """Creates the webhook, fills it with the necessary details and information, and executes it"""
    url = WEBHOOK_URL

    content = requests.get(wallpaper_url, PARSER)

    webhook = DiscordWebhook(url=url)

    embed = DiscordEmbed(title="Wallpaper of the day", description=f"**{get_title(content)}** - **{get_name(content)}**", color="A020F0")
    embed.set_url(url=wallpaper_url)
    embed.set_image(url=get_image(content))
    embed.add_embed_field(name="\u200b", value="[See my source code](https://github.com/Xephire/Wallpaper-Bot)")
    webhook.add_embed(embed)
    webhook.execute()

def choose_wallpaper() -> str:
    """Chooses the first wallpaper from that day's top wallpapers"""
    url = "https://steamcommunity.com/workshop/browse/?appid=431960&browsesort=trend&section=readytouseitems&requiredtags%5B0%5D=Approved&requiredtags%5B1%5D=Everyone&requiredtags%5B2%5D=Wallpaper&excludedtags%5B0%5D=Anime&excludedtags%5B1%5D=Cartoon&excludedtags%5B2%5D=Game&excludedtags%5B3%5D=Girls&excludedtags%5B4%5D=Guys&excludedtags%5B5%5D=MMD&created_date_range_filter_start=0&created_date_range_filter_end=0&updated_date_range_filter_start=0&updated_date_range_filter_end=0&actualsort=trend&p=1&days=1"
    content = requests.get(url, PARSER)
    soup = BeautifulSoup(content.text, features=PARSER)
    item = soup.find("a", attrs={"class": "ugc"})
    return item["href"]


def scheduler():
    """A make-shift scheduler that checks if the time is 7am UTC and will send the wallpaper when it detects sorted
      Made my own function instead of using the built-in scheduler as it is easier to modify."""
    print("Scheduler running")
    run = True
    while True:
        if datetime.datetime.now().hour == 7 and run:
            send_wallpaper(wallpaper_url=choose_wallpaper())
            print(f"Wallpaper successfully sent at {datetime.datetime.now()}")
            run = False
        elif datetime.datetime.now().hour != 7  :
            run = True

def main():
  """Starts the HTTP server and runs the scheduler"""
  keep_alive()
  scheduler()

if __name__ == "__main__":
    main()
