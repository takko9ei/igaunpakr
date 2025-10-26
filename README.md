# IGAUnpakr

## 中文

### 免责声明

本项目的开发初衷是为了分析网络上一个具有特定文件格式（`.iga`）的游戏中出现的 bug，同时学习原项目（Pascal）的实现。该游戏由作者本人购入正版。作者未曾向网络上传输任何解包文件，并在分析完成后立即删除了所有本地解包文件。

本项目仅作学习和技术研究用途，并遵守相关法律法规。

**严禁将使用本项目解包的任何文件在网络上分发。** 任何因使用本项目而引发的法律问题或纠纷，作者概不负责。

### 致谢

本项目是 RikuKH3 的 Pascal 版本程序的 Python 实现，并修复了原项目中的一些已知 bug。

原仓库地址：[https://github.com/RikuKH3/igapack](https://github.com/RikuKH3/igapack)

在此向原作者 RikuKH3 致谢。

### 使用方法

#### 解包

将需要解密的文件（`.iga` 格式）拖拽到本程序的入口文件上（若直接使用 Python 环境运行，则拖拽到 `.py` 文件；若使用的是打包后的程序，则拖拽到 `.exe` 文件）。

#### 封包

1. 修改（替换）解包出来的文件夹里的文件，注意保持命名。
2. （关键） 拖动整个文件夹（必须包含 iga_filelist.txt）到 igapack.exe 图标上。
3. 新的 .iga 文件会生成在文件夹旁边。

**关于 txt 中的数字**
解包和封包依赖于这行数字。不需要动它，保持解包的原样即可。

**关于 txt 中的文件名和生成的文件夹名**
若你修改他们（在保持 txt 中的文件名与文件夹中的文件命名相同的情况下），可以正常封包，但是这一封包可能无法在游戏中正常工作。

**再次强调：** 本项目所解密之文件只能用于分析兼容性问题、理解加密算法等学习用途。请在分析完毕后尽快删除，且**切勿向网络上传播任何解密后的文件**。

本项目使用 Nuitka 打包，在运行时有小概率被 Windows Defender 误报，请添加过滤规则，或者在自己的 Python 环境中运行本项目。

---

## English

### Disclaimer

This project was developed solely to analyze a bug within a legally purchased game that uses a specific file format (`.iga`), and practicing implement of related algorithm implemented in orinial Pascal program. The author has not uploaded any unpacked game files to the internet and deleted all local unpacked files immediately after the analysis was complete.

This project is intended for educational and technical research purposes only, in accordanceance with applicable laws and regulations.

**Distribution of any files unpacked using this project on the network is strictly prohibited.** The author assumes no responsibility for any legal issues or disputes arising from the use of this project.

### Acknowledgements

This project is a Python implementation of the Pascal program by RikuKH3, with several bug fixes applied.

Original repository: [https://github.com/RikuKH3/igapack](https://github.com/RikuKH3/igapack)

Special thanks to the original author, RikuKH3.

### Usage

#### Unpacking

To use the program, drag and drop the target file (`.iga` format) onto the program's entry point (the `.py` file if running in a Python environment, or the `.exe` file if using the packaged executable).

#### Packing

1. Modify (replace) the files inside the unpacked folder. Be sure to keep the filenames unchanged.
2. (Crucial) Drag the **entire folder** (which must contain `iga_filelist.txt`) onto the `igapack.exe` icon.
3. A new .iga file will be generated alongside the folder.

**About the number in the .txt file**
Unpacking and packing rely on this number. Do not modify it; keep it exactly as it was from the unpack.

**About the filenames in the .txt and the actual filenames**
If you modify them (even if you keep the filenames in the .txt and the actual files in the folder consistent), the tool will pack it successfully, but this new archive will likely not work in the game.

**Reiteration:** Files decrypted by this project are to be used only for study purposes, such as analyzing compatibility issues or understanding the encryption algorithm. Please delete all decrypted files immediately after your analysis is complete, and **do not upload any decrypted files to the network.**

This project is packaged using Nuitka and may trigger a false positive from Windows Defender at runtime. Please add an exclusion rule or run the project in your own Python environment.
