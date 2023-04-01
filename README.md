# Stable diffusion webui video

This script is created for use in the project https://github.com/AUTOMATIC1111/stable-diffusion-webui

using img2img generates pictures one after another 

# Example



https://user-images.githubusercontent.com/107195976/191963848-6eb8e169-dee3-46d7-8310-db45046353fd.mp4


https://user-images.githubusercontent.com/107195976/191579132-f6f1c2e8-ba3d-4caf-aac4-f48ff4928516.mp4


https://user-images.githubusercontent.com/107195976/191961159-c878aca6-267d-4f35-afb9-2b1908a620c8.mp4



# Install
copy video.py in stable-diffusion-webui/scripts folder

# Using
1. create a picture or upload (it will be used as the first frame)
2. write a prompt
3. write end prompt
4. select video settings
5. run

# Usage

![image](https://user-images.githubusercontent.com/107195976/191533315-b09e0e08-ec0c-4a86-a1fc-c451438a4e98.png)

Extended Version:
![image](https://user-images.githubusercontent.com/12010863/195175113-12df7e14-4f96-4737-99c5-873b2278c796.png)

1.) End Prompt Trigger
Lets you define at how much Percent 0-100 the End Prompt will added to the original prompt

2.) Zoom Rotate
When zoom is activated you can select to rotate the image per rendered frame. Values from - to + 3.6° are accepted. (sanity limit else you get dark corners)

3.) TranslateXY
Shifts the image in X and Y directions. check boxes if you want to go the opposite direction.
If its tiled it takes the opposite end and copies it at the end of the scrolling direction.
If not it does some color palette maintaining noise stretchy stuff at the end which works but is kind of hacky. 
Numpy Expert anyone? (would be good to keep the color palette intact)   

# Multiprompt

This script contains all functionality of the original one, but also adds multiprompt. To use it just check the box with "Use Multipromt?" caption and give the ABSOLUTE path of the file into the text box below. This file needs to be a properly formated .yaml file. Here is a simple example of such a file:

~~~
# Starts with a cat and makes it a dog after half of the time and start to slowly zoom in.
- - 10
  - cat
  - global_prompt: poster art
- - 10
  - dog
  - negative_prompt: human
    zoom: true
    zoom_level: 1.02
~~~

This example begins with a comment. Comments are allowed in the files look up YAML comments for more information. It's recommended to use global prompts for the style of the video, so that style and content are separated. Each scene has to begin with an integer number that represents the duration of the scene. This number is an arbitrary time unit which will automatically be scaled to fit the selected length of your video. In the next line comes the prompt for that scene. These first two arguments are required for any scene. After that come keyword arguments.

WARNING: Note that in the last line of the example there is no "-" symbol before the part with "zoom_level: 1.02"  and the same is true for the line above. That is correct, only the first keyword argument must have a "-", every following keyword argument must not have a "-" in the beginning. This is because of the way YAML understands the minus (it represents a list element) and the keyword dictionary is the optional third list element in each scene data list. But the keyword arguments are not different list elements, they are all elements of the same dictionary.

"global_prompt" is a prompt that will be added to the prompt of all scenes. If you want to set it for all scenes put it in the first scene. Using this keyword argument later will overwrite the global prompt defined earlier, if any, like it's the case with all keyword arguments. "zoom" is a boolean for enabling zoom, but for anything to actually happen we also have to set "zoom_level" to a value different than 1.


## Use Prompt Mixing?

This options allows the prompts to be mixed when changing the "scene". This means that when a new prompt is used for n images (selected amount on the slider) both prompts will be combined, that of the new scene and the old one. If you for example have 30 FPS and select Prompt Mixing Loops = 15 this would result in 0,5 seconds of mixed prompts in between scenes. In the example above this would mean it does not directly go from "cat" to "dog", but uses "cat, dog" for 15 images. The results of this method do heavily vary depending on the concrete prompts and the model you are using, but sometimes it produces some really neat transformations that look much more fluid than without prompt mixing.

If you use prompt mixing you can also choose if the prompts are just concatenated or if they should be weighted so that the prompt slowly shifts from one to another. By default "Gradual Prompt Mixing?" is true, meaning if you enable prompt mixing it will be gradual prompt mixing, if you prefer concatenation just uncheck the "Gradual Prompt Mixing?" checkbox.


## Tipps on using this script

- I tested this script with different models and it works, but the results do vary a lot. If a multiprompt does not give good results on one model it might on a different model.
- Test your prompts separately but using txt2img if you're not sure if they will work as expected.
- Generate short versions with low FPS first to see how you can improve the multiprompt txt before you start making longer versions.
- Separate content and style by using the global prompt feature, you can have several global prompts in one file, they just get concatenated.
- Generate an appropriate starting image with txt2img.
- You can make the video more fluid by reducing the denoising strength while increasing the sampling steps and FPS. The last example on YouTube "Evolution 4 (Stable Diffusion Video)" for example has 30 FPS and I used 60 sampling steps with a denoising strength of 0.5 and it looks almost fluid.
- If you only have 6GB VRAM like me you can make 1:1 with 512x512 (Standard) or 16:9 with 640x360. I tested this resolutions a lot and never had any problems. Anythings bigger did cause problems, although not always.
- Zoom and rotate do still work, so feel free to also use them.
- I find that a prompt mixing of 20 with 30 FPS, so 2/3 of a second, seems to be good for longer videos with higher quality, but for better results it might be preferable to reduce prompt mixing to 10 or even 5 and add a short additional transion "scene" to the multiprompt.
- A higher CFG Scale should give results closer to the prompt but with worse image quality. I guess around 20 should be reasonable, but it might be worth to test different values.
- Try different sampling methods, that might also help to improve results.
- Prompt end still works, with an End Prompt Blend Trigger Percent of 0 it can be used to add more global prompts without having to edit the multiprompt txt.
- For abrupt scene transitions you can use the "Use strong denoising for scene transition?" option. Select the denoising strength you wish to use and for how many frames it should be used when a new scene starts. This is the opposite of what prompt mixing does and using it together will give wierd results. But you can use keywords to disable one and enable the other so that some scene transitions use prompt mixing and some use strong denoising.
- It works with ControlNet if you have enough VRAM. But there is an issue with "Interrupt", only restarting the UI will acutally interrupt it, otherwise only image generation gets interrupted, but not ControlNet. 

## Examples for multiprompt

These are three different examples of the multiprompt example from above.


https://user-images.githubusercontent.com/58605249/212650165-2fda65a0-e86a-4996-be1c-07b51b6feb9c.mp4


https://user-images.githubusercontent.com/58605249/212650239-f1aff68d-1044-4ff7-a53e-e411b1d0c8b9.mp4


Here is an example of a more complex multiprompt and it's results.

~~~
# Multiprompt for a video about evolution.
- - 10
  - molecules, atoms, quantum physics, mysterious, electromagnetic interaction
  - global_prompt: centered:1.5, highly detailed, poster art:0.2, 2d game concept art:0.2, realistic:0.5, octane render:0.5
    global_negative_prompt: comic, writing, watermark, figurine, table, caption
- - 10
  - protein, biochemistry, nucleus, DNA replication
- - 10
  - bacteria, unicellular organism, cell
- - 10
  - multicellular organism, tardigrade:0.5, underwater
- - 10
  - sea worm in the ocean
- - 10
  - prehistoric fish in the ocean
- - 10
  - coelacanth in the ocean, prehistoric fish
- - 10
  - prehistoric reptilian, on the beach
- - 10
  - amphibian, prehistoric frog, in the grass
- - 10
  - rodent, prehistoric rat, in the grass
- - 10
  - prehistoric squirrel
- - 10
  - monkey in the jungle
- - 10
  - human monkey in the jungle
- - 10
  - neanderthal
- - 10
  - Stone Age man
- - 10
  - viking, pagan warrior
- - 10
  - knight of teutonic order, medieval combat, castle
- - 10
  - man in suit, 19th century suit, woman in 19th century cloth, industrial revolution
- - 10
  - man with phone, modern building, modern clothing
- - 10
  - man in the future, futuristic building, VR
- - 10
  - cyborg, in spaceship, futuristic
- - 10
  - alien cyborg, in alien spaceship, cybernetic, alien technology
- - 10
  - singularity, cyber technology, psychedelic, lovecraftian creature
  - zoom: true
    zoom_level: 1.04
    rotate: true
    rotate_degree: 1
- - 20
  - creation of universe, psychedelic, holy
  - negative_prompt: comic, writing, watermark, figurine, table
~~~

Short version:

https://www.youtube.com/watch?v=7WQ2rpi-7Us


Long version, better quality, 16:9, 30 FPS, added music

https://www.youtube.com/watch?v=bb5TzMyQZuA&t=1s


Example of another multiprompt using strong denoising for more abrupt scene transitions:

https://www.youtube.com/watch?v=BYsFdL0RJGk


## Keyword arguments

Here is a list of all arguments including all available keyword arguments and their expected data type:

~~~
## List of all properties

Required arguments (positional):
- [0] = duration: int
- [1] = prompt: str
- [2] = keyword_dict (optional)

Optional arguments (keywords):
- prompt_global: str
- negative_prompt_global: str
- negative_prompt: str

- seed: int
- subseed: int
- subseed_strength: float
- seed_resize_from_h: int
- seed_resize_from_w: int

- steps: int
- cfg_scale: float
- restore_faces: bool
- tiling: bool
- denoising_strength: float

- zoom: bool
- zoom_level: float
- direction_x: float        # For zooming on x-axis
- direction_y: float        # For zooming on y-axis

- rotate: bool
- rotate_degree: float

- is_tiled: bool

- trnx: bool                 # Translate on x-axis?
- trnx_left: bool            # Translate on x-axis to the left?
- trnx_percent: float        # Translate on x-axis how much percent?
- trny: bool                 # Translate on y-axis?
- trny_up: bool              # Translate on y-axis up?
- trny_percent: float        # Translate on y-axis how much percent?

- use_prompt_mixing: bool
- prompt_mixing_loops: int   # Mix prompt for how many frames?
- gradual_mixing: bool

- strong_denoising_transition: bool   # Enables or disables strong denoising at scene transition
- strong_denoising: float             # Denoising strength at scene transition
- strong_denoising_steps: int         # How many frames to use the strong denoising?
~~~

## Model ignoring beginning of prompt bug

When testing the new version of this script I realized that there is a problem with some models like protogenX58 giving really bad results and I finally found out that the problem is that in some models the first part of the prompt is ignored. If only the character or the whole first word is ignored is word-dependend so for some word is this, for some that. But all tests consistently showed that for every word when putting a comma in front of it the comma gets ignored instead of the word or parts of it, so just putting a comma in front of all prompts does fix this behaviour. This script has the option to automatically add a comma in front of every prompt before processing which is controlled by the "Add comma before prompt to hotfix issue with ignored prompts in some models?" checkbox.


## FFMPEG bug

This is fixed now. I leave this explantion here anyways, for the case anybody need to manually use FFMPEG for another reason.

Sometimes, especially when making longer videos with higher framerates I get the error message that width or height can't be zero and it does not create a video. But the images have been created. To still get the video you can just run FFMPEG manually. To do this you have to create a txt file containing all absolute paths of the images in a certain format in the right order. To do this efficiently I use the following code and run it on a Python interpreter.

~~~
import os

files = []
for name in os.listdir("C:\\Users\\{YourUserName}\\stable-diffusion-webui\\outputs\\img2img-images\\"):
    if os.path.isfile("C:\\Users\\{YourUserName}\\stable-diffusion-webui\\outputs\\img2img-images\\" + name):
        if int(name[:5]) >= 2098:    # <--- The number of the first image to use
            files.append(name)
files.sort()
with open("C:\\Users\\{YourUserName}\\stable-diffusion-webui\\outputs\\img2img-videos\\{YourFileName}.txt", "a") as myfile:
    for elem in files:
        myfile.write("file 'C:\\Users\\{YourUserName}\\stable-diffusion-webui\\outputs\\img2img-images\\" + elem + "'\n")
    myfile.close()
~~~

This is just an example of how I do it, you of course have to put in the correct paths of your system and replace the number where the arrow points and the file name of the txt. All images generated by img2img have a number that is just counting up, put the number of the first image of the video that failed to finish. This should create a txt file listing all images in the right format and order in the img2img-videos directory.

Now you can manually run FFMPEG. Open a console an navigate to your FFMPEG folder (or add it to the PATH). Then run the following (also put in the correct paths here): 

~~~
ffmpeg.exe -y -r 30 -f concat -safe 0 -i "C:\Users\{YourUserName}\stable-diffusion-webui\outputs\img2img-videos\{YourFileName}.txt" -vcodec libx264 -filter:v minterpolate -crf 10 -pix_fmt yuv420p "C:\Users\{YourUserName}\stable-diffusion-webui\outputs\img2img-videos\{YourFileName}.mp4"
~~~

This should give you the video that has failed from the raw images.
