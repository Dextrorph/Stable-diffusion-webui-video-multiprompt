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

This script contains all functionality of the original one, but also adds multiprompt. To use it just check the box with "Use Multipromt?" caption and give the ABSOLUTE path of the file into the text box below. This file needs to be a properly formated txt file. Here is a simple example of such a file:

~~~
# Starts with a cat and makes it a dog after half of the time.
$psychedelic, realistic, high quality
1::cat::person, human
200::dog::person, human
300::dog::person, human
~~~

This example begins with a comment. Comments are allowed in the files, but only full lines, comments on the same line as prompts will be considered prompt and used as such. So make sure to always use '#' as first character of a line containing a comment (whitespace is no problem). After that there is a line beginning with the '$' symbol. Everything behind this symbol is considered to be a global prompt, so it will be added to every single prompt. Use this if you want to add the same word to all prompts. It's recommended to use these global prompts for the style of the video, so that style and content are separated. After that comes the actual multiprompt. Each line has to begin with a number. This number is an arbitrary time unit which will automatically be scaled to fit the selected length of your video. Only the relative size matters. In the given example from 1 to 199 the prompt will be "cat, psychedelic, realistic, high quality" and from 200 to 450 it will be "dog, psychedelic, realistic, high quality". Why 450, not 300? Because the number marks the beginning, the actual length will be calculated, the last scene has a length that is the average of all other scenes. To make the last scene longer you can just add it twice, then the length of the last scene will be added to that of the second to last one, like in this example.

The basic structure of a line in the script representing a "scene" looks like this:
~~~
Number::Prompt::Negative Prompt
~~~

The :: for separating the number from the prompt is required, the second :: can be left away if no negative prompt is used.

## Use seed for n images

This option is experimental and I strongly recommend not to use it, as it seems to mess up the results. What it does is reusing the same seed for the selected number of images. I don't know why it gives the results that it does, probably has to do with subseeds and the separate Pytorch seed, so it should only be used for experimentation.

## Use Prompt Mixing?

This options allows the prompts to be mixed when changing the "scene". This means that when a new prompt is used for n images (selected amount on the slider) both prompts will be combined, that of the new scene and the old one. If you for example have 30 FPS and select Prompt Mixing Loops = 15 this would result in 0,5 seconds of mixed prompts in between scenes. In the example above this would mean it does not directly go from "cat" to "dog", but uses "cat, dog" for 15 images. The results of this method do heavily vary depending on the concrete prompts and the model you are using, but sometimes it produces some really neat transformations that look much more fluid than without prompt mixing.


## Tipps on using this script

- I tested this script with different models and it works, but the results do vary a lot. If a multiprompt does not give good results on one model it might on a different model.
- Test your prompts separately but using txt2img if you're not sure if they will work as expected.
- Generate short versions with low FPS first to see how you can improve the multiprompt txt before you start making longer versions.
- Separate content and style by using the global prompt feature (with $), you can have several global prompts in one file, they just get concatenated.
- Generate an appropriate starting image with txt2img.
- You can make the video more fluid by reducing the denoising strength while increasing the sampling steps and FPS. The last example on YouTube "Evolution 4 (Stable Diffusion Video)" for example has 30 FPS and I used 60 sampling steps with a denoising strength of 0.5 and it looks almost fluid.
- If you only have 6GB VRAM like me you can make 1:1 with 512x512 (Standard) or 16:9 with 640x360. I tested this resolutions a lot and never had any problems. Anythings bigger did cause problems, although not always.
- Zoom and rotate do still work, so feel free to also use them.
- I find that a prompt mixing of 20 with 30 FPS, so 2/3 of a second, seems to be good for longer videos with higher quality, but for better results it might be preferable to reduce prompt mixing to 10 or even 5 and add a short additional transion "scene" to the multiprompt.
- A higher CFG Scale should give results closer to the prompt but with worse image quality. I guess around 20 should be reasonable, but it might be worth to test different values.
- Try different sampling methods, that might also help to improve results.
- Prompt end still works, with an End Prompt Blend Trigger Percent of 0 it can be used to add more global prompts without having to edit the multiprompt txt.

## Examples for multiprompt

These are three different examples of the multiprompt example from above.

https://user-images.githubusercontent.com/58605249/211693510-aaf14830-b3d2-4989-a2c5-75742cc9dc84.mp4


https://user-images.githubusercontent.com/58605249/211693537-5aa8414d-37f4-48dd-955b-e3bd15b9bb79.mp4


https://user-images.githubusercontent.com/58605249/211693603-c0b52992-8db0-44ac-a7ff-4c5882c8f4e0.mp4


Here is an example of a more complex multiprompt and two small results.

~~~
# Multiprompt for a video about evolution
1::chemical reaction, molecules, atoms, protein::
25::bacteria::
50::multicellular organism, underwater::
75::sea worm in the ocean::
100::fish in the ocean::
110::coelacanth in the ocean, prehistoric fish::
125::coelacanth crawling on the beach, prehistoric fish::underwater, fish
150::reptilian::
175::amphibian, frog::
200::rodents, rat::
225::squirrel::
250::monkey::
275::human monkey::
300::neanderthal::comic
325::Stone Age man::comic
350::knight::comic
375::man with phone::
400::man in the future::
425::cyborg::
450::alien cyborg::
475::singularity, cyber technology, psychedelic::
500::creation of universe, psychedelic::
~~~



https://user-images.githubusercontent.com/58605249/211694043-74c67076-4e49-4e43-a9ce-de4b1edb1c1c.mp4



https://user-images.githubusercontent.com/58605249/211694087-05b8936c-6be9-4407-9e61-8c4013504803.mp4



Long version, better quality, 16:9, 30 FPS

https://www.youtube.com/watch?v=-CuH8WdsKag&t=11s


Version with improved multipromt txt file (more precise prompts), 30 FPS

https://www.youtube.com/watch?v=oBkNe_uzgXA&t=32s


## FFMPEG bug

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

Now you can manually run FFMPEG. Open a console an navigate to your FFMPEG folder (or add it the PATH). Then run the following (also put in the correct paths here): 

~~~
ffmpeg.exe -y -r 30 -f concat -safe 0 -i "C:\Users\{YourUserName}\stable-diffusion-webui\outputs\img2img-videos\{YourFileName}.txt" -vcodec libx264 -filter:v minterpolate -crf 10 -pix_fmt yuv420p "C:\Users\{YourUserName}\stable-diffusion-webui\outputs\img2img-videos\{YourFileName}.mp4"
~~~

This should give you the video that has failed from the raw images.
