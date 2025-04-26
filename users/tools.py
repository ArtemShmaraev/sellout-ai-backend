from dadata import Dadata

def check_adress(text):
    token = "7b8466ea8df30fc6a906c7e351e1da4160766933"
    secret = "962187b66460ed2f92c257b7bb2778d2c293cefb"
    dadata = Dadata(token)
    result = dadata.suggest("address", text)
    if len(result) > 0:
        return result[0]
    return None


check_adress("белгород губкина 17б")

