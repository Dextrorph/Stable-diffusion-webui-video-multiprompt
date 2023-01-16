import numpy as np
from tqdm import trange
import glob
import os
import modules.scripts as scripts
import gradio as gr
import subprocess
from modules import processing, shared, sd_samplers, images
from modules.processing import Processed
from modules.sd_samplers import samplers
from modules.shared import opts, cmd_opts, state
from PIL import Image
import modules
import yaml


class Script(scripts.Script):
    def title(self):
        return "Videos multiprompt"

    def show(self, is_img2img):
        return is_img2img

    def ui(self, is_img2img):

        prompt_end_trigger=gr.Slider(minimum=0.0, maximum=0.9, step=0.1, label='End Prompt Blend Trigger Percent', value=0)
        prompt_end = gr.Textbox(label='Prompt end', value="")

        smooth = gr.Checkbox(label='Smooth video', value=True)
        seconds = gr.Slider(minimum=1, maximum=250, step=1, label='Seconds', value=1)
        fps = gr.Slider(minimum=1, maximum=60, step=1, label='FPS', value=10)

        denoising_strength_change_factor = gr.Slider(minimum=0.9, maximum=1.1, step=0.01,
                                                     label='Denoising strength change factor', value=1)

        zoom = gr.Checkbox(label='Zoom', value=False)
        zoom_level = gr.Slider(minimum=1, maximum=1.1, step=0.001, label='Zoom level', value=1)
        direction_x = gr.Slider(minimum=-0.1, maximum=0.1, step=0.01, label='Direction X', value=0)
        direction_y = gr.Slider(minimum=-0.1, maximum=0.1, step=0.01, label='Direction Y', value=0)

        rotate = gr.Checkbox(label='Rotate', value=False)
        rotate_degree = gr.Slider(minimum=-3.6, maximum=3.6, step=0.1, label='Degrees', value=0)

        is_tiled = gr.Checkbox(label="Is the Image Tiled?", value = False)
        trnx = gr.Checkbox(label='TranslateX', value=False)
        trnx_left = gr.Checkbox(label='Left', value=False)
        trnx_percent = gr.Slider(minimum=0, maximum=50, step=1, label='PercentX', value=0)
        trny = gr.Checkbox(label='TranslateY', value=False)
        trny_up = gr.Checkbox(label='Up', value=False)
        trny_percent = gr.Slider(minimum=0, maximum=50, step=1, label='PercentY', value=0)
        show = gr.Checkbox(label='Show generated pictures in ui', value=False)

        use_multiprompt = gr.Checkbox(label='Use multiprompt?', value=False)
        multiprompt_path = gr.Textbox(label='Multiprompt yaml path', value="")
        use_prompt_mixing = gr.Checkbox(label='Use Prompt Mixing?', value=False)
        prompt_mixing_loops = gr.Slider(minimum=0, maximum=120, step=1, label='Prompt Mixing Loops', value=0)
        gradual_mixing = gr.Checkbox(label='Gradual Prompt Mixing?', value=True)
        comma_fix = gr.Checkbox(label='Add comma before prompt to hotfix issue with ignored prompts in some models?', value=True)

        return [show, prompt_end, prompt_end_trigger, seconds, fps, smooth, denoising_strength_change_factor,
                zoom, zoom_level, direction_x, direction_y,
                rotate, rotate_degree,
                is_tiled, trnx, trnx_left, trnx_percent, trny, trny_up, trny_percent,
                use_multiprompt, multiprompt_path, use_prompt_mixing, prompt_mixing_loops, gradual_mixing, comma_fix]

    def zoom_into(self, img, zoom, direction_x, direction_y):
        neg = lambda x: 1 if x > 0 else -1
        if abs(direction_x) > zoom-1:
            # *0.999999999999999 to avoid a float rounding error that makes it higher than desired
            direction_x = (zoom-1)*neg(direction_x)*0.999999999999999
        if abs(direction_y) > zoom-1:
            direction_y = (zoom-1)*neg(direction_y)*0.999999999999999
        w, h = img.size
        x = w/2+direction_x*w/4
        y = h/2-direction_y*h/4
        zoom2 = zoom * 2
        img = img.crop((x - w / zoom2, y - h / zoom2,
                        x + w / zoom2, y + h / zoom2))
        return img.resize((w, h), Image.LANCZOS)

    def rotate(self, img: Image, degrees: float):
        img = img.rotate(degrees)
        return img

    def blend(self, signal, noisey):
        noisey = noisey[np.random.permutation(noisey.shape[0]), :, :]
        noisey = noisey[:, np.random.permutation(noisey.shape[1]), :]
        # TODO figure out how to do this in numpy i guess we can save time here. this runs with 32 ms.
        img_tmp = Image.fromarray(signal)
        noise = Image.fromarray(noisey)
        img_tmp.putalpha(1)
        noise.putalpha(1)
        blend = Image.blend(img_tmp, noise, 0.3)
        blend.convert("RGB")
        bg = Image.new("RGB", blend.size, (255, 255, 255))
        bg.paste(blend)
        result = np.array(bg)
        return result

    def translateY(self, img: Image, percent: int, is_tiled: bool, up: bool = False):
        w, h = img.size
        scl = h*(percent/100.0)
        h = int(scl)
        na = np.array(img)
        if up:
            nextup = na[0:h, :, :]
            nextdown = na[-h:, :, :]
            if is_tiled:
                nextup = na[-h:, :, :]
            else:
                nextup = self.blend(nextup, nextdown)
            na = np.vstack((nextup, na))
            na = na[:-h, :]
        else:
            nextdown = na[-h:, :, :]
            nextup = na[0:h, :, :]
            if is_tiled:
                nextdown = na[0:h, :, :]
            else:
                nextdown = self.blend(nextdown, nextup)
            na = np.vstack((na, nextdown))
            na = na[h:, :]
        img = Image.fromarray(na)
        return img

    def translateX(self, img: Image, percent: int, is_tiled: bool, left: bool = False):
        w, h = img.size
        scl = w*(percent/100)
        w = int(scl)
        na = np.array(img)

        if left:
            nextleft = na[:, 0:w:, :]
            nextright = na[:, -w:, :]
            if is_tiled:
                nextleft = na[:, -w:, :]
            else:
                nextleft = self.blend(nextleft, nextright)
            na = np.hstack((nextleft, na))
            na = na[:, :-w]
        else:
            nextright = na[:, -w:, :]
            nextleft = na[:, 0:w:, :]
            if is_tiled:
                nextright = na[:, 0:w, :]
            else:
                nextright = self.blend(nextright, nextleft)
            na = np.hstack((na, nextright))
            na = na[:, w:]
        img = Image.fromarray(na)
        return img

    def run(self, p,
            show, prompt_end, prompt_end_trigger, seconds, fps, smooth, denoising_strength_change_factor,
            zoom, zoom_level, direction_x, direction_y,
            rotate, rotate_degree,
            is_tiled, trnx, trnx_left, trnx_percent, trny, trny_up, trny_percent,
            use_multiprompt, multiprompt_path, use_prompt_mixing, prompt_mixing_loops, gradual_mixing, comma_fix):
        processing.fix_seed(p)

        p.batch_size = 1
        p.n_iter = 1

        batch_count = p.n_iter
        p.extra_generation_params = {
            "Denoising strength change factor": denoising_strength_change_factor,
        }

        output_images, info = None, None
        initial_seed = None
        initial_info = None

        loops = seconds * fps

        grids = []
        all_images = []
        state.job_count = loops * batch_count

        initial_color_corrections = [processing.setup_color_correction(p.init_images[0])]

        if use_multiprompt:
            multiprompt = get_multiprompt_from_path(multiprompt_path)
        else:
            multiprompt = []
        
        # Scales the multiprompt to number of loops
        multiprompt.sort()
        if len(multiprompt) > 0:
            multiprompt_scale = (loops / multiprompt[-1][0]) * (len(multiprompt) / (len(multiprompt) + 1))
        for data in multiprompt:
            data[0] = int(data[0] * multiprompt_scale)

        global_prompt = ''
        negative_global_prompt = ''

        for n in range(batch_count):
            history = []
            processing_data = []

            for i in range(loops):
                p.n_iter = 1
                p.batch_size = 1
                p.do_not_save_grid = True

                if opts.img2img_color_correction:
                    p.color_corrections = initial_color_corrections

                if use_multiprompt and len(multiprompt) > 0:
                    for j in range(len(multiprompt)):
                        if i == multiprompt[j][0]:
                            if "negative_prompt" in multiprompt[j][2]:
                                processing_data = [multiprompt[j][1], multiprompt[j][2]["negative_prompt"], multiprompt[j][2].copy()]
                            else:
                                processing_data = [multiprompt[j][1], '', multiprompt[j][2].copy()]

                            if "global_prompt" in multiprompt[j][2].keys():
                                global_prompt = multiprompt[j][2]["global_prompt"]
                            if "negative_global_prompt" in multiprompt[j][2].keys():
                                negative_global_prompt = multiprompt[j][2]["negative_global_prompt"]

                        if i >= multiprompt[j][0]:
                            if use_prompt_mixing and i - multiprompt[j][0] < prompt_mixing_loops and j > 0:
                                if gradual_mixing:
                                    scale = (i - multiprompt[j][0]) / prompt_mixing_loops
                                    processing_data[0] = combine_prompts(multiprompt[j-1][1], multiprompt[j][1], scale)
                                else:
                                    processing_data[0] = multiprompt[j][1] + ', ' + multiprompt[j-1][1]
                            else:
                                processing_data[0] = multiprompt[j][1]

                            if global_prompt != '':
                                if processing_data[0] == '':
                                    processing_data[0] = global_prompt
                                else:
                                    processing_data[0] = processing_data[0] + ', ' + global_prompt

                            if negative_global_prompt != '':
                                if processing_data[1] == '':
                                    processing_data[1] = negative_global_prompt
                                else:
                                    processing_data[1] = processing_data[1] + ', ' + negative_global_prompt

                            if comma_fix:
                                processing_data[0] = ',' + processing_data[0]

                            apply_scene_to_processing(p, *processing_data)

                            if "zoom" in processing_data[2].keys():
                                zoom = processing_data[2]["zoom"]
                            if "zoom_level" in processing_data[2].keys():
                                zoom_level = processing_data[2]["zoom_level"]
                            if "direction_x" in processing_data[2].keys():
                                direction_x = processing_data[2]["direction_x"]
                            if "direction_y" in processing_data[2].keys():
                                direction_y = processing_data[2]["direction_y"]
                            if "rotate" in processing_data[2].keys():
                                rotate = processing_data[2]["rotate"]
                            if "rotate_degree" in processing_data[2].keys():
                                rotate_degree = processing_data[2]["rotate_degree"]
                            if "is_tiled" in processing_data[2].keys():
                                is_tiled = processing_data[2]["is_tiled"]
                            if "trnx" in processing_data[2].keys():
                                trnx = processing_data[2]["trnx"]
                            if "trnx_left" in processing_data[2].keys():
                                trnx_left = processing_data[2]["trnx_left"]
                            if "trnx_percent" in processing_data[2].keys():
                                trnx_percent = processing_data[2]["trnx_percent"]
                            if "trny" in processing_data[2].keys():
                                trny = processing_data[2]["trny"]
                            if "trny_up" in processing_data[2].keys():
                                trny_up = processing_data[2]["trny_up"]
                            if "trny_percent" in processing_data[2].keys():
                                trny_percent = processing_data[2]["trny_percent"]
                            if "seed_reuse" in processing_data[2].keys():
                                seed_reuse = processing_data[2]["seed_reuse"]
                            if "use_prompt_mixing" in processing_data[2].keys():
                                use_prompt_mixing = processing_data[2]["use_prompt_mixing"]
                            if "prompt_mixing_loops" in processing_data[2].keys():
                                prompt_mixing_loops = processing_data[2]["prompt_mixing_loops"]
                            if "gradual_mixing" in processing_data[2].keys():
                                gradual_mixing = processing_data[2]["gradual_mixing"]
                                
                if i > int(loops*prompt_end_trigger) and prompt_end not in p.prompt and prompt_end != '':
                    p.prompt = prompt_end.strip() + ' ' + p.prompt.strip()

                state.job = f"Iteration {i + 1}/{loops}, batch {n + 1}/{batch_count}"

                if i == 0:
                    # First image
                    init_img = p.init_images[0]
                    seed = p.seed
                    images.save_image(init_img, p.outpath_samples, "", seed, p.prompt)
                    history.append(init_img)
                else:
                    processed = processing.process_images(p)
                    init_img = processed.images[0]
                    history.append(init_img)

                    seed = processed.seed

                    if initial_seed is None:
                        initial_seed = processed.seed
                        initial_info = processed.info

                    if rotate and rotate_degree != 0:
                        init_img = self.rotate(init_img, rotate_degree*-1)

                    if zoom and zoom_level != 1:
                        init_img = self.zoom_into(init_img, zoom_level, direction_x, direction_y)

                    if trnx and trnx_percent > 0:
                        init_img = self.translateX(init_img, trnx_percent, is_tiled, trnx_left)
                    
                    if trny and trny_percent > 0:
                        init_img = self.translateY(init_img, trny_percent, is_tiled, trny_up)

                p.init_images = [init_img]

                p.seed = seed + 1
                p.denoising_strength = min(max(p.denoising_strength * denoising_strength_change_factor, 0.1), 1)

            grid = images.image_grid(history, rows=1)
            if opts.grid_save:
                images.save_image(grid, p.outpath_grids, "grid", initial_seed, p.prompt, opts.grid_format, info=info,
                                 short_filename=not opts.grid_extended_filename, grid=True, p=p)

            grids.append(grid)
            all_images += history

        if opts.return_grid:
            all_images = grids + all_images

        processed = Processed(p, all_images if show else [], initial_seed, initial_info)

        files = [i for i in glob.glob(f'{p.outpath_samples}/*.png')]
        files.sort(key=lambda f: os.path.getmtime(f))
        files = files[-loops:]
        files = files + [files[-1]]  # minterpolate smooth break last frame, dupplicate this

        video_name = files[-1].split('\\')[-1].split('.')[0] + '.mp4'
        save_dir = os.path.join(os.path.split(os.path.abspath(p.outpath_samples))[0], 'img2img-videos')

        video_path = make_video_ffmpeg(save_dir, video_name, files=files, fps=fps, smooth=smooth)
        play_video_ffmpeg(video_path)
        processed.info = processed.info + '\nvideo save in ' + video_path

        return processed


def install_ffmpeg(path):
    from basicsr.utils.download_util import load_file_from_url
    from zipfile import ZipFile

    ffmpeg_url = 'https://github.com/GyanD/codexffmpeg/releases/download/5.1.1/ffmpeg-5.1.1-full_build.zip'
    ffmpeg_dir = os.path.join(path, 'ffmpeg')

    ckpt_path = load_file_from_url(url=ffmpeg_url, model_dir=ffmpeg_dir)

    if not os.path.exists(os.path.abspath(os.path.join(ffmpeg_dir, 'ffmpeg.exe'))):
        with ZipFile(ckpt_path, 'r') as zipObj:
            listOfFileNames = zipObj.namelist()
            for fileName in listOfFileNames:
                if '/bin/' in fileName:
                    zipObj.extract(fileName, ffmpeg_dir)
        os.rename(os.path.join(ffmpeg_dir, listOfFileNames[0][:-1], 'bin', 'ffmpeg.exe'), os.path.join(ffmpeg_dir, 'ffmpeg.exe'))
        os.rename(os.path.join(ffmpeg_dir, listOfFileNames[0][:-1], 'bin', 'ffplay.exe'), os.path.join(ffmpeg_dir, 'ffplay.exe'))
        os.rename(os.path.join(ffmpeg_dir, listOfFileNames[0][:-1], 'bin', 'ffprobe.exe'), os.path.join(ffmpeg_dir, 'ffprobe.exe'))

        os.rmdir(os.path.join(ffmpeg_dir, listOfFileNames[0][:-1], 'bin'))
        os.rmdir(os.path.join(ffmpeg_dir, listOfFileNames[0][:-1]))
    return


def find_ff(name='mpeg'):
    """Check whether `name` is on PATH and marked as executable."""
    from shutil import which
    ffmpeg_path = which('ff' + name)
    if ffmpeg_path is None:
        install_ffmpeg(modules.paths.script_path)
        ffmpeg_path = 'ffmpeg/ff' + name
    return ffmpeg_path


def make_video_ffmpeg(save_dir, video_name, files=[], fps=10, smooth=True):
    path = modules.paths.script_path
    # save_dir = 'outputs/img2img-videos/'
    os.makedirs(save_dir, exist_ok=True)

    ff_path = find_ff('mpeg')

    video_name = os.path.join(save_dir, video_name)
    txt_name = video_name + '.txt'

    # save pics path in txt
    open(txt_name, 'w').write('\n'.join(["file '" + os.path.join(path, f) + "'" for f in files]))

    # -vf "tblend=average,framestep=1,setpts=0.50*PTS"
    subprocess.call(' '.join([
        f'{ff_path} -y',
        f'-r {fps}',
        '-f concat -safe 0',
        f'-i "{txt_name}"',
        '-vcodec libx264',
        '-filter:v minterpolate' if smooth else '',   # smooth between images
        '-crf 10',
        '-pix_fmt yuv420p',
        f'"{video_name}"'
    ]))
    return video_name


def play_video_ffmpeg(video_path):
    ff_path = find_ff('play')
    subprocess.Popen(
        f'''{ff_path} "{video_path}"'''
    )


def get_multiprompt_from_path(path):
    multiprompt = []
    if not os.path.isfile(path):
        raise FileNotFoundError("can't find multiprompt file")
    with open(path) as multiprompt_file:
        multiprompt = yaml.safe_load(multiprompt_file.read())
    for scene in multiprompt:
        if len(scene) == 2:
            scene.append({})
            
    time_trigger_value = 0
    for i in range(len(multiprompt)):
        save_value = multiprompt[i][0]
        multiprompt[i][0] = time_trigger_value
        time_trigger_value += save_value
    multiprompt.append([time_trigger_value, multiprompt[-1][1], multiprompt[-1][2]])
            
    return multiprompt


# Applies scene configuration to Processing object.
def apply_scene_to_processing(p, prompt, negative_prompt, args_dict):
    p.prompt = prompt
    p.negative_prompt = negative_prompt

    if "seed" in args_dict.keys():
        p.seed = args_dict["seed"]
        
    if "subseed" in args_dict.keys():
        p.subseed = args_dict["subseed"]
        
    if "subseed_strength" in args_dict.keys():
        p.subseed_strength = args_dict["subseed_strength"]
        
    if "seed_resize_from_h" in args_dict.keys():
        p.seed_resize_from_h = args_dict["seed_resize_from_h"]
        
    if "seed_resize_from_w" in args_dict.keys():
        p.seed_resize_from_w = args_dict["seed_resize_from_w"]
        
    if "steps" in args_dict.keys():
        p.steps = args_dict["steps"]
        
    if "cfg_scale" in args_dict.keys():
        p.cfg_scale = args_dict["cfg_scale"]
        
    if "restore_faces" in args_dict.keys():
        p.restore_faces = args_dict["restore_faces"]
        
    if "tiling" in args_dict.keys():
        p.tiling = args_dict["tiling"]
        
    if "denoising_strength" in args_dict.keys():
        p.denoising_strength = args_dict["denoising_strength"]


def combine_prompts(first_prompt, second_prompt, weight=0.5):
    if ',' in first_prompt:
        first_list = [elem.strip() for elem in first_prompt.split(',')]
    else:
        first_list = [first_prompt.strip()]
    for i in range(len(first_list)):
        if ':' not in first_list[i]:
            first_list[i] =  first_list[i] + ':1'
    first_dict = {}
    for elem in first_list:
        prompt, prompt_weight = elem.split(':')
        prompt_weight = float(prompt_weight)
        first_dict[prompt] = prompt_weight
    
    if ',' in second_prompt:
        second_list = [elem.strip() for elem in second_prompt.split(',')]
    else:
        second_list = [second_prompt.strip()]    
    for i in range(len(second_list)):
        if ':' not in second_list[i]:
            second_list[i] =  second_list[i] + ':1'
    second_dict = {}
    for elem in second_list:
        prompt, prompt_weight = elem.split(':')
        prompt_weight = float(prompt_weight)
        second_dict[prompt] = prompt_weight
    
    first_weight = 1 - weight
    for key in first_dict.keys():
        first_dict[key] = first_dict[key] * first_weight
    for key in second_dict.keys():
        second_dict[key] = second_dict[key] * weight
    
    result = first_dict.copy()
    for key in second_dict.keys():
        if key in result.keys():
            result[key] = result[key] + second_dict[key]
        else:
            result[key] = second_dict[key]
    
    added = 0
    for key in result.keys():
        added += result[key]
    normalization_factor = 0.5 / (added / len(result.keys()))
    for key in result.keys():
        result[key] = result[key] * normalization_factor
    
    return ', '.join([key + ':' + str(result[key]) for key in result.keys()])
