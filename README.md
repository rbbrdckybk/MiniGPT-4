# MiniGPT-4

Simplified local setup of [MiniGPT-4](https://github.com/Vision-CAIR/MiniGPT-4) running in an Anaconda environment. Fixes for various Windows OS issues are provided, as well as links to pre-prepared Vicuna weights.

# Requirements

You'll need an Nvidia GPU with at least 12GB of VRAM (24GB+ is preferred). These instructions were tested on a Windows 10 machine with an Nvidia 3080Ti GPU, but should work on Linux as well (not tested).

# Setup

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
Note that if you get an error while installing pycocotools on Windows, you may need to install the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). See [this issue](https://github.com/cocodataset/cocoapi/issues/169#issuecomment-724622726) for more information.

**[5]** Install PyTorch:
```
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

**[6]** Prepare your own weights by following the official instructions (step 2) [here](https://github.com/Vision-CAIR/MiniGPT-4#installation). This involves waiting for your access request to be approved, then downloading ~200GB of LLaMA weights, and then using the Vicuna toolset to prepare working weights.

**-OR-** 

Simply reference these pre-prepared weights (credit to [wangrongsheng](https://huggingface.co/wangrongsheng)) by opening **minigpt4/configs/models/minigpt4.yaml** & edit line 16:

if you have 24GB+ of VRAM:
```
llama_model: "wangrongsheng/MiniGPT-4-LLaMA"
```
if you have 12GB+ of VRAM:
```
llama_model: "wangrongsheng/MiniGPT-4-LLaMA-7B"
```

**[7]** Download and reference the pretrained MiniGPT-4 checkpoint (links provided by official repo here @ [step 3](https://github.com/Vision-CAIR/MiniGPT-4#installation)):

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

**[8]** If you're on Windows, you'll need to run these commands to [fix a known issue with bitsandbytes](https://github.com/TimDettmers/bitsandbytes/issues/175):
```
pip uninstall bitsandbytes
pip install git+https://github.com/Keith-Hon/bitsandbytes-windows.git
```
You'll also need to place [this DLL](https://github.com/DeXtmL/bitsandbytes-win-prebuilt/blob/main/libbitsandbytes_cuda116.dll) into your **[Anaconda root directory]\envs\textgen\lib\site-packages\bitsandbytes** folder.

Skip this step entirely if you're on Linux!

**[9]** (optional) Download my simple API server & client implementation: I've removed gradio and set MiniGPT-4 up as a simple Flask server that you can run locally to handle API requests. I've also coded a simple client example so you can see how to interact with it.
```
pip install Flask
curl -L -o api-server.py -C - "https://raw.githubusercontent.com/rbbrdckybk/MiniGPT-4/main/api-server.py"
curl -L -o api-client-example.py -C - "https://raw.githubusercontent.com/rbbrdckybk/MiniGPT-4/main/api-client-example.py"
mkdir img
curl -L -o img/simpsons.jpg -C - "https://raw.githubusercontent.com/rbbrdckybk/MiniGPT-4/main/img/simpsons.jpg"
```
See below for usage instructions!

# Usage

Run the official gradio demo to verify that everything works:
```
python demo.py --cfg-path eval_configs/minigpt4_eval.yaml --gpu-id 0
```
Note that several large files (~15GB total) will be downloaded on the first run.

If you downloaded my API server & client in step 9 (verify that the official gradio demo works properly before continuing!), you can test them by starting the server with:
```
python api-server.py
```
Once the server is running, you can start the client with:
```
python api-client-example.py
```
You should see the client send the example image (img/simpsons.jpg) to the server and ask MiniGPT-4 several questions about it. Import the **MiniGPT4_Client** class from api-client-example.py into your own projects to easily interact with MiniGPT-4!
