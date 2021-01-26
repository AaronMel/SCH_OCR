import pytesseract
from pytesseract import Output
from PIL import Image, ImageFont, ImageDraw, ImageFilter
import enchant
import re
# from DictionaryProcessing import wordFilter

# # spellchecking dictionaries
# dictPathCes = "/usr/share/hunspell/cs_CZ.dic"
# dictPathEng = "/usr/share/hunspell/en_US.dic"
# dictPathGer = "/usr/share/hunspell/de_DE.dic"
# affPathCes = "/usr/share/hunspell/cs_CZ.aff"
# affPathEng = "/usr/share/hunspell/en_US.aff"
# affPathGer = "/usr/share/hunspell/de_DE.aff"

def rectangle2(draw, x ,y ,l ,h, Outline):
    x1 = x + l
    y1 = y + h
    draw.rectangle((x1, y1, x, y), outline=Outline)
    return draw

def chackNumberAndUnits(input, units):
    for unit in units:
        a = "[0-9]+(" + unit + "\.*)$"
        if None != re.match(a, input.lower(), re.IGNORECASE):
            return unit
    return None

def chackUnits(input, units):
    for unit in units:
        a = "(" + unit + ")$"
        if None != re.match(a, input.lower(), re.IGNORECASE):
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

    def OCR(self, imageFile, filter=True, filterType="gauss"):
        base = {
            "dataGauss": [],
            "dataCont": []
        }

        image = Image.open(imageFile)
        imageForOCR = image.copy()
        if filter:
        # Filters for ocr (blurs)
            pass
            """
            if filterType == "gauss":

            elif filterType == "bblur":
                boxImage = imageForOCR.filter(ImageFilter.BoxBlur(1))
                designatedImage = boxImage
            elif filterType == "blur":
                blurImage = imageForOCR.filter(ImageFilter.BLUR)
                designatedImage = blurImage
            elif filterType == "cont":

            elif filterType == "find":
                findImage = imageForOCR.filter(ImageFilter.FIND_EDGES)
                designatedImage = findImage
            elif filterType == "edge":
                edgeImage = imageForOCR.filter(ImageFilter.EDGE_ENHANCE_MORE)
                designatedImage = edgeImage
        else:
            designatedImage = imageForOCR
            """
        gaussImage = imageForOCR.filter(ImageFilter.GaussianBlur(1))
        resultsGauss = pytesseract.image_to_data(gaussImage, lang=self.language, output_type=Output.DICT)

        contImage = imageForOCR.filter(ImageFilter.CONTOUR)
        resultsCont = pytesseract.image_to_data(contImage, lang=self.language, output_type=Output.DICT)

        print(resultsGauss)

        for i in range(0, len(resultsGauss["text"])):
            xcoordsGauss = resultsGauss["left"][i]
            ycoordsGauss = resultsGauss["top"][i]
            widthGauss = resultsGauss["width"][i]
            heightGauss = resultsGauss["height"][i]

            textGauss = resultsGauss["text"][i]
            confPtsGauss = int(resultsGauss["conf"][i])

            if confPtsGauss >= self.minConfPts:
                if int(xcoordsGauss) != 0:
                    object = {
                        "codeName": str(i),
                        "x": xcoordsGauss,
                        "y": ycoordsGauss,
                        "w": widthGauss,
                        "h": heightGauss,
                        "ocrText": textGauss,
                        "rawOcrText": textGauss,
                        "confPts": confPtsGauss,
                        "typeOfObject": "unknown"
                    }
                    base["dataGauss"].append(object)

        for i in range(0, len(resultsCont["text"])):
            xcoordsCont = resultsCont["left"][i]
            ycoordsCont = resultsCont["top"][i]
            widthCont = resultsCont["width"][i]
            heightCont = resultsCont["height"][i]

            textCont = resultsCont["text"][i]
            confPtsCont = int(resultsCont["conf"][i])

            if confPtsCont >= self.minConfPts:
                if int(xcoordsCont) != 0:
                    object = {
                        "codeName": str(i),
                        "x": xcoordsCont,
                        "y": ycoordsCont,
                        "w": widthCont,
                        "h": heightCont,
                        "ocrText": textCont,
                        "rawOcrText": textCont,
                        "confPts": confPtsCont,
                        "typeOfObject": "unknown"
                    }
                    base["dataCont"].append(object)

        return base

    def filter(self, base):
        keyUnits = ["m","g","s"]
        prefixes = ["k","d","c","m" ]
        units = ["ks","PCS","n.","č.","h","m","d"]
        allUnits = units + unitsMaker(keyUnits, prefixes)
        print (allUnits)
        currencies = ["kč","czk","eur","eu","usd","gbp","$","€","£"]

        dictionary = enchant.Dict("cs")
        output = {
            "dataGauss": [],
            "dataCont": [],
            "dataConfirmed": []
        }

        for record in base["dataGauss"]:
            a = 60
            b = 35
            rawOcrText = record["rawOcrText"]
            ID = record["codeName"]
            confPts = record["confPts"]
            if rawOcrText.isspace() or not rawOcrText:
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\" \" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\.\.\.\.+\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"..\" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\—\—+\ *)', rawOcrText):
                print(str(ID)+ " - " + str(record["confPts"]) + " - " + "\"——\" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\-\-+\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"--\" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\|+\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"|\" - "+ str(record["rawOcrText"]))
                pass
            else:
                if  None != chackNumberAndUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "number and unit"
                    output["dataGauss"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "unit"
                    output["dataGauss"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, currencies):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "currency"
                    output["dataGauss"].append(record)
                elif None != re.match('[0-9][0-9](:[0-9][0-9])+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "time"
                    output["dataGauss"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9][0-9][\.\/][0-9][0-9][\.\/][0-9][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "date"
                    output["dataGauss"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["dataGauss"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["dataGauss"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "integer number"
                    output["dataGauss"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                else:
                    ocrTextClear = ""
                    for character in rawOcrText:
                        if character.isalnum():
                            ocrTextClear += character
                    if ocrTextClear != "":
                        if  None != chackUnits(ocrTextClear, allUnits):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "unit"
                            output["dataGauss"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif  None != chackUnits(ocrTextClear, currencies):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "currency"
                            output["dataGauss"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif dictionary.check(ocrTextClear):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "word"
                            output["dataGauss"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        else:
                            record["ocrText"] = rawOcrText
                            output["dataGauss"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))

        for record in base["dataCont"]:
            a = 60
            b = 35
            rawOcrText = record["rawOcrText"]
            ID = record["codeName"]
            confPts = record["confPts"]
            if rawOcrText.isspace() or not rawOcrText:
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\" \" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\.\.\.\.+\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"..\" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\—\—+\ *)', rawOcrText):
                print(str(ID)+ " - " + str(record["confPts"]) + " - " + "\"——\" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\-\-+\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"--\" - "+ str(record["rawOcrText"]))
                pass
            elif None != re.match('(\ *\|+\ *)', rawOcrText):
                print(str(ID) + " - " + str(record["confPts"]) + " - " + "\"|\" - "+ str(record["rawOcrText"]))
                pass
            else:
                if  None != chackNumberAndUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "number and unit"
                    output["dataCont"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "unit"
                    output["dataCont"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, currencies):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "currency"
                    output["dataCont"].append(record)
                elif None != re.match('[0-9][0-9](:[0-9][0-9])+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "time"
                    output["dataCont"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9][0-9][\.\/][0-9][0-9][\.\/][0-9][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "date"
                    output["dataCont"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["dataCont"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["dataCont"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "integer number"
                    output["dataCont"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                else:
                    ocrTextClear = ""
                    for character in rawOcrText:
                        if character.isalnum():
                            ocrTextClear += character
                    if ocrTextClear != "":
                        if  None != chackUnits(ocrTextClear, allUnits):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "unit"
                            output["dataCont"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif  None != chackUnits(ocrTextClear, currencies):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "currency"
                            output["dataCont"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif dictionary.check(ocrTextClear):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "word"
                            output["dataCont"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        else:
                            record["ocrText"] = rawOcrText
                            output["dataCont"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))

       


                # ocrTextClear = ""
                # for character in rawOcrText:
                #     if character.isalnum():
                #         ocrTextClear += character
                # if ocrTextClear != "":
                #     if dictionary.check(ocrTextClear):
                #         record["confPts"] = 100
                #         record["ocrText"] = rawOcrText
                #         record["typeOfObject"] = 1
                #         output["data"].append(record)
                #         print(str(ID) + " - " + str(record["typeOfObject"]) + " - "+ str(ocrTextClear) + " - "+ str(record["ocrText"]))
                #     elif confPts >= a:
                #         record["ocrText"] = rawOcrText
                #         record["typeOfObject"] = 2
                #         output["data"].append(record)
                #         print(str(ID) + " - " + str(record["typeOfObject"]) + " - "+ str(record["rawOcrText"]) + " - "+ str(record["ocrText"]))
                #     elif confPts < a and confPts >= b:
                #         words = dictionary.suggest(rawOcrText.replace("*"," ").replace("-"," ").replace("/"," ").replace("."," "))
                #         if int(len(words)) > 0:
                #             record["ocrText"] =  words[0]
                #             record["typeOfObject"] = 3
                #             output["data"].append(record)
                #             print(str(ID) + " - " + str(record["typeOfObject"]) + " - "+ str(record["rawOcrText"]) + " - "+ str(record["ocrText"]))
                #         else:
                #             record["ocrText"] = rawOcrText
                #             record["typeOfObject"] = 4
                #             output["data"].append(record)
                #             print(str(ID) + " - " + str(record["typeOfObject"]) + " - "+ str(record["rawOcrText"]) + " - "+ str(record["ocrText"]))
                #     elif confPts < b:
                #         record["ocrText"] = rawOcrText
                #         record["typeOfObject"] = 5
                #         output["data"].append(record)
                #         print(str(ID) + " - " + str(record["typeOfObject"]) + " - "+ str(record["rawOcrText"]) + " - "+ str(record["ocrText"]))
                #
                #

        for a in range(len(base["dataGauss"])):
            xcoordsGauss = base["dataGauss"][a]["x"]
            ycoordsGauss = base["dataGauss"][a]["y"]
            widthGauss = base["dataGauss"][a]["w"]
            heightGauss = base["dataGauss"][a]["h"]
            typeGauss = base["dataGauss"][a]["typeOfObject"]

            textGauss = base["dataGauss"][a]["ocrText"]
            confPtsGauss = int(base["dataGauss"][a]["confPts"])

            for b in range(len(base["dataCont"])):
                xcoordsCont = base["dataCont"][b]["x"]
                ycoordsCont = base["dataCont"][b]["y"]
                textCont = base["dataCont"][b]["ocrText"]

                if confPtsGauss >= self.minConfPts:
                    if xcoordsGauss - xcoordsCont <= 5:
                        if ycoordsGauss - ycoordsCont <= 5:
                            if textGauss == textCont:
                                #if typeGauss != "unknown":

                                confirText = textGauss
                                confirX = xcoordsGauss
                                confirY = ycoordsGauss
                                confirW = widthGauss
                                confirH = heightGauss
                                confirType = typeGauss

                                object = {
                                    "codeName": str(a),
                                    "x": confirX,
                                    "y": confirY,
                                    "w": confirW,
                                    "h": confirH,
                                    "ocrText": confirText,
                                    "rawOcrText": confirText,
                                    "confPts": 100,
                                    "typeOfObject": confirType
                                }
                                output["dataConfirmed"].append(object)
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
    yellow = (255,192,3)
    orange = (255, 209, 51)
    green = (170, 207, 66)
    blue = (0,112,192)
    blueLight = (4, 178, 241)
    purpleLight = (156, 51, 255)
    ping = (233, 51, 255)
    purple = (88, 24, 69)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16)
    for i in range(len(dictionary)):
        xcoords = dictionary[i]["x"]
        ycoords = dictionary[i]["y"]
        width = dictionary[i]["w"]
        height = dictionary[i]["h"]
        textImage = dictionary[i]["ocrText"]
        ID = dictionary[i]["codeName"]
        type = dictionary[i]["typeOfObject"]
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
        elif type == "currency":
            color = purple



        draw = rectangle2(draw, xcoords, ycoords, width, height, color)
        draw.text((xcoords, ycoords), textImage + "\n" + ID, font=font, fill=color)
    output.save(path)
