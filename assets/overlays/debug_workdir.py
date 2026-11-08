import sys
sys.path.insert(0, ".")
from viralforge.render import ffmpeg
from PIL import Image
import numpy as np

workdir = "data/cache/ai_enhance_v4_El_método_exprés_para_el_reactivo_limitante"

# Let's inspect base_video.mp4
dur = ffmpeg.probe_duration(f"{workdir}/base_video.mp4")
print("base_video.mp4 duration:", dur)

# Let's check rendered_final.mp4 in workdir
final_p = f"{workdir}/rendered_final.mp4"
dur_f = ffmpeg.probe_duration(final_p)
print("workdir rendered_final.mp4 duration:", dur_f)

# Extract frame from workdir/rendered_final.mp4 at 9.0s
ffmpeg.run(["-ss", "9.0", "-i", final_p, "-vframes", "1", "assets/overlays/workdir_rendered_9s.png"])
im = Image.open("assets/overlays/workdir_rendered_9s.png")
arr = np.array(im)
top_area = arr[50:230, 140:580]
print("workdir rendered_final.mp4 top area at 9s: mean =", top_area.mean(), "max =", top_area.max())
