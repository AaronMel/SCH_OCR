import pytesseract
from pytesseract import Output
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import enchant
import re


def rectangle2(draw, x, y, lenght, height, Outline):
    x1 = x + lenght
    y1 = y + height
    draw.rectangle((x1, y1, x, y), outline=Outline)
    return draw


def chackNumberAndUnits(input, units):
    for unit in units:
        a = "[0-9]+(" + unit + ")"
        b = "[0-9]+[\\.\\,][0-9]+(" + unit + ")"
        if None != re.match(a, input.lower()) or None != re.match(b, input.lower()):
            return unit
    return None


def chackUnits(input, units):
    for unit in units:
        a = "(" + unit + "\\.*)$"
        if None != re.match(a, input.lower()):
            return unit
    return None


def unitsMaker(units, prefixes):
    allUnits = []
    for unit in units:
        allUnits.append(str(unit))
        for prefixe in prefixes:
            allUnits.append(str(prefixe + unit))
    return allUnits


class SolutionOCR:
    def __init__(self, language, minConfPts):
        self.language = language
        self.minConfPts = minConfPts

    def OCR(self, imageFile):
        base = {
            "data": []
        }

        image = Image.open(imageFile)
        imageForOCR = image.copy()
        gaussImage = imageForOCR.filter(ImageFilter.GaussianBlur(1))
        boxImage = imageForOCR.filter(ImageFilter.BoxBlur(5))
        blurImage = imageForOCR.filter(ImageFilter.BLUR)
        results = pytesseract.image_to_data(gaussImage, lang=self.language, output_type=Output.DICT)
        for i in range(0, len(results["text"])):
            xcoords = results["left"][i]
            ycoords = results["top"][i]
            width = results["width"][i]
            height = results["height"][i]
            ocrText = results["text"][i]
            confPts = int(results["conf"][i])
            rawOcrText = results["text"][i]
            if confPts > self.minConfPts:
                object = {
                    "codeName": str(i),
                    "x": xcoords,
                    "y": ycoords,
                    "w": width,
                    "h": height,
                    "ocrText": ocrText,
                    "rawOcrText": rawOcrText,
                    "confPts": confPts,
                    "typeOfObject": "unknown"
                }
                base["data"].append(object)
        return base

    def filter(self, base):
        a = 60
        keyUnits = ["m", "g", "s"]
        prefixes = ["k", "d", "c", "m"]
        units = ["ks", "PCS", "n\\.", "č\\.", "h", "m", "d"]
        allUnits = units + unitsMaker(keyUnits, prefixes)
        print(allUnits)
        currencies = ["kč", "czk", "eur", "eu", "usd", "gbp", "$", "€", "£"]

        regex = re.compile(
                r'^(?:http|ftp)s?://'
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                r'localhost|'
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                r'(?::\d+)?'
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        dictionary = enchant.Dict("cs")

        output = {
            "data": []
        }

        for record in base["data"]:
            rawOcrText = record["rawOcrText"]
            ID = record["codeName"]
            confPts = record["confPts"]
            if rawOcrText.isspace() or not rawOcrText:
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\" \" - " + str(record["rawOcrText"]))
                pass
            elif None != re.match('(\\ *\\.\\.\\.\\.+\\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"..\" - " + str(record["rawOcrText"]))
                pass
            elif None != re.match('(\\ *\\—\\—+\\ *)', rawOcrText):
                print(str(ID)+ " - " + str(record["confPts"]) + " - " + "\"——\" - " + str(record["rawOcrText"]))
                pass
            elif None != re.match('(\\ *\\-\\-+\\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"--\" -" + str(record["rawOcrText"]))
                pass
            elif None != re.match('(\\ *\\|+\\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"|\" - " + str(record["rawOcrText"]))
                pass
            else:
                if  None != re.match(regex, rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "URL"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif  None != chackNumberAndUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "number and unit"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "unit"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, currencies):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "currencie"
                    output["data"].append(record)
                elif None != re.match('[0-9][0-9](:[0-9][0-9])+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "time"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9][0-9][\\.\\/][0-9][0-9][\\.\\/][0-9][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "date"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9]+[\\.\\,][0-9]+', rawOcrText) and None == re.search('[a-z]', rawOcrText.lower()):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9]+', rawOcrText) and None == re.search('[a-z]', rawOcrText.lower()):

                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "integer number"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                else:
                    ocrTextClear = ""
                    for character in rawOcrText:
                        if character.isalnum():
                            ocrTextClear += character
                    if ocrTextClear != "":
                        # if  None != chackUnits(ocrTextClear, allUnits):
                        #     record["ocrText"] = rawOcrText
                        #     record["typeOfObject"] = "unit"
                        #     output["data"].append(record)
                        #     print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        if  None != chackUnits(ocrTextClear, currencies):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "currencie"
                            output["data"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif dictionary.check(ocrTextClear):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "word"
                            output["data"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        else:
                            if confPts <= a:
                                words = dictionary.suggest(rawOcrText.replace("*"," ").replace("-"," ").replace("/"," ").replace("."," "))
                                if int(len(words)) > 0:
                                    record["ocrText"] =  words[0]
                                    record["typeOfObject"] = "repaired word"
                                    output["data"].append(record)
                                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                            else:
                                record["ocrText"] = rawOcrText
                                output["data"].append(record)
                                print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                    else: 
                        if confPts > a:
                            record["ocrText"] = rawOcrText
                            output["data"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
        print("finish")
        return output


def imageDebug(imageFile, dictionary, path):
    baseImage = Image.open(imageFile)
    output = baseImage.copy()
    output = output.convert("RGB")
    draw = ImageDraw.Draw(output)
    red = (255, 0, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    yellow = (255, 192, 3)
    orange = (255, 209, 51)
    green = (170, 207, 66)
    blue = (0, 112, 192)
    blueLight = (4, 178, 241)
    purpleLight = (156, 51, 255)
    ping = (233, 51, 255)
    purple = (88, 24, 69)
    greenLight = (140, 252, 53)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16)
    for i in range(len(dictionary["data"])):
        xcoords = dictionary["data"][i]["x"]
        ycoords = dictionary["data"][i]["y"]
        width = dictionary["data"][i]["w"]
        height = dictionary["data"][i]["h"]
        textImage = dictionary["data"][i]["ocrText"]
        ID = dictionary["data"][i]["codeName"]
        type = dictionary["data"][i]["typeOfObject"]
        color = red
        if type == "unknown":
            color = red
        elif type == "word":
            color = green
        elif type == "integer number":
            color = blue
        elif type == "decimal number":
            color = blueLight
        elif type == "date":
            color = orange
        elif type == "time":
            color = yellow
        elif type == "number and unit":
            color = purpleLight
        elif type == "unit":
            color = ping
        elif type == "currencie":
            color = purple
        elif type == "URL":
            color = greenLight
        elif type == "repaired word":
            color = greenLight

        draw = rectangle2(draw, xcoords, ycoords, width, height, color)
        draw.text((xcoords, ycoords), textImage + "\n" + ID, font=font, fill=color)
    output.save(path)
