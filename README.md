# Video Listening Trainer

I made this to practice my listening comprehension. It allows you to select a video along with its subtitles and test your ability to understand what is being said. This does require that the subtitles be good for the video because both the text and the timing are important.

![Example Use](https://github.com/hjlbs/spanish/blob/main/images/sample.png)

# Finding videos

I am not advocating anything illegal but if you have permission, you can download youtube videos that have subtitles and use that. Try googling "download youtube video" and "download youtube video subtitles" that should help you find some good stuff.

# How to use

Download the ``spanish.py`` file to your computer. At this point I have only tested windows. Follow the installation guide below to install the tools necessary to run it. Let me know if it works for you or if something breaks and I will look into it. This was just a fun project for me that I threw together in a day so be kind.

---

# **Interactive Video Listening Trainer - Installation Guide**

This guide will help you install everything you need to run the **Interactive Video Listening Trainer** on **Windows**, even if you’ve never installed programming tools before.

---

## **Step 1: Install Python 3 (the easy way)**

You don’t need to go to any website!
Windows lets you install **Python 3 directly from the Microsoft Store**.

### **How to do it:**

1. Open **PowerShell**.
   Press:

   ```
   Windows Key + X → Click "Windows PowerShell" or "Terminal"
   ```

2. In PowerShell, type:

   ```powershell
   python3
   ```

3. This will open the **Microsoft Store** automatically.

4. Click **Get** or **Install**.

5. Wait for the installation to finish. It’s free!

---

### **Check that Python is installed**

1. Go back to **PowerShell**.

2. Type:

   ```powershell
   python3 --version
   ```

3. You should see something like:

   ```
   Python 3.11.5
   ```

---

## **Step 2: Install VLC Media Player**

VLC lets the trainer play video and sound.

### **How to install VLC:**

1. Open your browser and go to:

   **[https://www.videolan.org/vlc/](https://www.videolan.org/vlc/)**

2. Click **Download VLC**.

3. Run the installer and follow the instructions.

---

## **Step 3: Install Python modules**

Now install the extra tools Python needs.

### **In PowerShell, type:**

```powershell
pip3 install python-vlc
pip3 install opencv-python
```

If `pip` doesn’t work, try:

```powershell
python3 -m pip install python-vlc
python3 -m pip install opencv-python
```

---

## **Step 4: Prepare your files**

1. Put your **video file** in the same folder as the trainer script.
   Example: `video.mp4`

2. Put your **subtitles (.srt)** file in the same folder.
   Example: `subtitles.srt`

---

## **Step 5: Run the trainer**

1. Open **PowerShell**.

2. Go to the folder where your files are.
   Example:

   ```powershell
   cd C:\Users\YourName\Downloads\ListeningTrainer
   ```

3. Run the program:

   ```powershell
   python3 spanish.py
   ```

4. A menu will pop up to choose your **video** and **subtitles**.

---

## **Features**

* Watch your video.
* Type what you hear.
* Get **live feedback**:

  * Correct letters: **black**
  * Incorrect letters: **red**
* Replay, skip, show answer, or go back.

---