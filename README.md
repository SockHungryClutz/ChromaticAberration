# Chromatic Aberration Plugin - Krita 4

Plugin to apply adjustable chromatic aberration effect to a layer

![Example Image of Effects](https://i.imgur.com/AYb7ViR.png)

## How to Install

 1. Open Krita, go to Settings->Manage Resources...->Open Resource Folder
 2. Open the pykrita folder inside the folder that pops up
 3. Download this repository and save the files and folders exactly as they are to the pykrita folder
 4. Close and reopen Krita
 5. Go to Settings->Configure Krita->Python Plugin Manager
 6. Scroll down and enable Chromatic Aberration, click OK to save
 7. Close and reopen Krita again

## How to Use

With an open document active, select a layer you want to apply the effect to, then click Tools->Scripts->Chromatic Aberration  
This will pop open a window with options to control the effect before applying:

![Default Look of the User Interface](https://i.imgur.com/iyW9Lt2.png)

* Shape and Direction:
  * Radial - Effect starts at the center and becomes more powerful at the edges
  * Linear - Effect is applied consistently over the whole image
    * The dial can be used to tune the direction of the effect if Linear is selected
* Max Displacement and Falloff:
  * The slider adjusts how powerful the effect is at it's strongest point if using Radial, or throughout if using Linear shape
  * Exponential Falloff - (Radial shape only) The effect is strong at the edges, but quickly loses strength towards the center
  * Linear Falloff - (Radial shape only) The effect gradually gets less powerful towards the center
* Deadzone - (Radial shape only) Percentage of the screen that will not be affected by the filter, staring at the center. Adjust this if the center of the image needs to stay in focus.
* Bilinear Interpolation - Checking this option will make the plugin run slightly slower, but will make edges created by the effect smoother and less aliased.
* Number of Worker Threads (FOR ADVANCED USERS) - As the warning says, this option is for users who know what their CPU is capable of. Larger values will apply the effect faster on very large images, but if the value exceeds the number of threads your CPU can reasonably handle the process will take longer. The default value of 4 will work well on the vast majority of CPUs that can handle Krita.

Once the effect is applied it will be placed on a new layer as a modified clone of the previously selected layer, the original layer is preserved.

### Extra Notes

This plugin relies on a shared C library for speeding up the computationally expensive parts. The source code for the C libraries is included in the `src` folder and has been precompiled for 32 and 64 bit versions of Windows, Mac OS, and Linux installations of Python. The source code can be compiled using gcc and the below commands:

```
gcc -shared -m32 -o ChromaticAberration_32.so -fPIC ChromaticAberration.c Utils.c
gcc -shared -o ChromaticAberration_64.so -fPIC ChromaticAberration.c Utils.c
```

Work on this plugin is more or less complete, there are a few niceties that could be added, but I will be putting those as well as a lot more features into a new Krita plugin later. I plan on making this part of a bigger plugin with more visual effects as I get the time to work on it. Once that plugin is released, this repository will effectively be outdated.