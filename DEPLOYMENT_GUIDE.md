# Beginner's Guide to Deploying Your Transcription Model

Welcome! This guide will walk you through every step of getting your transcription model up and running on your computer. No technical experience required!

## What You'll Need

Before we start, you'll need:
- A computer with internet connection
- About 30 minutes of your time
- A free HuggingFace account (we'll create this together)

---

## Part 1: Install Docker (Think of it as a "Virtual Box" for your app)

Docker is a tool that lets your app run the same way on any computer. Think of it like a mini-computer inside your computer!

### For Windows Users:

1. **Download Docker Desktop**:
   - Go to [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
   - Click the big blue "Download for Windows" button
   - Wait for the file to download (it's about 500MB)

2. **Install Docker**:
   - Double-click the downloaded file (DockerDesktopInstaller.exe)
   - Click "OK" when it asks about WSL 2 (don't worry about what this means!)
   - Wait for the installation to finish (5-10 minutes)
   - Click "Close and restart" when it's done

3. **Start Docker**:
   - After your computer restarts, click the Docker Desktop icon on your desktop
   - Wait for Docker to start (you'll see a whale icon in your taskbar)
   - You might need to create a free Docker account (just follow the on-screen instructions)

### For Mac Users:

1. **Download Docker Desktop**:
   - Go to [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
   - Click "Download for Mac"
   - Choose the right version:
     - If your Mac is from 2021 or later: choose "Apple Chip"
     - If your Mac is older: choose "Intel Chip"

2. **Install Docker**:
   - Open the downloaded .dmg file
   - Drag the Docker icon to your Applications folder
   - Open Docker from your Applications folder
   - Click "Open" if you see a security warning

3. **Start Docker**:
   - Wait for Docker to start (you'll see a whale icon in your menu bar)
   - You might need to create a free Docker account (just follow the on-screen instructions)

### How to Know Docker is Running:
- **Windows**: Look for a whale icon in your taskbar (bottom right)
- **Mac**: Look for a whale icon in your menu bar (top right)
- The whale should be **still** (when it's running), not animated

---

## Part 2: Get Your HuggingFace Token

HuggingFace is a company that provides AI models. You need a free account to use their speaker diarization model.

1. **Create an Account**:
   - Go to [https://huggingface.co/join](https://huggingface.co/join)
   - Fill in your email, username, and password
   - Click "Sign up"
   - Check your email and click the verification link

2. **Accept the Pyannote Model License**:
   - Go to [https://huggingface.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
   - Click the big "Agree and access repository" button
   - This is free! You're just agreeing to use the model responsibly

3. **Get Your Access Token**:
   - Click on your profile picture in the top right corner
   - Click "Settings"
   - In the left menu, click "Access Tokens"
   - Click "Create new token"
   - Choose "Read" (this means the token can only read models, not modify anything)
   - Give it a name, like "transcription-model"
   - Click "Create token"

4. **Copy Your Token**:
   - You'll see a long string starting with `hf_`
   - **Click the copy icon** to copy it
   - **IMPORTANT**: Save this token in a safe place! You'll need it soon, and you can only see it once

---

## Part 3: Download the Code

Now we'll get your transcription model code onto your computer.

1. **Download the Code**:
   - Go to [your GitHub repository](https://github.com/andreacaravello/Transcription-Model)
   - Click the green "Code" button
   - Click "Download ZIP"
   - Wait for the download to finish

2. **Unzip the File**:
   - Find the downloaded ZIP file (usually in your Downloads folder)
   - **Windows**: Right-click the file > "Extract All..." > Choose where to save it (e.g., Desktop)
   - **Mac**: Double-click the ZIP file, and it will automatically unzip

3. **Remember Where You Saved It**:
   - You'll now have a folder called "Transcription-Model-main"
   - Keep this folder somewhere easy to find (like your Desktop or Documents)

---

## Part 4: Set Up Your Configuration File

Now we'll tell your app to use the HuggingFace token you created.

1. **Open the Folder**:
   - Navigate to the "Transcription-Model-main" folder you just unzipped

2. **Find the Template File**:
   - Look for a file called `.env.template`
   - **Can't see it?** You might need to show hidden files:
     - **Windows**: In File Explorer, click "View" > check "Hidden items"
     - **Mac**: In Finder, press `Command + Shift + .` (period)

3. **Create Your Configuration File**:
   - Right-click on `.env.template`
   - Select "Open with" > choose **Notepad** (Windows) or **TextEdit** or **VSCode** (Mac)
   - You'll see this line:
     ```
     HUGGINGFACE_TOKEN =your_token_here
     ```

4. **Add Your Token**:
   - Replace `your_token_here` with your actual HuggingFace token
   - It should look like this:
     ```
     HUGGINGFACE_TOKEN=hf_abcdef123456789XYZQWERTYUIOP
     ```
   (Your token will be much longer and different)

5. **Save the File With a New Name**:
   - Click "File" > "Save As"
   - Name it exactly: `.env` (with the dot at the start, NO cute)
   - **IMPORTANT**: Save it in the same folder as `.env.template`
   - Save it as **All Files** or **Plain Text** (not as a .txt file)

---

## Part 5: Open the Terminal (Command Prompt)

Don't worry! The terminal looks scary, but it's just a way to give your computer instructions by typing.

### For Windows Users:

1. Open **Command Prompt** or **PowerShell**:
   - Press `Windows key + R`
   - Type `cmd` or **powershell**
   - Press Enter

2. **Navigate to Your Folder**:
   - Type `cd` followed by a space
   - Drag and drop your "Transcription-Model-main" folder into the window
   - Press Enter

### For Mac Users:

1. Open **Terminal**:
   - Press `Command + Space`
   - Type "Terminal"
   - Press Enter

2. **Navigate to Your Folder**:
   - Type `cd` followed by a space
   - Drag and drop your "Transcription-Model-main" folder into the window
   - Press Enter

### How to Know You're in the Right Place:
- The terminal should now show the path to your folder
- Example: `C:\Users\YourName\Desktop\Transcription-Model-main`

---

## Part 6: Build Your Docker Container ("Create the Virtual Box")

Now we'll tell Docker to create a container (mini-computer) with everything your app needs.

1. **Run the Build Command**:
   - In your terminal window, type this exact command:
     ```bash
     docker build -t transcriber .
     ```
   - Press Enter

2. **Wait Patiently**:
   - This will take 5-10 minutes
   - You'll see lots of text scrolling — this is normal!
   - Docker is downloading everything your app needs:
     - Python (the programming language)
     - Whisper (the transcription model)
     - Pyannote (the speaker diarization model)
     - And more!

3. **How to Know It's Done**:
   - When it's finished, you'll see something like:
     ```
     Successfully built abc12345678
     Successfully tagged transcriber:latest
     ```
   - You'll see your terminal cursor again, waiting for another command

---

## Part 7: Run Your App!

Now for the exciting part — starting your transcription app!

1. **Start the Container**:
   - In your terminal, type this command:
     ```bash
     docker run --env-file .env -p 7860:7860 transcriber
     ```
   - Press Enter

2. **Wait for Startup**:
   - The first time you run it, it needs to download the Whisper model (2-5 minutes)
   - You'll see messages like:
     ```
     Info     Started server process
     INFO:     Waiting for application startup
     INFO:     Application startup complete
     ```

3. **Know When It's Ready**:
   - When you see:
     ```
     RUNNING ON http://0.0.0.0:7860
     ```
   - Your app is running! 🎉

4. **Open Your App in a Browser**:
   - Open your favorite web browser (Chrome, Firefox, Safari, etc.)
   - In the address bar, type:
     ```
     http://localhost:7860
     ```
   - Press Enter

---

## Part 8: Using Your Transcription App

Congratulations! You're now looking at your transcription app!

### How to Transcribe an Audio File:

1. **Choose your settings**:
   - **Whisper model**: Start with "base" (it's fast and accurate)
     - `base` = Fast, good for most uses
     - `small` = Slower, more accurate
     - `medium` = Even slower, even more accurate (bnt uses more memory)

2. **Enable diarization**:
   - Check the box if you want to know who said what
   - Leave it unchecked for just a plain transcript

3. **Upload your audio file**:
   - Click "Click to upload" or drag and drop your audio file
   - Supported formats: mp3, wav, m4a, ogg, and more

4. **Click "Transcribe"**:
   - Wait while the app processes your audio
   - A 5-minute audio file usually takes 1-3 minutes to process

5. **View your results**:
   - **Transcript**: The raw text of what was said
   - **Diarization**: When each speaker spoke (with timestamps)
   - **Transcript + Diarization**: The full transcript with speaker labels

6. **Copy your results**:
   - Click inside any text box
   - Press `Ctrl + A` (Windows) or `Command + A` (Mac) to select all
   - Copy and paste into Word, Google Docs, or anywhere else

---

## Part 9: Stopping Your App

When you're done using the app, you should stop it:

1. **Stop the app**:
   - Go back to your terminal window
   - Press `Ctrl + C` (Windows) or `Control + C` (Mac)
   - The app will stop, and you'll see your cursor again

2. **Running it again**:
   - Just run the same command again:
     ```bash
     docker run --env-file .env -p 7860:7860 transcriber
     ```

---

## Troubleshooting

### Problem: "Docker is not running"
- **Solution**: Open Docker Desktop and wait for it to start

### Problem: "Port 7860 is already in use"
- **Solution**: Either the app is already running, or something else is using that port
  - Try going to http://localhost:7860 to see if it's running
  - Or stop all Docker containers and try again:
    ```bash
    docker stop $(docker ps -a)
    ```

### Problem: "Error loading .env file"
- **Solution**: Make sure your `.env` file is:
  - In the same folder as your other project files
  - Named exactly `.env` (not .env.txt or env)
  - Contains your real HuggingFace token

### Problem: "Diarization failed"
- **Solution**: Make sure you accepted the Pyannote model license on HuggingFace
  - Go back to Part 2 and complete step 2

### Problem: "Out of memory"
- **Solution**: Try using a smaller Whisper model:
  - Use "tiny" instead of "base"
  - Try shorter audio files (under 10 minutes)

---

## Next Steps

Now that you have your transcription model running:

- **Try different audio files**: Upload interviews, meetings, podcasts, etc.
- **Experiment with models**: Try `small` or `medium` for better accuracy
- **Share with others**: If you're on the same network, others can access your app too!
- **Keep learning**: Now that you've deployed an AI model, you can do so much more!

---

## Congratulations! 🎊

You've just deployed your very own AI transcription model! That's an amazing accomplishment, especially if this was your first time working with Docker or AI models.

If you get stuck or need help:
- Re-read the section you're stuck on
- Check the Troubleshooting section
- Ask for help from someone who knows a bit about computers

Enjoy your transcription model! 🎉