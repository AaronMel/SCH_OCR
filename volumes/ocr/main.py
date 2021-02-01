from SolutionOCR import SolutionOCR, imageDebug

ImageFile1 = "./input/Seznam.jpg"
ImageFile2 = "./input/uctenka.jpg"

# basic image output not refined
output_basic = './output/basicImageDebug001.jpg'
output_basic2 = './output/basicImageDebug002.jpg'
# refined image output all languages optimized
output_dict = './output/dictImageDebug001.jpg'
output_dict2 = './output/dictImageDebug002.jpg'

# Log deletion #
with open('./output/imageLog.txt', "w", encoding="utf-8") as log:
    log.write("Log file 1" + "\n")
with open('./output/imageLog2.txt', "w", encoding="utf-8") as log:
    log.write("Log file 2" + "\n")
### SEZNAM ###

ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1)
imageDebug(ImageFile1, output["dataGauss"], output_basic)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output["dataConfirmed"], output_dict)

outputTextFile_path = './output/imageLog.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["dataConfirmed"])):
    textFile.write(str(output["dataConfirmed"][i]) + '\n')
textFile.close()
"""
### ÚČTENKA ###
ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile2)
imageDebug(ImageFile2, output["dataGauss"], output_basic2)
output = ocr_cz.filter(output)
imageDebug(ImageFile2, output["dataConfirmed"], output_dict2)

outputTextFile_path = './output/imageLog2.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["dataConfirmed"])):
    textFile.write(str(output["dataConfirmed"][i]) + '\n')
textFile.close()
"""