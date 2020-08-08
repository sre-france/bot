![SRE Paris Bot](https://raw.githubusercontent.com/sre-paris/bot/master/media/img/cover.png)

A simple bot that fights spam on [Telegram location-based groups](https://telegram.org/blog/contacts-local-groups).

**TL;DR:** Private groups created as a location-based group are not private. They will stay open to everyone on the location area and you can't change the location.

# Rationale

The Site Reliability Engineering Paris group has been using for several years a public Telegram group to discuss, share and organize events related to the SRE principles and practices in Paris.

From the beginning the idea was to create an open and public Telegram group to allow anyone to join and participate but in the last few months the number of spammers (users offering off-topic services or posting offensive content) has increased a lot due to 2 main reasons:

1. It's a public group
2. It's a location-based group

So we decide to make it private but as it was initially created as **location-based** group even if it doesn't appear as a public group people can still find and join the group if they are in the center of Paris, and of course it happened a lot.

That could seem like a bug but for Telegram it's a feature. There's only a mention on the desktop application (version 2.2) but nothing on the Android app (version 6.3.0), see screenshot below:

![Telegram Desktop vs Android](https://raw.githubusercontent.com/sre-paris/bot/master/media/img/telegram-desktop-android.png)

# Workarounds

## 1. Change group's location

We tried to set new coordinates for the group, but it's not supported via the official apps. But there's the method [`setChatLocation`](https://core.telegram.org/tdlib/docs/classtd_1_1td__api_1_1set_chat_location.html) on the Telegram API. But it seems to work only on small groups otherwise you'll see a `PARTICIPANTS_TOO_MUCH` error message:

```python
>>> r = tg.call_method(
    "setChatLocation",
    {
        "chat_id": 0000000,
        "location": {
            "@type": "chatLocation",
            "location": {
                "@type": "location",
                "latitude": 47.3350133,
                "longitude": -2.880869,
            },
            "address": "Hoedic, France",
        },
    },
    block=True,
)
>>> r.error_info
{
    "@type": "error",
    "code": 400,
    "message": "PARTICIPANTS_TOO_MUCH",
    "@extra": {"request_id": "xyz"},
}

```

So it didn't work :/

## 2. Use a bot to kick spammers out

There's a lot of Telegram bots doing moderation tasks all around Internet but in our use case we only wanted to automatically kick out people joining the group via the *Groups nearby* feature, and still allowing people invited for other members or joining via the *Invite Link*.

Our first try was to use the [Telegram Bot API](https://core.telegram.org/bots/api) but we saw that it doesn't provide any way to know if someone has joined the group via *Groups nearby* or *Invite Link*, the JSON payload returned by the API is exactly the same on both cases.

So we found a way to know that using the [TDLib](https://core.telegram.org/tdlib) (Telegram Database Library) and a [Python client](https://github.com/alexander-akhmetov/python-telegram). Here's an excerpt of the JSON payload of someone joining via an *Invite link* looks like:

```json
{
    "@type": "updateNewMessage",
    "message": {
        "@type": "message",
        "chat_id": 00000,
        "content": {
            "@type": "messageChatJoinByLink"
        },
        "date": 1596896989,
        "id": 11111,
        "sender_user_id": 22222,
    }
}

```

and the same excerpt for some joining by via *Groups nearby* looks like:

```json
update["message"]["content"]["@type"]

{
    "@type": "updateNewMessage",
    "message": {
        "@type": "message",
        "chat_id": 00000,
        "content": {
            "@type": "messageChatAddMembers",
            "member_user_ids": [
                22222
            ]
        },
        "date": 1596896858,
        "id": 11112,
        "sender_user_id": 22222,
    }
}

```

The important things to see on those payloads are:

* The type of content is `messageChatJoinByLink` for people joining via *Invite link*
* The `sender_user_id` of someone joining the group by himself (*Groups nearby*) will be included on the list of IDs of `member_user_ids`

Then with these criteria in mind we created this [bot](main.py) and it works very well!


# Usage

```
pip install -r requirements.txt
export API_ID="xxx"
export API_HASH="xxx"
export BOT_TOKEN="xxx:yyy"
export ENC_KEY="xyz123"
python main.py
```
