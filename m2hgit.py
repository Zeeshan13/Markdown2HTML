import os
import re
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension

# Configure GitHub repository details
GITHUB_USER = "Zeeshan13"
GITHUB_REPO = "Markdown2HTML"
GITHUB_BRANCH = "main"

# CSS for styling
css_content = """
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 20px;
}

h1, h2, h3, h4, h5, h6 {
    color: #0056b3;
    margin-top: 1em;
}

code {
    background-color: #f4f4f4;
    padding: 4px;
    border-radius: 4px;
    font-family: monospace;
    color: #272822;
}

pre {
    background: #f4f4f4;
    color: #272822;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    white-space: pre-wrap;
    font-family: monospace;
}

a {
    color: #0056b3;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
    object-fit: contain;
}

img[src$=".svg"] {
    background-color: white;
    padding: 10px;
}

img:not([src]), img[src=""] {
    min-width: 100px;
    min-height: 100px;
    background: #f0f0f0;
    border: 1px dashed #999;
}
"""

def fix_github_image_links(md_content):
    """
    Converts GitHub image links (including blob links) to raw content URLs
    """
    def replace_github_link(match):
        image_path = match.group(1)
        
        # Debug: Log the original image path
        print(f"Original image path: {image_path}")
        
        # Transform GitHub blob URLs to raw URLs
        if "github.com" in image_path and "/blob/" in image_path:
            raw_url = image_path.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            print(f"Transformed GitHub blob URL to: {raw_url}")
            return f"![]({raw_url})"
        
        # Skip if already a raw URL
        if image_path.startswith(("http://", "https://")):
            print(f"Skipping already full URL: {image_path}")
            return match.group(0)
        
        # Handle relative paths
        if image_path.startswith("./"):
            image_path = image_path[2:]
        
        # Transform relative paths to raw GitHub URLs
        clean_path = image_path.lstrip("/")
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{clean_path}"
        print(f"Transformed relative path to: {raw_url}")
        return f"![]({raw_url})"

    # Match all Markdown image links
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
    return image_pattern.sub(replace_github_link, md_content)

def convert_md_to_html(md_content, css_filename="styles.css"):
    """
    Convert markdown content to HTML with proper styling and image handling
    """
    # Fix image links
    md_content = fix_github_image_links(md_content)
    
    # Convert to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            CodeHiliteExtension(linenums=False),
            'fenced_code',
            TocExtension(permalink=True),
            'md_in_html'
        ],
    )
    
    # Create HTML document with error handling
    html_with_css = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="{css_filename}">
    <script>
        window.addEventListener('load', function() {{
            document.querySelectorAll('img').forEach(function(img) {{
                img.onerror = function() {{
                    console.error('Failed to load image:', this.src);
                    this.style.border = '1px solid red';
                    this.style.padding = '10px';
                    this.alt = 'Failed to load image: ' + this.src;
                }};
            }});
        }});
    </script>
</head>
<body>
{html_content}
</body>
</html>
"""
    return html_with_css

def process_markdown_files():
    """
    Process all markdown files in the current directory and subdirectories
    """
    css_filename = "styles.css"

    # Save the CSS file
    with open(css_filename, "w", encoding="utf-8") as css_file:
        css_file.write(css_content)
    print(f"CSS saved to {css_filename}")

    # Process markdown files
    for root, _, files in os.walk("."):
        for filename in files:
            if filename.endswith(".md"):
                md_filepath = os.path.join(root, filename)
                try:
                    with open(md_filepath, "r", encoding="utf-8") as md_file:
                        md_content = md_file.read()
                    
                    html_content = convert_md_to_html(md_content, css_filename)
                    html_filename = f"{os.path.splitext(md_filepath)[0]}.html"
                    
                    with open(html_filename, "w", encoding="utf-8") as html_file:
                        html_file.write(html_content)
                    
                    print(f"Converted {md_filepath} to {html_filename}")
                except Exception as e:
                    print(f"Error processing {md_filepath}: {str(e)}")

if __name__ == "__main__":
    process_markdown_files()
