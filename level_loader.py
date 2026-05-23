import json


def load_level(path):

    with open(path, "r") as f:
        data = json.load(f)

    defaults = {

        "Lives": 3,

        "Difficulty": 5,

        "Ball_Starting_Speed": 0.5,

        "Background_Color": ["#000000"],

        "Background_Sprite": "",

        "Block_Colors": ["#ff6666"],

        "Block_Sprites": [],

        "Spiral_Speed": 0.25,

        "Spiral_Thickness": 2,

        "Spiral_Colors": [
            "#ffffff",
            "#999999"
        ],

        "Phrases": [],

        "Phrase_Appear_Speed": 20.0,

        "Phrase_Scroll_Speed": 40,

        "Phrase_Max_Count": 6,

        "Phrase_Color": "#ffffff"
    }

    for key, value in defaults.items():

        if key not in data:
            data[key] = value

    return data