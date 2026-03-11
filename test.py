import cv2

# Load your screenshot of the full prayer region
img = cv2.imread("resources/prayers.png")

# This will store the coords
coords = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: {x}, {y}")
        coords.append((x, y))

cv2.imshow("Prayer Region", img)
cv2.setMouseCallback("Prayer Region", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()

print("All clicked coordinates:", coords)