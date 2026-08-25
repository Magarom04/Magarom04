from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance


# ============================================================
# SETTINGS
# ============================================================

INPUT_DIR = Path("assets/anime")
OUTPUT_FILE = Path("assets/anime-matrix.gif")

# More columns = more detail
COLS = 160

# Distance between dots
DOT_SPACING = 4

# Maximum dot radius
MAX_RADIUS = 2.0

# Time each anime stays visible
FRAME_DURATION = 2500

# Image adjustments
CONTRAST = 1.25
SATURATION = 1.15


# ============================================================
# FIND IMAGES
# ============================================================

EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

image_files = sorted(
    [
        file
        for file in INPUT_DIR.iterdir()
        if file.suffix.lower() in EXTENSIONS
    ]
)

if not image_files:
    raise SystemExit(
        "ERROR: No anime images found in assets/anime/"
    )

print(f"Found {len(image_files)} anime images.")


# ============================================================
# CREATE DOT-MATRIX FRAME
# ============================================================

def create_dot_matrix(image_path):

    print(f"Processing: {image_path.name}")

    # --------------------------------------------------------
    # OPEN IMAGE
    # --------------------------------------------------------

    image = Image.open(image_path).convert("RGB")

    original_width, original_height = image.size

    # --------------------------------------------------------
    # CROP TO SQUARE
    # --------------------------------------------------------

    width = COLS
    height = COLS

    # Find the center crop.
    source_width, source_height = image.size

    square_size = min(
        source_width,
        source_height
    )

    left = (source_width - square_size) // 2
    top = (source_height - square_size) // 2
    right = left + square_size
    bottom = top + square_size

    image = image.crop(
        (left, top, right, bottom)
    )

    # Resize to a high-detail square.
    image = image.resize(
        (width, height),
        Image.Resampling.LANCZOS
    )

    # --------------------------------------------------------
    # IMPROVE IMAGE
    # --------------------------------------------------------

    image = ImageEnhance.Contrast(image).enhance(
        CONTRAST
    )

    image = ImageEnhance.Color(image).enhance(
        SATURATION
    )

    # --------------------------------------------------------
    # CREATE BLACK CANVAS
    # --------------------------------------------------------

    canvas_width = width * DOT_SPACING
    canvas_height = height * DOT_SPACING

    canvas = Image.new(
        "RGB",
        (
            canvas_width,
            canvas_height
        ),
        (0, 0, 0)
    )

    draw = ImageDraw.Draw(canvas)

    # --------------------------------------------------------
    # CREATE COLORED DOTS
    # --------------------------------------------------------

    for y in range(height):

        for x in range(width):

            r, g, b = image.getpixel(
                (x, y)
            )

            # ------------------------------------------------
            # CALCULATE BRIGHTNESS
            # ------------------------------------------------

            brightness = (
                0.299 * r
                + 0.587 * g
                + 0.114 * b
            )

            # Very dark pixels disappear.
            if brightness < 20:
                continue

            # Normalize brightness.
            intensity = brightness / 255.0

            # ------------------------------------------------
            # DOT SIZE
            # ------------------------------------------------

            radius = (
                0.45
                + intensity * MAX_RADIUS
            )

            # Keep dark areas more sparse.
            if brightness < 55:
                radius *= 0.65

            # ------------------------------------------------
            # DOT POSITION
            # ------------------------------------------------

            cx = (
                x * DOT_SPACING
                + DOT_SPACING // 2
            )

            cy = (
                y * DOT_SPACING
                + DOT_SPACING // 2
            )

            # ------------------------------------------------
            # DRAW COLORED DOT
            # ------------------------------------------------

            draw.ellipse(
                (
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius
                ),
                fill=(r, g, b)
            )

    return canvas


# ============================================================
# GENERATE FRAMES
# ============================================================

frames = []

for image_file in image_files:

    try:

        frame = create_dot_matrix(
            image_file
        )

        frames.append(frame)

    except Exception as error:

        print(
            f"WARNING: Could not process "
            f"{image_file.name}: {error}"
        )


# ============================================================
# CHECK FRAMES
# ============================================================

if not frames:

    raise SystemExit(
        "ERROR: No frames were generated."
    )


# ============================================================
# CREATE GIF
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

frames[0].save(
    OUTPUT_FILE,
    save_all=True,
    append_images=frames[1:],
    duration=FRAME_DURATION,
    loop=0,
    optimize=False
)


# ============================================================
# DONE
# ============================================================

print()
print("==============================================")
print("COLORED ANIME DOT-MATRIX CREATED")
print("==============================================")
print(f"Frames : {len(frames)}")
print(f"Output : {OUTPUT_FILE}")
print("==============================================")