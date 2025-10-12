# app/start.py — Arranque con splash y luego menú principal
import customtkinter as ctk
from app.splash import Splash
from app.main import open_main_menu

def run_splash_then():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    root = ctk.CTk()
    root.withdraw()  # root oculto durante el splash

    splash = Splash(root)

    def _launch_main():
        # Abre el menú principal como Toplevel sobre el mismo root
        open_main_menu(root)

    splash.run(duration_ms=1000, on_done=_launch_main)
    root.mainloop()

if __name__ == "__main__":
    run_splash_then()
