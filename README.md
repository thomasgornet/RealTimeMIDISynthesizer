# Real-Time MIDI Synthesizer  

## Overview  

This project is a real-time MIDI synthesizer that I developed as part of the **Analog Signal Processing Honors (ECE 210H) course**. Unlike assigned coursework, I independently designed and implemented this project, driven by my passion for both **music and embedded systems**. The synthesizer processes MIDI keyboard inputs on a **Raspberry Pi 4** using **Python**, generating real-time waveforms and applying **digital signal processing (DSP) effects** such as:  

- **Pitch shifting** (via FFT-based frequency modulation)  
- **Vibrato** (using interpolation-based pitch modulation)  
- **Distortion** (waveform clipping for a crunchy effect)  
- **Chorus** (delayed, modulated copies for a fuller sound)  
- **Bit-crushing** (quantization for a lo-fi effect)  

This project brings together concepts from **Fourier Transforms, time/frequency modulation, and low-frequency oscillators (LFOs)**—all of which are integral to **ECE 210H**. As a musician and engineer, I wanted to create something that blends **musical creativity with real-time signal processing** while also exploring **embedded audio programming**.  

## Key Features  

- **MIDI Keyboard Input Handling** – Processes MIDI messages for real-time note control.  
- **Waveform Synthesis** – Generates sine and saw waves, with potential for more complex synthesis.  
- **Real-Time Signal Processing** – Applies various DSP effects to enhance and manipulate sound.  
- **Embedded Implementation** – Runs efficiently on a **Raspberry Pi 4** with minimal latency.  

For a deeper dive into the theory, implementation, and results, check out the full project report below! 🚀🎹  

[Video demo of my project!](https://youtu.be/pJ_WUidqRsw)

<img width="946" alt="image" src="https://github.com/user-attachments/assets/b8f7fd44-e210-40f6-8f9e-8a32325bb586" />




<br/>
<br/>

# DSP MIDI Synthesizer Project Report  
**Thomas Gornet**  

## Introduction  

This project explores real-time MIDI audio synthesizing using a **MIDI Keyboard, a Raspberry Pi 4, and Python**. The implementation also integrates several **audio signal processing effects**, such as:  

- **Pitch shifting**  
- **Vibrato**  
- **Distortion**  
- **Chorus**  
- **Reverb**  

These effects simulate those found on a synthesizer. The project incorporates concepts from **ECE 210 and 210H**, including **Fourier Transforms, FFTs, time modulation, frequency modulation, and LFOs**.  

I chose this project due to my passion for music. As a **piano player**, I saw an opportunity to combine **waveform manipulation, real-time signal processing, and embedded systems**—concepts that align closely with **ECE 210H coursework**.  

## Theory  

### Key Features and Their Theory  

### 1. MIDI Input Handling  

**MIDI** (Musical Instrument Digital Interface) is a protocol that standardizes communication between electronic musical instruments, computers, and audio devices. Unlike audio signals, **MIDI transmits control messages**, including:  

- **Note on/off messages**  
- **Pitch wheel data**  
- **Control change messages**  

These messages are **mapped to frequencies, control signals, and waveform parameters**, allowing real-time synthesis and signal processing.  

### 2. Waveform Synthesis  

Once MIDI messages are decoded, they are converted into audible **waveforms**. This project generates **sine and saw waves**, though more complex waveforms can be synthesized. Since these waveforms are digital, they contain **finite sampled points** that approximate a continuous signal based on a given **sampling frequency**.  

### 3. Signal Processing  

After converting MIDI messages into time-domain waveforms, the system applies **various audio effects** to manipulate the sound.  

#### **Pitch Shifting**  
Pitch is adjusted using an **FFT (Fast Fourier Transform)**. The waveform is transformed into the frequency domain, where frequencies are modulated based on an **exponential pitch relationship**. After modification, an **inverse FFT** reconstructs the time-domain signal.  

![Pitch Shifting](https://github.com/user-attachments/assets/80c2a883-0068-45fb-83ae-ebc0ba7da747)  

#### **Vibrato**  
Vibrato modulates pitch at a low frequency. Instead of FFT, this project uses **interpolation**, which dynamically stretches or shrinks the waveform, achieving the same **pitch variation effect**.  

![Vibrato](https://github.com/user-attachments/assets/d05f7546-20e5-40ee-afd9-ce24bc8a9a24)  

#### **Distortion**  
Distortion amplifies and **clips** the waveform, emulating signal saturation found in analog circuits, adding a "crunchy" sound.  

![Distortion](https://github.com/user-attachments/assets/51a5661c-a8b0-4048-971c-8bdad183f501)  

#### **Chorus**  
The **chorus effect** combines **delayed, pitch-modulated copies** of the waveform, creating a fuller sound similar to **natural variations in a choir or band**.  

![Chorus](https://github.com/user-attachments/assets/57ab860e-c0b5-4fd5-a644-38a252ee73e2)  

#### **Bit-Crushing**  
A bit crusher **reduces the sampling rate** of a sound, introducing **quantization artifacts** that result in a lo-fi, vintage effect.  

![Bit-Crushing](https://github.com/user-attachments/assets/8548bc89-ec63-43ae-b3a4-937eb5e2d94e)  

## Development  

### Setting Up the Raspberry Pi  
The initial setup was **time-consuming**, with issues in **SSH connectivity and Python library installation**.  

- **SSH was resolved** using a **direct Ethernet connection**.  
- **Python dependencies** were installed via a **virtual environment**.  

### MIDI Input System  
Using the **Mido Python library**, MIDI messages were processed by iterating through incoming signals and **mapping them to frequencies using a dictionary**.  

### Audio Output  
Audio output was implemented using the **pyaudio library**, streaming generated waveforms through the Raspberry Pi’s audio system.  

### Waveform Generation  
Waveform synthesis introduced a **phase misalignment bug**, causing periodic **popping noises** when holding a note. This was due to **discontinuities between audio stream iterations**.  

- **Solution:** Tracked phase shifts and ensured continuity between cycles.  

### Signal Processing Implementation  

1. **Distortion:** Implemented by **scaling and clipping amplitudes** using NumPy.  
2. **Pitch Shifting (FFT-Based):**  
   - **Initial Issue:** Frequency bin shifts caused **unexpected artifacts**.  
   - **Solution:** Used **NumPy interpolation** to align bins properly.  
   - **New Issue:** Lost **phase information**, causing discontinuities.  
   - **Final Fix:** Tracked **phase shifts across FFTs**.  
3. **Vibrato:** Implemented with **interpolation instead of FFT**, achieving **smoother modulation**.  
4. **Chorus:** Encountered **circular shift bugs**, resulting in **unwanted noise**.  
   - **Workaround:** Mixed the chorus effect with the original waveform in different ratios.  
5. **Bit-Crusher:** Implemented via **quantization-based rounding**, artificially reducing the sample rate.  

### Hyperparameter Adjustments  
- **Increased audio stream duration** to **reduce phase artifacts**, but not too much to **avoid latency issues**.  
- **Decreased FFT bin count** to **improve real-time responsiveness**.  

## Results  

The project **met expectations**, producing a **playable keyboard with waveform synthesis and signal processing effects**. However, some challenges remain:  

- **Convolution-based reverb** was **difficult to implement** due to **increased sample length**.  
- **Chorus effect** remains **noisier than desired**.  
- Despite minor artifacts, **all effects function as intended**.  

## Conclusion  

This project successfully demonstrated the integration of **MIDI input, waveform synthesis, and real-time signal processing** on a **Raspberry Pi 4 using Python**. Key achievements include:  

- **MIDI input handling**  
- **Waveform generation**  
- **Implementation of pitch shifting, vibrato, distortion, and chorus effects**  

Despite some **phase alignment and latency challenges**, the synthesizer **performs well**, offering a functional range of sounds and effects. Through this project, I gained hands-on experience with:  

- **Real-time DSP**  
- **Debugging signal processing algorithms**  
- **Waveform manipulation**  

This experience deepened my understanding of **ECE 210H principles** and their **practical applications** in embedded systems and music technology.  



