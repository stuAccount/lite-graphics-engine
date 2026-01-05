#!/usr/bin/env python3
"""
Computer Graphics Lab System (计算机图形学实验大作业)
Single-file implementation using Python standard library only
Author: Jesse
Date: 2026-01-05
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json
import math


# ============================================================================
# GLOBAL DATA STRUCTURE
# ============================================================================
shapes = []  # List of shape dictionaries: {'type': 'line', 'points': [...], 'color': '#000'}
current_mode = 'line'  # Current drawing mode
current_color = '#000000'  # Current color
temp_points = []  # Temporary points for multi-click shapes
clip_window = None  # Clipping rectangle [x1, y1, x2, y2]


# ============================================================================
# ALGORITHM LIBRARY
# ============================================================================

class Algorithms:
    """Static methods for all graphics algorithms"""
    
    @staticmethod
    def bresenham_line(x0, y0, x1, y1):
        """Bresenham's line algorithm - returns list of (x, y) pixel coordinates"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return points
    
    @staticmethod
    def midpoint_circle(cx, cy, radius):
        """Midpoint circle algorithm - returns list of (x, y) pixel coordinates"""
        points = []
        x = 0
        y = radius
        d = 1 - radius
        
        # Helper to add 8-way symmetric points
        def add_symmetric(xc, yc, x, y):
            pts = [
                (xc + x, yc + y), (xc - x, yc + y),
                (xc + x, yc - y), (xc - x, yc - y),
                (xc + y, yc + x), (xc - y, yc + x),
                (xc + y, yc - x), (xc - y, yc - x)
            ]
            return pts
        
        while x <= y:
            points.extend(add_symmetric(cx, cy, x, y))
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        
        return points
    
    @staticmethod
    def bezier_curve(p0, p1, p2, p3, steps=100):
        """Cubic Bezier curve with 4 control points - returns list of (x, y) coordinates"""
        points = []
        for i in range(steps + 1):
            t = i / steps
            t2 = t * t
            t3 = t2 * t
            mt = 1 - t
            mt2 = mt * mt
            mt3 = mt2 * mt
            
            x = mt3 * p0[0] + 3 * mt2 * t * p1[0] + 3 * mt * t2 * p2[0] + t3 * p3[0]
            y = mt3 * p0[1] + 3 * mt2 * t * p1[1] + 3 * mt * t2 * p2[1] + t3 * p3[1]
            points.append((int(x), int(y)))
        
        return points
    
    @staticmethod
    def dot_matrix_char(char, x, y, scale=1):
        """8x8 dot matrix character - returns list of (x, y) pixel coordinates"""
        # Hardcoded 8x8 patterns for demonstration (A, B, C)
        patterns = {
            'A': [
                "  ████  ",
                " ██  ██ ",
                "██    ██",
                "████████",
                "██    ██",
                "██    ██",
                "██    ██",
                "        "
            ],
            'B': [
                "███████ ",
                "██    ██",
                "██    ██",
                "███████ ",
                "██    ██",
                "██    ██",
                "███████ ",
                "        "
            ],
            'C': [
                " ██████ ",
                "██    ██",
                "██      ",
                "██      ",
                "██      ",
                "██    ██",
                " ██████ ",
                "        "
            ]
        }
        
        pattern = patterns.get(char.upper(), patterns['A'])
        points = []
        
        for row_idx, row in enumerate(pattern):
            for col_idx, pixel in enumerate(row):
                if pixel == '█':
                    # Add scaled pixels
                    for dy in range(scale):
                        for dx in range(scale):
                            points.append((x + col_idx * scale + dx, y + row_idx * scale + dy))
        
        return points
    
    @staticmethod
    def scanline_fill(vertices, bbox):
        """Scanline fill algorithm for polygon - returns list of (x, y) pixel coordinates"""
        if len(vertices) < 3:
            return []
        
        points = []
        min_y = max(int(min(v[1] for v in vertices)), bbox[1])
        max_y = min(int(max(v[1] for v in vertices)), bbox[3])
        
        for y in range(min_y, max_y + 1):
            intersections = []
            n = len(vertices)
            
            for i in range(n):
                v1 = vertices[i]
                v2 = vertices[(i + 1) % n]
                
                if v1[1] == v2[1]:  # Horizontal edge
                    continue
                
                if y < min(v1[1], v2[1]) or y > max(v1[1], v2[1]):
                    continue
                
                x = v1[0] + (y - v1[1]) * (v2[0] - v1[0]) / (v2[1] - v1[1])
                intersections.append(int(x))
            
            intersections.sort()
            
            # Fill between pairs of intersections
            for i in range(0, len(intersections) - 1, 2):
                x1 = max(intersections[i], bbox[0])
                x2 = min(intersections[i + 1], bbox[2])
                for x in range(x1, x2 + 1):
                    points.append((x, y))
        
        return points
    
    @staticmethod
    def cohen_sutherland_clip(x0, y0, x1, y1, clip_rect):
        """Cohen-Sutherland line clipping - returns clipped line or None"""
        INSIDE = 0  # 0000
        LEFT = 1    # 0001
        RIGHT = 2   # 0010
        BOTTOM = 4  # 0100
        TOP = 8     # 1000
        
        xmin, ymin, xmax, ymax = clip_rect
        
        def compute_code(x, y):
            code = INSIDE
            if x < xmin:
                code |= LEFT
            elif x > xmax:
                code |= RIGHT
            if y < ymin:
                code |= BOTTOM
            elif y > ymax:
                code |= TOP
            return code
        
        code0 = compute_code(x0, y0)
        code1 = compute_code(x1, y1)
        accept = False
        
        while True:
            if code0 == 0 and code1 == 0:  # Both inside
                accept = True
                break
            elif (code0 & code1) != 0:  # Both outside same region
                break
            else:
                # Pick outside point
                code_out = code0 if code0 != 0 else code1
                
                # Find intersection
                if code_out & TOP:
                    x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
                    y = ymax
                elif code_out & BOTTOM:
                    x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
                    y = ymin
                elif code_out & RIGHT:
                    y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
                    x = xmax
                elif code_out & LEFT:
                    y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
                    x = xmin
                
                # Update point and code
                if code_out == code0:
                    x0, y0 = x, y
                    code0 = compute_code(x0, y0)
                else:
                    x1, y1 = x, y
                    code1 = compute_code(x1, y1)
        
        if accept:
            return (int(x0), int(y0), int(x1), int(y1))
        return None


# ============================================================================
# TRANSFORMATION FUNCTIONS
# ============================================================================

def translate_shape(shape, dx, dy):
    """Translate shape by offset"""
    if 'points' in shape:
        shape['points'] = [(x + dx, y + dy) for x, y in shape['points']]

def rotate_shape(shape, angle_deg, cx=400, cy=300):
    """Rotate shape around center point"""
    angle = math.radians(angle_deg)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    if 'points' in shape:
        new_points = []
        for x, y in shape['points']:
            # Translate to origin
            x -= cx
            y -= cy
            # Rotate
            new_x = x * cos_a - y * sin_a
            new_y = x * sin_a + y * cos_a
            # Translate back
            new_points.append((new_x + cx, new_y + cy))
        shape['points'] = new_points

def scale_shape(shape, factor, cx=400, cy=300):
    """Scale shape around center point"""
    if 'points' in shape:
        new_points = []
        for x, y in shape['points']:
            # Translate to origin
            x -= cx
            y -= cy
            # Scale
            new_x = x * factor
            new_y = y * factor
            # Translate back
            new_points.append((new_x + cx, new_y + cy))
        shape['points'] = new_points


# ============================================================================
# PIXEL CANVAS CLASS
# ============================================================================

class PixelCanvas:
    """Wrapper for PhotoImage with batch pixel update optimization"""
    
    def __init__(self, canvas, width, height, bg_color='white'):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.bg_color = bg_color
        
        # Create PhotoImage
        self.image = tk.PhotoImage(width=width, height=height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.clear()
    
    def clear(self):
        """Clear canvas to background color"""
        self.image.put(self.bg_color, to=(0, 0, self.width, self.height))
    
    def put_pixels(self, pixels, color):
        """Batch update pixels - optimized version"""
        if not pixels:
            return
        
        # Filter out-of-bounds pixels
        valid_pixels = [(x, y) for x, y in pixels 
                       if 0 <= x < self.width and 0 <= y < self.height]
        
        if not valid_pixels:
            return
        
        # Batch update by drawing individual pixels
        # PhotoImage.put is efficient for this use case
        for x, y in valid_pixels:
            self.image.put(color, (x, y))
    
    def render_shape(self, shape):
        """Render a single shape using appropriate algorithm"""
        shape_type = shape.get('type')
        points = shape.get('points', [])
        color = shape.get('color', '#000000')
        
        pixels = []
        
        if shape_type == 'line' and len(points) >= 2:
            x0, y0 = map(int, points[0])
            x1, y1 = map(int, points[1])
            pixels = Algorithms.bresenham_line(x0, y0, x1, y1)
        
        elif shape_type == 'circle' and len(points) >= 2:
            cx, cy = map(int, points[0])
            edge_x, edge_y = map(int, points[1])
            radius = int(math.sqrt((edge_x - cx)**2 + (edge_y - cy)**2))
            pixels = Algorithms.midpoint_circle(cx, cy, radius)
        
        elif shape_type == 'bezier' and len(points) >= 4:
            p0, p1, p2, p3 = points[:4]
            curve_points = Algorithms.bezier_curve(p0, p1, p2, p3)
            # Draw curve with Bresenham between consecutive points
            for i in range(len(curve_points) - 1):
                pixels.extend(Algorithms.bresenham_line(
                    curve_points[i][0], curve_points[i][1],
                    curve_points[i + 1][0], curve_points[i + 1][1]
                ))
        
        elif shape_type == 'char' and len(points) >= 1:
            x, y = map(int, points[0])
            char = shape.get('char', 'A')
            scale = shape.get('scale', 2)
            pixels = Algorithms.dot_matrix_char(char, x, y, scale)
        
        elif shape_type == 'polygon' and len(points) >= 3:
            # Draw outline
            for i in range(len(points)):
                p0 = points[i]
                p1 = points[(i + 1) % len(points)]
                pixels.extend(Algorithms.bresenham_line(
                    int(p0[0]), int(p0[1]), int(p1[0]), int(p1[1])
                ))
            
            # Fill if specified
            if shape.get('filled', False):
                bbox = (0, 0, self.width, self.height)
                fill_pixels = Algorithms.scanline_fill(points, bbox)
                pixels.extend(fill_pixels)
        
        self.put_pixels(pixels, color)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class GraphicsEngine:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Computer Graphics Lab System (计算机图形学实验大作业)")
        self.root.geometry("900x700")
        
        # Canvas dimensions
        self.canvas_width = 800
        self.canvas_height = 600
        
        # Create UI
        self.create_menu()
        self.create_canvas()
        self.create_status_bar()
        
        # Mouse state
        self.dragging = False
        self.drag_start = None
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Initial redraw
        self.redraw()
        self.update_status()
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件 (File)", menu=file_menu)
        file_menu.add_command(label="保存 (Save)", command=self.save_project)
        file_menu.add_command(label="打开 (Open)", command=self.load_project)
        file_menu.add_separator()
        file_menu.add_command(label="清空 (Clear All)", command=self.clear_all)
        file_menu.add_separator()
        file_menu.add_command(label="退出 (Exit)", command=self.root.quit)
        
        # Draw menu
        draw_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="绘制 (Draw)", menu=draw_menu)
        draw_menu.add_command(label="画线 (Line)", command=lambda: self.set_mode('line'))
        draw_menu.add_command(label="画圆 (Circle)", command=lambda: self.set_mode('circle'))
        draw_menu.add_command(label="贝塞尔曲线 (Bezier)", command=lambda: self.set_mode('bezier'))
        draw_menu.add_command(label="点阵字符 (Char)", command=lambda: self.set_mode('char'))
        draw_menu.add_command(label="多边形 (Polygon)", command=lambda: self.set_mode('polygon'))
        draw_menu.add_separator()
        draw_menu.add_command(label="选择颜色 (Color)", command=self.choose_color)
        
        # Transform menu
        transform_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="变换 (Transform)", menu=transform_menu)
        transform_menu.add_command(label="平移 (Translate)", command=self.transform_translate)
        transform_menu.add_command(label="旋转 (Rotate)", command=self.transform_rotate)
        transform_menu.add_command(label="缩放 (Scale)", command=self.transform_scale)
        
        # Fill/Clip menu
        fillclip_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="填充/裁剪 (Fill/Clip)", menu=fillclip_menu)
        fillclip_menu.add_command(label="填充多边形 (Fill Polygon)", command=self.fill_polygon)
        fillclip_menu.add_command(label="设置裁剪窗口 (Set Clip Window)", command=lambda: self.set_mode('clip'))
        fillclip_menu.add_command(label="执行裁剪 (Apply Clip)", command=self.apply_clipping)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助 (Help)", menu=help_menu)
        help_menu.add_command(label="关于 (About)", command=self.show_about)
    
    def create_canvas(self):
        """Create drawing canvas"""
        canvas_frame = tk.Frame(self.root, bg='gray')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, 
                               width=self.canvas_width, 
                               height=self.canvas_height,
                               bg='white', 
                               cursor='crosshair')
        self.canvas.pack()
        
        # Create pixel canvas
        self.pixel_canvas = PixelCanvas(self.canvas, 
                                       self.canvas_width, 
                                       self.canvas_height)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_var = tk.StringVar()
        status_bar = tk.Label(self.root, 
                            textvariable=self.status_var, 
                            bd=1, 
                            relief=tk.SUNKEN, 
                            anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self):
        """Update status bar text"""
        global current_mode, current_color, temp_points
        mode_text = {
            'line': '画线模式',
            'circle': '画圆模式',
            'bezier': '贝塞尔曲线模式 (需要4个点)',
            'char': '字符模式',
            'polygon': '多边形模式 (右键完成)',
            'clip': '裁剪窗口选择模式'
        }
        status = f"当前模式: {mode_text.get(current_mode, current_mode)} | 颜色: {current_color}"
        if temp_points:
            status += f" | 临时点: {len(temp_points)}"
        self.status_var.set(status)
    
    def set_mode(self, mode):
        """Set drawing mode"""
        global current_mode, temp_points
        current_mode = mode
        temp_points = []
        self.update_status()
    
    def choose_color(self):
        """Choose drawing color"""
        global current_color
        from tkinter import colorchooser
        color = colorchooser.askcolor(current_color)
        if color[1]:
            current_color = color[1]
            self.update_status()
    
    def redraw(self):
        """Complete redraw of all shapes"""
        global shapes
        self.pixel_canvas.clear()
        
        # Draw clip window if set
        global clip_window
        if clip_window:
            x1, y1, x2, y2 = clip_window
            # Draw rectangle outline in red
            rect_points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
            for i in range(4):
                p0 = rect_points[i]
                p1 = rect_points[(i + 1) % 4]
                pixels = Algorithms.bresenham_line(int(p0[0]), int(p0[1]), int(p1[0]), int(p1[1]))
                self.pixel_canvas.put_pixels(pixels, '#FF0000')
        
        # Render all shapes
        for shape in shapes:
            self.pixel_canvas.render_shape(shape)
    
    def on_mouse_down(self, event):
        """Handle mouse button press"""
        global current_mode, temp_points, shapes, current_color
        
        x, y = event.x, event.y
        
        if current_mode == 'line':
            temp_points.append((x, y))
            if len(temp_points) == 2:
                shapes.append({
                    'type': 'line',
                    'points': temp_points.copy(),
                    'color': current_color
                })
                temp_points = []
                self.redraw()
        
        elif current_mode == 'circle':
            temp_points.append((x, y))
            if len(temp_points) == 2:
                shapes.append({
                    'type': 'circle',
                    'points': temp_points.copy(),
                    'color': current_color
                })
                temp_points = []
                self.redraw()
        
        elif current_mode == 'bezier':
            temp_points.append((x, y))
            if len(temp_points) == 4:
                shapes.append({
                    'type': 'bezier',
                    'points': temp_points.copy(),
                    'color': current_color
                })
                temp_points = []
                self.redraw()
        
        elif current_mode == 'char':
            char = simpledialog.askstring("字符", "输入一个字符 (A/B/C):", initialvalue='A')
            if char:
                shapes.append({
                    'type': 'char',
                    'points': [(x, y)],
                    'char': char[0].upper(),
                    'scale': 2,
                    'color': current_color
                })
                self.redraw()
        
        elif current_mode == 'polygon':
            temp_points.append((x, y))
        
        elif current_mode == 'clip':
            self.drag_start = (x, y)
            self.dragging = True
        
        self.update_status()
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        pass
    
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        global current_mode, clip_window
        
        if current_mode == 'clip' and self.dragging:
            x, y = event.x, event.y
            x1, y1 = self.drag_start
            clip_window = (min(x1, x), min(y1, y), max(x1, x), max(y1, y))
            self.dragging = False
            self.redraw()
    
    def save_project(self):
        """Save shapes to JSON file"""
        global shapes
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(shapes, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", f"已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")
    
    def load_project(self):
        """Load shapes from JSON file"""
        global shapes
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    shapes = json.load(f)
                self.redraw()
                messagebox.showinfo("成功", f"已加载: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"加载失败: {e}")
    
    def clear_all(self):
        """Clear all shapes"""
        global shapes, temp_points, clip_window
        if messagebox.askyesno("确认", "确定要清空所有图形吗？"):
            shapes = []
            temp_points = []
            clip_window = None
            self.redraw()
    
    def transform_translate(self):
        """Apply translation to all shapes"""
        global shapes
        if not shapes:
            messagebox.showwarning("警告", "没有图形可以变换")
            return
        
        dx = simpledialog.askinteger("平移", "X方向偏移量:", initialvalue=50)
        dy = simpledialog.askinteger("平移", "Y方向偏移量:", initialvalue=50)
        
        if dx is not None and dy is not None:
            for shape in shapes:
                translate_shape(shape, dx, dy)
            self.redraw()
    
    def transform_rotate(self):
        """Apply rotation to all shapes"""
        global shapes
        if not shapes:
            messagebox.showwarning("警告", "没有图形可以变换")
            return
        
        angle = simpledialog.askfloat("旋转", "旋转角度 (度):", initialvalue=45)
        if angle is not None:
            cx = self.canvas_width // 2
            cy = self.canvas_height // 2
            for shape in shapes:
                rotate_shape(shape, angle, cx, cy)
            self.redraw()
    
    def transform_scale(self):
        """Apply scaling to all shapes"""
        global shapes
        if not shapes:
            messagebox.showwarning("警告", "没有图形可以变换")
            return
        
        factor = simpledialog.askfloat("缩放", "缩放因子 (例如 1.5 放大, 0.5 缩小):", initialvalue=1.5)
        if factor is not None and factor > 0:
            cx = self.canvas_width // 2
            cy = self.canvas_height // 2
            for shape in shapes:
                scale_shape(shape, factor, cx, cy)
            self.redraw()
    
    def fill_polygon(self):
        """Toggle fill for last polygon"""
        global shapes
        # Find last polygon
        for shape in reversed(shapes):
            if shape['type'] == 'polygon':
                shape['filled'] = not shape.get('filled', False)
                self.redraw()
                return
        messagebox.showwarning("警告", "没有找到多边形")
    
    def apply_clipping(self):
        """Apply Cohen-Sutherland clipping to all lines"""
        global shapes, clip_window
        
        if not clip_window:
            messagebox.showwarning("警告", "请先设置裁剪窗口")
            return
        
        new_shapes = []
        for shape in shapes:
            if shape['type'] == 'line' and len(shape['points']) >= 2:
                x0, y0 = map(int, shape['points'][0])
                x1, y1 = map(int, shape['points'][1])
                result = Algorithms.cohen_sutherland_clip(x0, y0, x1, y1, clip_window)
                if result:
                    new_shapes.append({
                        'type': 'line',
                        'points': [(result[0], result[1]), (result[2], result[3])],
                        'color': shape['color']
                    })
            else:
                new_shapes.append(shape)
        
        shapes = new_shapes
        self.redraw()
        messagebox.showinfo("完成", "裁剪已应用")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "关于",
            "Computer Graphics Lab System\n"
            "计算机图形学实验大作业\n\n"
            "功能:\n"
            "- Bresenham 画线\n"
            "- 中点画圆\n"
            "- Bezier 曲线\n"
            "- 点阵字符\n"
            "- 扫描线填充\n"
            "- Cohen-Sutherland 裁剪\n"
            "- 几何变换\n"
            "- JSON 文件存取\n\n"
            "作者: Jesse\n"
            "日期: 2026-01-05"
        )


# ============================================================================
# POLYGON COMPLETION (Right-click handler)
# ============================================================================

def complete_polygon(event):
    """Complete polygon on right-click"""
    global temp_points, shapes, current_mode, current_color
    
    if current_mode == 'polygon' and len(temp_points) >= 3:
        shapes.append({
            'type': 'polygon',
            'points': temp_points.copy(),
            'color': current_color,
            'filled': False
        })
        temp_points = []
        app.redraw()
        app.update_status()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    root = tk.Tk()
    app = GraphicsEngine(root)
    
    # Bind right-click for polygon completion
    app.canvas.bind('<Button-2>', complete_polygon)  # macOS: Button-2
    app.canvas.bind('<Button-3>', complete_polygon)  # Windows/Linux: Button-3
    
    root.mainloop()
