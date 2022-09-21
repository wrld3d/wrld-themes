<a href="http://www.wrld3d.com/">
    <img src="http://cdn2.eegeo.com/wp-content/uploads/2017/04/WRLD_Blue.png" align="right" height="80px" />
</a>

# WRLD Themes

![WRLD](http://cdn2.eegeo.com/wp-content/uploads/2017/04/screenselection01.png)

The [WRLD SDK](http://www.wrld3d.com/) can be used to render beautiful maps in a variety of themes. Using different themes, you can display the map with different seasons, times of day, weather effects, and more. A theme determines the style of the map by specifying the texture resources, lighting parameters, and overlay effects used for rendering.

Each WRLD SDK includes a default theme, specified by a theme manifest. You can change that default to an alternate theme manifest created by WRLD, or you can build your own themes.

* [Using Preset Themes](#using-preset-themes)
    * [Available WRLD Themes](#available-wrld-themes)
* [About Themes](#about-themes)
    * [Theme Manifests](#theme-manifests)
    * [Themes](#themes)
    * [States](#states)
* [Building Custom Themes](#building-custom-themes)
    * [Building Theme Manifests](#building-theme-manifests)
    * [Creating Embedded Manifests](#creating-embedded-manifests)
* [Support](#support)


## Using Preset Themes

At startup, every WRLD SDK downloads a [theme manifest](#theme-manifests), which is a file specifying the themes to be used.  The URL for the theme manifest can be set as a configuration option in each SDK:
* [Android](https://wrld3d.com/android/latest/docs/api/MapViewResources/)
* [iOS](https://wrld3d.com/ios/latest/docs/api/Classes/WRLDMapOptions.html)
* [JavaScript](https://docs.wrld3d.com/wrld.js/latest/docs/api/L.Wrld.map/)
* [Unity](https://wrld3d.com/unity/latest/docs/types/Wrld.ConfigParams/)

Although you can use a standard theme manifest in Unity, the Unity enviroment enables much more customization of the visual effects which can be applied to the basic map.  See [here](https://wrld3d.com/unity/latest/docs/examples/custom-materials/) for details.

In the [WRLD Example App](https://github.com/wrld3d/wrld-example-app), the theme manifest URL is set in the config files for [Android](https://github.com/wrld3d/wrld-example-app/blob/master/android/assets/ApplicationConfigs/standard_config.json#L15) and [iOS](https://github.com/wrld3d/wrld-example-app/blob/master/ios/Resources/ApplicationConfigs/standard_config.json#L15).

### Available WRLD Themes

The current set of theme manifests is available [here](https://cdn-resources.wrld3d.com/mobile-themes-new/latest/versions.json).
This is a JSON file which maps a manifest identifier to a partial URL containing a version number, for example:

```javascript
{
    "default": "mobile-themes-new/v1141/default/", 
    "legacy": "mobile-themes-new/v1141/legacy/", 
    "ambientwhite": "mobile-themes-new/v1141/ambientwhite/", 
    "ambientdark": "mobile-themes-new/v1141/ambientdark/", 
    "ambientcolor": "mobile-themes-new/v1141/ambientcolor/", 
    "scifi": "mobile-themes-new/v1141/scifi/", 
    "scifiv": "mobile-themes-new/v1141/scifiv/", 
    "cardboard": "mobile-themes-new/v1141/cardboard/"
}
```

To construct the full URL for the configuration option, use the appropriate URL components from the following table:

SDK | Protocol + host | filename | example 
----|-----------------|----------|----------
Android, iOS, Unity | http://cdn1.wrld3d.com/ | manifest.bin.gz | http://cdn-resources.wrld3d.com/mobile-themes-new/v1141/default/manifest.bin.gz
JavaScript (wrld.js) | https://webgl-cdn1.wrld3d.com/ | web.manifest.bin | https://webgl-cdn1.wrld3d.com/mobile-themes-new/v1141/default/web.manifest.bin

The current set of themes provide a variety of styles for the map.

Name | Sample 
-----|-------------
default | ![default](sample-images/default.png)
legacy  | ![legacy](sample-images/legacy.png)
ambientwhite | ![ambientwhite](sample-images/light.png)
ambientdark |![ambientdark](sample-images/dark.png)
ambientcolor |![ambientdark](sample-images/minimal.png)
scifi |![scifi](sample-images/scifi.png)
scifiv |![scifiv](sample-images/scifi2.png)
cardboard | ![cardboard](sample-images/cardboard.png)


## About Themes

This repository contains the resources and scripts required to generate your own custom theme manifests.  The current WRLD themes are build from the assets stored here, so if you want to understand them in more depth, or if you want to build your own themes, read on.

### Theme Manifests
A theme manifest is a JSON file describing all the themes available to an app running the WRLD SDK. It contains information about all the textures, lighting parameters, material parameters, and vehicle models used to style the map. Each theme in the theme manifest provides the receiving app with a different configuration of these parameters and thus a different visual style.

### Themes
A theme consists of a number of [states](#states), as well as a position on the globe. The [default WRLD theme manifest](https://github.com/wrld3d/wrld-themes/blob/master/manifest/manifest_roots/default.yaml) includes themes for San Francisco, London, New York, and several other locations. By default, the map will display the geographically nearest theme.

For each location, there is one theme per season. For example, the default theme defines `SummerLondon` (defined  [here](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/london.yaml#L293)), `WinterLondon`(defined [here](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/london.yaml#L578)), and so on. These variants can be selected by the app.

### States
A theme state contains a set of textures to use for terrain and buildings, lighting parameters, and optionally an overlay effect. The states used by the default eeGeo theme manifest are combinations of four times of day, and five types of weather.
```
Time                        Weather
------------------------------------
                            Default
Day                         Overcast
Night                       Snowy
Dawn                        Rainy
Dusk                        Foggy
```
For example, `DayDefault` (defined [here](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/sanfrancisco.yaml#L306)), `NightSnowy` (defined [here](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/sanfrancisco.yaml#L342)), and `DawnRainy`(defined [here](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/sanfrancisco.yaml#L378)) are examples of states.

![WRLD Environment Themes](http://cdn2.eegeo.com/wp-content/uploads/2016/03/eegeo-environment-themes.jpg)

## Building Custom Themes

You can build custom themes by defining your own textures, [lighting parameters](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/defaultlighting.yaml), [placename styles](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/defaultplacenames.yaml), and more.  The best way to get started is to explore and modify the existing theme definitions in this repository.

One special case to note is the [water reflection cube map](https://github.com/wrld3d/wrld-themes/blob/master/manifest/themes/defaultwater.yaml).  To override this, specify the base filename in the YAML and then define six cube map PNGs using the naming convention `ThemeName/water_reflection_posX.png`, `ThemeName/water_reflection_negX.png`, etc. See [here](https://github.com/wrld3d/wrld-themes/tree/master/themes/Default) for an example.

### Building Theme Manifests
If you wish to generate entirely new themes, you can do so by using `make` in the root of this repo. This will generate a theme manifest from the YAML files under [manifest](https://github.com/wrld3d/wrld-themes/tree/master/manifest) in the repo, as well as all the required models and textures in the correct format for each platform. Finally, these resources are uploaded to an Amazon S3 location where you can serve them to your app.

#### Requirements

* Windows*
* Bash (for Windows, Git for Windows' bundled version works fine)
* Python version 2.7 installed and in your path
* Clang/MinGW installed and in your path

\* (Some of the 3rd-party texture tools used have bugs on OS X. You can replace the Windows executables and run it anyway, but expect to see quality issues. Specifically poor quality mipmaps.)

#### Usage
1.  First, make the desired changes to the textures, or YAML files.
2.  Run the `setup.sh` script.
3.  Modify the `REMOTE_BASE_DIR` variable in the [makefile](https://github.com/wrld3d/wrld-themes/blob/master/makefile) to point to an S3 bucket you wish the resources to be uploaded to.
4.  Run the following command: `mingw32-make.exe VERSION=<version> AWS_ACCESS_KEY_ID=<aws_access_key> AWS_SECRET_ACCESS_KEY=<aws_secret> EEGEO_ASSETS_HOST_NAME=<asset_host_name> THEME_ASSETS_HOST_NAME=<asset_host_name>`
    * `VERSION` is a unique version string for the resulting theme.
    * `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` should be keys for an AWS user with permissions to write to the S3 bucket specified in step 3.
    * `EEGEO_ASSETS_HOST_NAME` is the host name that wrld provided assets will be served from. It will be included in the theme manifest to tell the app where to request resources from. You will need to request this from WRLD.
    * `THEME_ASSETS_HOST_NAME` is the host name you plan to serve the theme resources from. It will be included in the theme manifest to tell the app where to request resources from.

Note that this process can take a long time to complete if you include a large number of themes and textures.

### Creating Embedded Manifests

In order to display the map before these themes have been fully downloaded, apps **must** contain an embedded theme manifest. The [Creating Embedded Manifests](#creating-embedded-manifests) section explains how to generate and embed this manifest.

The [create_embedded_manifest](https://github.com/wrld3d/wrld-themes/blob/master/create_embedded_manifest.py) script can be used to generate an embedded theme manifest and its textures from a regular theme manifest. These resources are required by the WRLD SDK at startup. All this script requires to run is Python version 2.7.

If you are using the [WRLD Example App](https://github.com/wrld3d/wrld-example-app) as a basis for your own project, you can skip this step entirely, as it already contains an embedded theme manifest. If not, then it provides an example of [where to place](#adding-to-a-project) the embedded resources.

#### Generating the manifest

The following example will generate an embedded manifest with one theme (`SummerSanFrancisco`) and one state (`DayDefault`), and output the result to `./some_folder/temp/embedded_theme`:
```sh
python create_embedded_manifest.py -i https://cdn-resources.wrld3d.com/mobile-themes-new/v540/manifest.txt.gz -o ./some_folder/temp/embedded_theme -t SummerSanFrancisco -s DayDefault
```

It is possible to include multiple themes and states if you want your app to be able to display more than one possible theme at startup, before streaming any additional resources:
```sh
python create_embedded_manifest.py -i https://cdn-resources.wrld3d.com/mobile-themes-new/v540/manifest.txt.gz -o ./some_folder/temp/embedded_theme -t SummerSanFrancisco WinterSanFrancisco -s DayDefault NightDefault
```

This could be useful, for example, if you want your app to open with the season or time of day dependent on the real life date and time. For most applications however, it is best to include as few themes and states as possible to minimize app size and startup time.

#### Adding to a project
After running the above script, the output folder should contain a file called `embedded_manifest.txt`, and also a folder full of textures for each platform. Note that although textures are generated for Android, iOS, OSX, and Windows, you can ignore any platforms that you are not using.

You should now do the following:

1.  The `embedded_manifest.txt` file must be copied into your app's resources. You can see an example of this in the [WRLD Example App](https://github.com/wrld3d/wrld-example-app) for [Android](https://github.com/wrld3d/wrld-example-app/blob/master/android/assets/embedded_manifest.bin), [iOS](https://github.com/wrld3d/wrld-example-app/blob/master/ios/Resources/embedded_manifest.bin), and [Windows](https://github.com/wrld3d/wrld-example-app/blob/master/windows/Resources/embedded_manifest.bin) applications.  These examples consume an optimized binary version of the theme produced by our internal build process, but text manifests are also supported.

2.  As in the [WRLD Example App](https://github.com/wrld3d/wrld-example-app), the contents of the iOS folder should then be placed under the [Resources/Textures/EmbeddedTheme](https://github.com/wrld3d/wrld-example-app/tree/master/ios/Resources/Textures/EmbeddedTheme) folder in your iOS project.

    The contents of the Android folder should be placed under [assets/Textures/EmbeddedTheme](https://github.com/wrld3d/wrld-example-app/tree/master/android/assets/Textures).
    
    The contents of the Windows folder should be placed under [Resources/Textures/EmbeddedTheme](https://github.com/wrld3d/wrld-example-app/tree/master/windows/Resources/Textures/EmbeddedTheme).

    (You can place these resources under a different path, but you will have to ensure you specify that path in your app's configuration.)
    
3.  Finally, edit the config of your app to use the correct paths for the new resources, and select an appropriate starting theme and state. Here are examples for [Android](https://github.com/wrld3d/wrld-example-app/blob/master/android/assets/ApplicationConfigs/standard_config.json#L15) and [iOS](https://github.com/wrld3d/wrld-example-app/blob/master/ios/Resources/ApplicationConfigs/standard_config.json#L15).  The starting theme and state are set [here](https://github.com/wrld3d/wrld-example-app/blob/master/src/VisualMap/SdkModel/VisualMapModule.cpp#L24).

After completing these steps, you should see your app open and display the embedded theme that you generated.



## Support

If you have any questions, bug reports, or feature requests, feel free to submit to the [issue tracker](https://github.com/wrld3d/wrld-themes/issues) for this repository.

## License

All textures and assets are released under the Creative Commons Attribution 4.0 International license. See the [LICENSE.md](https://github.com/wrld3d/wrld-themes/blob/master/LICENSE.md) file for details.
