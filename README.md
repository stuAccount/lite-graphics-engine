# Computer Graphics Lab System

A comprehensive graphics drawing tool built with Python and Tkinter, implementing pixel-level rendering algorithms for educational purposes.

## ✨ Features

### Drawing Algorithms
- **Bresenham Line Algorithm** - Efficient line drawing
- **Midpoint Circle Algorithm** - Perfect circle rendering
- **Cubic Bezier Curves** - Smooth curves with 4 control points
- **8x8 Dot Matrix Characters** - Retro character rendering (A, B, C)

### Advanced Features
- **Scanline Fill** - Polygon filling algorithm
- **Cohen-Sutherland Clipping** - Line clipping within rectangular windows
- **Geometric Transformations**:
  - Translation (平移)
  - Rotation (旋转)
  - Scaling (缩放)

### File System
- **Save/Load Projects** - JSON-based serialization
- **Editable Shapes** - Load and continue editing saved work

## 🎯 Technical Constraints

This project strictly adheres to course requirements:

- ✅ **Single File Architecture** - All code in `main.py`
- ✅ **Standard Library Only** - No `numpy`, `pandas`, or `opencv`
- ✅ **Pixel-Level Rendering** - Uses `PhotoImage.put` only, NO `create_line` etc.
- ✅ **Batch Updates** - Optimized to prevent UI freezing

## 🚀 Quick Start

### Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) for project management.

**For macOS Users**:
Due to Tcl/Tk version conflicts on macOS, it is recommended to use Homebrew's Python(3.12) and Tcl/Tk: 

```bash
# 1. Install uv
brew install uv

# 2. Install Python 3.12 and Tkinter
brew install python@3.12 python-tk@3.12

# 3. Create virtual environment using system Python (fixes Tkinter issues)
uv venv --python /opt/homebrew/bin/python3.12
```

### Running on MacOS/Linux

```bash
# Clone the repository
git clone <repo-url>
cd lite-graphics-engine
```

#### Option 1: Using uv
```bash
uv run main.py
```

#### Option 2: Using System Python

```bash
# macOS/Linux with Python 3.12+
python3 main.py
```


### Running on Windows

#### Option 1: Run from Source
```bash
python main.py
```

#### Option 2: Download Pre-built EXE
1. Go to the **Actions** tab in GitHub
2. Click the latest successful workflow run
3. Download the **Final-Windows-Exe** artifact
4. Extract and run `CG_Lab_System.exe`

## 📖 Usage Guide

### Drawing Modes

1. **Line (画线)** - Click two points to draw a line
2. **Circle (画圆)** - Click center, then click edge point
3. **Bezier Curve (贝塞尔曲线)** - Click 4 control points
4. **Character (字符)** - Click position, enter character (A/B/C)
5. **Polygon (多边形)** - Click multiple points, right-click to complete

### Transformations

1. Draw some shapes
2. Select transformation from menu:
   - **Translate** - Enter X and Y offsets
   - **Rotate** - Enter angle in degrees
   - **Scale** - Enter scale factor (>1 to enlarge, <1 to shrink)
3. All shapes are transformed together

### Clipping

1. Draw some lines
2. Select **"设置裁剪窗口"** from menu
3. Click and drag to define clipping rectangle
4. Select **"执行裁剪"** to apply

### Fill Polygon

1. Draw a polygon
2. Select **"填充多边形"** from menu
3. The last polygon will be filled/unfilled

### Save/Load

- **Save** - Saves all shapes to JSON file
- **Open** - Loads shapes from JSON file
- **Note**: Shapes remain editable after loading!

## 🏗️ Architecture

```
main.py (Single File)
├── Global Data Structure (shapes list)
├── Algorithm Library
│   ├── Bresenham Line
│   ├── Midpoint Circle
│   ├── Bezier Curve
│   ├── Dot Matrix
│   ├── Scanline Fill
│   └── Cohen-Sutherland Clip
├── Transformation Functions
│   ├── Translate
│   ├── Rotate
│   └── Scale
├── PixelCanvas Class
│   ├── PhotoImage wrapper
│   ├── Batch pixel updates
│   └── Shape rendering
└── GraphicsEngine Class
    ├── UI (Menu, Canvas, Status)
    ├── Event handlers
    └── File I/O
```

## 🔧 Development

### Tech Stack
- **Language**: Python 3.12
- **GUI**: Tkinter (standard library)
- **Rendering**: PhotoImage pixel manipulation
- **Persistence**: JSON
- **Packaging**: PyInstaller via GitHub Actions

### Performance Optimization

The system uses **batch pixel updates** to prevent UI freezing:

```python
# Collect all pixels first
pixels = algorithm.generate_pixels()

# Update all at once
image.put_pixels(pixels, color)
```

## 📦 Building Windows EXE

The GitHub Actions workflow automatically builds a Windows EXE on every push to `main`:

```yaml
pyinstaller --onefile --windowed --clean --name CG_Lab_System main.py
```

Options explained:
- `--onefile` - Single EXE file
- `--windowed` - GUI mode (no console window)
- `--clean` - Clean build cache

## 📝 Course Requirements Coverage

| Requirement | Status | Implementation |
|------------|--------|----------------|
| Line Drawing | ✅ | Bresenham algorithm |
| Circle Drawing | ✅ | Midpoint circle |
| Curve Drawing | ✅ | Cubic Bezier |
| Character Rendering | ✅ | 8x8 dot matrix |
| Fill Algorithm | ✅ | Scanline fill |
| Clipping | ✅ | Cohen-Sutherland |
| Transformations | ✅ | Translate/Rotate/Scale |
| File I/O | ✅ | JSON save/load |
| Single File | ✅ | All in main.py |
| No External Libs | ✅ | Standard library only |
| Pixel Rendering | ✅ | PhotoImage.put |

## 🎓 Credits

Developed for Computer Graphics Lab 

Author: Jesse  
Date: 2026-01-05

## 📄 License

Educational use only - Computer Graphics Lab Assignment
