from PIL import Image, ImageDraw, ImageFont
import numpy as np


def create_die_face(size, value):
    """
    Creates an image of a die face with the specified value.

    :param size: Size of the die image (width and height).
    :param value: Die face value (1 to 6).
    :return: An Image object representing the die face.
    """
    die = Image.new('RGB', (size, size), 'black')
    draw = ImageDraw.Draw(die)

    # Define positions for pips based on die face value
    positions = {
        1: [(0.5, 0.5)],
        2: [(0.25, 0.25), (0.75, 0.75)],
        3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
        4: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75)],
        5: [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)],
        6: [(0.25, 0.25), (0.75, 0.25), (0.25, 0.5), (0.75, 0.5), (0.25, 0.75), (0.75, 0.75)],
    }

    # Draw the pips
    radius = size * 0.08  # Radius of the pips
    for pos in positions[value]:
        x = pos[0] * size
        y = pos[1] * size
        draw.ellipse(
            [(x - radius, y - radius), (x + radius, y + radius)],
            fill='white'
        )
    return die


def image_to_dice_art(input_image_path, output_image_path, grid_width=100, die_size=20):
    """
    Converts an input image into a die art image.

    :param input_image_path: Path to the input image.
    :param output_image_path: Path to save the output dice art image.
    :param grid_width: Number of dice along the width.
    :param die_size: Size of each die image.
    """
    # Load the image
    original_image = Image.open(input_image_path)

    # Convert to grayscale
    gray_image = original_image.convert('L')

    # Calculate grid height to maintain aspect ratio
    grid_height = int((grid_width * gray_image.height) / gray_image.width)

    # Resize the image to match the grid
    small_image = gray_image.resize((grid_width, grid_height), Image.ANTIALIAS)

    # Convert image data to a numpy array
    image_data = np.array(small_image)

    # Normalize brightness levels to die faces (1 to 6)
    die_faces = np.ceil((image_data / 255) * 5).astype(int)
    die_faces = np.clip(die_faces, 1, 6)  # Ensure values are between 1 and 6

    # Create die face images
    die_images = {}
    for i in range(1, 7):
        die_images[i] = create_die_face(die_size, i)

    # Create the final image canvas
    final_image = Image.new('RGB', (grid_width * die_size, grid_height * die_size), 'white')

    # Draw the dice onto the final image
    for y in range(grid_height):
        for x in range(grid_width):
            die_face = die_faces[y, x]
            die_image = die_images[die_face]
            final_image.paste(die_image, (x * die_size, y * die_size))

    # Save the final image
    final_image.save(output_image_path)


# Example usage
if __name__ == '__main__':
    input_image_path = 'input_image.jpg'       # Replace with your input image path
    output_image_path = 'dice_art_black_1.png'   # Output image path
    grid_width = 200                     # Number of dice along the width
    die_size = 20                        # Size of each die image in pixels

    image_to_dice_art(input_image_path, output_image_path, grid_width, die_size)
    print("Dice art image has been created and saved to", output_image_path)

    # Generate and save die face images
    # die_size = 10  # Adjust the size as needed
    # for i in range(1, 7):
    #     die_image = create_die_face(die_size, i)
    #     die_image.save(f'die_face_{i}.png')
    #     print(f'Die face {i} saved as die_face_{i}.png')
