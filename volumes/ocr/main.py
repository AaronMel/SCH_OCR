from SolutionOCR import SolutionOCR, imageDebug
import datetime

ImageFile = "./input/seznam.jpg"
# ImageFile = "./input/uctenka.jpg"
# ImageFile = "./input/tabulka.png"
# ImageFile = "./input/smlouva.jpg"
output_path1 = './output/imageDebugv1.jpg'
output_path2 = './output/imageDebug2.jpg'

ocr_cz = SolutionOCR("ces", 0)


x = datetime.datetime.now()
output = ocr_cz.OCR(ImageFile)
y = datetime.datetime.now() - x
print(y)
imageDebug(ImageFile, output, output_path1)
output = ocr_cz.filter(output)
y = datetime.datetime.now() - x
print(y)
imageDebug(ImageFile, output, output_path2)
outputTextFile_path = './output/imageLog.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()
y = datetime.datetime.now() - x
print(y)
