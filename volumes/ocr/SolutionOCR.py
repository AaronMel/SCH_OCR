import pytesseract
from pytesseract import Output
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import enchant
import re

from difflib import SequenceMatcher


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


def rectangleOverlay(x11, x21, y11, y21, w11, w21, h11, h21):
    x12 = x11 + w11
    x22 = x21 + w21
    y12 = y11 + h11
    y22 = y21 + h21
    
    dx = min(x12, x22) - max(x11, x21)
    dy = min(y12, y22) - max(y11, y21)
    if (dx>=0) and (dy>=0):
        return dx*dy
    else:
        return 0
    
    
def noiseFilter(input):
    if input.isspace() or not input:
        return False
    elif None != re.match('(\\ *\\.\\.\\.\\.+\\ *)', input):
        return False
    elif None != re.match('(\\ *\\—\\—+\\ *)', input):
        return False
    elif None != re.match('(\\ *\\-\\-+\\ *)', input):
        return False
    elif None != re.match('(\\ *\\|+\\ *)', input):
        return False
    else:
        return True
    
    
    
    


def outputSortingOCR(input, minConfPts):
    base = {
        "data": []
    }
    
    for i in range(0, len(input["text"])):
        
        xcoords = input["left"][i]
        ycoords = input["top"][i]
        width = input["width"][i]
        height = input["height"][i]
        ocrText = input["text"][i]
        confPts = int(input["conf"][i])
        rawOcrText = input["text"][i]
        if confPts >= minConfPts and (xcoords != 0 or ycoords != 0) :
            object = {
                "codeName": str(i),
                "x": xcoords,
                "y": ycoords,
                "w": width,
                "h": height,
                "ocrText": ocrText,
                "rawOcrText": rawOcrText,
                "confPts": confPts,
                "typeOfObject": "unknown",
                "numberOfFinds": 1
            }
            base["data"].append(object)
    return base
    

def comperOCR(input):
    
    overlayMin = 0.9
    bothOverlayMin = 0.7
    scequenceRatioMin = 0.5
    
    output = {
        "data": []
    }
    
    for i in range(len(input["results"])):
        result = input["results"][i]
        if i > -1:
            for j in range(len(result["data"])):
                added = True
                for k in range(len(output["data"])):
                    x1 = result["data"][j]["x"]
                    x2 = output["data"][k]["x"]
                    y1 = result["data"][j]["y"]
                    y2 = output["data"][k]["y"]
                    h1 = result["data"][j]["h"]
                    h2 = output["data"][k]["h"]
                    w1 = result["data"][j]["w"]
                    w2 = output["data"][k]["w"]
                    p3 = rectangleOverlay(x1, x2, y1, y2, w1, w2, h1, h2)
                    R1 = p3 / (h1 * w1)
                    R2 = p3 / (h2 * w2)
                    if R1 >= overlayMin or R2 >= overlayMin or (R1 >= bothOverlayMin and R2 >= bothOverlayMin) :
                        textImage1 = result["data"][j]["ocrText"]
                        textImage2 = output["data"][k]["ocrText"]
                        
                        len1 = len(textImage1)
                        len2 = len(textImage2)
                        
                        ratio1 = 0.5
                        ratio2 = 0.5
                        
                        if len2 > 0:
                            ratio1 = len1 / len2
                            if len1 > 0:
                                ratio2 = len2 / len1
                            else:
                                ratio2 = 0
                                ratio1 = -100
                        else:
                            ratio1 = 0
                            ratio2 = -100
                        
                        
                        
                        
                        
                        
                        
                        scequenceRatio = SequenceMatcher(None, textImage1, textImage2).ratio()
                        if  1 == scequenceRatio:
                            added = False
                            output["data"][k]["numberOfFinds"] = output["data"][k]["numberOfFinds"]  + 2
                            # print("schodné - ", textImage1, " - ", textImage2, " - ", output["data"][k]["numberOfFinds"])
                        elif scequenceRatioMin <= scequenceRatio:
                            record = result["data"][j]
                            record["codeName"] = result["data"][j]["codeName"]
                            output["data"][k]["numberOfFinds"] = output["data"][k]["numberOfFinds"] + scequenceRatio * 2 * ratio2
                            record["numberOfFinds"] = record["numberOfFinds"] + scequenceRatio * 2 * ratio1
                            output["data"].append(record)
                            added = False
                            # print("podobné - ", textImage1, " - ", textImage2, " - ", output["data"][k]["numberOfFinds"])
                        else:
                            output["data"][k]["numberOfFinds"] = output["data"][k]["numberOfFinds"] - (1 - scequenceRatio * 2 * ratio2)
                            record["numberOfFinds"] = record["numberOfFinds"] - (1 - scequenceRatio * 2 * ratio1)
                            added = False
                            record = result["data"][j]
                            record["codeName"] = str(j)
                            output["data"].append(record)
                            # print("neschodné - ", textImage1, " - ", textImage2, " - ", output["data"][k]["numberOfFinds"])
            
                if added:
                    if noiseFilter(result["data"][j]["ocrText"]):
                        record = result["data"][j]
                        record["codeName"] = str(j)
                        output["data"].append(record)
                        # print("nenalezeno - ", result["data"][j]["ocrText"])
                    # else:
                        # print("šum - ", result["data"][j]["ocrText"])
    output2 = {
        "data": []
    }
    
    for i in range(len(output["data"])):
        result = output["data"][i]
        if result["numberOfFinds"] >= 1:
            output2["data"].append(result)
    
    return output2

    

class SolutionOCR:
    def __init__(self, language, minConfPts):
        self.language = language
        self.minConfPts = minConfPts

    def OCR(self, imageFile):


        image = Image.open(imageFile)
        imageForOCR = image.copy()
        
        gaussImage = imageForOCR.filter(ImageFilter.GaussianBlur(1))
        boxImage = imageForOCR.filter(ImageFilter.BoxBlur(5))
        blurImage = imageForOCR.filter(ImageFilter.BLUR)
        output_path3 = './output/imageDebugv3.jpg'
        
        output = {
            "results": []
        }
        
        result = outputSortingOCR(pytesseract.image_to_data(imageForOCR, lang=self.language, output_type=Output.DICT),0)
        output["results"].append(result)
        result = outputSortingOCR(pytesseract.image_to_data(gaussImage, lang=self.language, output_type=Output.DICT),0)
        output["results"].append(result)
        result = outputSortingOCR(pytesseract.image_to_data(blurImage, lang=self.language, output_type=Output.DICT),0)
        output["results"].append(result)
        return comperOCR(output)
        
        
        
    
        

    def filter(self, base):
        a = 60
        keyUnits = ["m", "g", "s"]
        prefixes = ["k", "d", "c", "m"]
        units = ["ks", "PCS", "n\\.", "č\\.", "h", "m", "d"]
        allUnits = units + unitsMaker(keyUnits, prefixes)
        # print(allUnits)
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
            if True:
                if  None != re.match(regex, rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "URL"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif  None != chackNumberAndUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "number and unit"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "unit"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, currencies):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "currencie"
                    output["data"].append(record)
                elif None != re.match('[0-9][0-9](:[0-9][0-9])+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "time"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9][0-9][\\.\\/][0-9][0-9][\\.\\/][0-9][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "date"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9]+[\\.\\,][0-9]+', rawOcrText) and None == re.search('[a-z]', rawOcrText.lower()):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9]+', rawOcrText) and None == re.search('[a-z]', rawOcrText.lower()):

                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "integer number"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
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
                            #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif dictionary.check(ocrTextClear):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "word"
                            output["data"].append(record)
                            #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        else:
                            if confPts <= a:
                                words = dictionary.suggest(rawOcrText.replace("*"," ").replace("-"," ").replace("/"," ").replace("."," "))
                                if int(len(words)) > 0:
                                    record["ocrText"] =  words[0]
                                    record["typeOfObject"] = "repaired word"
                                    output["data"].append(record)
                                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                                else:
                                    record["ocrText"] = rawOcrText
                                    record["typeOfObject"] = "deleted"
                                    output["data"].append(record)
                            else:
                                record["ocrText"] = rawOcrText
                                output["data"].append(record)
                                #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                    else: 
                        if confPts > a:
                            record["ocrText"] = rawOcrText
                            output["data"].append(record)
                            #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        else:
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "deleted"
                            output["data"].append(record)
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
        elif type == "deleted":
            color = black

        draw = rectangle2(draw, xcoords, ycoords, width, height, color)
        draw.text((xcoords, ycoords), textImage + "\n" + ID, font=font, fill=color)
    output.save(path)
