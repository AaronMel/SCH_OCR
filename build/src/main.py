from SolutionOCR import SolutionOCR, imageDebug

ImageFile = "./input/Seznam.jpg"
output_path1 = './output/imageDebugv1.jpg'
output_path2 = './output/imageDebug2.jpg'

ocr_cz = SolutionOCR("ces", 5)
output = ocr_cz.OCR(ImageFile)
imageDebug(ImageFile, output, output_path1)

# imageDebug(ImageFile, output, output_path1)



outputTextFile_path = './output/imageLog.txt'
textFile = open(outputTextFile_path, 'w+')
for i in range(len(output["data"])):
    print(str(output["data"][i]))
    textFile.write(str(output["data"][i]) + '\n')
textFile.close()
