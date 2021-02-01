from SolutionOCR import SolutionOCR, imageDebug
import datetime

# ImageFile = "./input/seznam.jpg"
ImageFile = "./input/uctenka.jpg"
# ImageFile = "./input/tabulka.png"
# ImageFile = "./input/smlouva.jpg"
output_path1 = './output/imageDebugv1.jpg'
output_path2 = './output/imageDebug2.jpg'

ocr_cz = SolutionOCR("ces", 30)


x = datetime.datetime.now()
output = ocr_cz.OCR(ImageFile)
imageDebug(ImageFile, output, output_path1)
y = datetime.datetime.now() - x
print(y, " OCR finish")


# output = ocr_cz.sortingFilter(output)
# imageDebug(ImageFile, output, output_path2)


outputTextFile_path = './output/imageLog.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()
