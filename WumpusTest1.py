import tkinter as tk
import random

GRID_SIZE = 4

# ----- World creation -----
def make_cell():
    return {"pit": False, "wumpus": False, "gold": False, 
            "breeze": False, "stench": False}

world = [[make_cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def reset_game():
    global world, agent

    # Recreate world
    world = [[make_cell() for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    place_objects()

    # Recreate percepts
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if world[i][j]["pit"]:
                for nx, ny in neighbors(i, j):
                    world[nx][ny]["breeze"] = True
            if world[i][j]["wumpus"]:
                for nx, ny in neighbors(i, j):
                    world[nx][ny]["stench"] = True

    # Reset agent
    agent = {
        "x": 0,
        "y": 0,
        "alive": True,
        "has_gold": False,
        "arrow": True
    }

    status.set("🔄 Game restarted! Use Arrow Keys to move, WASD to shoot")
    draw_grid()

def neighbors(x, y):
    return [(i,j) for i,j in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
            if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE]

def place_objects():
    # pits
    for _ in range(3):
        while True:
            x,y = random.randint(0,3), random.randint(0,3)
            if (x,y) != (0,0) and not world[x][y]["pit"]:
                world[x][y]["pit"] = True
                break
    # wumpus
    while True:
        x,y = random.randint(0,3), random.randint(0,3)
        if (x,y) != (0,0) and not world[x][y]["pit"]:
            world[x][y]["wumpus"] = True
            break
    # gold
    while True:
        x,y = random.randint(0,3), random.randint(0,3)
        if (x,y) != (0,0) and not world[x][y]["pit"] and not world[x][y]["wumpus"]:
            world[x][y]["gold"] = True
            break

place_objects()

for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        if world[i][j]["pit"]:
            for nx,ny in neighbors(i,j):
                world[nx][ny]["breeze"] = True
        if world[i][j]["wumpus"]:
            for nx,ny in neighbors(i,j):
                world[nx][ny]["stench"] = True

agent = {"x": 0, "y": 0, "alive": True, "has_gold": False, "arrow": True}

# ----- GUI Setup -----
root = tk.Tk()
root.title("Wumpus World")

status = tk.StringVar()
status.set("Use Arrow Keys to move, WASD to shoot")

grid_frame = tk.Frame(root)
grid_frame.pack()

cells = [[None]*GRID_SIZE for _ in range(GRID_SIZE)]

restart_btn = tk.Button(
    root,
    text="🔄 Restart Game",
    font=("Comic Sans MS", 16, "bold"),
    bg="orange",
    fg="black",
    width=15,
    command=reset_game
)
restart_btn.pack(pady=10)

def draw_grid():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            text = ""
            color = "purple"

            if agent["x"] == i and agent["y"] == j:
                text = "🤖"
                color = "lavender"

            # Increase width, height, and font size for bigger cells
            lbl = tk.Label(
                grid_frame, 
                text=text, 
                width=8,        # increase width
                height=4,        # increase height
                bg=color, 
                font=("Arial", 24, "bold"),  # increase font size
                relief="ridge"
            )
            lbl.grid(row=i, column=j, padx=2, pady=2)  # increase spacing
            cells[i][j] = lbl


def perceive():
    p = []
    c = world[agent["x"]][agent["y"]]
    if c["breeze"]: p.append("Breeze")
    if c["stench"]: p.append("Stench")
    if c["gold"]: p.append("Glitter")
    return p

def animate_status(text, index=0):
    if index <= len(text):
        status.set(text[:index])
        root.after(50, lambda: animate_status(text, index + 1))

def animate_arrow(dx, dy, x=None, y=None):
    if x is None and y is None:
        x, y = agent["x"], agent["y"]

    # Stop if arrow leaves the grid
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
        status.set("❌ *Sorry buddy* 😞 You missed the shot! Better luck next time")
        return

    # Save current cell text & background
    current_text = cells[x][y]["text"]
    current_bg = cells[x][y]["bg"]

    # Arrow emoji based on direction
    arrow_char = "➡️" if dy == 1 else "⬅️" if dy == -1 else "⬆️" if dx == -1 else "⬇️"
    cells[x][y].config(text=arrow_char, bg="yellow")

    # HIT WUMPUS
    if world[x][y]["wumpus"] is True:
        world[x][y]["wumpus"] = False  # remove Wumpus
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                world[i][j]["stench"] = False

        # Arrow keeps moving for a short trail effect
        def kill_animation(step=0, max_steps=2):
            # Mark the current cell with kill effect for first step
            if step == 0:
                cells[x][y].config(text="💀", bg="red")
                status.set("🎯 *Great Warrior* ⚔️ You killed the Wumpus! Now find the gold.")
            elif step <= max_steps:
                # Move arrow visually even after killing
                nx, ny = x + dx*step, y + dy*step
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    prev_text = cells[nx][ny]["text"]
                    prev_bg = cells[nx][ny]["bg"]
                    cells[nx][ny].config(text=arrow_char, bg="yellow")
                    # restore previous cell after delay
                    root.after(150, lambda: cells[nx][ny].config(text=prev_text, bg=prev_bg))
                    root.after(150, lambda: kill_animation(step+1, max_steps))
            else:
                draw_grid()  # finally redraw grid to remove Wumpus
                return

        kill_animation()
        return

    # NORMAL arrow movement
    def restore():
        cells[x][y].config(text=current_text, bg=current_bg)
        animate_arrow(dx, dy, x + dx, y + dy)

    root.after(150, restore)

def reveal_all_animation():
    def reveal_cell(i=0, j=0):
        if i >= GRID_SIZE:
            return
        cell = world[i][j]
        text = ""
        color = "cyan"
        if cell["pit"]:
            text = "🕳"
        elif cell["wumpus"]:
            text = "👹"
        elif cell["gold"]:
            text = "💰"
        cells[i][j].config(text=text, bg=color)
        if j + 1 < GRID_SIZE:
            root.after(100, lambda: reveal_cell(i, j + 1))
        else:
            root.after(100, lambda: reveal_cell(i + 1, 0))
    reveal_cell()

def game_over_animation(color1, color2, flashes=6, delay=300):
    def flash(count):
        if count == 0:
            return
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                cells[i][j].config(
                    bg=color1 if count % 2 == 0 else color2
                )
        root.after(delay, lambda: flash(count - 1))
    flash(flashes)

def check_status():
    c = world[agent["x"]][agent["y"]]

    if c["pit"]:
        agent["alive"] = False
        animate_status("💀 You’re lost in the pit forever! Your adventure ends here… 💀")
        game_over_animation("blue", "green")
        # Delay the reveal until after the game over animation
        root.after(6*300, reveal_all_animation)  # 6 flashes * 300ms

    elif c["wumpus"] is True:
        agent["alive"] = False
        animate_status("👹 The Wumpus claims its prey! Game over, brave soul ** 👹")
        game_over_animation("red", "black")
        root.after(6*300, reveal_all_animation)

    elif c["gold"]:
        agent["has_gold"] = True
        c["gold"] = False
        animate_status("🏆 Treasure secured! You’re the hero of the dungeon! 🏆")
        game_over_animation("gold", "white")
        root.after(6*300, reveal_all_animation)

    else:
        p = perceive()
        status.set("Percepts: " + (", ".join(p) if p else "None"))



def move(dx, dy):
    if not agent["alive"] or agent["has_gold"]:
        return
    nx,ny = agent["x"]+dx, agent["y"]+dy
    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
        agent["x"], agent["y"] = nx,ny
        check_status()
        draw_grid()

def shoot(dx, dy):
    if not agent["arrow"]:
        status.set("No arrow left!")
        return

    agent["arrow"] = False  # only one arrow
    # start the arrow animation
    animate_arrow(dx, dy)

# ----- Keyboard Controls -----
root.bind("<Up>", lambda e: move(-1,0))
root.bind("<Down>", lambda e: move(1,0))
root.bind("<Left>", lambda e: move(0,-1))
root.bind("<Right>", lambda e: move(0,1))

root.bind("w", lambda e: shoot(-1,0))
root.bind("s", lambda e: shoot(1,0))
root.bind("a", lambda e: shoot(0,-1))
root.bind("d", lambda e: shoot(0,1))

tk.Label(
    root,
    textvariable=status,
    font=("Comic Sans MS", 20, "bold"),
    wraplength=600,
    justify="center"
).pack(pady=10)

draw_grid()
root.mainloop()

