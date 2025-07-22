import vlc
import time
import threading
import tkinter as tk
from tkinter import filedialog
import difflib
import platform
import re
import string

def parse_srt_and_expand_gaps(filename, total_video_duration=None):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = re.compile(r'(\d+)\s+(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s+(.+?)(?=\n\n|\Z)', re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for _, start, end, text in matches:
        start_sec = to_seconds(start)
        end_sec = to_seconds(end)
        clean_text = text.replace('\n', ' ').strip()
        subtitles.append({'start': start_sec, 'end': end_sec, 'text': clean_text})

    segments = []
    for i in range(len(subtitles)):
        current = subtitles[i]
        start = current['start']
        end = subtitles[i+1]['start'] if i < len(subtitles)-1 else (total_video_duration if total_video_duration else current['end'])
        segments.append({
            'start': start,
            'end': end,
            'type': 'text',
            'text': current['text']
        })
    return segments

def to_seconds(time_str):
    h, m, rest = time_str.split(':')
    s, ms = rest.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def normalize_text(text):
    translator = str.maketrans('', '', string.punctuation + '¿¡')
    return ' '.join(text.lower().translate(translator).split())

def diff_text(user_input, correct_text):
    diff = difflib.ndiff(correct_text.split(), user_input.split())
    return '\n'.join(diff)

def generate_dynamic_hint(user_input, correct_text):
    hint = ''
    i = 0
    j = 0
    while j < len(correct_text):
        char = correct_text[j]
        if i < len(user_input):
            ## handle correct input
            if user_input[i] == char:
                hint += f"[ok]{user_input[i]}[/ok]"
                i += 1
                j += 1
            ## ignore extra spaces
            elif user_input[i] == ' ' and char != ' ':
                i += 1
                continue
            ## handle if the correct text has a special character but the user didn't input it
            elif not char.isalpha() and char not in "0123456789":
                hint += char
                j += 1
            ## finally, if they are not equal show an error
            else:
                hint += f"[err]{user_input[i]}[/err]"
                i += 1
                j += 1
        else:
            if char.isalpha() or char in "0123456789":
                hint += '_'
            else:
                hint += char
            j += 1
    return hint

class VideoPlayer:
    def __init__(self, parent, video_path):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.video_frame = tk.Frame(parent, width=640, height=360)
        self.video_frame.pack()

        self.parent = parent
        self.video_frame.update()
        self.handle = self.video_frame.winfo_id()

        self.media = self.instance.media_new(video_path)
        self.player.set_media(self.media)

        system = platform.system()
        if system == "Windows":
            self.player.set_hwnd(self.handle)
        elif system == "Linux":
            self.player.set_xwindow(self.handle)
        elif system == "Darwin":
            self.player.set_nsobject(self.handle)
        else:
            raise RuntimeError("Sistema operativo no soportado")

        self.segment_start = None
        self.segment_end = None
        self._check_thread = None
        self.running = False

    def play_segment(self, start, end):
        self.segment_start = start
        self.segment_end = end
        self.player.play()
        time.sleep(0.1)
        self.player.set_time(int(start * 1000))

        if self._check_thread is None or not self._check_thread.is_alive():
            self.running = True
            self._check_thread = threading.Thread(target=self._monitor_segment)
            self._check_thread.start()

    def _monitor_segment(self):
        while self.running:
            current_time = self.player.get_time() / 1000.0
            if current_time >= self.segment_end:
                self.player.pause()
                break
            time.sleep(0.05)

    def repeat_segment(self):
        if self.segment_start is not None and self.segment_end is not None:
            self.play_segment(self.segment_start, self.segment_end)

    def stop(self):
        self.running = False
        self.player.stop()

class App:
    def __init__(self, root):
        self.root = root
        root.title("Entrenamiento interactivo con pistas dinámicas")

        self.video_path = filedialog.askopenfilename(title="Elige el vídeo", filetypes=[("Videos", "*.mp4 *.avi *.mov *.mkv")])
        if not self.video_path:
            print("No se seleccionó vídeo.")
            root.destroy()
            return

        self.srt_path = filedialog.askopenfilename(title="Elige el archivo de subtítulos (.srt)", filetypes=[("Subtítulos", "*.srt")])
        if not self.srt_path:
            print("No se seleccionó subtítulo.")
            root.destroy()
            return

        instance = vlc.Instance()
        media = instance.media_new(self.video_path)
        media.parse()
        total_video_duration = media.get_duration() / 1000.0

        self.segments = parse_srt_and_expand_gaps(self.srt_path, total_video_duration)
        self.current_index = 0

        self.video_player = VideoPlayer(root, self.video_path)

        self.label = tk.Label(root, text="Escribe lo que escuchas (las letras se completan abajo):")
        self.label.pack()

        self.entry = tk.Entry(root, width=80)
        self.entry.pack()
        self.entry.bind("<KeyRelease>", self.update_hint)
        self.entry.bind("<Return>", self.check_input)

        buttons_frame = tk.Frame(root)
        buttons_frame.pack(pady=5)

        self.prev_button = tk.Button(buttons_frame, text="Anterior", command=self.previous_segment)
        self.prev_button.grid(row=0, column=0, padx=5)

        self.repeat_button = tk.Button(buttons_frame, text="Repetir", command=self.repeat_segment)
        self.repeat_button.grid(row=0, column=1, padx=5)

        self.show_answer_button = tk.Button(buttons_frame, text="Mostrar respuesta", command=self.show_answer)
        self.show_answer_button.grid(row=0, column=2, padx=5)

        self.skip_button = tk.Button(buttons_frame, text="Saltar", command=self.skip_segment)
        self.skip_button.grid(row=0, column=3, padx=5)

        self.status = tk.Label(root, text="", fg="blue")
        self.status.pack()

        self.text_widget = tk.Text(root, height=3, font=("Courier", 16))
        self.text_widget.pack()
        self.text_widget.configure(state='disabled')

        self.answer_shown = False

        self.play_current_segment()

    def play_current_segment(self):
        if self.current_index < 0:
            self.current_index = 0

        if self.current_index >= len(self.segments):
            self.status.config(text="¡Completado!", fg="green")
            self.text_widget.configure(state='normal')
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.configure(state='disabled')
            return

        seg = self.segments[self.current_index]
        self.entry.delete(0, tk.END)
        self.status.config(text=f"Fragmento {self.current_index + 1}/{len(self.segments)}", fg="blue")
        self.update_hint()

        self.video_player.play_segment(seg['start'], seg['end'])
        self.answer_shown = False

    def format_hint_for_display(self, hint):
        self.text_widget.configure(state='normal')
        self.text_widget.delete("1.0", tk.END)

        parts = re.split(r'(\[ok\].*?\[/ok\]|\[err\].*?\[/err\])', hint)

        for part in parts:
            if part.startswith("[ok]"):
                self.text_widget.insert(tk.END, part[4:-5], ("ok",))
            elif part.startswith("[err]"):
                self.text_widget.insert(tk.END, part[5:-6], ("err",))
            else:
                self.text_widget.insert(tk.END, part)

        self.text_widget.tag_configure("ok", foreground="black")
        self.text_widget.tag_configure("err", foreground="red")
        self.text_widget.configure(state='disabled')

    def update_hint(self, event=None):
        seg = self.segments[self.current_index]
        correct_text = seg['text']
        user_text = self.entry.get()

        hint = generate_dynamic_hint(user_text, correct_text)
        self.format_hint_for_display(hint)

    def repeat_segment(self):
        self.video_player.repeat_segment()

    def show_answer(self):
        seg = self.segments[self.current_index]
        if self.answer_shown:
            return
        correct_text = seg['text']
        self.text_widget.configure(state='normal')
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, f"Texto correcto:\n{correct_text}\n")
        self.text_widget.configure(state='disabled')
        self.answer_shown = True

    def skip_segment(self):
        self.current_index += 1
        self.play_current_segment()

    def previous_segment(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.play_current_segment()

    def check_input(self, event):
        seg = self.segments[self.current_index]
        correct_text = seg['text']
        user_text = self.entry.get()

        if normalize_text(user_text) == normalize_text(correct_text):
            self.status.config(text="¡Correcto!", fg="green")
            self.current_index += 1
            self.root.after(500, self.play_current_segment)
        else:
            self.status.config(text="No es correcto. Intenta otra vez.", fg="red")
            self.update_hint()
            self.repeat_segment()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
