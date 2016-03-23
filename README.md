<a href="http://www.eegeo.com/">
    <img src="http://cdn2.eegeo.com/wp-content/uploads/2016/03/eegeo_logo_quite_big.png" alt="eeGeo Logo" title="eegeo" align="right" height="80px" />
</a>

# eeGeo Themes

* [Support](#support)
* [Theme Manifests](#theme-manifests)
    * [Themes](#themes)
    * [States](#states)
* [Creating Embedded Manifests](#creating-embedded-manifests)
    * [Generating the manifest](#generating-the-manifest)
    * [Adding to a project](#adding-to-a-project)
* [Building Theme Manifests](#building-theme-manifests)
    * [Requirements](#requirements)
    * [Usage](#usage)

The [eeGeo SDK](http://www.eegeo.com/) can be used to render beautiful maps in a variety of themes. Using different themes, you can display the map with different seasons, times of day, weather effects, and more. A theme determines the style of the map by specifying the texture resources, lighting parameters, and overlay effects used for rendering.

At startup, the eeGeo SDK downloads a [theme manifest](#theme-manifests), which is a JSON file containing the themes that the app requires. In order to display the map before these themes have been fully downloaded, apps **must** contain an embedded theme manifest. The [Creating Embedded Manifests](#creating-embedded-manifests) section explains how to generate and embed this manifest.

This repository also contains the resources and scripts required to generate custom theme manifests for use with the [eeGeo 3D mapping platform](http://www.eegeo.com/). Generating custom themes is entirely optional however, as the eeGeo SDK comes with a collection of preset themes.

## Support

If you have any questions, bug reports, or feature requests, feel free to submit to the [issue tracker](https://github.com/eegeo/eegeo-themes/issues) for this repository.

## Theme Manifests
A theme manifest is a JSON file describing all the themes available to an app running the eeGeo SDK. It contains information about all the textures, lighting parameters, material parameters, and vehicle models used to style the map. Each theme in the theme manifest provides the receiving app with a different configuration of these parameters and thus a different visual style.

### Themes
A theme consists of a number of [states](#states), as well as a position on the globe. The default eeGeo theme manifest includes themes for San Francisco, London, New York, and several other locations. By default, the map will display the geographically nearest theme.

For each location, there is one theme per season. For example: `SummerLondon`, `WinterLondon`, and so on. These variants can be selected by the app.

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
For example, `DayDefault`, `NightSnowy`, and `DawnRainy` are examples of states.

![eeGeo Environment Themes](http://cdn2.eegeo.com/wp-content/uploads/2016/03/eegeo-environment-themes.jpg)

## Creating Embedded Manifests

The [create_embedded_manifest](https://github.com/eegeo/eegeo-themes/blob/master/create_embedded_manifest.py) script can be used to generate an embedded theme manifest and its textures from a regular theme manifest. These resources are required by the eeGeo SDK at startup. All this script requires to run is Python version 2.7.

If you are using the [eeGeo Example App](https://github.com/eegeo/eegeo-example-app) as a basis for your own project, you can skip this step entirely, as it already contains an embedded theme manifest. If not, then it provides an example of [where to place](#adding-to-a-project) the embedded resources.

### Generating the manifest

The following example will generate an embedded manifest with one theme (`SummerSanFrancisco`) and one state (`DayDefault`), and output the result to `./some_folder/temp/embedded_theme`:
```sh
python create_embedded_manifest.py -i http://d2xvsc8j92rfya.cloudfront.net/mobile-themes-new/v540/manifest.txt.gz -o ./some_folder/temp/embedded_theme -t SummerSanFrancisco -s DayDefault
```

It is possible to include multiple themes and states if you want your app to be able to display more than one possible theme at startup, before streaming any additional resources:
```sh
python create_embedded_manifest.py -i http://d2xvsc8j92rfya.cloudfront.net/mobile-themes-new/v540/manifest.txt.gz -o ./some_folder/temp/embedded_theme -t SummerSanFrancisco WinterSanFrancisco -s DayDefault NightDefault
```

This could be useful, for example, if you want your app to open with the season or time of day dependent on the real life date and time. For most applications however, it is best to include as few themes and states as possible to minimize app size and startup time.

### Adding to a project
After running the above script, the output folder should contain a file called `embedded_manifest.txt`, and also a folder full of textures for each platform. Note that although textures are generated for Android, iOS, OSX, and Windows, you can ignore any platforms that you are not using.

You should now do the following:

1.  The `embedded_manifest.txt` file must be copied into your app's resources. You can see an example of this in the [eeGeo Example App](https://github.com/eegeo/eegeo-example-app) for [Android](https://github.com/eegeo/eegeo-example-app/blob/master/android/assets/embedded_manifest.txt), [iOS](https://github.com/eegeo/eegeo-example-app/blob/master/ios/Resources/embedded_manifest.txt), and [Windows](https://github.com/eegeo/eegeo-example-app/blob/master/windows/Resources/embedded_manifest.txt) applications.

2.  As in the [eeGeo Example App](https://github.com/eegeo/eegeo-example-app), the contents of the iOS folder should then be placed under the [Resources/Textures/EmbeddedTheme](https://github.com/eegeo/eegeo-example-app/tree/master/ios/Resources/Textures/EmbeddedTheme) folder in your iOS project.

    The contents of the Android folder should be placed under [assets/Textures/EmbeddedTheme](https://github.com/eegeo/eegeo-example-app/tree/master/android/assets/Textures).
    
    The contents of the Windows folder should be placed under [Resources/Textures/EmbeddedTheme](https://github.com/eegeo/eegeo-example-app/tree/master/windows/Resources/Textures/EmbeddedTheme).

    (You can place these resources under a different path, but you will have to ensure you specify that path in your app's configuration.)
    
3.  Finally, edit the config of your app to use the correct paths for the new resources, and select an appropriate starting theme and state. Here are examples for [Android](https://github.com/eegeo/eegeo-example-app/blob/master/android/jni/AppHost.cpp#L188-L191) and [iOS](https://github.com/eegeo/eegeo-example-app/blob/master/ios/ios_src/AppHost.mm#L136-L139).

    Make sure that if you set `EmbeddedThemeNameContains = "Summer"` that your embedded manifest contains a theme with "Summer" in its name. Similarly, make sure that if you set `EmbeddedThemeStateName = "DayDefault"` that the `DayDefault` state is present in your embedded manifest.

After completing these steps, you should see your app open and display the embedded theme that you generated.

## Building Theme Manifests
If you wish to generate entirely new themes, you can do so by using `make` in the root of this repo. This will generate a theme manifest from the YAML files under [manifest](https://github.com/eegeo/eegeo-themes/tree/master/manifest) in the repo, as well as all the required models and textures in the correct format for each platform. Finally, these resources are uploaded to an Amazon S3 location where you can serve them to your app.

### Requirements

* Windows*
* Bash / MinGW (for Windows, git's bundled version works fine)
* Python version 2.7 installed and in your path
* Clang installed and in your path

\* (Some of the 3rd-party texture tools used have bugs on OS X. You can replace the Windows executables and run it anyway, but expect to see quality issues. Specifically poor quality mipmaps.)

### Usage
1.  First, make the desired changes to the textures, or YAML files.
2.  Run the `setup.sh` script.
3.  Modify the `REMOTE_BASE_DIR` variable in the [makefile](https://github.com/eegeo/eegeo-themes/blob/master/makefile) to point to an S3 bucket you wish the resources to be uploaded to.
4.  Run the following command: `mingw32-make.exe VERSION=<version> AWS_ACCESS_KEY_ID=<aws_access_key> AWS_SECRET_ACCESS_KEY=<aws_secret> ASSETS_HOST_NAME=<asset_host_name>`
    * `VERSION` is a unique version string for the resulting theme.
    * `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` should be keys for an AWS user with permissions to write to the S3 bucket specified in step 3.
    * `ASSETS_HOST_NAME` is the host name you plan to serve the theme resources from. It will be included in the theme manifest to tell the app where to request resources from.
    
Note that this process can take a long time to complete if you include a large number of themes and textures.

## License

The eeGeo 3D Maps SDK is released under the Eegeo Platform SDK Evaluation license. See the [LICENSE.md](https://github.com/eegeo/eegeo-themes/blob/master/LICENSE.md) file for details.