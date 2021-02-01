import pytesseract
from pytesseract import Output
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import enchant
import re
from difflib import SequenceMatcher


import datetime


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
        
        
    

    
    
    



    



class SolutionOCR:
    def __init__(self, language, minConfPts):
        self.language = language
        self.minConfPts = minConfPts

    def OCR(self, imageFile):
        print("OCR start")
        x = datetime.datetime.now()

        image = Image.open(imageFile)
        imageForOCR = image.copy()
        
        gaussImage = imageForOCR.filter(ImageFilter.GaussianBlur(1))
        boxImage = imageForOCR.filter(ImageFilter.BoxBlur(5))
        blurImage = imageForOCR.filter(ImageFilter.BLUR)
        y = datetime.datetime.now() - x
        print(y, " image pripering")
        
        results = {
            "results": []
        }

        result = self.outputSortingOCR(pytesseract.image_to_data(imageForOCR, lang=self.language, output_type=Output.DICT),self.minConfPts)
        results["results"].append(result)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " OCR 1 strart")
        result = self.outputSortingOCR(pytesseract.image_to_data(gaussImage, lang=self.language, output_type=Output.DICT),self.minConfPts)
        results["results"].append(result)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " OCR 2 strart")
        result = self.outputSortingOCR(pytesseract.image_to_data(blurImage, lang=self.language, output_type=Output.DICT),self.minConfPts)
        results["results"].append(result)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " OCR 3 strart")
        output = self.comperOCR(results)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " comper OCR strart 1")
        
        output = self.sortingFilter(output)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " sorting filter finish")
        
        output = self.multiplicityFilter(output)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " multiplicity filter strart 1")
        
        results = {
            "results": []
        }
        results["results"].append(output)
        output = self.comperOCR(results)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " comper OCR strart 2")
        
        output = self.multiplicityFilter(output)
        y = datetime.datetime.now() - x
        x = datetime.datetime.now()
        print(y, " multiplicity filter strart 2")
        
        return output
        
        
    def comperOCR(self, input):
        
        overlayMin = 0.7                # 0.1 - 1
        bothOverlayMin = 0.5           # 0.1 - 1
        scequenceRatioMin = 0.4         # 0.1 - 1
        
        buffer = {
            "data": []
        }
        
        for i in range(len(input["results"])):
            result = input["results"][i]
            if i > -1:
                for j in range(len(result["data"])):
                    added = True
                    for k in range(len(buffer["data"])):
                        x1 = result["data"][j]["x"]
                        x2 = buffer["data"][k]["x"]
                        y1 = result["data"][j]["y"]
                        y2 = buffer["data"][k]["y"]
                        h1 = result["data"][j]["h"]
                        h2 = buffer["data"][k]["h"]
                        w1 = result["data"][j]["w"]
                        w2 = buffer["data"][k]["w"]
                        p3 = rectangleOverlay(x1, x2, y1, y2, w1, w2, h1, h2)
                        R1 = p3 / (h1 * w1)
                        R2 = p3 / (h2 * w2)
                        if R1 >= overlayMin or R2 >= overlayMin or (R1 >= bothOverlayMin and R2 >= bothOverlayMin) :
                            textImage1 = result["data"][j]["ocrText"]
                            textImage2 = buffer["data"][k]["ocrText"]
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
                            # print(buffer["data"][k]["codeName"], " - ", textImage1," - ", textImage2," - ", R1," - ", R2," - ", scequenceRatio)
                            if  1 == scequenceRatio:
                                added = False
                                buffer["data"][k]["numberOfFinds"] = buffer["data"][k]["numberOfFinds"]  + 1
                                # print("shodné - ", textImage1," - ", textImage2," - ", R1," - ", R1)
                            elif scequenceRatioMin <= scequenceRatio:
                                record = result["data"][j]
                                record["codeName"] = buffer["data"][k]["codeName"]
                                buffer["data"][k]["numberOfFinds"] = buffer["data"][k]["numberOfFinds"] + scequenceRatio  * ratio2
                                record["numberOfFinds"] = record["numberOfFinds"] + scequenceRatio  * ratio1
                                buffer["data"].append(record)
                                added = False
                                
                            else:
                                buffer["data"][k]["numberOfFinds"] = buffer["data"][k]["numberOfFinds"] - (scequenceRatioMin - scequenceRatio * ratio2)
                                record["numberOfFinds"] = record["numberOfFinds"] - (scequenceRatioMin - scequenceRatio * ratio1)
                                added = False
                                record = result["data"][j]
                                record["codeName"] = buffer["data"][k]["codeName"]
                                buffer["data"].append(record)
                
                    if added:
                        record = result["data"][j]
                        record["codeName"] = len(buffer["data"])
                        buffer["data"].append(record)

        output = {
            "data": []
        }
        
        for i in range(len(buffer["data"])):
            result = buffer["data"][i]
            if result["numberOfFinds"] >= 0.5:
                output["data"].append(result)
        output["data"] = sorted(output["data"], key=lambda student: student["codeName"])
        return output

    def outputSortingOCR(self, input, minConfPts):
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
            if confPts >= minConfPts and (xcoords != 0 or ycoords != 0) and noiseFilter(rawOcrText) :
                object = {
                    "codeName": i,
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
        
        
        
        
    def multiplicityFilter(self, input):
        output = {
            "data": []
        }
        
        buffer = {
            "data": []
        }
        
        for i in range(len(input["data"])):
            if len(buffer["data"]) == 0:
                buffer["data"].append(input["data"][i])
            else:
                if input["data"][i]["codeName"] == buffer["data"][0]["codeName"]:
                    buffer["data"].append(input["data"][i])
                else:
                    
                    if len(buffer["data"]) == 1:
                        
                        # print(str(buffer["data"][0]["codeName"]), " ",end ="")
                        # for j in range(len(buffer["data"])):
                        #     print(str(buffer["data"][j]["rawOcrText"]), " ", end ="")
                        # print("")
                        
                        if buffer["data"][0]["numberOfFinds"] > 1:
                            output["data"].append(buffer["data"][0])
                        elif buffer["data"][0]["numberOfFinds"] > 0.5:
                            if buffer["data"][0]["confPts"] > 50:
                                output["data"].append(buffer["data"][0])
                        else:
                            if buffer["data"][0]["confPts"] > 90:
                                output["data"].append(buffer["data"][0])
                            
                        buffer = {
                            "data": []
                        }
                        buffer["data"].append(input["data"][i])
                        
                    else:
                        buffer["data"] = sorted(buffer["data"], key=lambda student: student["numberOfFinds"])
                        if buffer["data"][-1]["numberOfFinds"] <= buffer["data"][-2]["numberOfFinds"] + 1:
                            # a = buffer["data"][-1]
                            # b = buffer["data"][-2]
                            # buffer = {
                            #     "data": []
                            # }
                            # 
                            # buffer["data"].append(b)
                            # buffer["data"].append(a)
                            
                            # print(str(buffer["data"][0]["codeName"]), " ",end =" ")
                            # for j in range(len(buffer["data"])):
                            #     print(str(buffer["data"][j]["rawOcrText"]), " ", end =" ")
                            # print("")
                            
                            # buffer = self.sortingFilter(buffer)
                            if buffer["data"][-1]["typeOfObject"] != "unknown" and buffer["data"][-2]["typeOfObject"] == "unknown":
                                output["data"].append(buffer["data"][-1])
                            elif buffer["data"][-1]["typeOfObject"] == "unknown" and buffer["data"][-2]["typeOfObject"] != "unknown":
                                output["data"].append(buffer["data"][-2])
                            else:
                                if buffer["data"][-1]["confPts"] >= buffer["data"][-2]["confPts"]:
                                    output["data"].append(buffer["data"][-1])
                                else:
                                    output["data"].append(buffer["data"][-2])
                        else:
                            output["data"].append(buffer["data"][-1])
                        
                        # print(str(buffer["data"][0]["codeName"]), " ",end =" ")
                        # for j in range(len(buffer["data"])):
                        #      print(str(buffer["data"][j]["rawOcrText"]), " ", end =" ")
                        # print("")
                        buffer = {
                            "data": []
                        }
                        buffer["data"].append(input["data"][i])
                        
            

            
        if len(buffer["data"]) == 1:
        
            # print(str(buffer["data"][0]["codeName"]), " ",end = "")
            # for j in range(len(buffer["data"])):
            #     print(str(buffer["data"][j]["rawOcrText"]), " ", end = "")
            # print("")
        
            if buffer["data"][0]["numberOfFinds"] > 1:
                output["data"].append(buffer["data"][0])
            elif buffer["data"][0]["numberOfFinds"] > 0.5:
                if buffer["data"][0]["confPts"] > 50:
                    output["data"].append(buffer["data"][0])
            else:
                if buffer["data"][0]["confPts"] > 90:
                    output["data"].append(buffer["data"][0])
                    
            buffer["data"].append(input["data"][i])
                
        else:
            buffer["data"] = sorted(buffer["data"], key=lambda student: student["numberOfFinds"])
            if buffer["data"][-1]["numberOfFinds"] <= buffer["data"][-2]["numberOfFinds"] + 0.5:
                
                
                # a = buffer["data"][-1]
                # b = buffer["data"][-2]
                # buffer = {
                #     "data": []
                # }
                # 
                # buffer["data"].append(b)
                # buffer["data"].append(a)
                # 
                # buffer = self.sortingFilter(buffer)
                
                if buffer["data"][-1]["typeOfObject"] != "unknown" and buffer["data"][-2]["typeOfObject"] == "unknown":
                    output["data"].append(buffer["data"][-1])
                elif buffer["data"][-1]["typeOfObject"] == "unknown" and buffer["data"][-2]["typeOfObject"] != "unknown":
                    output["data"].append(buffer["data"][-2])
                else:
                    if buffer["data"][-1]["confPts"] >= buffer["data"][-2]["confPts"]:
                        output["data"].append(buffer["data"][-1])
                    else:
                        output["data"].append(buffer["data"][-2])
            else:
                output["data"].append(buffer["data"][-1])
                
            # print(str(buffer["data"][0]["codeName"]), " ", end =" ")
            # for j in range(len(buffer["data"])):
            #     print(str(buffer["data"][j]["rawOcrText"]), " ", end =" ")
            # print("")
                        
                    
                    
        
        return output
        
        
        

    def sortingFilter(self, base):
        
        a = 60
        keyUnits = ["m", "g", "s"]
        prefixes = ["k", "d", "c", "m"]
        units = ["ks", "PCS", "n\\.", "č\\.", "h", "m", "d"]
        allUnits = units + unitsMaker(keyUnits, prefixes)
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
            if record["typeOfObject"] == "unknown":
                rawOcrText = record["rawOcrText"]
                ID = record["codeName"]
                confPts = record["confPts"]
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
                elif None != re.match('([0-9][0-9](:[0-9][0-9])+\\.?)$', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "time"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9]+[\\.\\/][0-9][0-9][\\.\\/][0-9][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "date"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9]+[\\.\\,][0-9]+', rawOcrText) and None == re.search('[a-z]', rawOcrText.lower()):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - " + str(record["ocrText"]))
                elif None != re.match('[0-9]+', rawOcrText) and None == re.search('[a-z]', rawOcrText.lower()) and None == re.search('\W', rawOcrText.lower()):

                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "integer number"
                    output["data"].append(record)
                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('(.{1,64}\\.[a-z]{2,3})$', rawOcrText):

                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "domain"
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
                                    #record["ocrText"] =  words[0]
                                    # record["typeOfObject"] = "repaired word"
                                    record["ocrText"] = rawOcrText
                                    record["typeOfObject"] = "unknown"
                                    output["data"].append(record)
                                    #print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                                else:
                                    record["ocrText"] = rawOcrText
                                    record["typeOfObject"] = "unknown"
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
                            record["typeOfObject"] = "unknown"
                            output["data"].append(record)
            else:
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
        ID = str(dictionary["data"][i]["codeName"])
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
        elif type == "domain":
            color = greenLight
        elif type == "deleted":
            color = black
        

        draw = rectangle2(draw, xcoords, ycoords, width, height, color)
        draw.text((xcoords, ycoords), textImage + "\n" + ID, font=font, fill=color)
    output.save(path)
