# Learning Module 03: Color Spaces — RGB vs YUV (YCbCr)

## 1. What We Built
In `src/preprocessing/color_space.py`, we implemented complete, mathematically rigorous conversions between RGB and ITU-R BT.601 / BT.709 YCbCr color spaces, alongside luminance and chrominance plane separation.

## 2. Why Color Spaces Matter in Compression
* **RGB Representation**:
  Camera sensors and display panels natively operate in RGB. However, the Red, Green, and Blue channels have high inter-channel correlation ($> 0.9$ in natural scenes). Compressing RGB channels independently wastes bits encoding redundant information.
* **YUV (YCbCr) Representation**:
  Decouples the luminance (perceived brightness, $Y$) from chrominance (color information, $Cb$ and $Cr$).
  Because the Human Visual System (HVS) possesses far fewer cone cells than rod cells in the retinal periphery, human vision has substantially lower spatial acuity for color changes than for luminance changes.

## 3. Mathematical Transformation (ITU-R BT.601)
Forward transformation:
$$\begin{bmatrix} Y \\ Cb \\ Cr \end{bmatrix} = \begin{bmatrix} 0.299 & 0.587 & 0.114 \\ -0.168736 & -0.331264 & 0.500000 \\ 0.500000 & -0.418688 & -0.081312 \end{bmatrix} \begin{bmatrix} R \\ G \\ B \end{bmatrix} + \begin{bmatrix} 0 \\ 128 \\ 128 \end{bmatrix}$$

Inverse transformation:
$$\begin{bmatrix} R \\ G \\ B \end{bmatrix} = \begin{bmatrix} 1.0 & 0.0 & 1.40200 \\ 1.0 & -0.344136 & -0.714136 \\ 1.0 & 1.77200 & 0.0 \end{bmatrix} \begin{bmatrix} Y \\ Cb - 128 \\ Cr - 128 \end{bmatrix}$$

## 4. Relevant Code Files
* [`src/preprocessing/color_space.py`](file:///Users/oshishmadhan/.gemini/antigravity/scratch/adaptive-compression/src/preprocessing/color_space.py):
  * `rgb_to_yuv(rgb_img, standard="BT601")`
  * `yuv_to_rgb(yuv_img, standard="BT601")`
  * `get_luminance(rgb_img)`
  * `split_yuv_channels(yuv_img)`

## 5. Design Decisions & Common Bugs
* **Integer Roundoff Error**: Converting uint8 RGB $\to$ float32 YUV $\to$ uint8 RGB introduces minor rounding variance ($\pm 1$ intensity level). Our tests assert that roundoff error is strictly $\le 2$ gray levels.
* **Chroma Offsets**: Forgetting to add/subtract the $+128$ DC bias when converting between signed color difference and unsigned 8-bit representations.

## 6. PRISM / Technical Interview Questions
1. *Q: Why is green given the highest weight ($0.587$) in the luminance calculation?*  
   **A**: Human photopic spectral sensitivity peaks around $555\text{ nm}$ (green-yellow). The human eye perceives green as substantially brighter than red ($0.299$) or blue ($0.114$).
2. *Q: What is the difference between BT.601 and BT.709?*  
   **A**: BT.601 is designed for standard-definition (SDTV) video with different color primaries. BT.709 is designed for high-definition (HDTV) displays with updated phosphor/spectral primaries, allocating more weight to green ($0.7152$) and less to red ($0.2126$).
