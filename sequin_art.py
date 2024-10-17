from PIL import Image, ImageDraw
import numpy as np


def create_sequin(size, color):
    """
    Creates an image of a sequin with the specified size and color.

    :param size: Diameter of the sequin.
    :param color: RGB tuple representing the color of the sequin.
    :return: An Image object representing the sequin.
    """
    sequin = Image.new('RGBA', (size, size), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(sequin)

    # Draw the sequin as a circle
    draw.ellipse([(0, 0), (size - 1, size - 1)], fill=color)

    # Optional: Add a highlight to simulate reflection
    # highlight_size = size // 4
    # highlight_position = (size // 4, size // 4)
    # draw.ellipse(
    #     [
    #         highlight_position,
    #         (highlight_position[0] + highlight_size, highlight_position[1] + highlight_size)
    #     ],
    #     fill=(255, 255, 255, 100)  # Semi-transparent white
    # )

    return sequin


def image_to_sequin_art(input_image_path, output_image_path, grid_width=100, sequin_size=10):
    """
    Converts an input image into a sequin embroidery art image.

    :param input_image_path: Path to the input image.
    :param output_image_path: Path to save the output sequin art image.
    :param grid_width: Number of sequins along the width.
    :param sequin_size: Diameter of each sequin in pixels.
    """
    # Load the image
    original_image = Image.open(input_image_path)

    # Ensure the image is in RGB mode
    rgb_image = original_image.convert('RGB')

    # Calculate grid height to maintain aspect ratio
    grid_height = int((grid_width * rgb_image.height) / rgb_image.width)

    # Resize the image to match the grid
    small_image = rgb_image.resize((grid_width, grid_height), Image.ANTIALIAS)

    # Convert image data to a numpy array
    image_data = np.array(small_image)

    # Create the final image canvas
    final_image = Image.new('RGB', (grid_width * sequin_size, grid_height * sequin_size), 'black')

    # Draw the sequins onto the final image
    for y in range(grid_height):
        for x in range(grid_width):
            color = tuple(image_data[y, x])
            sequin = create_sequin(sequin_size, color)
            final_image.paste(sequin, (x * sequin_size, y * sequin_size), sequin)

    # Save the final image
    final_image.save(output_image_path)


# Example usage
if __name__ == '__main__':
    input_image_path = 'input_image.jpg'       # Replace with your input image path
    output_image_path = 'sequin_art.png'   # Output image path

    grid_width = 200                     # Number of sequins along the width
    sequin_size = 10                     # Diameter of each sequin in pixels

    # Create the sequin art image
    image_to_sequin_art(input_image_path, output_image_path, grid_width, sequin_size)
    print("Sequin art image has been created and saved to", output_image_path)

    # sequin = create_sequin(10, (255, 0, 0))
    # sequin.show()
