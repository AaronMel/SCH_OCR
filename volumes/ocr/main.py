from SolutionOCR import SolutionOCR, imageDebug

ImageFile = "./input/Seznam.jpg"
output_path1 = './output/imageDebugv1.jpg'
output_path2 = './output/imageDebug2.jpg'

ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile)
imageDebug(ImageFile, output, output_path1)
output = ocr_cz.filter(output)
imageDebug(ImageFile, output, output_path2)

outputTextFile_path = './output/imageLog.txt'
textFile = open(outputTextFile_path, 'w+', encoding='utf-8')
for i in range(len(output["data"])):
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()
