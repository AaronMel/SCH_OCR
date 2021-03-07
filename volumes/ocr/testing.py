from condor import Condor
import datetime

from PIL import Image, ImageFont, ImageDraw
from condor import rectangle2

baseImageFile = "./input/uctenka.jpg"
output_path2 = './output/imageDebug2.jpg'
keylist = './valuables_keys.txt'
ocr_cz = Condor("ces", 30)

def roi_finder(valuableList, imageFile):

    output = ocr_cz.OCR(imageFile)

    vFile = open(valuableList, "r", encoding='utf-8')
    Vlist = []
    Vcontent = vFile.read().split("\n")
    #print(Vcontent)
    for item in Vcontent:
        Vlist.append(item)
    vFile.close()
    #print(Vlist)

    base = {
        "matches": []
    }

    wantedBase = {
        "members": []
    }

    for record in output["data"]:
        x = record["x"]
        y = record["y"]
        w = record["w"]
        h = record["h"]
        text = record["ocrText"]
        # insert something to find parts of string (containing ':') and splitting them and using if key is first
        for member in Vlist:
            if text == member:
                Mx = x
                My = y
                Mw = w
                Mh = h
                Mtext = text
                object = {
                    "x": Mx,
                    "y": My,
                    "w": Mw,
                    "h": Mh,
                    "name": Mtext
                }
                wantedBase["members"].append(object)
    
    #print("Val base: {}".format(wantedBase["members"]))
    for recordMember in wantedBase["members"]:
        print("############################ \n {}".format(recordMember["name"]))
        Vy = recordMember["y"]
        Vh = recordMember["h"]

        Vx = recordMember["x"]
        Vw = recordMember["w"]

        Ay = Vy
        By = Vy + (Vh * 0.25)
        Cy = Vy + (Vh * 0.5)
        Dy = Vy + (Vh * 0.75)
        Ey = Vy + Vh

        Ax = Vx
        Bx = Vx + (Vw * 0.25)
        Cx = Vx + (Vw * 0.5)
        Dx = Vx + (Vw * 0.75)
        Ex = Vx + Vw

        for recordOCR in output["data"]:
            posY = recordOCR["y"]
            posH = recordOCR["h"]

            posX = recordOCR["x"]
            posW = recordOCR["w"]

            Fy = posY
            Gy = posY + posH

            Fx = posX
            Gx = posX + posW
            
            conf = 0
            if Vx < posX:
                for i in range(Fy, Gy+1):
                    if Ay == i:
                        conf = conf + 1
                    elif By == i:
                        conf = conf + 1                
                    elif Cy == i:
                        conf = conf + 1
                    elif Dy == i:
                        conf = conf + 1
                    elif Ey == i:
                        conf = conf + 1
            #print("Horizontal search conf: {}".format(conf))
            if conf >= 1: 
                Vname = recordMember["name"]
                posName = recordOCR["ocrText"]
                print("######## Horizontal search ########")
                print("Val: {}".format(Vname))
                print("Pos: {}".format(posName))
                confControl = 0
                for recordControl in wantedBase["members"]:
                    #print("Record Control: {}".format(recordControl["name"]))
                    if posName == recordControl["name"]:
                        confControl = 1
                if confControl == 0:
                    object = {
                        "Vx": Vx,
                        "Vy": Vy,
                        "Vw": Vw,
                        "Vh": Vh,
                        "Vname": Vname,
                        "Mx": posX,
                        "My": posY,
                        "Mw": posW,
                        "Mh": posH,
                        "Mname": posName
                    }
                    base["matches"].append(object)

            conf = 0
            if Vy < posY:
                for i in range(Fx, Gx+1):
                    if Ax == i:
                        conf = conf + 1
                    elif Bx == i:
                        conf = conf + 1                
                    elif Cx == i:
                        conf = conf + 1
                    elif Dx == i:
                        conf = conf + 1
                    elif Ex == i:
                        conf = conf + 1
            #print("Vertical search conf: {}".format(conf))
            if conf >= 1: 
                Vname = recordMember["name"]
                posName = recordOCR["ocrText"]
                print("######## Vertical search ########")
                print("Val: {}".format(Vname))
                print("Pos: {}".format(posName))
                confControl = 0
                for recordControl in wantedBase["members"]:
                    #print("Record Control: {}".format(recordControl["name"]))
                    if posName == recordControl["name"]:
                        confControl = 1
                if confControl == 0:
                    object = {
                        "Vx": Vx,
                        "Vy": Vy,
                        "Vw": Vw,
                        "Vh": Vh,
                        "Vname": Vname,
                        "Mx": posX,
                        "My": posY,
                        "Mw": posW,
                        "Mh": posH,
                        "Mname": posName
                    }
                    base["matches"].append(object)

    return base

def roi_imageDebug(imageFile, wordDisplay, outputPath):
    baseImage = Image.open(imageFile)
    output = baseImage.copy()
    output = output.convert("RGB")
    draw = ImageDraw.Draw(output)

    red = (255, 0, 0)
    green = (0, 255, 0)

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 16)
    for i in range(len(wordDisplay["matches"])):

        ValuableX = wordDisplay["matches"][i]["Vx"]
        ValuableY = wordDisplay["matches"][i]["Vy"]
        ValuableW = wordDisplay["matches"][i]["Vw"]
        ValuableH = wordDisplay["matches"][i]["Vh"]
        ValuableText = wordDisplay["matches"][i]["Vname"]
        ValuableColor = red

        MatchedX = wordDisplay["matches"][i]["Mx"]
        MatchedY = wordDisplay["matches"][i]["My"]
        MatchedW = wordDisplay["matches"][i]["Mw"]
        MatchedH = wordDisplay["matches"][i]["Mh"]
        MatchedText = wordDisplay["matches"][i]["Mname"]
        MatchedColor = green
        
        draw = rectangle2(draw, ValuableX, ValuableY, ValuableW, ValuableH, ValuableColor)
        draw.text((ValuableX, ValuableY), ValuableText, font=font, fill=ValuableColor)

        draw = rectangle2(draw, MatchedX, MatchedY, MatchedW, MatchedH, MatchedColor)
        draw.text((MatchedX, MatchedY), MatchedText, font=font, fill=MatchedColor)

    output.save(outputPath)

time1 = datetime.datetime.now()
roiOut = roi_finder(keylist, baseImageFile)
#print(roiOut["matches"])
roi_imageDebug(baseImageFile, roiOut, output_path2)
time2 = datetime.datetime.now() - time1
print("Total time: {}".format(time2))
