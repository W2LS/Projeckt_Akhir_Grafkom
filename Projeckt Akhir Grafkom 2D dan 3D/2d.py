from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys
import math
from OpenGL.GL import *


pygame.font.init()
font = pygame.font.SysFont("Arial", 16)

def draw_ui():
    info_lines = [
        "[1] Titik   [2] Garis   [3] Kotak   [4] Ellipse",
        "[R] Merah   [G] Hijau   [B] Biru",
        "[+/-] Ketebalan Garis",
        "[T] Translate  [Y] Rotate  [U] Scale",
        "[Q] Set Window   [WASD] Geser Window",
        "[BACKSPACE] Refresh Window",
        "[C] Cancel Transform",
        "[DEL] Hapus Semua Objek",
        "[ESC] Keluar"
    ]

    # Tambahkan status aktif
    shape_label = {
        "point": "Titik",
        "line": "Garis",
        "rect": "Kotak",
        "ellipse": "Ellipse"
    }.get(current_shape, "???")

    transform_label = {
        None: "Normal",
        "translate": "Translate",
        "rotate": "Rotate",
        "scale": "Scale"
    }.get(transform_mode, "???")

    color_name = (
        "Merah" if current_color == [1.0, 0.0, 0.0]
        else "Hijau" if current_color == [0.0, 1.0, 0.0]
        else "Biru" if current_color == [0.0, 0.0, 1.0]
        else f"{current_color}"
    )

    status_line = f"Bentuk: {shape_label}  |  Warna: {color_name}  |  Mode: {transform_label}  |  Ketebalan: {line_width}"
    info_lines.append("-" * 40)
    info_lines.append(status_line)

    # Buat surface teks
    ui_surface = pygame.Surface((400, len(info_lines) * 20), pygame.SRCALPHA)
    ui_surface.fill((0, 0, 0, 100))  # latar semi-transparan

    for i, line in enumerate(info_lines):
        text = font.render(line, True, (255, 255, 255))
        ui_surface.blit(text, (5, i * 20))

    # Konversi surface jadi array & flip secara vertikal
    data = pygame.image.tostring(ui_surface, "RGBA", True)
    width, height = ui_surface.get_size()

    glWindowPos2f(10, 580 - height)
    glDrawPixels(width, height, GL_RGBA, GL_UNSIGNED_BYTE, data)



# Data objek yang digambar
objects = []

# Pengaturan objek aktif
current_shape = "point"              # point, line, rect, ellipse
current_color = [1.0, 0.0, 0.0]      # warna default merah
line_width = 2

# Window untuk clipping
window_start = None
window_end = None

# Kode Cohen-Sutherland
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

# Mode transformasi
transform_mode = None
selected_object = None

# --- Variabel klik & tahan untuk semua bentuk ---
drawing_shape = False               # sedang menggambar?
start_point = None                  # titik awal klik mouse
temp_object = None                  # objek sementara (preview)


def is_point_near_line(px, py, x1, y1, x2, y2, threshold):
    if x1 == x2 and y1 == y2:
        return math.hypot(px - x1, py - y1) < threshold

    line_mag = math.hypot(x2 - x1, y2 - y1)
    if line_mag == 0:
        return False
    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
    if u < 0 or u > 1:
        return False

    ix = x1 + u * (x2 - x1)
    iy = y1 + u * (y2 - y1)
    dist = math.hypot(px - ix, py - iy)
    return dist < threshold



# algoritma Cohen-Sutherland
def compute_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin: code |= LEFT
    elif x > xmax: code |= RIGHT
    if y < ymin: code |= BOTTOM
    elif y > ymax: code |= TOP
    return code


# memotong garis yang berada sebagian di luar jendela clipping 
def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)
    accept = False

    while True:
        if code1 == 0 and code2 == 0:
            accept = True
            break
        elif (code1 & code2) != 0:
            break
        else:
            x, y = 0, 0
            outcode = code1 if code1 else code2

            if outcode & TOP:
                x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
                y = ymax
            elif outcode & BOTTOM:
                x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
                y = ymin
            elif outcode & RIGHT:
                y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
                x = xmax
            elif outcode & LEFT:
                y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
                x = xmin

            if outcode == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1, xmin, ymin, xmax, ymax)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2, xmin, ymin, xmax, ymax)

    if accept:
        return (x1, y1, x2, y2)
    else:
        return None

def is_inside_window(x, y, xmin, ymin, xmax, ymax):
    return xmin <= x <= xmax and ymin <= y <= ymax


# translasi atau pergeseran posisi objek berdasarkan jarak dx dan dy.
def translate(points, dx, dy, obj_type=None):
    if obj_type == "ellipse":
        # format: [(cx, cy, rx, ry), list_of_points]
        cx, cy, rx, ry = points[0]
        new_center = (cx + dx, cy + dy, rx, ry)
        moved_points = [(x + dx, y + dy) for x, y in points[1]]
        return [new_center, moved_points]
    else:
        return [(x + dx, y + dy) for x, y in points]


# Rotasi objek berdasarkan sudut tertentu (dalam derajat) terhadap titik pusat origin.
def rotate(points, angle_deg, origin, obj_type=None):
    angle_rad = math.radians(angle_deg)
    ox, oy = origin

    if obj_type == "ellipse":
        center, ellipse_pts = points
        rotated_pts = []
        for x, y in ellipse_pts:
            dx, dy = x - ox, y - oy
            rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            rotated_pts.append((ox + rx, oy + ry))
        return [center, rotated_pts]

    else:
        rotated = []
        for x, y in points:
            dx, dy = x - ox, y - oy
            rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            rotated.append((ox + rx, oy + ry))
        return rotated


# Fungsi untuk menskalakan objek berdasarkan faktor skala sx dan sy terhadap titik origin.
# Jika obj_type adalah "ellipse", maka akan mengubah radius elips.
def scale(points, sx, sy, origin, obj_type=None):
    if obj_type == "ellipse":
        cx, cy, rx, ry = points[0]  # pusat elips & radius
        new_rx = rx * sx
        new_ry = ry * sy

        scaled_points = []
        for i in range(360):
            theta = math.radians(i)
            x = cx + new_rx * math.cos(theta)
            y = cy + new_ry * math.sin(theta)
            scaled_points.append((x, y))

        new_center = (cx, cy, new_rx, new_ry)
        return [new_center, scaled_points]

    else:
        ox, oy = origin
        return [(ox + (x - ox) * sx, oy + (y - oy) * sy) for x, y in points]

# Fungsi ini digunakan untuk mendeteksi objek mana yang diklik oleh pengguna.
def get_clicked_object(x, y, threshold=6):
    for i, (obj_type, points, color) in enumerate(objects):
        if obj_type == "point":
            px, py = points[0]
            if abs(x - px) <= threshold and abs(y - py) <= threshold:
                return i

        elif obj_type == "line":
            x1, y1 = points[0]
            x2, y2 = points[1]
            if is_point_near_line(x, y, x1, y1, x2, y2, threshold):
                return i

        elif obj_type == "rect":
            # Periksa apakah klik dekat ke sisi kotak (4 sisi)
            for j in range(len(points)):
                x1, y1 = points[j]
                x2, y2 = points[(j + 1) % len(points)]
                if is_point_near_line(x, y, x1, y1, x2, y2, threshold):
                    return i

        elif obj_type == "ellipse":
            for px, py in points[1]:  # akses ke titik-titik elips
                if math.hypot(x - px, y - py) <= threshold:
                    return i

    return None


def draw_all_objects():
    glLineWidth(line_width)

    has_window = window_start is not None and window_end is not None
    if has_window:
        xmin = min(window_start[0], window_end[0])
        xmax = max(window_start[0], window_end[0])
        ymin = min(window_start[1], window_end[1])
        ymax = max(window_start[1], window_end[1])

    for obj in objects:
        obj_type, points, color = obj
        is_selected = (selected_object is not None and objects[selected_object] == obj)

        # --- Gambar objek utama seperti biasa ---
        if obj_type == "point":
            x, y = points[0]
            if has_window and is_inside_window(x, y, xmin, ymin, xmax, ymax):
                glColor3f(0.0, 1.0, 0.0)
            elif has_window:
                continue
            else:
                glColor3fv(color)

            glPointSize(line_width)
            glBegin(GL_POINTS)
            glVertex2f(x, y)
            glEnd()
            glPointSize(1)

        elif obj_type == "line":
            if has_window:
                clip = cohen_sutherland_clip(*points[0], *points[1], xmin, ymin, xmax, ymax)
                if clip:
                    glColor3f(0.0, 1.0, 0.0) if (
                        is_inside_window(points[0][0], points[0][1], xmin, ymin, xmax, ymax) and
                        is_inside_window(points[1][0], points[1][1], xmin, ymin, xmax, ymax)
                    ) else glColor3fv(color)
                    glBegin(GL_LINES)
                    glVertex2f(clip[0], clip[1])
                    glVertex2f(clip[2], clip[3])
                    glEnd()
            else:
                glColor3fv(color)
                glBegin(GL_LINES)
                glVertex2fv(points[0])
                glVertex2fv(points[1])
                glEnd()

        elif obj_type == "rect":
            if has_window:
                clipped_edges = []
                for i in range(len(points)):
                    x1, y1 = points[i]
                    x2, y2 = points[(i + 1) % len(points)]
                    clip = cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
                    if clip:
                        clipped_edges.append(clip)

                if not clipped_edges:
                    continue  # Tidak ada sisi yang terlihat, lewati

                # Warna: hijau jika semua titik asli ada dalam window
                inside_count = sum(1 for px, py in points if is_inside_window(px, py, xmin, ymin, xmax, ymax))
                glColor3f(0.0, 1.0, 0.0) if inside_count == len(points) else glColor3fv(color)

                # Gambar sisi yang lolos clipping
                for edge in clipped_edges:
                    glBegin(GL_LINES)
                    glVertex2f(edge[0], edge[1])
                    glVertex2f(edge[2], edge[3])
                    glEnd()
            else:
                glColor3fv(color)
                glBegin(GL_LINE_LOOP)
                for p in points:
                    glVertex2f(p[0], p[1])
                glEnd()


        elif obj_type == "ellipse":
            if isinstance(points[0], tuple) and len(points[0]) == 4:
                ellipse_points = points[1]
            else:
                ellipse_points = points

            if has_window:
                # Pisahkan kurva ke beberapa segmen yang masih masuk window
                segments = []
                current_segment = []

                for x, y in ellipse_points:
                    if is_inside_window(x, y, xmin, ymin, xmax, ymax):
                        current_segment.append((x, y))
                    else:
                        if current_segment:
                            segments.append(current_segment)
                            current_segment = []
                if current_segment:
                    segments.append(current_segment)

                if not segments:
                    continue  # semua titik di luar window

                # Warna hijau jika semua titik masuk
                total_visible = sum(len(seg) for seg in segments)
                is_fully_inside = total_visible == len(ellipse_points)
                glColor3f(0.0, 1.0, 0.0) if is_fully_inside else glColor3fv(color)

                glLineWidth(line_width)
                for segment in segments:
                    if len(segment) >= 2:
                        glBegin(GL_LINE_STRIP)
                        for x, y in segment:
                            glVertex2f(x, y)
                        glEnd()
            else:
                glColor3fv(color)
                glLineWidth(line_width)
                glBegin(GL_LINE_LOOP)
                for x, y in ellipse_points:
                    glVertex2f(x, y)
                glEnd()







        # --- Tambahkan Highlight untuk objek terpilih ---
        if is_selected:
            glColor3f(1.0, 1.0, 0.0)  # Kuning
            glLineWidth(2)
            if obj_type == "point":
                glPointSize(line_width + 4)
                glBegin(GL_POINTS)
                glVertex2f(points[0][0], points[0][1])
                glEnd()
                glPointSize(1)
            elif obj_type == "line":
                glBegin(GL_LINES)
                glVertex2fv(points[0])
                glVertex2fv(points[1])
                glEnd()
            elif obj_type == "rect":
                glBegin(GL_LINE_LOOP)
                for p in points:
                    glVertex2f(p[0], p[1])
                glEnd()
            elif obj_type == "ellipse":
                if isinstance(points[0], tuple) and len(points[0]) == 4:
                    ellipse_points = points[1]
                else:
                    ellipse_points = points

                glBegin(GL_LINE_LOOP)
                for x, y in ellipse_points:
                    glVertex2f(x, y)
                glEnd()



    # Gambar window kuning
    if has_window:
        glColor3f(1.0, 1.0, 0.0)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(xmin, ymin)
        glVertex2f(xmax, ymin)
        glVertex2f(xmax, ymax)
        glVertex2f(xmin, ymax)
        glEnd()





setting_window = False
setting_window_dragging = False

def main():
    global current_shape, current_color, line_width
    global window_start, window_end, transform_mode, selected_object
    global setting_window, setting_window_dragging

    pygame.init()
    screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    gluOrtho2D(0, 800, 0, 600)

    clock = pygame.time.Clock()

    # Klik & tahan (drag) untuk menggambar
    drawing_shape = False
    start_point = None
    temp_object = None

    while True:
        glClear(GL_COLOR_BUFFER_BIT)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            elif event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                y = 600 - y

                if transform_mode:
                    idx = get_clicked_object(x, y)
                    if idx is not None:
                        selected_object = idx
                    continue

                if setting_window:
                    window_start = (x, y)
                    window_end = (x, y)
                    setting_window_dragging = True  # mulai drag window
                else:
                    if current_shape == "point":
                        objects.append(["point", [(x, y)], current_color[:]])
                        temp_object = None
                    else:
                        drawing_shape = True
                        start_point = (x, y)
                        temp_object = None

            elif event.type == MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                y = 600 - y

                if setting_window and setting_window_dragging:
                    window_end = (x, y)

                elif drawing_shape:
                    if current_shape == "line":
                        temp_object = ["line", [start_point, (x, y)], current_color[:]]
                    elif current_shape == "rect":
                        x1, y1 = start_point
                        x2, y2 = x, y
                        rect = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                        temp_object = ["rect", rect, current_color[:]]
                    elif current_shape == "ellipse":
                        x1, y1 = start_point
                        cx = (x1 + x) / 2
                        cy = (y1 + y) / 2
                        rx = abs(x - x1) / 2
                        ry = abs(y - y1) / 2

                        ellipse_points = []
                        for i in range(360):
                            theta = math.radians(i)
                            px = cx + rx * math.cos(theta)
                            py = cy + ry * math.sin(theta)
                            ellipse_points.append((px, py))

                        temp_object = ["ellipse", [(cx, cy, rx, ry), ellipse_points], current_color[:]]


            elif event.type == MOUSEBUTTONUP:
                if setting_window_dragging:
                    setting_window_dragging = False
                    setting_window = False
                elif drawing_shape:
                    drawing_shape = False
                    if temp_object:
                        # Untuk ellipse: titik-titik sudah dihitung saat drag (MOUSEMOTION)
                        # Jadi tidak perlu diproses ulang di sini
                        objects.append(temp_object)
                    start_point = None
                    temp_object = None


            elif event.type == KEYDOWN:
                if event.key == K_1:
                    current_shape = "point"
                elif event.key == K_2:
                    current_shape = "line"
                elif event.key == K_3:
                    current_shape = "rect"
                elif event.key == K_4:
                    current_shape = "ellipse"
                elif event.key == K_r:
                    current_color = [1.0, 0.0, 0.0]
                elif event.key == K_g:
                    current_color = [0.0, 1.0, 0.0]
                elif event.key == K_b:
                    current_color = [0.0, 0.0, 1.0]
                elif event.unicode == '+' or event.unicode == '=':
                    line_width = min(line_width + 1, 10)
                elif event.unicode == '-' or event.key == K_KP_MINUS:
                    line_width = max(1, line_width - 1)
                elif event.key == K_t:
                    transform_mode = 'translate'
                elif event.key == K_y:
                    transform_mode = 'rotate'
                elif event.key == K_u:
                    transform_mode = 'scale'
                elif event.key == K_c:
                    transform_mode = None
                    selected_object = None
                elif event.key == K_q:
                    window_start = None
                    window_end = None
                    setting_window = True
                elif event.key == K_DELETE:
                    objects.clear()
                    window_start = None
                    window_end = None
                    transform_mode = None
                    selected_object = None
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == K_BACKSPACE:
                    if setting_window or setting_window_dragging:
                        setting_window = False
                        setting_window_dragging = False
                        window_start = None
                        window_end = None


                # Transformasi objek
                if transform_mode == 'translate' and selected_object is not None:
                    obj_type, points, color = objects[selected_object]
                    dx, dy = 0, 0
                    if event.key == K_LEFT:
                        dx = -10
                    elif event.key == K_RIGHT:
                        dx = 10
                    elif event.key == K_UP:
                        dy = 10
                    elif event.key == K_DOWN:
                        dy = -10
                    if dx != 0 or dy != 0:
                        moved = translate(points, dx, dy, obj_type)
                        objects[selected_object] = [obj_type, moved, color]
                elif transform_mode == 'rotate' and selected_object is not None:
                    obj_type, points, color = objects[selected_object]

                    # Tentukan pusat rotasi berdasarkan tipe objek
                    if obj_type == "point":
                        origin = points[0]
                    elif obj_type == "line":
                        x1, y1 = points[0]
                        x2, y2 = points[1]
                        origin = ((x1 + x2) / 2, (y1 + y2) / 2)
                    elif obj_type == "rect":
                        xs = [p[0] for p in points]
                        ys = [p[1] for p in points]
                        origin = (sum(xs) / len(xs), sum(ys) / len(ys))
                    elif obj_type == "ellipse":
                        if isinstance(points[0], tuple) and len(points[0]) == 4:
                            cx, cy, rx, ry = points[0]
                            origin = (cx, cy)
                        else:
                            origin = points[0]  # fallback (misalnya format lama)

                    # Jalankan rotasi terhadap titik pusat
                    if event.key == K_z:
                        rotated = rotate(points, -10, origin, obj_type)
                        objects[selected_object] = [obj_type, rotated, color]
                    elif event.key == K_x:
                        rotated = rotate(points, 10, origin, obj_type)
                        objects[selected_object] = [obj_type, rotated, color]


                elif transform_mode == 'scale' and selected_object is not None:
                    obj_type, points, color = objects[selected_object]

                    # Tentukan titik tengah (origin) berdasarkan jenis objek
                    if obj_type == "ellipse" and isinstance(points[0], tuple) and len(points[0]) == 4:
                        cx, cy, rx, ry = points[0]
                        origin = (cx, cy)
                    elif obj_type == "rect":
                        xs = [p[0] for p in points]
                        ys = [p[1] for p in points]
                        origin = (sum(xs) / len(xs), sum(ys) / len(ys))
                    elif obj_type == "line":
                        x1, y1 = points[0]
                        x2, y2 = points[1]
                        origin = ((x1 + x2) / 2, (y1 + y2) / 2)
                    else:
                        origin = points[0]

                    if event.key == K_n:
                        scaled = scale(points, 1.1, 1.1, origin, obj_type)
                        objects[selected_object] = [obj_type, scaled, color]
                    elif event.key == K_m:
                        scaled = scale(points, 0.9, 0.9, origin, obj_type)
                        objects[selected_object] = [obj_type, scaled, color]




                if window_start and window_end:
                    wx1, wy1 = window_start
                    wx2, wy2 = window_end
                    dx, dy = 0, 0
                    if event.key == K_a:
                        dx = -10
                    elif event.key == K_d:
                        dx = 10
                    elif event.key == K_w:
                        dy = 10
                    elif event.key == K_s:
                        dy = -10
                    if dx != 0 or dy != 0:
                        window_start = (wx1 + dx, wy1 + dy)
                        window_end = (wx2 + dx, wy2 + dy)

        draw_all_objects()
        draw_ui()

        # Gambar objek sementara (preview saat drag)
        if temp_object:
            glColor3fv(temp_object[2])
            glLineWidth(line_width)

            if temp_object[0] == "line":
                glBegin(GL_LINES)
                glVertex2fv(temp_object[1][0])
                glVertex2fv(temp_object[1][1])
                glEnd()

            elif temp_object[0] == "rect":
                glBegin(GL_LINE_LOOP)
                for p in temp_object[1]:
                    glVertex2f(p[0], p[1])
                glEnd()

            elif temp_object[0] == "ellipse":
                glBegin(GL_LINE_LOOP)
                for px, py in temp_object[1][1]:  # akses ke list of points
                    glVertex2f(px, py)
                glEnd()


        # Gambar preview window saat sedang di-drag
        if setting_window_dragging:
            glColor3f(1.0, 1.0, 0.0)
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
            glVertex2f(window_start[0], window_start[1])
            glVertex2f(window_end[0], window_start[1])
            glVertex2f(window_end[0], window_end[1])
            glVertex2f(window_start[0], window_end[1])
            glEnd()

        pygame.display.flip()
        if not setting_window_dragging and setting_window and window_start != window_end:
            setting_window = False
        
        clock.tick(60)




if __name__ == "__main__":
    main()
