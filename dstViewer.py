import sys
from pyembroidery import read_dst
import matplotlib.pyplot as plt


def render_dst(dst_path, output_image_path):
    # Read the DST file
    pattern = read_dst(dst_path)

    # Extract stitch coordinates
    stitches = pattern.get_as_stitchblock()

    if not stitches:
        print("No stitches found in the DST file.")
        return

    # Prepare data for plotting
    x = []
    y = []
    for stitch_block in stitches:
        x_block = [point[0] for point in stitch_block[0]]
        y_block = [-point[1] for point in stitch_block[0]]  # Invert Y-axis for correct orientation
        x.append(x_block)
        y.append(y_block)

    # Plot the stitches
    plt.figure(figsize=(8, 8))
    for x_block, y_block in zip(x, y):
        plt.plot(x_block, y_block)
    plt.axis('equal')
    plt.axis('off')
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.show()
    print(f"Rendered image saved to {output_image_path}")


# Example usage
if __name__ == "__main__":
    dstPath = "output_design.dst"  # Path to your DST file
    outputImagePath = "dst_preview.png"  # Output image file path
    render_dst(dstPath, outputImagePath)
