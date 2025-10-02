#!/usr/bin/env python3

import sys
from pathlib import Path
from docling.document_converter import DocumentConverter

def convert_pdf_to_markdown(pdf_path, output_path):
    """
    Convert a PDF file to markdown using Docling.

    Args:
        pdf_path (str): Path to the PDF file
        output_path (str): Path to save the markdown output
    """
    converter = DocumentConverter()

    # Convert the PDF
    result = converter.convert(pdf_path)

    # Export to markdown
    markdown_content = result.document.export_to_markdown()

    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Successfully converted {pdf_path} to {output_path}")
    return markdown_content

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_pdf.py <pdf_path> <output_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2]

    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found at {pdf_path}")
        sys.exit(1)

    convert_pdf_to_markdown(pdf_path, output_path)