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

This script contains all functionality of the original one, but also adds multiprompt. To use them just check the box with "Use Multipromt?" caption and give the ABSOLUTE path of the file into the text box below. This file needs to be a properly formatted txt file. Here is an simple example of such a file:

~~~
# Starts with a cat and makes it a dog after half of the time.
$psychedelic, realistic, high quality
1::cat::person, human
200::dog::person, human
300::dog::person, human
~~~

This example begins with a comment. Comments are allowed in the files, but only full lines, comments on the line as prompts will be considered prompt and used as such. So make sure to always use '#' as first character of a line containing a comment (whitespace is no problem). After that there is a line beginning with the '$' symbol. Everything behind this symbol is considered to be a global prompt, so it will be added to every single prompt. Use this if you want to add the same word to all prompts. It's recommended to use these global prompts for the style of the video, so that style and content are separated logically. After that comes the actual multipromt. Each line has to begin with a number. This number is an arbitrary time unit which will automatically be scaled to fit the selected length of your video. Only the relative size matters. In the given example from 1 to 199 the prompt will be "cat, psychedelic, realistic, high quality" and from 200 to 450 it will be "dog, psychedelic, realistic, high quality". Why 450, not 300? Because the number marks the beginning, the actual length will be calculated, the last scene has a length that is the average of all other scenes. To make the last scene longer you can just add it twice, then the length of the last scene will be added to that of the scond to last one, like in this example.

## Use seed for n images

This option is experimental and I strongly recommend not to use it, as it seems to mess up the results. What it does is reusing the same seed for the selected number of images. I don't know why it gives the results that it does, probably has to do with subseeds and the separate Pytorch seed, so it should only be used for experimentation.

## Use Prompt Mixing?

This options allows the prompts to be mixed when changing the "scene". This means that when a new prompt is used for n images (selected amount on the slider) both prompt will be combined, that of the new scene and the old one. If you for example have 30 FPS and select Prompt Mixing Loop = 15 this would result in 0,5 seconds of mixed prompt in between scenes. In the example above this would mean it does not directly go from "cat" to "dog", but uses "cat, dog" for 15 images. The results on this method do heavily vary depending on the concrete prompts and the model you are using, but sometimes it produces some really neat transformations that look much more fluid than without prompt mixing.

