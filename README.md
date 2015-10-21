# Build Manifest
---
Themes allow developers to customise things like textures, models and some behaviours (e.g. traffic vehicles, speeds)

## Requirements:
* Windows only at the moment (some of the 3rd party texture tools we use have bugs on mac). You can replace the windows executables and make it run on mac OS X, but expect to see quality issues (poor quality mipmaps).
* Bash / MinGW (for Windows, git's bundled version works fine)
* Python version >= 2.7 installed and in your path
* Clang installed and in your path


# Create Embedded Manifest
---
This script will generate a cut-down theme manifest for embedding into an app, and download the textures that it needs.

## Example usage:

### One Theme, One State

`python create_embedded_manifest.py -i http://url.of.manifest.txt.gz -t SummerSanFrancisco -s DayDefault -o C:/temp/embedded_themes`

This will output a manifest with one theme (SummerSanFrancisco) and one state (DayDefault). It will also output a folder for each platform supported by the manifest (iOS, Android, etc.) containing the textures used by SanFrancisco/DayDefault.

The manifest, and these texture folders, will be saved to C:/temp/embedded_themes.

### One Theme, Two States

`python create_embedded_manifest.py -i http://url.of.manifest.txt.gz -t SummerSanFrancisco -s DayDefault DayRainy -o C:/temp/embedded_themes`

This will output one theme, but with two states: DayDefault and DayRainy. Using this embedded manifest would allow an app to start up with or without rain, before streaming any additional resources.

### Two Themes, Two States

`python create_embedded_manifest.py -i http://url.of.manifest.txt.gz -t SummerSanFrancisco WinterSanFrancisco -s DayDefault DayRainy -o C:/temp/embedded_themes`

This will output two themes. Both SummerSanFrancisco and WinterSanFrancisco will have both states, DayDefault and DayRainy. This embedded manifest would allow an app to start up with either the Summer or Winter theme, and also with or without rain, before streaming any additional resources.