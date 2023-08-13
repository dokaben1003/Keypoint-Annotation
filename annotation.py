import tkinter as tk
from PIL import ImageTk, Image
from tkinter import filedialog
import os
import time
import sys

def resource_path(relative_path):
    """実行可能ファイルのリソースパスを解決する関数"""
    try:
        # PyInstallerで実行されている場合
        base_path = sys._MEIPASS
    except AttributeError:
        # 通常のPython実行時の場合
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ImageDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Key Point Annotation")
        self.root.configure(bg="#F0F0F0")  # 背景色を設定
        self.image_path = None
        self.text_path = None
        self.canvas = None
        self.circle = None
        self.scale = 1.0
        self.clicked_x = 0
        self.clicked_y = 0
        self.star_count = 0
        self.points = []

        # フレームを作成して中央に配置
        button_frame = tk.Frame(self.root, bg="#F0F0F0")
        button_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        button_frame.pack(expand=True, pady=100)

        # ボタンのスタイルを設定
        button_style = {
            "font": ("Helvetica", 10),
            "width": 20,
            "height": 1,
            "bg": "#555555",
            "fg": "#FFFFFF",
            "bd": 0,  # ボーダーを削除
            "highlightthickness": 0,  # ハイライトを削除
            "borderwidth": 0,  # ボーダーを削除（macOS用）
            "highlightbackground": "#F0F0F0"  # 背景色を設定（macOS用）
        }

        # 「Open Image」ボタンをフレーム内で横に並べ、中央に配置します
        self.open_button = tk.Button(button_frame, text="Open Image", command=self.open_image, **button_style)
        self.open_button.pack(side=tk.LEFT, padx=20, pady=10)

        # 「Exit」ボタンをフレーム内で横に並べ、中央に配置します
        self.exit_button = tk.Button(button_frame, text="Exit", command=self.quit, **button_style)
        self.exit_button.pack(side=tk.LEFT, padx=20, pady=10)

        # クリックした座標を表示するためのLabelウィジェットを作成
        self.coordinates_label = tk.Label(self.root, text="", font=("Helvetica", 14), bg="#F0F0F0")
        self.coordinates_label.pack(anchor=tk.NW, padx=10, pady=0)

        # ★の数を表示するためのLabelウィジェットを作成
        self.star_count_label = tk.Label(self.root, text="", font=("Helvetica", 14), bg="#F0F0F0")
        self.star_count_label.pack(anchor=tk.NW, padx=10, pady=0)

        
        # 標準のウィンドウフレームを復元
        self.root.overrideredirect(False)

        self.canvas_width = None
        self.canvas_height = None

        # ボタン4およびボタン5のイベントをバインド
        self.root.bind("<Button-4>", self.scroll_up)
        self.root.bind("<Button-5>", self.scroll_down)


    def open_image(self):
        self.start_time = time.time()
        file_path = filedialog.askopenfilename(
            filetypes=[("Image file", ".bmp .png .jpg .tif"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"),
                       ("Tiff", ".tif")])

        if self.image_path == None:
            txt_path = resource_path(file_path).split(".")[0] + ".txt"
            with open(txt_path, 'w') as f:
                pass

        if file_path:
            self.image_path = resource_path(file_path)
            self.display_image()


    def save_coordinates(self, event):
        clicked_x = (event.x + self.canvas.canvasx(0)) / self.scale
        clicked_y = (event.y + self.canvas.canvasy(0)) / self.scale

        # ★の数をカウントして表示
        self.star_count += 1
        self.star_count_label.config(text=f"★ Count: {self.star_count}")
        
        # クリックされた座標を表示
        self.coordinates_label.config(text=f"Clicked coordinates: (x, y) = ({clicked_x:.2f}, {clicked_y:.2f})")
        
        pos_str = "(x,y)=(" + str(clicked_x) + "," + str(clicked_y) + ")"
        txt_path = self.image_path.split(".")[0] + ".txt"
        with open(txt_path, "a") as f:
            f.write(pos_str + "\n")

        # ★の数が0の場合は表示しない
        if self.star_count == 0:
            self.star_count_label.pack_forget()
        else:
            self.star_count_label.pack(anchor=tk.NW, padx=20, pady=10)

        
        # クリックされた座標を示す円を作成
        self.points.append((clicked_x, clicked_y))
        self.draw_points()


    def draw_points(self):
        self.canvas.delete("points")
        for point in self.points:
            x, y = point
            x = x * self.scale
            y = y * self.scale
            self.canvas.create_text(x, y, text="★", fill="green", tags="points")

    def display_image(self):
        if self.canvas:
            self.canvas.destroy()  # 既存のキャンバスを破棄

        image = Image.open(self.image_path)

        # 画面サイズを取得
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # キャンバスの幅と高さを設定
        self.canvas_width = screen_width
        self.canvas_height = screen_height


        # 画像を表示するためのウィジェットを作成
        image_tk = ImageTk.PhotoImage(image=image)

        # Scrollbarを追加
        v_scrollbar = tk.Scrollbar(self.root, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvasの作成
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height,
                                scrollregion=(0, 0, image.width, image.height),
                                yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーとCanvasを連動させる
        v_scrollbar.config(command=self.canvas.yview)
        h_scrollbar.config(command=self.canvas.xview)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
        self.canvas.image = image_tk

        # クリックイベントをキャンバスにバインド
        self.canvas.bind("<Button-1>", self.save_coordinates)

        # ボタン4およびボタン5のイベントをバインド
        self.root.bind("<Button-4>", self.scroll_up)
        self.root.bind("<Button-5>", self.scroll_down)


        # イベントループ
        self.root.mainloop()

    def quit(self):
        self.root.destroy()

    def scroll_up(self, event):
        self.canvas.yview_scroll(-1, "units")

    def scroll_down(self, event):
        self.canvas.yview_scroll(1, "units")


if __name__ == "__main__":
    image_display = ImageDisplay()
    image_display.root.mainloop()
