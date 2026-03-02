# GDtoGIF
A Py Program That turn your Video in Google Drive into A 5 Sec HD Gif

<h1>GD-TO-GIF</h1>
<p>A Python Program That turn Your GD(Google Drive) 
    Video Into a GIF Using Only the Link</p>

<h2>How Its Work?</h2>
<p>
    When You Insert Your GD File Link
    The Program Takes the first 5 Seconds of your Video then Generate the Gif Using
    <b>FFMpeg</b> And Finally export the ouput into your Download Folder
</p>

<h2>How to use it?</h2>
<h4>Install Python</h4>
<p>You need to Install Python</p>

<h4>Install Dependencies</h4>
<ul>
    <li>Open Your terminal in VSCODE</li>
    <li>run this command</li>
    <p>pip install yt-dlp</p>
</ul>

<h4>Install FFMpeg</h4>
<ul>
    <li>Open your Terminal in VSCODE</li>
    <li>Run this Command</li>
    <p>winget install ffmpeg</p>
</ul>

<h4>Refresh and Run</h4>

<ul>
    <li>Refresh Your Path by Pasting this Command</li>
    <p>$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")</p>
    <li>Run Program</li>
    <p>python gdrive_to_gif.py</p>
</ul>
