# Computer

## Local configuration

The Django configuration can be overriden by a `local.py` file located in the same folder as the `manage.py` file.

The minimal configuration in this file should look something like this:

```python
MODELS = {
    "nlu": {
        "path": "PATH/TO/NN-MODEL.keras',
        "mappings": "PATH/TO/mappings.json",
    }
}


APIS = {
    "WEATHER": {
        "BASE_URL": "https://api.openweathermap.org/data",
        "VERSION": "2.5",
        "GENRAL_ENDPOINT": "forecast",
        "APPID": "APPID",
    }
}
```

## Bot Personality
https://blog.myralabs.com/your-chatbot-needs-a-name-b8f92f337386

* Don't pretend to be a human! Personality doesn't mean person.
* Should the script's tone be familiar or professional?
* Should the bot have a name?
* Should the bot be polite and conversational or entirely focused on the task at hand?
* Would jokes be appropriate? If yes, be mindful of repetitive interactions, and repetitive punch lines.
* Does your bot platform allow the easy A/B testing of different messages and tones?
