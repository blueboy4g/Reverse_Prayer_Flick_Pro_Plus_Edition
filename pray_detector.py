import time

import cv2
import numpy as np
import mss
from skimage.metrics import structural_similarity as ssim

templates = {
    "mage": cv2.imread("resources/Deflect_Magic.png", cv2.IMREAD_GRAYSCALE),
    "range": cv2.imread("resources/Deflect_Ranged.png", cv2.IMREAD_GRAYSCALE),
    "melee": cv2.imread("resources/Deflect_Melee.png", cv2.IMREAD_GRAYSCALE),
    "soul_split": cv2.imread("resources/Soul_Split.png", cv2.IMREAD_GRAYSCALE),
}

template = cv2.imread("resources/Deflect_Magic.png", cv2.IMREAD_GRAYSCALE)
# Multiple templates for different prayers
t_h, t_w = template.shape

def find_scaled_image():
    time.sleep(2)
    with mss.mss() as sct:
        screen = np.array(sct.grab(sct.monitors[1]))
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        best_match = None
        best_score = 0

        min_size = 10
        max_size = 30

        min_scale = min_size / max(t_h, t_w)
        max_scale = max_size / max(t_h, t_w)

        scales = np.linspace(min_scale, max_scale, 30)

        for scale in scales:
            resized = cv2.resize(template, None, fx=scale, fy=scale)
            h, w = resized.shape

            if h > gray.shape[0] or w > gray.shape[1]:
                continue

            result = cv2.matchTemplate(gray, resized, cv2.TM_CCOEFF_NORMED)
            score = result.max()

            # Weight score by size so bigger matches are preferred
            weighted_score = score * (w * h / (t_w * t_h))

            if weighted_score > best_score:
                best_score = weighted_score
                loc = np.unravel_index(result.argmax(), result.shape)
                best_match = (int(loc[1]), int(loc[0]), int(w), int(h))

        print(f"Best match: {best_match} with weighted score: {best_score}")

        # Show rectangle on screen for verification
        x, y, w, h = best_match
        # screen_bgr = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)  # convert to BGR for rectangle
        # cv2.rectangle(screen_bgr, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # cv2.imshow("Best Match", screen_bgr)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return best_match
# Best match: (1773, 630, 30, 30) with weighted score: 0.7283371686935425


def is_praying(region, step=2, threshold=0.4):
    """
    Check if any of the prayer templates appear inside a region on the screen.
    Uses sliding window + SSIM for similarity.

    Args:
        region: (x, y, w, h) on screen to search
        step: pixels to move the window each iteration
        threshold: minimum SSIM to consider a match

    Returns:
        best_type: type of prayer detected, or False
    """
    x0, y0, w_region, h_region = region
    x0 = max(x0 - 25, 0)
    y0 = max(y0 - 25, 0)
    w_region += 50
    h_region += 50

    with mss.mss() as sct:
        region_dict = {"top": y0, "left": x0, "width": w_region, "height": h_region}
        screenshot = np.array(sct.grab(region_dict))
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        rh, rw = gray.shape

        best_score = 0
        best_type = False

        for prayer_type, template in templates.items():
            th, tw = template.shape

            # Sliding window over the region
            for y in range(0, rh - th + 1, step):
                for x in range(0, rw - tw + 1, step):
                    patch = gray[y:y + th, x:x + tw]
                    score = ssim(patch, template)
                    if score > best_score:
                        best_score = score
                        best_type = prayer_type

        if best_score >= threshold:
            print(f"Detected {best_type} prayer with SSIM {best_score:.3f}")
            return best_type

    return False
