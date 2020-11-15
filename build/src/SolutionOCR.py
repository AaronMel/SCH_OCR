import pytesseract
from pytesseract import Output
from PIL import Image, ImageFont, ImageDraw, ImageFilter
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

class SolutionOCR:
    def __init__(self, language, minConfPts):
        self.language = language
        self.minConfPts = minConfPts

    def OCR(self, imageFile):
        base = {
            "data": []
        }

        image = Image.open(imageFile)
        imageForOCR = image.copy() # 813
        # Filters for ocr (blurs)
        gaussImage = imageForOCR.filter(ImageFilter.GaussianBlur(1)) # 828 confPts: avg. 93
        boxImage = imageForOCR.filter(ImageFilter.BoxBlur(5))
        blurImage = imageForOCR.filter(ImageFilter.BLUR) # 836
        results = pytesseract.image_to_data(gaussImage, lang=self.language, output_type=Output.DICT)
        for i in range(0, len(results["text"])):
            xcoords = results["left"][i]
            ycoords = results["top"][i]
            width = results["width"][i]
            height = results["height"][i]

            ocrText = results["text"][i]
            confPts = int(results["conf"][i])

            rawOcrText = results["text"][i]
            #print(str(i))
            if ocrText.isspace() or not ocrText or ocrText == "|" or ocrText == "." or ocrText == "-":
                continue

            # numbers, codes and units detector
            # if not confPts == 100:
            #     if ocrText.isalnum():
            #         if ocrText.isdigit():
            #             confPts = 100
            #         elif ocrText.count("-") >= 1:
            #             #INSERT CODE FILTER#
            #             confPts = 100
            #         else:
            #             #INSERT UNITS FILTER#
            #             pass
            # 
            # # decimal numbers detector
            # # may need to be optimized
            # if not confPts == 100:
            #     if ocrText.count(",") == 1:
            #         decimal = ocrText.replace(",", ".")
            #         try:
            #             float(decimal)
            #             confPts = 100
            #             ocrText = decimal
            #         except ValueError:
            #             pass
            # if not confPts == 100:
            #     if ocrText.count(".") == 1:
            #         try:
            #             float(ocrText)
            #             confPts = 100
            #         except ValueError:
            #             pass

            # may need to add special dictionary checkpoint for shortcuts etc. (must be first)

            # grammar check
            # may need to be optimized

            # if not confPts == 100:
            #     if not wordFilter.langDetec(ocrText):
            #         if wordFilter.spellchecker(ocrText, dictPathCes, affPathCes)[0]:
            #             ocrText = wordFilter.spellchecker(ocrText, dictPathCes, affPathCes)[1]
            #             confPts = 100
            #         """
            #         elif wordFilter.spellchecker(ocrText, dictPathEng, affPathEng)[0]:
            #             ocrText = wordFilter.spellchecker(ocrText, dictPathEng, affPathEng)[1]
            #             confPts = 100
            #         elif wordFilter.spellchecker(ocrText, dictPathGer, affPathGer)[0]:
            #             ocrText = wordFilter.spellchecker(ocrText, dictPathGer, affPathGer)[1]
            #             confPts = 100
            #         """
            #     else:
            #         confPts = 100
            
            if confPts > self.minConfPts:
                object = {
                    'codeName': str(i),
                    'x': xcoords,
                    'y': ycoords,
                    'w': width,
                    'h': height,
                    'ocrText': ocrText,
                    'rawOcrText': rawOcrText,
                    'confPts': confPts
                }
                base["data"].append(object)

                #debugImage(imageFile, ocrText, xcoords, ycoords, i)
        return base

def imageDebug(imageFile, dictionary, path):
    baseImage = Image.open(imageFile)
    output = baseImage.copy()
    draw = ImageDraw.Draw(output)
    red = (255, 0, 0)
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 16)
    for i in range(len(dictionary["data"])):
        xcoords = dictionary["data"][i]['x']
        ycoords = dictionary["data"][i]['y']
        width = dictionary["data"][i]['w']
        height = dictionary["data"][i]['h']
        textImage = dictionary['data'][i]['ocrText']
        ID = dictionary['data'][i]['codeName']

        draw = rectangle2(draw, xcoords, ycoords, width, height, red)
        draw.text((xcoords, ycoords), textImage + "\n" + ID, font=font, fill=red)
    output.save(path)
