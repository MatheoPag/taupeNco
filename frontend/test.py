import tkinter as tk

# Liste de nombreux curseurs Tkinter/Tk
# Certains peuvent ne pas exister selon l'OS
CURSORS = [
    "arrow",
    "based_arrow_down",
    "based_arrow_up",
    "boat",
    "bogosity",
    "bottom_left_corner",
    "bottom_right_corner",
    "bottom_side",
    "bottom_tee",
    "box_spiral",
    "center_ptr",
    "circle",
    "clock",
    "coffee_mug",
    "cross",
    "cross_reverse",
    "crosshair",
    "diamond_cross",
    "dot",
    "dotbox",
    "double_arrow",
    "draft_large",
    "draft_small",
    "draped_box",
    "exchange",
    "fleur",
    "gobbler",
    "gumby",
    "hand1",
    "hand2",
    "heart",
    "icon",
    "iron_cross",
    "left_ptr",
    "left_side",
    "left_tee",
    "leftbutton",
    "ll_angle",
    "lr_angle",
    "man",
    "middlebutton",
    "mouse",
    "pencil",
    "pirate",
    "plus",
    "question_arrow",
    "right_ptr",
    "right_side",
    "right_tee",
    "rightbutton",
    "rtl_logo",
    "sailboat",
    "sb_down_arrow",
    "sb_h_double_arrow",
    "sb_left_arrow",
    "sb_right_arrow",
    "sb_up_arrow",
    "sb_v_double_arrow",
    "shuttle",
    "sizing",
    "spider",
    "spraycan",
    "star",
    "target",
    "tcross",
    "top_left_arrow",
    "top_left_corner",
    "top_right_corner",
    "top_side",
    "top_tee",
    "trek",
    "ul_angle",
    "umbrella",
    "ur_angle",
    "watch",
    "xterm",
]

root = tk.Tk()
root.title("Tous les curseurs Tkinter")
root.geometry("900x700")

canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

frame = tk.Frame(canvas)

frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

title = tk.Label(
    frame,
    text="Survole chaque bouton pour tester le curseur",
    font=("Arial", 16, "bold"),
    pady=20
)
title.pack()

for cursor_name in CURSORS:

    try:
        btn = tk.Button(
            frame,
            text=cursor_name,
            width=30,
            height=2,
            cursor=cursor_name
        )
        btn.pack(pady=4)

    except tk.TclError:
        # Certains curseurs ne sont pas supportés selon le système
        lbl = tk.Label(
            frame,
            text=f"{cursor_name} ❌ non supporté",
            fg="red"
        )
        lbl.pack()

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

root.mainloop()