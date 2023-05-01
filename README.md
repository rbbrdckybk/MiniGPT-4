# MiniGPT-4

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



