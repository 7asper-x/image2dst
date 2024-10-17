import cv2
import numpy as np
from pyembroidery import EmbPattern, write_dst, STITCH, JUMP, COLOR_CHANGE


def image_to_dst(image_path, dst_path, stitch_length=5.0):
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print("Error: Unable to load image.")
        return

    # Threshold the image to binary
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours in the image
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize the embroidery pattern
    pattern = EmbPattern()

    # Loop through each contour
    for contour in contours:
        # Approximate the contour to reduce the number of points
        epsilon = 0.005 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Create a list to hold stitch points
        stitch_points = []

        for point in approx:
            x, y = point[0]
            stitch_points.append((x, y))

        # Simplify the path by reducing points based on stitch length
        simplified_points = [stitch_points[0]]
        for point in stitch_points[1:]:
            prev_point = simplified_points[-1]
            distance = np.hypot(point[0] - prev_point[0],
                                point[1] - prev_point[1])
            if distance >= stitch_length:
                simplified_points.append(point)

        if len(simplified_points) < 2:
            continue  # Skip small contours

        # Add stitches to the pattern
        pattern.add_stitch_absolute(
            JUMP, simplified_points[0][0], simplified_points[0][1])
        for point in simplified_points[1:]:
            pattern.add_stitch_absolute(
                STITCH, point[0], point[1])
        # Close the contour by stitching back to the start
        pattern.add_stitch_absolute(
            STITCH, simplified_points[0][0], simplified_points[0][1])
        # Add color change command between contours
        pattern.add_command(COLOR_CHANGE)

    # Finish the pattern
    pattern.end()

    # Write the pattern to a DST file
    write_dst(pattern, dst_path)

    print(f"Successfully converted {image_path} to {dst_path}")


# Example usage
if __name__ == "__main__":
    imagePath = "input_image.jpg"  # Replace with your image path
    dstPath = "output_design.dst"  # Output DST file path
    image_to_dst(imagePath, dstPath)
