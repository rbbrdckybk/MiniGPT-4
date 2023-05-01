# MiniGPT-4

Simplified local setup of MiniGPT-4 running in an Anaconda environment.

# Requirements

You'll need an Nvidia GPU with at least 12GB of VRAM. The below instructions were tested on a Windows 10 machine with an Nvidia 3080Ti GPU, but should work on Linux as well.

# Setup

These instructions were tested on several Windows 10 desktops with a variety of modern Nvidia GPUs ranging from 8-12GB VRAM, and also on an Ubuntu Server 20.04.3 system with an old Nvidia Tesla M40 GPU (24GB VRAM).

**[1]** Install [Anaconda](https://www.anaconda.com/products/individual), open the root terminal, and create a new environment (and activate it):
```
conda create --name minigpt4 python=3.9
conda activate minigpt4
```

**[2]** Install a couple required Python packages:
```
conda install -c anaconda git urllib3
```

**[3]** Clone the official MiniGPT-4 repository and switch to its directory:
```
git clone https://github.com/Vision-CAIR/MiniGPT-4.git
cd MiniGPT-4
```

**[4]** Install requirements:
```
curl -L -o requirements.txt -C - "https://raw.githubusercontent.com/rbbrdckybk/MiniGPT-4/main/requirements.txt"
pip install -r requirements.txt
```
Note that if you get an error while installing pycocotools on Windows, you may need to install the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

**[5]** Prepare your own weights by following step 2 instructions [here](https://github.com/Vision-CAIR/MiniGPT-4#installation). 

**-OR-** simply reference these pre-prepared weights by opening **minigpt4/configs/models/minigpt4.yaml** & edit line 16:

if you have 24GB+ of VRAM:
```
llama_model: "wangrongsheng/MiniGPT-4-LLaMA"
```
if you have 12GB+ of VRAM:
```
llama_model: "wangrongsheng/MiniGPT-4-LLaMA-7B"
```

**[6]** Download and reference the pretrained MiniGPT-4 checkpoint:

if you have 24GB+ of VRAM, [download this checkpoint](https://drive.google.com/file/d/1a4zLvaiDBr-36pasffmgpvH5P7CKmpze/view?usp=share_link).

if you have 12GB+ of VRAM, [download this checkpoint](https://drive.google.com/file/d/1RY9jV0dyqLX-o38LrumkKRh6Jtaop58R/view?usp=sharing).

Place the downloaded checkpoint file in your MiniGPT-4 directory, then open **eval_configs/minigpt4_eval.yaml** and modify line 11:

if you have 24GB+ of VRAM:
```
ckpt: 'pretrained_minigpt4.pth'
```
if you have 12GB+ of VRAM (feel free to correct the typo in the official filename):
```
ckpt: 'prerained_minigpt4_7b.pth'
```

**[7]** If you're on Windows, you'll need to run these commands to [fix a known issue with bitsandbytes](https://github.com/TimDettmers/bitsandbytes/issues/175):
```
pip uninstall bitsandbytes
pip install git+https://github.com/Keith-Hon/bitsandbytes-windows.git
```
Skip this step entirely if you're on Linux!


# Usage

Run the gradio demo:
```
python demo.py --cfg-path eval_configs/minigpt4_eval.yaml --gpu-id 0
```
