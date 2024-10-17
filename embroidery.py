import cv2
import numpy as np
from pyembroidery import EmbPattern, EmbThread, write_dst


def add_fill_stitches(pattern, points):
    # Get the bounding rectangle of the contour
    x_coords = [point[0] for point in points]
    y_coords = [point[1] for point in points]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)

    # Define stitch spacing in millimeters
    stitch_spacing = 1.0  # Adjust as needed

    # Generate horizontal lines within the bounding box
    y = min_y
    while y <= max_y:
        intersect_points = []
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            if (p1[1] <= y <= p2[1]) or (p2[1] <= y <= p1[1]):
                if p2[1] - p1[1] != 0:
                    x = p1[0] + ((y - p1[1]) * (p2[0] - p1[0])) / (p2[1] - p1[1])
                    intersect_points.append(x)
        intersect_points.sort()
        for i in range(0, len(intersect_points), 2):
            if i + 1 < len(intersect_points):
                x_start = intersect_points[i]
                x_end = intersect_points[i + 1]
                y_pos = y
                pattern.move_abs(x_start, y_pos)
                pattern.stitch_abs(x_end, y_pos)
        y += stitch_spacing  # Move to the next line


def image_to_embroidery_cv(image_path, output_path, max_colors=5):
    # Load the image
    image = cv2.imread(image_path)
    original_height, original_width = image.shape[:2]

    # Desired physical dimensions in millimeters
    desired_width_mm = 200.0  # 20 cm
    desired_height_mm = 100.0  # 10 cm

    # Calculate aspect ratios
    image_aspect = original_width / original_height
    desired_aspect = desired_width_mm / desired_height_mm

    # Adjust image size to match desired aspect ratio
    if image_aspect > desired_aspect:
        # Crop width
        new_width = int(original_height * desired_aspect)
        new_height = original_height
    else:
        # Crop height
        new_width = original_width
        new_height = int(original_width / desired_aspect)

    # Center crop
    x_start = (original_width - new_width) // 2
    y_start = (original_height - new_height) // 2
    image = image[y_start:y_start + new_height, x_start:x_start + new_width]

    # Now, resize the image to a manageable number of pixels
    max_pixels = 500  # Adjust as needed for detail and performance
    scale_factor = min(max_pixels / new_width, max_pixels / new_height)
    image = cv2.resize(
        image,
        (int(new_width * scale_factor), int(new_height * scale_factor)),
        interpolation=cv2.INTER_AREA
    )

    # Update image dimensions
    image_height, image_width = image.shape[:2]

    # Calculate scaling factors to convert pixels to embroidery units (0.1 mm per unit)
    units_per_mm = 10.0  # Since 1 unit = 0.1 mm
    scale_x = (desired_width_mm * units_per_mm) / image_width
    scale_y = (desired_height_mm * units_per_mm) / image_height

    # Reduce the number of colors using k-means clustering
    data = image.reshape((-1, 3))
    data = np.float32(data)

    # Define criteria and apply k-means
    criteria = (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(
        data, max_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )

    # Convert back to uint8 and reshape to the original image shape
    centers = np.uint8(centers)
    segmented_data = centers[labels.flatten()]
    segmented_image = segmented_data.reshape((image.shape))

    # Create an embroidery pattern
    pattern = EmbPattern()

    # Iterate over each color
    for i, color in enumerate(centers):
        # Create a mask for the current color
        mask = cv2.inRange(segmented_image, color, color)

        # Find contours for the current color
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if not contours:
            continue

        # Add a thread for the current color
        thread = EmbThread()
        thread.set_color(int(color[2]), int(color[1]), int(color[0]))  # Convert BGR to RGB
        pattern.add_thread(thread)
        pattern.color_change()

        for contour in contours:
            # Simplify the contour
            epsilon = 0.005 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Convert contour to a list of points
            points = [point[0] for point in approx]

            if len(points) < 3:
                continue  # Skip if not enough points to form a shape

            # Scale points to embroidery units
            scaled_points = [
                (
                    point[0] * scale_x,  # X coordinate in units
                    point[1] * scale_y   # Y coordinate in units
                )
                for point in points
            ]

            # Add fill stitches inside the contour
            add_fill_stitches(pattern, scaled_points)

        # Trim after each color
        pattern.trim()

    # Finish the pattern
    pattern.end()

    # Save the .dst file
    write_dst(pattern, output_path)
    print(f"Embroidery file saved to {output_path}")


if __name__ == '__main__':
    # Example usage
    input_image_path = 'input_image.jpg'  # Replace with your image path
    output_dst_path = 'output.dst'
    image_to_embroidery_cv(
        input_image_path,
        output_dst_path,
        max_colors=10  # Adjust as needed
    )

