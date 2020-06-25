filePath = "Samples\Hammer [2.8x4in].svg";
bladeHeight = 20;
bladeWidth = 0.88;
baseHeight = 2;
baseWidth = 7.5;
importDpi = 96;

module svgPath(filePath) {
    import(file = filePath, center = false, dpi = importDpi);
}

module cutterBody(extrudeHeight, extrudeWidth) {
    linear_extrude(height = extrudeHeight, convexity=4) {
        difference() {
            offset(r=extrudeWidth){
                svgPath(filePath);
            }
            offset(r=0){
                svgPath(filePath);
            }
        }
    };
}

union() {
    cutterBody(bladeHeight, bladeWidth);
    cutterBody(baseHeight, baseWidth);
}