from SolutionOCR import SolutionOCR, imageDebug

ImageFile1 = "./input/Seznam.jpg"
ImageFile2 = "./input/uctenka.jpg"

# basic image output not refined
output_basic = './output/basicImageDebug.jpg'

output_basic1 = './output/basicImageDebug1.jpg'
output_basic2 = './output/basicImageDebug2.jpg'
output_basic3 = './output/basicImageDebug3.jpg'
output_basic4 = './output/basicImageDebug4.jpg'
output_basic5 = './output/basicImageDebug5.jpg'
output_basic6 = './output/basicImageDebug6.jpg'
# refined image output all languages optimized
output_dict = './output/dictImageDebug.jpg'

output_dict1 = './output/dictImageDebug1.jpg'
output_dict2 = './output/dictImageDebug2.jpg'
output_dict3 = './output/dictImageDebug3.jpg'
output_dict4 = './output/dictImageDebug4.jpg'
output_dict5 = './output/dictImageDebug5.jpg'
output_dict6 = './output/dictImageDebug6.jpg'


ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1)
imageDebug(ImageFile1, output, output_basic)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output, output_dict)

outputTextFile_path = './output/imageLog.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()

"""
# GaussianBlur
ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1)
imageDebug(ImageFile1, output, output_basic1)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output, output_dict1)

outputTextFile_path = './output/imageLog1.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    # print(str(output["data"][i]))
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()

# BoxBlur
ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1, filterType="bblur")
imageDebug(ImageFile1, output, output_basic2)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output, output_dict2)

outputTextFile_path = './output/imageLog2.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    # print(str(output["data"][i]))
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()

# blur
ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1, filterType="blur")
imageDebug(ImageFile1, output, output_basic3)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output, output_dict3)

outputTextFile_path = './output/imageLog3.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    # print(str(output["data"][i]))
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()

# contour
ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1, filterType="cont")
imageDebug(ImageFile1, output, output_basic4)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output, output_dict4)

outputTextFile_path = './output/imageLog4.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    # print(str(output["data"][i]))
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()

# find edges
ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1, filterType="find")
imageDebug(ImageFile1, output, output_basic5)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output, output_dict5)

outputTextFile_path = './output/imageLog5.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    # print(str(output["data"][i]))
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()

# edge enhance more
ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile1, filterType="edge")
imageDebug(ImageFile1, output, output_basic6)
output = ocr_cz.filter(output)
imageDebug(ImageFile1, output, output_dict6)

outputTextFile_path = './output/imageLog6.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    # print(str(output["data"][i]))
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()
"""
