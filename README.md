# Simple Cookie

A script to automate the modeling of a cookie cutter. 

## Introduction

The script is designed to take high contrast outline of an image and output a STL file suitable for 3D printing. Transparency files are supported.

## Parameters

| Short | Full      |  Description |
|---    |---        |---           |
| -i    | --input   | Input file or folder (**required**) |
| -o    | --output  | Output folder path (Default is same as input) |
| -h    | --height  | Scale to specified height (in inches) |
| -w    | --widht   | Scale to specified width (in inches) |   

For scaling only height or width is needed. Which ever one is provided the other will be scaled proportionately. 

## Examples

`python simplecookie.py -i Samples/Hammer.png -h 4`

This use the Hammer.png as the source file and scale it to 4 inches tall before generating the STL

`python simplecookie.py -i Samples/Hammer.png`

This works much the same as above, but will pass the scaling through as is. 

*Note: All files are processed at 96 dpi. If no scaling parameter is passed using other dpi may result in unsatisfactory results.*

## External Dependencies

- ImageMagick
- Potrace
- Inkscape >= 0.92

## Roadmap

- Non-proportional scaling
- Inner cutout support
- Selectable Output
- Docker build