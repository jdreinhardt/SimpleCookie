import os
import sys
import getopt
from lxml import etree, objectify
from subprocess import Popen, PIPE, check_call

def generateCookieCutter(inputs, output, dimensions):
    svgFiles = imageToSvg(inputs, output, dimensions)
    svgToStl(svgFiles)


def imageToSvg(inputs, outputPath, dimensions):
    '''
    Takes an array of image files to process and returns an array of SVG files
    '''
    outputs = []
    scaleWidth = dimensions[0]
    scaleHeight = dimensions[1]
    if (scaleWidth == 'x'):
        scaleWidth = -1
    if (scaleHeight == 'y'):
        scaleHeight = -1

    for f in inputs:
        filename, ext = os.path.splitext(f)
        ext = ext[1:].strip().lower()
        tempName = f
        if (ext not in ("bmp","pnm")):
            tempName =  filename + ".bmp"
            os.system("convert -flatten '%s' '%s'" % (f, tempName))
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)
        svgFile = os.path.join(outputPath, (filename + ".svg"))
        os.system("potrace -s -r 96 -o '%s' '%s'" % (svgFile, tempName))
        os.remove(tempName)
        outputFileName = svgFile

        # Uses the Inkscape Command line to Scale viewBox to path and mirror image. 
        # Tested using Inkscape 1.0 in Arch Linux Kernel 5.7. Should work using Inkscape 0.92
        # or newer. Verbs currently require access to an X server to run.
        os.system("inkscape -g --actions=\"verb:FitCanvasToSelectionOrDrawing;verb:EditSelectAll;verb:ObjectFlipHorizontally;verb:FileSave;verb:FileClose;verb:FileQuit\" '%s'" % (svgFile))

        tree = objectify.parse(svgFile)
        root = tree.getroot()
        svgHeight = root.attrib['height'][:-2]
        svgWidth = root.attrib['width'][:-2]
        updatedHeight = svgHeight
        updatedWidth = svgWidth

        if (scaleHeight != -1 or scaleWidth != -1):
            scaleFactor = 0
            dpi = 96 # Default DPI used by Autodesk Fusion 360 for SVG import

            if (scaleHeight != -1):
                updatedHeight = scaleHeight
                root.attrib['height'] = updatedHeight + "in"
            else:
                scaleFactor = float(scaleWidth) / float(svgWidth)
                updatedHeight = float(svgHeight) * scaleFactor
                root.attrib['height'] = str(updatedHeight) + "in"

            if (scaleWidth != -1):
                updatedWidth = scaleWidth
                root.attrib['width'] = updatedWidth + "in"
            else:
                scaleFactor = float(scaleHeight) / float(svgHeight)
                updatedWidth = float(svgWidth) * scaleFactor
                root.attrib['width'] = str(updatedWidth) + "in"

            root.attrib['viewBox'] = "0 0 " + str(float(updatedWidth) * dpi) + " " + str(float(updatedHeight) * dpi)

            matrix = (root.g.attrib['transform'][7:-1]).split(",")
            for i in range(len(matrix)):
                matrix[i] = float(matrix[i]) * dpi * scaleFactor

            updatedTransform = "matrix(" + ",".join(map(str, matrix)) + ")"
            root.g.attrib['transform'] = updatedTransform

            outputFileName = filename + " [" + str(round(float(updatedWidth), 1)).rstrip('0').rstrip('.') + "x" + str(round(float(updatedHeight), 1)).rstrip('0').rstrip('.') + "in].svg"

        root.g.attrib['fill'] = 'none'
        root.g.attrib['stroke'] = 'black'
        root.g.attrib['stroke-width'] = '5'
        with open(svgFile, "wb") as file:
            file.write(etree.tostring(tree))
            file.close

        os.rename(svgFile, outputFileName)
        outputs.append(outputFileName)
    
    return outputs

def svgToStl(filesArray):
    bladeHeight = 20
    bladeWidth = 0.88
    baseHeight = 2
    baseWidth = 7.5
    importDpi = 96

    for file in filesArray:
        filePath = os.path.abspath(file)
        stlPath = os.path.splitext(filePath)[0] + ".stl"

        scadTemplate = 'filePath = "%s";\nbladeHeight = %s;\nbladeWidth = %s;\nbaseHeight = %s;\nbaseWidth = %s;\nimportDpi = %s;\n\nmodule svgPath(filePath) {\n  import(file = filePath, center = false, dpi = importDpi);\n}\n\nmodule cutterBody(extrudeHeight, extrudeWidth) {\n  linear_extrude(height = extrudeHeight) {\n    difference() {\n      offset(r=extrudeWidth){\n        svgPath(filePath);\n      }\n      offset(r=0){\n        svgPath(filePath);\n      }\n    }\n  };\n}\n\nunion() {\n  cutterBody(bladeHeight, bladeWidth);\n  cutterBody(baseHeight, baseWidth);\n}' % (filePath, bladeHeight, bladeWidth, baseHeight, baseWidth, importDpi)

        #print("Generating STL file. This may take some time. Please be patient.")
        
        os.system("echo '%s' | openscad -o '%s' /dev/stdin" % (scadTemplate, stlPath))

def main(argv):
    inputs = []
    output = "./"
    dimensions = ['x', 'y']

    try:
        opts, args = getopt.getopt(argv,"i:o:h:w:", ["help","input","output","height","width"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == "--help":
            usage()
            sys.exit()
        elif o in ("-i", "--input"):
            if (os.path.isfile(a)):
                inputs.append(a)
            else:
                for root, dirs, files in os.walk(a):
                    for filename in files:
                        inputs.append(os.path.join(root, filename))
        elif o in ("-o", "--output"):
            if (os.path.isdir(a)):
                output = a
            else:
                print("Output is not a directory")
                sys.exit(2)
        elif o in ("-h", "--height"):
            dimensions[1] = a
        elif o in ("-w", "--width"):
            dimensions[0] = a
        else:
            assert False, "unhandled option"

    if not inputs:
        print("ERROR: no input file found. Specify using -i")
        sys.exit(10)
    if (dimensions[0] != 'x' and dimensions[1] != 'y'):
        print("ERROR: scaling both height and width is not currently supported")
        sys.exit(11)

    generateCookieCutter(inputs, output, dimensions)

def usage():
    '''
    Help parameters.
    '''
    usage = """
    Convert Images to SVG outlines

    --help          What you're reading

    -i, --input     Input file or folder (required)
    -o, --output    Output folder path ( Default is ./ )
    -h, --height    Scale to specified height (in inches)
    -w, --width     Scale to specified width (in inches)

    For scaling only height or width is needed. Which ever one is provided the 
    other will be scaled proportionately. 
    """
    print(usage)

if __name__ == '__main__':
    main(sys.argv[1:])