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
            "data": [],
            "dataGauss": [],
            "dataCont": [],
            "dataConfirmed": []
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

        for a in range(0, len(resultsGauss["text"])):
            xcoordsGauss = resultsGauss["left"][a]
            ycoordsGauss = resultsGauss["top"][a]
            widthGauss = resultsGauss["width"][a]
            heightGauss = resultsGauss["height"][a]

            textGauss = resultsGauss["text"][a]
            confPtsGauss = int(resultsGauss["conf"][a])

            object = {
                "codeName": str(a),
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

            for b in range(0, len(resultsCont["text"])):
                xcoordsCont = resultsCont["left"][b]
                ycoordsCont = resultsCont["top"][b]
                widthCont = resultsCont["width"][b]
                heightCont = resultsCont["height"][b]

                textCont = resultsCont["text"][b]
                confPtsCont = int(resultsCont["conf"][b])

                if confPtsGauss > self.minConfPts:
                    if xcoordsGauss == xcoordsCont:
                        if ycoordsGauss == ycoordsCont:
                            if textGauss == textCont:
                                confirText = textGauss
                                confirX = xcoordsGauss
                                confirY = ycoordsGauss
                                confirW = widthGauss
                                confirH = heightGauss

                                object = {
                                    "codeName": str(a),
                                    "x": confirX,
                                    "y": confirY,
                                    "w": confirW,
                                    "h": confirH,
                                    "ocrText": confirText,
                                    "rawOcrText": confirText,
                                    "confPts": 100,
                                    "typeOfObject": "unknown"
                                }
                                base["dataConfirmed"].append(object)

        for i in range(0, len(resultsCont["text"])):
            xcoordsCont = resultsCont["left"][i]
            ycoordsCont = resultsCont["top"][i]
            widthCont = resultsCont["width"][i]
            heightCont = resultsCont["height"][i]

            textCont = resultsCont["text"][i]
            confPtsCont = int(resultsCont["conf"][i])

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
        """
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
        """



    def filter(self, base):
        keyUnits = ["m","g","s"]
        prefixes = ["k","d","c","m" ]
        units = ["ks","PCS","n.","č.","h","m","d"]
        allUnits = units + unitsMaker(keyUnits, prefixes)
        print (allUnits)
        currencies = ["kč","czk","eur","eu","usd","gbp","$","€","£"]

        dictionary = enchant.Dict("cs")
        output = {
            "data": []
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
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "unit"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, currencies):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "currencie"
                    output["data"].append(record)
                elif None != re.match('[0-9][0-9](:[0-9][0-9])+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "time"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9][0-9][\.\/][0-9][0-9][\.\/][0-9][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "date"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+', rawOcrText):
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
                        if  None != chackUnits(ocrTextClear, allUnits):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "unit"
                            output["data"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif  None != chackUnits(ocrTextClear, currencies):
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
                            record["ocrText"] = rawOcrText
                            output["data"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
        for record in base["dataConfirmed"]:
            a = 60
            b = 35
            rawOcrText = record["rawOcrText"]
            ID = int(record["codeName"])
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
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, allUnits):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "unit"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif  None != chackUnits(rawOcrText, currencies):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "currencie"
                    output["data"].append(record)
                elif None != re.match('[0-9][0-9](:[0-9][0-9])+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "time"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9][0-9][\.\/][0-9][0-9][\.\/][0-9][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "date"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+[\.\,][0-9]+', rawOcrText):
                    record["ocrText"] = rawOcrText
                    record["typeOfObject"] = "decimal number"
                    output["data"].append(record)
                    print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                elif None != re.match('[0-9]+', rawOcrText):
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
                        if  None != chackUnits(ocrTextClear, allUnits):
                            record["ocrText"] = rawOcrText
                            record["typeOfObject"] = "unit"
                            output["data"].append(record)
                            print(str(ID) + " - " + str(record["confPts"]) + " - " + str(record["typeOfObject"]) + " - "+ str(record["ocrText"]))
                        elif  None != chackUnits(ocrTextClear, currencies):
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
                            record["ocrText"] = rawOcrText
                            output["data"].append(record)
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



        draw = rectangle2(draw, xcoords, ycoords, width, height, color)
        draw.text((xcoords, ycoords), textImage + "\n" + ID, font=font, fill=color)
    output.save(path)
