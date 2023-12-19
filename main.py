import cv2
import numpy as np
import webcolors
import tkinter as tk
from tkinter import filedialog
import scipy
from scipy.spatial import KDTree

class WarnaDominan:
    def __init__(self, img, pilihDominan=5):
        self.img = cv2.imread(img)
        self.img_bar = None
        self.nilai_rgb = []
        self.pilihDominan = pilihDominan
        self.tinggi, self.lebar, _ = self.img.shape
        self.data = np.float32(np.reshape(self.img, (self.tinggi * self.lebar, 3)))
        self.namaWarna, self.namaWarna2 = [], []

        self.dapatkanDominanWarna()

    def dapatkanDominanWarna(self):
        self._tampilGambar()

    def _buatBar(self, tinggi, lebar, warna):
        bar = np.zeros((tinggi, lebar, 3), np.uint8)
        bar[:] = warna
        red, green, blue = int(warna[2]), int(warna[1]), int(warna[0])
        return bar, (red, green, blue)

    def _opsiBeda(self):
        css3_db = webcolors.CSS3_HEX_TO_NAMES
        nama = []
        nilai_rgb = []

        for warna_hex, nama_warna in css3_db.items():
            nama.append(nama_warna)
            nilai_rgb.append(webcolors.hex_to_rgb(warna_hex))

        kdt_db = KDTree(nilai_rgb)
        jarak, index = kdt_db.query((254,0,0))
        print(f"Nilai yang mendekati: {nama[index]}")

    def _tampilGambar(self):
        kriteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        tanda = cv2.KMEANS_RANDOM_CENTERS
        kepadatan, labels, pusat = cv2.kmeans(self.data, self.pilihDominan, None, kriteria, 10, tanda)

        font = cv2.FONT_HERSHEY_SIMPLEX
        bars = []

        for index, baris in enumerate(pusat):
            bar, rgb = self._buatBar(200, 200, baris)
            bars.append(bar)
            self.nilai_rgb.append(rgb)

        beda = {}
        nama = []
        nilai_rgb= []
        for nilai_warna in self.nilai_rgb:
            for hex_warna, nama_warna in webcolors.CSS3_HEX_TO_NAMES.items():
                r, g, b = webcolors.hex_to_rgb(hex_warna)
                beda[sum([  (r - nilai_warna[0]) ** 2,
                            (g - nilai_warna[1]) ** 2, 
                            (b - nilai_warna[2]) ** 2]  )] = nama_warna
                # print(beda)
                # =============
                nama.append(nama_warna)
                nilai_rgb.append(webcolors.hex_to_rgb(hex_warna))

            kdt_db = KDTree(nilai_rgb)
            jarak, index = kdt_db.query(nilai_warna)
            self.namaWarna.append(beda[min(beda.keys())])
            self.namaWarna2.append(nama[index])

        self.img_bar = np.hstack(bars)

        for index, baris in enumerate(self.nilai_rgb):
            cv2.putText(self.img_bar, f'{self.namaWarna2[index]}', (5 + 200 * index, 100 - 10),
                                font, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

            cv2.putText(self.img_bar, f'RGB: {baris}', (5 + 200 * index, 200 - 10),
                                font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            # print(f'{index + 1}. RGB{baris} - {self.namaWarna}')
        cv2.imshow('Gambar', self.img)
        cv2.imshow('Warna Dominan', self.img_bar)
        cv2.waitKey(0)

class WarnaDominanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Warna Dominan App")

        self.image_path = ""
        self.pilih_warna_dominan = 0

        browse_button = tk.Button(root, text="Browse Image", command=self.pilih_gambar)
        browse_button.pack(pady=10)

        warna_label = tk.Label(root, text="Pilih Warna Dominan:")
        warna_label.pack(pady=5)

        self.entry_warna = tk.Entry(root)
        self.entry_warna.insert(0, "5")
        self.entry_warna.pack(pady=5)

        analyze_button = tk.Button(root, text="Analyze Dominant Colors", command=self.analisis_warna)
        analyze_button.pack(pady=10)

    def pilih_gambar(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path = file_path

    def analisis_warna(self):
        self.pilih_warna_dominan = int(self.entry_warna.get())
        if self.image_path:
            warna_dominan = WarnaDominan(self.image_path, self.pilih_warna_dominan)
            cv2.destroyAllWindows()  # Menutup jendela sebelumnya
        else:
            print("Pilih gambar terlebih dahulu.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("%dx%d" % (root.winfo_screenwidth(), root.winfo_screenheight()))
    app = WarnaDominanApp(root)
    root.mainloop()
