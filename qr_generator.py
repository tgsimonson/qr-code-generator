"""
qr_generator.py

generates a qr code from a user-supplied url and displays it in a
tkinter window titled "img", matching the assignment output layout

usage:
    python qr_generator.py
    python qr_generator.py https://www.bioxsystems.com/
"""

import sys
import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse

import qrcode
from PIL import ImageTk

# qr configuration constants
QR_VERSION = 1              # smallest size, auto-expands via fit=True
QR_BOX_SIZE = 10            # pixels per module
QR_BORDER = 4               # quiet zone width in modules, 4 is the spec minimum
QR_FILL_COLOR = "black"
QR_BACK_COLOR = "white"
DEFAULT_URL = "https://www.bioxsystems.com/"
OUTPUT_FILE = "qrcode.png"


def is_valid_url(candidate):
    """
    returns true if the candidate string parses as an http or https url
    with a network location present
    """
    try:
        parsed = urlparse(candidate)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def build_qr_image(url):
    """
    builds a pil image containing the qr code encoding the given url
    error correction level m tolerates about 15 percent damage
    """
    qr = qrcode.QRCode(
        version=QR_VERSION,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=QR_BOX_SIZE,
        border=QR_BORDER,
    )
    qr.add_data(url)
    qr.make(fit=True)
    wrapper = qr.make_image(fill_color=QR_FILL_COLOR, back_color=QR_BACK_COLOR)

    # the library returns a 1-bit image, which some viewers and document
    # renderers handle poorly, so convert to rgb before returning
    return wrapper.get_image().convert("RGB")


def save_qr_image(image, path=OUTPUT_FILE):
    """
    writes the qr image to disk and returns the path written
    """
    image.save(path)
    return path


def display_qr_image(image, window_title="img"):
    """
    renders the qr image in a tkinter window
    the photoimage reference is bound to the label to prevent garbage collection
    """
    root = tk.Tk()
    root.title(window_title)
    root.configure(bg="white")

    photo = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=photo, bg="white", borderwidth=20, relief="flat")
    label.image = photo
    label.pack(padx=10, pady=10)

    # close on escape in addition to the window close button
    root.bind("<Escape>", lambda event: root.destroy())

    root.resizable(False, False)
    root.mainloop()


def prompt_for_url():
    """
    reads a url from the console, falling back to the default if the
    user submits an empty line
    """
    entered = input(f"enter a url [{DEFAULT_URL}]: ").strip()
    return entered if entered else DEFAULT_URL


def main():
    # accept the url as a command line argument or prompt for it
    url = sys.argv[1].strip() if len(sys.argv) > 1 else prompt_for_url()

    if not is_valid_url(url):
        message = f"invalid url: {url}\nurls must begin with http:// or https://"
        print(message)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Invalid URL", message)
            root.destroy()
        except tk.TclError:
            pass
        sys.exit(1)

    image = build_qr_image(url)
    saved_path = save_qr_image(image)
    print(f"qr code generated for {url}")
    print(f"saved to {saved_path}")

    display_qr_image(image)


if __name__ == "__main__":
    main()
