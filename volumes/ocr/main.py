from SolutionOCR import SolutionOCR, imageDebug
import datetime

import reportlab.rl_config
from reportlab.lib import utils
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from PIL import ImageFont

# ImageFile = "./input/seznam.jpg"
# ImageFile = "./input/uctenka.jpg"
# ImageFile = "./input/tabulka.png"
ImageFile = "./input/smlouva.jpg"

output_path1 = './output/imageDebugv1.jpg'
output_path2 = './output/imageDebug2.jpg'
output_path3 = './output/imageDebug3.pdf'
ocr_cz = SolutionOCR("ces", 30)


x = datetime.datetime.now()
output = ocr_cz.OCR(ImageFile)
imageDebug(ImageFile, output, output_path1)
y = datetime.datetime.now() - x
print(y, " OCR finish")

t1 = datetime.datetime.now()
print("PDF build start")

img = utils.ImageReader(ImageFile)

img_width, img_height = img.getSize()
aspect = img_height / float(img_width)

my_canvas = canvas.Canvas(output_path3, pagesize=(img_width, img_height))

my_canvas.drawImage(ImageFile, 0, 0, width=img_width, height=img_height)

reportlab.rl_config.TTFSearchpath = './'
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

for record in output["data"]:
    x = record["x"]
    y = record["y"]
    w = record["w"]
    h = record["h"]
    text = record["ocrText"]

    p = h / (w / len(text))
    if p >= 0.5 and p <= 4.5:
        wtest = 0
        matrickMin = round(h*0.75)
        matrickMax = round(h*2.25)
        matrick = round((matrickMin + matrickMax)/2)
        matrick = h
        paroximation = matrick
        best = [0, 10000]
        for i in range(20):
            font = ImageFont.truetype('./arial.ttf', matrick)
            size2 = font.getsize(text)
            wtest = size2[0]
            if best[1] > abs(w - wtest):
                best[0] = matrick
                best[1] = abs(w - wtest)

            if paroximation == 0:
                break
            else:
                # tfzu = w - wtest
                if wtest > w:
                    paroximation = round(paroximation / 2)
                    matrick = matrick - paroximation
                elif wtest < w:
                    paroximation = round(paroximation / 2)
                    matrick = matrick + paroximation
                else:
                    break
        my_text = my_canvas.beginText()
        my_text.setTextOrigin(x, img_height - y - round(h) * (3/4))
        my_text.setFillColor(colors.transparent)
        #my_text.setFillColor(colors.red)
        my_text.setFont("Arial", best[0])
        my_text.textLine(text=text)
        my_canvas.drawText(my_text)
my_canvas.save()

t2 = datetime.datetime.now() - t1
print(t2, " PDF build finish")

outputTextFile_path = './output/imageLog.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()
