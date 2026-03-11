import time

import cv2
import numpy as np
import mss
from skimage.metrics import structural_similarity as ssim

templates = {
    "Magic": cv2.imread("resources/Deflect_Magic.png", cv2.IMREAD_GRAYSCALE),
    "Range": cv2.imread("resources/Deflect_Ranged.png", cv2.IMREAD_GRAYSCALE),
    "Melee": cv2.imread("resources/Deflect_Melee.png", cv2.IMREAD_GRAYSCALE),
    "Soul_Split": cv2.imread("resources/Soul_Split.png", cv2.IMREAD_GRAYSCALE),
}

template = cv2.imread("resources/prayers.png", cv2.IMREAD_GRAYSCALE)
# Multiple templates for different prayers
t_h, t_w = template.shape

def find_scaled_image():
    """
    Finds the template on screen at its original size (no scaling).
    Returns (x, y, w, h) of the match.
    """
    time.sleep(2)
    with mss.mss() as sct:
        # Grab full screen
        screen = np.array(sct.grab(sct.monitors[1]))
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        th, tw = template.shape  # template height and width
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Only consider matches above a threshold (adjust 0.8 → 0.95)
        if max_val < 0.8:
            print("No match found")
            return None

        top_left = max_loc
        x, y = top_left
        best_match = (x, y, tw, th)

        print(f"Best match: {best_match} with score: {max_val:.3f}")

        # Show rectangle for verification
        screen_bgr = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        cv2.rectangle(screen_bgr, (x, y), (x + tw, y + th), (0, 0, 255), 2)
        # cv2.imshow("Best Match", screen_bgr)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return best_match


# Define the relative positions of icons inside the detected region
# These are offsets from the top-left of the region: (x, y, w, h)
# You can fill these after inspecting the region
PRAYER_ICON_POSITIONS = {
    "Magic": (132, 71, 164, 103),
    "Range": (173, 70, 206, 103),
    "Melee": (8, 104,43, 137),
    "Soul_Split": (7, 240, 42, 274),
}

PRAYER_ICON_SETTINGS = {
    "Magic":       {"pos": (132, 71, 33, 33), "min_ratio": 0.007},
    "Range":      {"pos": (173, 70, 33, 33), "min_ratio": 0.005},
    "Melee":      {"pos": (8, 104, 33, 33),   "min_ratio": 0.0075},
    "Soul_Split": {"pos": (7, 240, 33, 33),   "min_ratio": 0.0015},
}

def is_praying(region, hsv_screenshot=None):
    """
    Detect active prayers using per-style thresholds.
    Returns a list of active prayers.
    """
    x0, y0, w_region, h_region = region

    with mss.mss() as sct:
        if hsv_screenshot is None:
            region_dict = {"top": y0, "left": x0, "width": w_region, "height": h_region}
            screenshot = np.array(sct.grab(region_dict))
            hsv_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)

        for prayer_type, settings in PRAYER_ICON_SETTINGS.items():
            px, py, pw, ph = settings["pos"]
            min_ratio = settings["min_ratio"]

            patch = hsv_screenshot[py:py + ph, px:px + pw]
            mask = cv2.inRange(patch, np.array([20, 150, 150]), np.array([40, 255, 255]))
            yellow_ratio = np.sum(mask > 0) / (pw * ph)
            #print(f"{prayer_type}: yellow_ratio = {yellow_ratio:.2%}")

            if yellow_ratio >= min_ratio:
                return prayer_type
                print(f"Detected active {prayer_type}")

    return False
