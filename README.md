# Chromatic Aberration Plugin - Krita 4

Plugin to apply adjustable chromatic aberration effect to a layer

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

* Shape and Direction:
  * Radial - Effect starts at the center and becomes more powerful at the edges
  * Linear - Effect is applied consistently over the whole image
    * The dial can be used to tune the direction of the effect if Linear is selected
* Max Displacement and Falloff:
  * The slider adjusts how powerful the effect is at it's strongest point if using Radial, or throughout if using Linear shape
  * Exponential Falloff - (Radial shape only) The effect is strong at the edges, but quickly loses strength towards the center
  * Linear Falloff - (Radial shape only) The effect gradually gets less powerful towards the center
* Deadzone - (Radial shape only) Percentage of the screen that will not be affected by the filter, staring at the center. Adjust this if the center of the image needs to stay in focus.

Once the effect is applied it will be placed on a new layer as a modified clone of the previously selected layer, the original layer is preserved.

### Extra Notes

Since this is a plugin, it runs single-threaded inside a python interpreter, therefore it is **much** slower than regular filters. To give a sense of how slow, it takes between 5 - 15 seconds to apply the filter to a 540x540 image depending on the settings (larger deadzone helps it run faster). It's expected to run at O(n) complexity, where n is the number of pixels in an image. This slowness is why I decided against adding a preview, just remember your settings, delete the new layer, and try again.

This is my first plugin for Krita, and I know the user interface could use more polish, but it's good enough for me to use, and I'm not sure how many other people will even use this, so it may not be worth the effort to improve. This plugin would be better suited as a filter, both in terms of organization and performance, but for now, this is good enough. Again, effort put in vs how useful the result is, if it's worth making this as a filter I'll look into it.