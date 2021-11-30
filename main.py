import tkinter as tk
import tkinter.ttk as ttk
from ttkthemes import ThemedTk
from tkSliderWidget import Slider
from tkinter.filedialog import asksaveasfile, askopenfilename
import json
import keyboard
import mouse
import random
from pathlib import Path
from scipy.interpolate import interp1d
import numpy as np


def on_change(event):
    for idx, slot in enumerate(slots):
        slot["block"] = blocks[idx].get()

    for i, label in enumerate(label_probs):
        actual = slider_blocks.getValues()
        if i == 0:
            chance = actual[i]
        elif i == 8:
            chance = 100 - actual[i - 1]
        else:
            chance = actual[i] - actual[i - 1]
        label.config(text=f"{chance:.1f} %")

    actual = slider_blocks.getValues()
    chances[actual_idx] = actual

    saveLast()


def select_func(idx):
    global chances
    global old_idx
    global actual_idx

    idx = str(idx)
    actual_idx = idx

    # TODO Interpolate between the two nearest values
    if idx not in chances:
        chances[idx] = [11, 22, 33, 44, 55, 66, 77, 88]

    actual = slider_blocks.getValues()
    slider_blocks.setValues(chances[idx])
    chances[old_idx] = actual
    old_idx = idx

    on_change(None)


def toggle_run():
    on_change(None)
    global running
    global indicator

    if running and indicator:
        indicator.destroy()
    else:
        try:
            max = int(entry_length.get())
        except:
            return

        interpolateHeight()
        indicator = tk.Toplevel(root)
        indicator.overrideredirect(1)
        indicator.title("Random Block Selector")
        indicator.attributes("-topmost", True)
        indicator.geometry("+{}+{}".format(0, 0))

        global w
        w = tk.Scale(indicator, from_=max, to=1)
        up = ttk.Button(indicator, text="up", command=lambda: w.set(w.get() + 1))
        down = ttk.Button(indicator, text="down", command=lambda: w.set(w.get() - 1))

        up.grid(row=0)
        w.grid(row=1)
        down.grid(row=2)

    running = not running


def click():
    if running:
        try:
            max = int(entry_length.get())
        except:
            return
        chances = linfit(w.get() * (100 / max))
        print(chances)
        ran = random.randint(0, 100)

        if ran > 0 and ran < chances[0]:
            keyboard.send("1")
        elif ran >= chances[0] and ran < chances[1]:
            keyboard.send("2")
        elif ran >= chances[1] and ran < chances[2]:
            keyboard.send("3")
        elif ran >= chances[2] and ran < chances[3]:
            keyboard.send("4")
        elif ran >= chances[3] and ran < chances[4]:
            keyboard.send("5")
        elif ran >= chances[4] and ran < chances[5]:
            keyboard.send("6")
        elif ran >= chances[5] and ran < chances[6]:
            keyboard.send("7")
        elif ran >= chances[6] and ran < chances[7]:
            keyboard.send("8")
        elif ran >= chances[7]:
            keyboard.send("9")


def saveMenu():
    on_change(None)
    if entry_save.get() == "":
        name = "untitled"
    else:
        name = entry_save.get()

    file = asksaveasfile(
        initialfile=f"{name}.json",
        defaultextension=".json",
        filetypes=[(".json", "*.json")],
        initialdir="./saves/",
    )
    save(file, name)


def saveLast():
    if entry_save.get() == "":
        name = ""
    else:
        name = entry_save.get()
    fle = Path("last.json")
    fle.touch(exist_ok=True)
    file = open(fle, "w")
    save(file, name)


def save(file, name):
    save_file = {
        "name": name,
        "length": entry_length.get(),
        "slots": slots,
        "gradient": [i["Value"] for i in slider_length.bars],
        "chances": chances,
    }
    json.dump(save_file, file)


def openFile():
    on_change(None)
    f = askopenfilename(
        initialdir="./saves/",
    )
    loadFile(f)


def loadFile(f):
    global chances
    global gradient
    global slots
    global file_name
    global max_length

    with open(f, "r") as j:
        load_file = json.loads(j.read())
        slots = load_file["slots"]
        file_name = load_file["name"]
        max_length = load_file["length"]
        chances = load_file["chances"]
        gradient = load_file["gradient"]
    load()


def load():
    global slider_length
    for slot, block in zip(slots, blocks):
        block.delete(0, "end")
        block.insert(0, slot["block"])
    entry_save.delete(0, "end")
    entry_save.insert(0, file_name)
    entry_length.delete(0, "end")
    entry_length.insert(0, max_length)
    # Creating the slider_length
    slider_length = Slider(
        root,
        width=400,
        height=60,
        min_val=0,
        max_val=100,
        init_lis=gradient,
        show_value=True,
        select_func=select_func,
        slide_func=on_change,
        addable=True,
        removable=True,
    )
    slider_length.grid(row=1, columnspan=5)
    slider_blocks.setValues(chances["0"])
    slider_length.setValues(gradient)


def reset():
    try:
        loadFile("reset.json")
    except Exception as e:
        print(e)
    entry_save.delete(0, "end")
    entry_save.insert(0, file_name)
    entry_length.delete(0, "end")
    entry_length.insert(0, max_length)
    on_change(None)


def interpolateHeight():
    bars_values = [i["Value"] for i in slider_length.bars]
    sorted_values = sorted(bars_values)
    sorted_index = sorted(range(len(bars_values)), key=bars_values.__getitem__)

    # interpolation_array = np.array(
    #     [x for _, x in sorted(zip(sorted_index, chances.values()))]
    # )
    interpolation_array = np.array(
        [[i for i in chances.values()][idx] for idx in sorted_index]
    )

    print(sorted_values)
    print(interpolation_array)

    global linfit
    linfit = interp1d(
        np.hstack((-0.1, np.array(sorted_values), 100.1)),
        np.vstack(
            (interpolation_array[0], interpolation_array, interpolation_array[-1])
        ),
        axis=0,
        kind="cubic",
    )


# Initializing values
old_idx = "0"
actual_idx = "0"
running = False
gradient = [50]
chances = {
    "0": [11, 22, 33, 44, 55, 66, 77, 88],
}
actual_height = 0
blocks = []
label_probs = []

# Creating slots dictionary
slots = [{"slot": i, "block": ""} for i in range(1, 10)]

# Creating the window
outside = ThemedTk(theme="yaru")
outside.title("Random Block Selector")
outside.iconphoto(False, tk.PhotoImage(file="icon.png"))
root = tk.Frame(outside)
root.pack(padx=15, pady=15, fill="both", expand=True)

# Creating reset, save and load menu
ttk.Label(root, text="Save name").grid(column=0, row=0)
entry_save = ttk.Entry(root)
button_save = ttk.Button(root, text="Save", command=saveMenu)
button_load = ttk.Button(root, text="Load", command=openFile)
button_reset = ttk.Button(root, text="Reset", command=reset)
entry_save.grid(column=1, row=0)
button_save.grid(column=4, row=0)
button_load.grid(column=3, row=0)
button_reset.grid(column=2, row=0)

# Creating the slider_length
slider_length = Slider(
    root,
    width=400,
    height=60,
    min_val=0,
    max_val=100,
    init_lis=gradient,
    show_value=True,
    select_func=select_func,
    slide_func=on_change,
    addable=True,
    removable=True,
)
slider_length.grid(row=1, columnspan=5)

# Setting input for Gradient Length
ttk.Label(root, text="Gradient Length").grid(column=0, row=2)
entry_length = ttk.Entry(root)
entry_length.insert(0, "100")

entry_length.grid(column=1, row=2)

# Creating the slider_blocks
slider_blocks = Slider(
    root,
    width=400,
    height=60,
    min_val=0,
    max_val=100,
    init_lis=chances["0"],
    show_value=True,
    select_func=on_change,
    slide_func=on_change,
)
slider_blocks.grid(row=3, columnspan=5)

# Creating blocks
ttk.Label(root, text="Slot").grid(column=0, row=4)
ttk.Label(root, text="Block").grid(column=1, row=4)
ttk.Label(root, text="Probability").grid(column=2, row=4)
for i in range(0, 9):
    ttk.Label(root, text=f"Slot {i+1}").grid(column=0, row=i + 5)
    entry = ttk.Entry(root)

    entry.grid(column=1, row=i + 5)
    blocks.append(entry)

    actual = slider_blocks.getValues()
    if i == 0:
        chance = actual[i]
    elif i == 8:
        chance = 100 - actual[i - 1]
    else:
        chance = actual[i] - actual[i - 1]

    a = ttk.Label(root, text=f"{chance:.1f} %")
    a.grid(column=2, row=i + 5)
    label_probs.append(a)

# Adding Hotkeys
keyboard.add_hotkey("ctrl+shift+a", toggle_run)
keyboard.add_hotkey("ctrl+s", saveMenu)
keyboard.add_hotkey("ctrl+o", openFile)
keyboard.add_hotkey("ctrl+plus", lambda: w.set(w.get() + 1))
keyboard.add_hotkey("ctrl+-", lambda: w.set(w.get() - 1))
mouse.on_button(click, buttons=("right"), types=("up"))

try:
    loadFile("last.json")
except Exception as e:
    print(e)

entry_length.bind("<KeyRelease>", on_change)
for i in blocks:
    i.bind("<KeyRelease>", on_change)

# Loop
root.mainloop()

interpolateHeight()
