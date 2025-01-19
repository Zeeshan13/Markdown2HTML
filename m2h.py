import os
import re
import shutil
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

def copy_image_to_output(image_path, output_dir):
    """
    Copies the image to the output directory, preserving its filename.
    """
    if os.path.isfile(image_path):
        try:
            os.makedirs(output_dir, exist_ok=True)
            shutil.copy(image_path, output_dir)
            return os.path.join(output_dir, os.path.basename(image_path))
        except Exception as e:
            print(f"Error copying image {image_path}: {e}")
    return image_path

def fix_image_links(md_content, output_dir):
    """
    Adjust image links in Markdown content to ensure they work correctly and copy images to output directory.
    """
    def replace_image_link(match):
        image_path = match.group(1)
        if not image_path.startswith(('http://', 'https://')):  # Handle local paths
            abs_image_path = os.path.abspath(image_path)
            relative_path = copy_image_to_output(abs_image_path, output_dir)
            return f'![Image Description]({os.path.basename(relative_path)})'
        return match.group(0)  # Return unchanged for URLs

    return re.sub(r'!\[.*?\]\((.*?)\)', replace_image_link, md_content)

def convert_md_to_html(md_content):
    """
    Convert Markdown content to HTML without adding pilcrows.
    """
    html_content = markdown.markdown(
        md_content,
        extensions=[
            CodeHiliteExtension(linenums=False),
            'fenced_code',
            TocExtension(permalink=False),  # Disable pilcrows
            'md_in_html'
        ]
    )
    return html_content

def main():
    """
    Main function to convert a Markdown file to HTML.
    """
    # Ask the user for the file path
    file_path = input("Enter the full path to your Markdown file: ").strip()

    # Verify the file exists
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    # Determine the output directory for the HTML and images
    base_name, _ = os.path.splitext(file_path)
    output_dir = os.path.dirname(file_path)

    # Read the Markdown file
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
    except Exception as e:
        print(f"Error reading the file: {e}")
        return

    # Fix image links in the Markdown content
    md_content = fix_image_links(md_content, output_dir)

    # Convert the Markdown content to HTML
    html_content = convert_md_to_html(md_content)

    # Write the HTML content to the output file
    output_file_path = f"{base_name}.html"
    try:
        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Converted Markdown</title>
</head>
<body>
{html_content}
</body>
</html>
""")
        print(f"Successfully converted to HTML. Output saved at: {output_file_path}")
    except Exception as e:
        print(f"Error writing the HTML file: {e}")

if __name__ == "__main__":
    main()
