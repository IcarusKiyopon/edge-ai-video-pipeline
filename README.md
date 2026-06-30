# 🎬 Fully Autonomous GenAI Video Orchestration Engine

A high-performance, asynchronous content generation pipeline that synthesizes narrative audio, calculates word-level transcription timestamps using edge-deployed machine learning, and programmatically renders stylized short-form videos with zero human intervention.

This engine completely automates the production of vertical video content (TikTok/Shorts/Reels) by chaining cloud LLMs, synthesized TTS, local quantized neural networks, and raw FFmpeg subprocesses.

## 🧠 System Architecture

The pipeline executes a 4-stage multi-modal assembly process:

1. **Agentic Script Generation (Groq LPUs / Llama 3.3)**
   * Utilizes `groq` to asynchronously stream zero-shot micro-fiction prompts to a Llama-3.3-70B model.
   * Generates highly variable, climax-driven horror stories parameterized by an array of thematic constraints.

2. **Audio Synthesis & Modulation (Edge-TTS)**
   * Converts the LLM output into high-fidelity neural speech.
   * Programmatically down-samples the speaking rate (`-7%`) and pitch (`-4Hz`) to create suspenseful pacing tailored for caption reading.

3. **Local Edge AI Transcription (Faster-Whisper)**
   * Bypasses cloud latency by deploying `faster-whisper` natively on the CPU.
   * Utilizes **INT8 quantization** to maintain ultra-fast inference speeds while mapping precise, word-by-word boundary timestamps for the generated audio.
   * Groups timestamp bounds into rapid 3-word visual chunks optimized for viewer retention.

4. **Compositing & Hardcoding (MoviePy + FFmpeg)**
   * **Spatial Math:** Dynamically calculates 9:16 aspect ratio crops on random horizontal background footage.
   * **Subprocess Execution:** Injects the `.srt` file directly into a raw FFmpeg stream, applying a custom `force_style` filter (Impact font, high-contrast neon/black stroking, elevated margins) to burn hardcoded subtitles into the final H.264 container.

## 🛠️ Tech Stack
* **Language:** Python 3.x (Async/Await)
* **Cloud AI:** Groq API (Llama 3.3-70B-Versatile)
* **Edge AI:** `faster-whisper` (CTranslate2)
* **Media Processing:** `moviepy`, FFmpeg, `edge-tts`

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/IcarusKiyopon/edge-ai-video-pipeline.git](https://github.com/IcarusKiyopon/edge-ai-video-pipeline.git)
   cd edge-ai-video-pipeline
   ```

**Install dependencies:**
Ensure you have FFmpeg installed on your system PATH. Then install the Python packages:

```bash
    pip install groq edge-tts faster-whisper moviepy srt python-dotenvConfigure the Environment:
```
**Create a .env file in the root directory and add your Groq API key:**

```plaintext
GROQ_API_KEY=your_api_key_here
Create a folder named gameplay_pool/ in the root directory and drop at least one .mp4 background video inside it.
```
**Execute the Pipeline:**

```bash
python main.py
```
The script will output the final rendered video to the automatically generated output/ directory.