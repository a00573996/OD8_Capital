# app/splash.py — Splash con barra de progreso determinada (seguro)
import customtkinter as ctk
from PIL import Image
import os

PRIMARY_BLUE = "#2563EB"
TEXT         = "#111827"
TEXT_MUTED   = "#6B7280"
CARD_BG      = "#FFFFFF"
BG           = "#F3F4F6"

class Splash:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.top = ctk.CTkToplevel(root)
        self.top.overrideredirect(True)
        try:
            self.top.attributes("-topmost", True)
        except Exception:
            pass

        w, h = 560, 360
        sw, sh = self.top.winfo_screenwidth(), self.top.winfo_screenheight()
        x, y = (sw - w)//2, int((sh - h)*0.33)
        self.top.geometry(f"{w}x{h}+{x}+{y}")

        outer = ctk.CTkFrame(self.top, fg_color=BG)
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        card = ctk.CTkFrame(outer, fg_color=CARD_BG, corner_radius=14)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        content = ctk.CTkFrame(card, fg_color=CARD_BG)
        content.pack(expand=True)

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "ZAVE LOGO.png")
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            cimg = ctk.CTkImage(img, size=(120, 120))
            ctk.CTkLabel(content, image=cimg, text="").pack(pady=(24, 8))
            self._logo_img = cimg  # evitar GC
        else:
            ctk.CTkLabel(content, text="💰", font=ctk.CTkFont("Segoe UI", 72)).pack(pady=(24, 8))

        ctk.CTkLabel(content, text="ZAVE", text_color=TEXT,
                     font=ctk.CTkFont("Segoe UI Semibold", 28)).pack()
        ctk.CTkLabel(content, text="Organiza tus finanzas — ODS 8",
                     text_color=TEXT_MUTED, font=ctk.CTkFont("Segoe UI", 14)).pack(pady=(4, 16))

        # Barra de progreso determinada (llenado suave)
        self.progress = ctk.CTkProgressBar(content, height=10, corner_radius=6, progress_color=PRIMARY_BLUE)
        self.progress.set(0.0)
        self.progress.pack(fill="x", padx=40, pady=(0, 8))
        self.lbl_status = ctk.CTkLabel(content, text="Cargando…", text_color=TEXT_MUTED,
                                       font=ctk.CTkFont("Segoe UI", 12))
        self.lbl_status.pack(pady=(0, 18))

        # Estado interno de la animación
        self._interval_ms = 20         # ~50 FPS
        self._duration_ms = 1200       # valor por defecto
        self._elapsed_ms  = 0
        self._tick_id     = None
        self._on_done     = None
        self._completed   = False

        self.top.protocol("WM_DELETE_WINDOW", self._on_user_close)

    # API pública
    def run(self, duration_ms: int = 1400, on_done=None):
        self._on_done     = on_done
        self._duration_ms = max(400, int(duration_ms))  # poner mínimo visual
        self._elapsed_ms  = 0
        self.progress.set(0.0)
        self._schedule_tick()

    # Lógica de progreso
    def _schedule_tick(self):
        # seguridad: si la ventana ya no existe, no programes más
        if not (self.top and self.top.winfo_exists()):
            return
        self._tick_id = self.top.after(self._interval_ms, self._tick)

    def _tick(self):
        self._tick_id = None
        if not (self.top and self.top.winfo_exists()):
            return

        self._elapsed_ms += self._interval_ms
        p = min(1.0, self._elapsed_ms / self._duration_ms)
        try:
            self.progress.set(p)
        except Exception:
            pass

        if p >= 1.0:
            self._finish()
        else:
            self._schedule_tick()

    # Cierre/avance seguro
    def _finish(self):
        if self._completed:
            return
        self._completed = True
        self._cancel_tick()
        # destruir splash primero
        self._destroy_only()
        # luego lanzar callback
        if callable(self._on_done):
            self.root.after(0, self._on_done)

    def _on_user_close(self):
        # Si el usuario cierra el splash, procedemos igual al main
        if not self._completed:
            self._completed = True
            self._cancel_tick()
            self._destroy_only()
            if callable(self._on_done):
                self.root.after(0, self._on_done)

    def _cancel_tick(self):
        if self._tick_id is not None:
            try:
                self.top.after_cancel(self._tick_id)
            except Exception:
                pass
            self._tick_id = None

    def _destroy_only(self):
        try:
            self.progress.set(1.0)
        except Exception:
            pass
        try:
            self.top.destroy()
        except Exception:
            pass
