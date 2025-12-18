# doc convertor


# # app/document_parser/converters.py
# import fitz  # PyMuPDF
# import os
# import html
# from pathlib import Path
# import json

# def pdf_to_html_advanced(pdf_path, output_path=None, include_images=True, 
#                         preserve_formatting=True, include_annotations=True, 
#                         extract_tables=True, password=None):
#     """
#     Advanced PDF to HTML converter with support for annotations, tables, and various PDF types
    
#     Args:
#         pdf_path (str): Path to the input PDF file
#         output_path (str): Path for the output HTML file (optional)
#         include_images (bool): Whether to extract and include images
#         preserve_formatting (bool): Whether to preserve text formatting
#         include_annotations (bool): Whether to extract highlights, sticky notes, etc.
#         extract_tables (bool): Whether to detect and format tables
#         password (str): Password for protected PDFs
    
#     Returns:
#         dict: Conversion results with status and file paths
#     """
    
#     # Open the PDF
#     try:
#         doc = fitz.open(pdf_path)
#         if doc.needs_pass:
#             if password:
#                 if not doc.authenticate(password):
#                     return {"success": False, "error": "Invalid password"}
#             else:
#                 return {"success": False, "error": "PDF requires password"}
#     except Exception as e:
#         return {"success": False, "error": f"Error opening PDF: {e}"}
    
#     # Check if PDF has text or is scanned
#     has_text = False
#     for page_num in range(min(3, len(doc))):  # Check first 3 pages
#         if doc[page_num].get_text().strip():
#             has_text = True
#             break
    
#     if not has_text:
#         print("Warning: This appears to be a scanned PDF. Text extraction may be limited.")
#         print("Consider using OCR tools like pytesseract for better results.")
    
#     # Generate output path if not provided
#     if output_path is None:
#         pdf_name = Path(pdf_path).stem
#         output_path = f"{pdf_name}.html"
    
#     # Create output directory for images if needed
#     if include_images:
#         img_dir = Path(output_path).stem + "_images"
#         os.makedirs(img_dir, exist_ok=True)
    
#     # Start building HTML content
#     html_content = []
#     html_content.append("""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Converted PDF</title>
#     <style>
#         body {
#             font-family: Arial, sans-serif;
#             max-width: 1000px;
#             margin: 0 auto;
#             padding: 20px;
#             line-height: 1.6;
#         }
#         .page {
#             margin-bottom: 30px;
#             page-break-after: always;
#             border-bottom: 2px solid #eee;
#             padding-bottom: 20px;
#         }
#         .page-number {
#             color: #666;
#             font-size: 12px;
#             margin-bottom: 10px;
#             font-weight: bold;
#         }
#         img {
#             max-width: 100%;
#             height: auto;
#             margin: 10px 0;
#             border: 1px solid #ddd;
#         }
#         .formatted-text {
#             white-space: pre-wrap;
#         }
        
#         /* Annotation styles */
#         .highlight {
#             background-color: yellow;
#             padding: 2px;
#             margin: 2px 0;
#             border-radius: 3px;
#         }
#         .highlight.red { background-color: #ffcccc; }
#         .highlight.green { background-color: #ccffcc; }
#         .highlight.blue { background-color: #ccccff; }
#         .highlight.pink { background-color: #ffccff; }
        
#         .sticky-note {
#             background-color: #fff3cd;
#             border: 1px solid #ffeaa7;
#             border-radius: 5px;
#             padding: 10px;
#             margin: 10px 0;
#             position: relative;
#         }
#         .sticky-note::before {
#             content: "📝 Note: ";
#             font-weight: bold;
#             color: #856404;
#         }
        
#         .annotation {
#             background-color: #e7f3ff;
#             border-left: 4px solid #007bff;
#             padding: 8px 12px;
#             margin: 5px 0;
#             border-radius: 3px;
#         }
        
#         /* Table styles */
#         .pdf-table {
#             border-collapse: collapse;
#             width: 100%;
#             margin: 15px 0;
#             border: 1px solid #ddd;
#         }
#         .pdf-table th, .pdf-table td {
#             border: 1px solid #ddd;
#             padding: 8px;
#             text-align: left;
#         }
#         .pdf-table th {
#             background-color: #f5f5f5;
#             font-weight: bold;
#         }
        
#         .metadata {
#             background-color: #f8f9fa;
#             border: 1px solid #dee2e6;
#             border-radius: 5px;
#             padding: 15px;
#             margin-bottom: 20px;
#         }
#     </style>
# </head>
# <body>""")
    
#     # Add PDF metadata
#     metadata = doc.metadata
#     if metadata:
#         html_content.append('<div class="metadata">')
#         html_content.append('<h3>Document Information</h3>')
#         for key, value in metadata.items():
#             if value:
#                 html_content.append(f'<p><strong>{key}:</strong> {html.escape(str(value))}</p>')
#         html_content.append('</div>')
    
#     # Process each page
#     annotations_found = []
    
#     for page_num in range(len(doc)):
#         page = doc[page_num]
        
#         # Add page header
#         html_content.append(f'<div class="page">')
#         html_content.append(f'<div class="page-number">Page {page_num + 1} of {len(doc)}</div>')
        
#         # Extract annotations first
#         page_annotations = []
#         if include_annotations:
#             for annot in page.annots():
#                 annot_dict = {
#                     'type': annot.type[1],  # Get annotation type name
#                     'content': annot.info.get('content', ''),
#                     'rect': list(annot.rect),
#                     'page': page_num + 1
#                 }
                
#                 # Get highlighted text for highlight annotations
#                 if annot.type[0] == 8:  # Highlight annotation
#                     try:
#                         # Get text in the annotation rectangle
#                         highlighted_text = page.get_textbox(annot.rect)
#                         annot_dict['highlighted_text'] = highlighted_text.strip()
#                     except:
#                         annot_dict['highlighted_text'] = ''
                
#                 page_annotations.append(annot_dict)
#                 annotations_found.append(annot_dict)
        
#         # Extract and format text
#         if preserve_formatting:
#             blocks = page.get_text("dict")
#             html_content.append('<div class="formatted-text">')
            
#             for block in blocks["blocks"]:
#                 if "lines" in block:  # Text block
#                     # Check if this block intersects with any highlights
#                     block_rect = fitz.Rect(block["bbox"])
                    
#                     for line in block["lines"]:
#                         line_html = ""
#                         line_rect = fitz.Rect(line["bbox"])
                        
#                         # Check for highlights on this line
#                         is_highlighted = False
#                         highlight_color = "yellow"
                        
#                         for annot in page_annotations:
#                             if annot['type'] == 'Highlight':
#                                 annot_rect = fitz.Rect(annot['rect'])
#                                 if line_rect.intersects(annot_rect):
#                                     is_highlighted = True
#                                     # You can add color detection logic here
#                                     break
                        
#                         for span in line["spans"]:
#                             text = html.escape(span["text"])
#                             font_size = span["size"]
#                             font_flags = span["flags"]
                            
#                             # Apply formatting based on font flags
#                             if font_flags & 2**4:  # Bold
#                                 text = f"<strong>{text}</strong>"
#                             if font_flags & 2**1:  # Italic
#                                 text = f"<em>{text}</em>"
                            
#                             # Apply font size if significantly different
#                             if font_size > 12:
#                                 text = f'<span style="font-size: {font_size}px;">{text}</span>'
                            
#                             line_html += text
                        
#                         if line_html.strip():
#                             if is_highlighted:
#                                 line_html = f'<span class="highlight">{line_html}</span>'
#                             html_content.append(line_html + "<br>")
            
#             html_content.append('</div>')
#         else:
#             # Simple text extraction with highlight detection
#             text = page.get_text()
#             paragraphs = text.split('\n\n')
            
#             for paragraph in paragraphs:
#                 if paragraph.strip():
#                     escaped_text = html.escape(paragraph.strip())
#                     html_content.append(f'<p>{escaped_text}</p>')
        
#         # Add annotations as separate elements
#         if include_annotations and page_annotations:
#             html_content.append('<div class="annotations-section">')
            
#             for annot in page_annotations:
#                 if annot['type'] == 'Text' or annot['type'] == 'Note':
#                     # Sticky notes
#                     if annot['content']:
#                         html_content.append(f'<div class="sticky-note">{html.escape(annot["content"])}</div>')
                
#                 elif annot['type'] == 'Highlight':
#                     # Highlights with content
#                     if annot['content'] or annot.get('highlighted_text'):
#                         highlight_text = annot.get('highlighted_text', '')
#                         note_text = annot['content']
                        
#                         html_content.append('<div class="annotation">')
#                         if highlight_text:
#                             html_content.append(f'<strong>Highlighted text:</strong> "{html.escape(highlight_text)}"<br>')
#                         if note_text:
#                             html_content.append(f'<strong>Note:</strong> {html.escape(note_text)}')
#                         html_content.append('</div>')
                
#                 elif annot['content']:
#                     # Other annotations with content
#                     html_content.append(f'<div class="annotation"><strong>{annot["type"]}:</strong> {html.escape(annot["content"])}</div>')
            
#             html_content.append('</div>')
        
#         # Extract tables (basic table detection)
#         if extract_tables:
#             tables = find_tables_in_page(page)
#             for table in tables:
#                 html_content.append(convert_table_to_html(table))
        
#         # Extract images
#         if include_images:
#             image_list = page.get_images()
            
#             for img_index, img in enumerate(image_list):
#                 try:
#                     xref = img[0]
#                     pix = fitz.Pixmap(doc, xref)
                    
#                     if pix.n - pix.alpha < 4:  # GRAY or RGB
#                         img_filename = f"{img_dir}/page_{page_num + 1}_img_{img_index + 1}.png"
#                         pix.save(img_filename)
                        
#                         # Add image to HTML
#                         rel_path = f"{img_dir}/page_{page_num + 1}_img_{img_index + 1}.png"
#                         html_content.append(f'<img src="{rel_path}" alt="Image from page {page_num + 1}" title="Page {page_num + 1}, Image {img_index + 1}">')
                    
#                     pix = None  # Release memory
                
#                 except Exception as e:
#                     print(f"Error extracting image on page {page_num + 1}: {e}")
        
#         html_content.append('</div>')
    
#     # Add summary of annotations
#     if annotations_found:
#         html_content.append('<div class="metadata">')
#         html_content.append('<h3>Annotations Summary</h3>')
        
#         annotation_types = {}
#         for annot in annotations_found:
#             annot_type = annot['type']
#             annotation_types[annot_type] = annotation_types.get(annot_type, 0) + 1
        
#         html_content.append('<ul>')
#         for annot_type, count in annotation_types.items():
#             html_content.append(f'<li>{annot_type}: {count}</li>')
#         html_content.append('</ul>')
#         html_content.append('</div>')
    
#     # Close HTML
#     html_content.append("""</body>
# </html>""")
    
#     # Write HTML file
#     try:
#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write('\n'.join(html_content))
        
#         # Save annotations as JSON for reference
#         if annotations_found:
#             json_path = Path(output_path).with_suffix('.annotations.json')
#             with open(json_path, 'w', encoding='utf-8') as f:
#                 json.dump(annotations_found, f, indent=2)  # Set a breakpoint for debugging
#         len_doc = len(doc)
#         doc.close()
        
#         return {
#             "success": True,
#             "html_file": output_path,
#             "annotations_count": len(annotations_found),
#             "pages_processed": len_doc,
#             "has_text": has_text,
#             "annotations_file": str(json_path) if annotations_found else None
#         }
    
#     except Exception as e:
#         doc.close()
#         return {"success": False, "error": f"Error writing files: {e}"}

# def find_tables_in_page(page):
#     """
#     Basic table detection using text positioning
#     This is a simplified approach - for better results, consider using libraries like camelot-py
#     """
#     tables = []
#     try:
#         # Get text with position information
#         blocks = page.get_text("dict")
        
#         # Look for patterns that might indicate tables
#         # This is a basic implementation - real table detection is complex
#         text_elements = []
        
#         for block in blocks["blocks"]:
#             if "lines" in block:
#                 for line in block["lines"]:
#                     for span in line["spans"]:
#                         if span["text"].strip():
#                             text_elements.append({
#                                 'text': span["text"].strip(),
#                                 'x': span["bbox"][0],
#                                 'y': span["bbox"][1],
#                                 'width': span["bbox"][2] - span["bbox"][0],
#                                 'height': span["bbox"][3] - span["bbox"][1]
#                             })
        
#         # Simple heuristic: if we have aligned text elements, it might be a table
#         # This is very basic and would need improvement for real use
        
#     except Exception as e:
#         print(f"Error detecting tables: {e}")
    
#     return tables

# def convert_table_to_html(table_data):
#     """Convert table data to HTML table format"""
#     if not table_data:
#         return ""
    
#     html = ['<table class="pdf-table">']
    
#     for i, row in enumerate(table_data):
#         if i == 0:
#             html.append('<thead><tr>')
#             for cell in row:
#                 html.append(f'<th>{html.escape(str(cell))}</th>')
#             html.append('</tr></thead><tbody>')
#         else:
#             html.append('<tr>')
#             for cell in row:
#                 html.append(f'<td>{html.escape(str(cell))}</td>')
#             html.append('</tr>')
    
#     html.append('</tbody></table>')
#     return '\n'.join(html)

# # Example usage
# if __name__ == "__main__":
#     pdf_file = "uploads/b.pdf"  # Replace with your PDF file path
    
#     if os.path.exists(pdf_file):
#         result = pdf_to_html_advanced(
#             pdf_path=pdf_file,
#             include_images=True,
#             preserve_formatting=True,
#             include_annotations=True,
#             extract_tables=True,
#             password=None  # Add password if needed
#         )
#         if result["success"]:
#             print(f"✓ Conversion successful!")
#             print(f"HTML file: {result['html_file']}")
#             print(f"Pages processed: {result['pages_processed']}")
#             print(f"Annotations found: {result['annotations_count']}")
#             if result.get('annotations_file'):
#                 print(f"Annotations saved to: {result['annotations_file']}")
            
#             if not result['has_text']:
#                 print("\n⚠️  Warning: Limited text found. This may be a scanned PDF.")
#                 print("For better results with scanned PDFs, consider using OCR:")
#                 print("pip install pytesseract pillow")
#         else:
#             print(f"✗ Conversion failed: {result['error']}")
#     else:
#         print(f"PDF file '{pdf_file}' not found.")
#         print("\nFeatures of this enhanced converter:")
#         print("✓ Highlights and sticky notes extraction")
#         print("✓ Password-protected PDF support")
#         print("✓ Scanned PDF detection")
#         print("✓ Table detection (basic)")
#         print("✓ Image extraction")
#         print("✓ Metadata extraction")
#         print("✓ Annotation summary")
# import os
# import json
# import time
# import base64
# from pathlib import Path
# from typing import Dict, List, Any, Optional, Union
# import fitz  # PyMuPDF - fastest option
# import pdfplumber  # Good for tables
# from pypdf import PdfReader  # Basic but fast
# import pymupdf4llm  # For better markdown conversion
# from PIL import Image
# import io
# import traceback
# from datetime import datetime
# import time

# start_time = time.time() 

# # Additional imports for enhanced functionality
# try:
#     import pandas as pd
#     HAS_PANDAS = True
# except ImportError:
#     HAS_PANDAS = False

# class EnhancedPDFConverter:
#     """Enhanced PDF converter with full format preservation and interactive features"""
    
#     def __init__(self, output_dir: str = "enhanced_conversion"):
#         self.output_dir = output_dir
#         self.ensure_directory_exists(output_dir)
#         self.conversion_stats = {
#             'start_time': None,
#             'end_time': None,
#             'pages_processed': 0,
#             'images_extracted': 0,
#             'tables_extracted': 0,
#             'annotations_found': 0,
#             'errors': []
#         }
        
#     def ensure_directory_exists(self, directory: str):
#         """Create directory if it doesn't exist"""
#         try:
#             Path(directory).mkdir(parents=True, exist_ok=True)
#         except Exception as e:
#             print(f"Warning: Could not create directory {directory}: {e}")
    
#     def make_json_serializable(self, obj: Any) -> Any:
#         """Convert objects to JSON-serializable format"""
#         try:
#             if isinstance(obj, bytes):
#                 try:
#                     return base64.b64encode(obj).decode('utf-8')
#                 except Exception:
#                     return f"<bytes object of length {len(obj)}>"
#             elif isinstance(obj, (datetime,)):
#                 return obj.isoformat()
#             elif hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool)):
#                 return str(obj)
#             elif isinstance(obj, (list, tuple)):
#                 return [self.make_json_serializable(item) for item in obj]
#             elif isinstance(obj, dict):
#                 return {str(key): self.make_json_serializable(value) for key, value in obj.items()}
#             elif obj is None:
#                 return None
#             elif isinstance(obj, (str, int, float, bool)):
#                 return obj
#             else:
#                 return str(obj)
#         except Exception as e:
#             self.conversion_stats['errors'].append(f"Serialization error: {e}")
#             return f"<serialization error: {type(obj).__name__}>"
    
#     def extract_image_with_metadata(self, doc, xref: int, page_num: int, save_base64: bool = False) -> Optional[Dict]:
#         """Extract image with full metadata and optional base64 encoding"""
#         try:
#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
#             image_ext = base_image["ext"]
            
#             # Convert to PIL Image for additional processing
#             try:
#                 image = Image.open(io.BytesIO(image_bytes))
#             except Exception as e:
#                 print(f"Warning: Could not process image {xref} with PIL: {e}")
#                 # Create basic metadata without PIL
#                 image_data = {
#                     'xref': int(xref),
#                     'page': int(page_num),
#                     'extension': str(image_ext),
#                     'width': 0,
#                     'height': 0,
#                     'mode': 'unknown',
#                     'format': 'unknown',
#                     'size_bytes': len(image_bytes),
#                     'filename': f"page_{page_num}_img_{xref}.{image_ext}",
#                     'extraction_error': str(e)
#                 }
#                 if save_base64:
#                     try:
#                         image_data['base64'] = base64.b64encode(image_bytes).decode('utf-8')
#                     except Exception:
#                         image_data['base64'] = ""
#                 return image_data
            
#             # Get image metadata safely
#             image_data = {
#                 'xref': int(xref),
#                 'page': int(page_num),
#                 'extension': str(image_ext),
#                 'width': int(image.width),
#                 'height': int(image.height),
#                 'mode': str(image.mode),
#                 'format': str(image.format) if image.format else "unknown",
#                 'size_bytes': len(image_bytes),
#                 'filename': f"page_{page_num}_img_{xref}.{image_ext}"
#             }
            
#             # Only include base64 if explicitly requested (for HTML output)
#             if save_base64:
#                 try:
#                     image_data['base64'] = base64.b64encode(image_bytes).decode('utf-8')
#                 except Exception as e:
#                     print(f"Warning: Could not encode image {xref} to base64: {e}")
#                     image_data['base64'] = ""
            
#             # Store raw bytes separately for saving to disk
#             image_data['_raw_bytes'] = image_bytes  # This will be removed before JSON serialization
            
#             self.conversion_stats['images_extracted'] += 1
#             return image_data
            
#         except Exception as e:
#             error_msg = f"Error extracting image {xref} on page {page_num}: {e}"
#             print(error_msg)
#             self.conversion_stats['errors'].append(error_msg)
#             return None
    
#     def extract_annotations(self, page) -> List[Dict]:
#         """Extract all annotations from a page"""
#         annotations = []
        
#         try:
#             annot_list = page.annots()
#             for annot in annot_list:
#                 try:
#                     annot_dict = {
#                         'type': str(annot.type[1]) if annot.type else 'unknown',
#                         'rect': [float(x) for x in annot.rect] if annot.rect else [],
#                         'content': str(annot.info.get('content', '')),
#                         'author': str(annot.info.get('title', '')),
#                         'page': int(page.number + 1),
#                         'creation_date': str(annot.info.get('creationDate', '')),
#                         'modification_date': str(annot.info.get('modDate', ''))
#                     }
                    
#                     # Add any additional annotation info safely
#                     for key, value in annot.info.items():
#                         if key not in annot_dict:
#                             annot_dict[key] = self.make_json_serializable(value)
                    
#                     annotations.append(annot_dict)
#                     self.conversion_stats['annotations_found'] += 1
                    
#                 except Exception as e:
#                     error_msg = f"Error processing annotation: {e}"
#                     print(error_msg)
#                     self.conversion_stats['errors'].append(error_msg)
                
#         except Exception as e:
#             error_msg = f"Error extracting annotations from page {page.number + 1}: {e}"
#             print(error_msg)
#             self.conversion_stats['errors'].append(error_msg)
            
#         return annotations
    
#     def extract_fonts_and_styles(self, page) -> Dict:
#         """Extract font and style information for format preservation"""
#         fonts_info = {}
        
#         try:
#             text_dict = page.get_text("dict")
            
#             for block in text_dict.get("blocks", []):
#                 if "lines" in block:
#                     for line in block["lines"]:
#                         for span in line.get("spans", []):
#                             try:
#                                 font_info = {
#                                     'font': str(span.get('font', '')),
#                                     'size': float(span.get('size', 0)),
#                                     'flags': int(span.get('flags', 0)),
#                                     'color': int(span.get('color', 0)),
#                                     'bbox': [float(x) for x in span.get('bbox', [])]
#                                 }
                                
#                                 font_key = f"{span.get('font', 'unknown')}_{span.get('size', 0)}"
#                                 if font_key not in fonts_info:
#                                     fonts_info[font_key] = font_info
#                             except Exception as e:
#                                 continue  # Skip problematic spans
                                
#         except Exception as e:
#             error_msg = f"Error extracting fonts: {e}"
#             print(error_msg)
#             self.conversion_stats['errors'].append(error_msg)
            
#         return fonts_info
    
#     def safe_get_text(self, page, method: str = "text") -> str:
#         """Safely extract text from page"""
#         try:
#             if method == "dict":
#                 return page.get_text("dict")
#             else:
#                 text = page.get_text()
#                 return str(text) if text else ""
#         except Exception as e:
#             error_msg = f"Error extracting text: {e}"
#             print(error_msg)
#             self.conversion_stats['errors'].append(error_msg)
#             return ""
    
#     def convert_with_full_preservation(self, file_path: str) -> Optional[Dict]:
#         """Enhanced conversion with maximum format preservation"""
#         self.conversion_stats['start_time'] = time.time()
        
#         try:
#             doc = fitz.open(file_path)
            
#             # Safely extract metadata
#             metadata = {}
#             try:
#                 raw_metadata = doc.metadata
#                 for key, value in raw_metadata.items():
#                     metadata[key] = self.make_json_serializable(value)
#             except Exception as e:
#                 print(f"Warning: Could not extract metadata: {e}")
#                 metadata = {'error': str(e)}
            
#             results = {
#                 'metadata': {
#                     'filename': str(Path(file_path).name),
#                     'total_pages': len(doc),
#                     'creation_date': metadata.get('creationDate', ''),
#                     'modification_date': metadata.get('modDate', ''),
#                     'author': metadata.get('author', ''),
#                     'title': metadata.get('title', ''),
#                     'subject': metadata.get('subject', ''),
#                     'creator': metadata.get('creator', ''),
#                     'producer': metadata.get('producer', ''),
#                     'format': metadata.get('format', ''),
#                     'encryption': metadata.get('encryption', ''),
#                 },
#                 'pages': [],
#                 'images': {},
#                 'fonts': {},
#                 'annotations': [],
#                 'text_extraction': {
#                     'plain_text': '',
#                     'markdown': '',
#                     'html': '',
#                     'structured_json': []
#                 },
#                 'tables': [],
#                 'links': [],
#                 'toc': [],
#                 'page_layouts': [],
#                 'conversion_stats': {}
#             }
            
#             # Safely extract table of contents
#             try:
#                 toc = doc.get_toc()
#                 results['toc'] = self.make_json_serializable(toc)
#             except Exception as e:
#                 print(f"Warning: Could not extract TOC: {e}")
#                 results['toc'] = []
            
#             # Process each page
#             for page_num in range(len(doc)):
#                 try:
#                     page = doc.load_page(page_num)
#                     page_data = self._process_page_comprehensive(page, page_num, doc)
#                     results['pages'].append(page_data)
                    
#                     # Aggregate data safely
#                     try:
#                         results['text_extraction']['plain_text'] += f"\n--- Page {page_num + 1} ---\n{page_data.get('text', '')}\n"
#                     except Exception as e:
#                         print(f"Warning: Could not aggregate text for page {page_num + 1}: {e}")
                    
#                     results['annotations'].extend(page_data.get('annotations', []))
#                     results['fonts'].update(page_data.get('fonts', {}))
#                     results['tables'].extend(page_data.get('tables', []))
#                     results['links'].extend(page_data.get('links', []))
                    
#                     # Store images with unique keys (without base64 for JSON)
#                     for img in page_data.get('images', []):
#                         img_key = f"page_{page_num + 1}_img_{img['xref']}"
#                         # Remove raw bytes before storing
#                         img_clean = {k: v for k, v in img.items() if k != '_raw_bytes'}
#                         results['images'][img_key] = img_clean
                    
#                     self.conversion_stats['pages_processed'] += 1
                    
#                 except Exception as e:
#                     error_msg = f"Error processing page {page_num + 1}: {e}"
#                     print(error_msg)
#                     self.conversion_stats['errors'].append(error_msg)
#                     continue
            
#             # Generate enhanced markdown and HTML
#             try:
#                 results['text_extraction']['markdown'] = pymupdf4llm.to_markdown(file_path)
#             except Exception as e:
#                 print(f"Warning: pymupdf4llm failed, using fallback: {e}")
#                 results['text_extraction']['markdown'] = self._generate_enhanced_markdown(results)
            
#             try:
#                 results['text_extraction']['html'] = self._generate_enhanced_html(results, file_path, doc)
#             except Exception as e:
#                 print(f"Warning: HTML generation failed: {e}")
#                 results['text_extraction']['html'] = f"<html><body><h1>HTML generation failed: {e}</h1></body></html>"
            
#             try:
#                 results['text_extraction']['structured_json'] = self._generate_structured_data(results)
#             except Exception as e:
#                 print(f"Warning: Structured data generation failed: {e}")
#                 results['text_extraction']['structured_json'] = []
            
#             # Add conversion stats
#             self.conversion_stats['end_time'] = time.time()
#             results['conversion_stats'] = self.conversion_stats.copy()
            
#             doc.close()
#             return results
            
#         except Exception as e:
#             error_msg = f"Critical error in conversion: {e}"
#             print(error_msg)
#             print(traceback.format_exc())
#             self.conversion_stats['errors'].append(error_msg)
#             self.conversion_stats['end_time'] = time.time()
#             return None
    
#     def _process_page_comprehensive(self, page, page_num: int, doc) -> Dict:
#         """Process a single page comprehensively"""
#         page_data = {
#             'page_number': page_num + 1,
#             'mediabox': [float(x) for x in page.mediabox],
#             'rotation': int(page.rotation),
#             'text': self.safe_get_text(page),
#             'text_blocks': {},
#             'images': [],
#             'tables': [],
#             'annotations': [],
#             'fonts': {},
#             'links': [],
#             'drawings': [],
#             'layout_analysis': {}
#         }
        
#         # Extract text blocks safely
#         try:
#             text_blocks = page.get_text("dict")
#             page_data['text_blocks'] = self.make_json_serializable(text_blocks)
#         except Exception as e:
#             print(f"Warning: Could not extract text blocks for page {page_num + 1}: {e}")
#             page_data['text_blocks'] = {}
        
#         # Extract annotations
#         try:
#             page_data['annotations'] = self.extract_annotations(page)
#         except Exception as e:
#             print(f"Warning: Annotation extraction failed for page {page_num + 1}: {e}")
#             page_data['annotations'] = []
        
#         # Extract fonts
#         try:
#             page_data['fonts'] = self.extract_fonts_and_styles(page)
#         except Exception as e:
#             print(f"Warning: Font extraction failed for page {page_num + 1}: {e}")
#             page_data['fonts'] = {}
        
#         # Extract images with metadata (without base64 for main data)
#         try:
#             image_list = page.get_images()
#             for img_index, img in enumerate(image_list):
#                 xref = img[0]
#                 image_data = self.extract_image_with_metadata(doc, xref, page_num + 1, save_base64=False)
#                 if image_data:
#                     page_data['images'].append(image_data)
#         except Exception as e:
#             print(f"Warning: Image extraction failed for page {page_num + 1}: {e}")
#             page_data['images'] = []
        
#         # Extract tables with enhanced detection
#         try:
#             tables = page.find_tables()
#             for table_index, table in enumerate(tables):
#                 try:
#                     table_data = {
#                         'page': page_num + 1,
#                         'table_index': table_index,
#                         'bbox': [float(x) for x in table.bbox],
#                         'data': [],
#                         'header': None,
#                         'cells_count': 0
#                     }
                    
#                     # Extract table data safely
#                     try:
#                         extracted_data = table.extract()
#                         if extracted_data:
#                             # Clean the data
#                             clean_data = []
#                             for row in extracted_data:
#                                 clean_row = [str(cell) if cell is not None else "" for cell in row]
#                                 clean_data.append(clean_row)
                            
#                             table_data['data'] = clean_data
                            
#                             # Try to identify header row
#                             if clean_data and len(clean_data) > 0:
#                                 table_data['header'] = clean_data[0]
#                                 table_data['cells_count'] = sum(len(row) for row in clean_data)
                    
#                     except Exception as e:
#                         print(f"Warning: Could not extract table data: {e}")
#                         table_data['extraction_error'] = str(e)
                    
#                     page_data['tables'].append(table_data)
#                     self.conversion_stats['tables_extracted'] += 1
                    
#                 except Exception as e:
#                     print(f"Error processing table {table_index} on page {page_num + 1}: {e}")
#         except Exception as e:
#             print(f"Warning: Table detection failed for page {page_num + 1}: {e}")
#             page_data['tables'] = []
        
#         # Extract links safely
#         try:
#             links = page.get_links()
#             for link in links:
#                 safe_link = {
#                     'kind': int(link.get('kind', 0)),
#                     'from': [float(x) for x in link.get('from', [])],
#                     'uri': str(link.get('uri', '')),
#                     'page': int(link.get('page', -1))
#                 }
#                 page_data['links'].append(safe_link)
#         except Exception as e:
#             print(f"Warning: Link extraction failed for page {page_num + 1}: {e}")
#             page_data['links'] = []
        
#         # Extract drawings/vector graphics safely
#         try:
#             drawings = page.get_drawings()
#             safe_drawings = []
#             for drawing in drawings:
#                 safe_drawing = {
#                     'rect': [float(x) for x in drawing.get('rect', [])],
#                     'items': len(drawing.get('items', []))
#                 }
#                 safe_drawings.append(safe_drawing)
#             page_data['drawings'] = safe_drawings
#         except Exception as e:
#             print(f"Warning: Drawing extraction failed for page {page_num + 1}: {e}")
#             page_data['drawings'] = []
        
#         return page_data
    
#     def _generate_enhanced_markdown(self, results: Dict) -> str:
#         """Generate enhanced markdown with preserved formatting"""
#         try:
#             md_content = f"# {results['metadata']['title'] or 'PDF Document'}\n\n"
            
#             if results['metadata']['author']:
#                 md_content += f"**Author:** {results['metadata']['author']}\n\n"
            
#             for page in results['pages']:
#                 md_content += f"## Page {page['page_number']}\n\n"
#                 md_content += str(page.get('text', '')) + "\n\n"
                
#                 # Add table information
#                 if page.get('tables'):
#                     md_content += "### Tables on this page:\n\n"
#                     for i, table in enumerate(page['tables']):
#                         md_content += f"#### Table {i+1}\n\n"
#                         if HAS_PANDAS and table.get('data'):
#                             try:
#                                 df = pd.DataFrame(table['data'][1:], columns=table['data'][0])
#                                 md_content += df.to_markdown(index=False) + "\n\n"
#                             except Exception as e:
#                                 md_content += f"Table data available (conversion error: {e}).\n\n"
                
#                 # Add image information
#                 if page.get('images'):
#                     md_content += f"### Images on this page: {len(page['images'])}\n\n"
            
#             return md_content
#         except Exception as e:
#             error_msg = f"Error generating markdown: {e}"
#             print(error_msg)
#             return f"# Markdown Generation Error\n\n{error_msg}"
    
#     def _generate_enhanced_html(self, results: Dict, file_path: str, doc) -> str:
#         """Generate enhanced HTML with preserved formatting and embedded images"""
#         try:
#             html_content = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{results['metadata']['title'] or 'PDF Document'}</title>
#     <style>
#         body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
#         .page {{ border: 1px solid #ccc; margin: 20px 0; padding: 20px; }}
#         .page-header {{ background: #f5f5f5; padding: 10px; margin: -20px -20px 20px -20px; }}
#         .annotation {{ background: yellow; opacity: 0.3; }}
#         .table-container {{ margin: 20px 0; overflow-x: auto; }}
#         table {{ border-collapse: collapse; width: 100%; }}
#         th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
#         th {{ background-color: #f2f2f2; }}
#         .image-container {{ margin: 20px 0; text-align: center; }}
#         .image-container img {{ max-width: 100%; height: auto; }}
#         .metadata {{ background: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px; }}
#         .error {{ background: #ffe6e6; padding: 10px; margin: 10px 0; border-left: 4px solid #ff4444; }}
#     </style>
# </head>
# <body>
#     <h1>{results['metadata']['title'] or 'PDF Document'}</h1>
#             """
            
#             # Add metadata
#             if results['metadata']['author']:
#                 html_content += f"<p><strong>Author:</strong> {results['metadata']['author']}</p>"
            
#             # Process pages
#             for page in results['pages']:
#                 html_content += f"""
#     <div class="page" id="page-{page['page_number']}">
#         <div class="page-header">
#             <h2>Page {page['page_number']}</h2>
#         </div>
#         <div class="content">
#             {str(page.get('text', '')).replace(chr(10), '<br>')}
#         </div>
#                 """
                
#                 # Add images with base64 embedding for HTML
#                 for img in page.get('images', []):
#                     try:
#                         # Re-extract image with base64 for HTML embedding
#                         if '_raw_bytes' in img:
#                             raw_bytes = img['_raw_bytes']
#                         else:
#                             # Re-extract from document
#                             base_image = doc.extract_image(img['xref'])
#                             raw_bytes = base_image["image"]
                        
#                         base64_data = base64.b64encode(raw_bytes).decode('utf-8')
                        
#                         html_content += f"""
#         <div class="image-container">
#             <img src="data:image/{img['extension']};base64,{base64_data}" 
#                  alt="Page {img['page']} Image" 
#                  title="Image: {img['filename']}" />
#             <p><small>{img['filename']} ({img['width']}x{img['height']})</small></p>
#         </div>
#                         """
#                     except Exception as e:
#                         html_content += f"""
#         <div class="error">
#             <p>Error loading image: {img.get('filename', 'unknown')} - {e}</p>
#         </div>
#                         """
                
#                 # Add tables
#                 for table in page.get('tables', []):
#                     if table.get('data'):
#                         try:
#                             html_content += '<div class="table-container"><table>'
#                             for row_idx, row in enumerate(table['data']):
#                                 tag = 'th' if row_idx == 0 else 'td'
#                                 html_content += '<tr>'
#                                 for cell in row:
#                                     html_content += f'<{tag}>{str(cell) if cell else ""}</{tag}>'
#                                 html_content += '</tr>'
#                             html_content += '</table></div>'
#                         except Exception as e:
#                             html_content += f'<div class="error">Error rendering table: {e}</div>'
                
#                 html_content += "</div>"
            
#             # Add conversion statistics
#             if self.conversion_stats.get('errors'):
#                 html_content += """
#     <div class="metadata">
#         <h3>Conversion Notes</h3>
#         <ul>
#                 """
#                 for error in self.conversion_stats['errors'][:10]:  # Show first 10 errors
#                     html_content += f"<li>{error}</li>"
#                 html_content += "</ul></div>"
            
#             html_content += """
# </body>
# </html>
#             """
            
#             return html_content
            
#         except Exception as e:
#             error_msg = f"Error generating HTML: {e}"
#             print(error_msg)
#             return f"<html><body><h1>HTML Generation Error</h1><p>{error_msg}</p></body></html>"
    
#     def _generate_structured_data(self, results: Dict) -> List[Dict]:
#         """Generate structured data optimized for AI/embedding use"""
#         structured_data = []
        
#         try:
#             for page in results['pages']:
#                 # Text chunks for embedding
#                 text_blocks = page.get('text_blocks', {})
#                 if isinstance(text_blocks, dict) and 'blocks' in text_blocks:
#                     for block_idx, block in enumerate(text_blocks['blocks']):
#                         if 'lines' in block:
#                             block_text = ""
#                             fonts_used = []
#                             font_sizes = []
                            
#                             for line in block['lines']:
#                                 for span in line.get('spans', []):
#                                     span_text = span.get('text', '')
#                                     if span_text:
#                                         block_text += span_text
#                                         fonts_used.append(str(span.get('font', '')))
#                                         font_sizes.append(float(span.get('size', 0)))
                            
#                             if block_text.strip():
#                                 structured_data.append({
#                                     'type': 'text_block',
#                                     'page': page['page_number'],
#                                     'block_index': block_idx,
#                                     'content': block_text.strip(),
#                                     'bbox': [float(x) for x in block.get('bbox', [])],
#                                     'metadata': {
#                                         'fonts': list(set(fonts_used)),
#                                         'font_sizes': list(set(font_sizes))
#                                     }
#                                 })
                
#                 # Table data for embedding
#                 for table_idx, table in enumerate(page.get('tables', [])):
#                     if table.get('data'):
#                         structured_data.append({
#                             'type': 'table',
#                             'page': page['page_number'],
#                             'table_index': table_idx,
#                             'content': str(table['data']),
#                             'header': table.get('header', []),
#                             'cells_count': table.get('cells_count', 0),
#                             'bbox': table.get('bbox', [])
#                         })
                
#                 # Image metadata for AI
#                 for img_idx, img in enumerate(page.get('images', [])):
#                     structured_data.append({
#                         'type': 'image',
#                         'page': page['page_number'],
#                         'image_index': img_idx,
#                         'content': f"Image: {img['filename']} ({img['width']}x{img['height']})",
#                         'metadata': {
#                             'filename': img['filename'],
#                             'dimensions': [img['width'], img['height']],
#                             'size_bytes': img['size_bytes'],
#                             'extension': img['extension']
#                         }
#                     })
        
#         except Exception as e:
#             error_msg = f"Error generating structured data: {e}"
#             print(error_msg)
#             structured_data.append({
#                 'type': 'error',
#                 'content': error_msg,
#                 'page': 0
#             })
        
#         return structured_data
    
#     def save_comprehensive_results(self, results: Dict, base_filename: str) -> Dict[str, str]:
#         """Save all conversion results with organized structure"""
#         base_name = Path(base_filename).stem
#         saved_files = {}
        
#         # Create organized directory structure
#         main_dir = os.path.join(self.output_dir, base_name)
#         self.ensure_directory_exists(main_dir)
        
#         # Prepare JSON-safe version of results (remove raw bytes)
#         json_safe_results = self.make_json_serializable(results)
        
#         # Save main content files
#         formats = {
#             'json': (json_safe_results, 'json'),
#             'markdown': (results['text_extraction']['markdown'], 'txt'),
#             'html': (results['text_extraction']['html'], 'txt'),
#             'plain_text': (results['text_extraction']['plain_text'], 'txt')
#         }
        
#         for format_name, (content, ext) in formats.items():
#             file_path = os.path.join(main_dir, f"{base_name}_{format_name}.{ext}")
            
#             try:
#                 if format_name == 'json':
#                     with open(file_path, 'w', encoding='utf-8') as f:
#                         json.dump(content, f, indent=2, ensure_ascii=False)
#                 else:
#                     with open(file_path, 'w', encoding='utf-8') as f:
#                         f.write(str(content))
                
#                 saved_files[format_name] = file_path
#                 print(f"✅ Saved {format_name}: {file_path}")
                
#             except Exception as e:
#                 error_msg = f"❌ Error saving {format_name}: {e}"
#                 print(error_msg)
#                 self.conversion_stats['errors'].append(error_msg)
        
#         # Save images separately (extract from original data)
#         if results.get('pages'):
#             images_dir = os.path.join(main_dir, "images")
#             self.ensure_directory_exists(images_dir)
            
#             for page in results['pages']:
#                 for img_data in page.get('images', []):
#                     try:
#                         if '_raw_bytes' in img_data:
#                             img_path = os.path.join(images_dir, img_data['filename'])
                            
#                             with open(img_path, 'wb') as f:
#                                 f.write(img_data['_raw_bytes'])
                            
#                             print(f"✅ Saved image: {img_path}")
                            
#                     except Exception as e:
#                         error_msg = f"❌ Error saving image {img_data.get('filename', 'unknown')}: {e}"
#                         print(error_msg)
#                         self.conversion_stats['errors'].append(error_msg)
        
#         # Save tables as CSV
#         if results.get('tables'):
#             tables_dir = os.path.join(main_dir, "tables")
#             self.ensure_directory_exists(tables_dir)
            
#             for table in results['tables']:
#                 try:
#                     if table.get('data'):
#                         csv_path = os.path.join(tables_dir, f"page_{table['page']}_table_{table['table_index']}.csv")
                        
#                         if HAS_PANDAS:
#                             try:
#                                 # Create DataFrame safely
#                                 data = table['data']
#                                 if len(data) > 1:
#                                     df = pd.DataFrame(data[1:], columns=data[0])
#                                 else:
#                                     df = pd.DataFrame(data)
#                                 df.to_csv(csv_path, index=False, encoding='utf-8')
#                             except Exception as e:
#                                 # Fallback to manual CSV writing
#                                 import csv
#                                 with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
#                                     writer = csv.writer(csvfile)
#                                     writer.writerows(table['data'])
#                         else:
#                             import csv
#                             with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
#                                 writer = csv.writer(csvfile)
#                                 writer.writerows(table['data'])
                        
#                         print(f"✅ Saved table: {csv_path}")
                        
#                 except Exception as e:
#                     error_msg = f"❌ Error saving table: {e}"
#                     print(error_msg)
#                     self.conversion_stats['errors'].append(error_msg)
        
#         # Save structured data for AI/embeddings
#         structured_path = os.path.join(main_dir, f"{base_name}_structured_for_ai.json")
#         try:
#             structured_data = self.make_json_serializable(results['text_extraction']['structured_json'])
#             with open(structured_path, 'w', encoding='utf-8') as f:
#                 json.dump(structured_data, f, indent=2, ensure_ascii=False)
#             saved_files['structured_ai'] = structured_path
#             print(f"✅ Saved AI-structured data: {structured_path}")
#         except Exception as e:
#             error_msg = f"❌ Error saving structured data: {e}"
#             print(error_msg)
#             self.conversion_stats['errors'].append(error_msg)
        
#         # Save conversion log
#         log_path = os.path.join(main_dir, f"{base_name}_conversion_log.txt")
#         try:
#             with open(log_path, 'w', encoding='utf-8') as f:
#                 f.write(f"PDF Conversion Log - {datetime.now().isoformat()}\n")
#                 f.write(f"=" * 50 + "\n\n")
#                 f.write(f"File: {base_filename}\n")
#                 f.write(f"Pages processed: {self.conversion_stats.get('pages_processed', 0)}\n")
#                 f.write(f"Images extracted: {self.conversion_stats.get('images_extracted', 0)}\n")
#                 f.write(f"Tables extracted: {self.conversion_stats.get('tables_extracted', 0)}\n")
#                 f.write(f"Annotations found: {self.conversion_stats.get('annotations_found', 0)}\n")
#                 f.write(f"Processing time: {self.conversion_stats.get('end_time', 0) - self.conversion_stats.get('start_time', 0):.2f} seconds\n\n")
                
#                 if self.conversion_stats.get('errors'):
#                     f.write("Errors encountered:\n")
#                     for i, error in enumerate(self.conversion_stats['errors'], 1):
#                         f.write(f"{i}. {error}\n")
#                 else:
#                     f.write("No errors encountered.\n")
            
#             saved_files['conversion_log'] = log_path
#             print(f"✅ Saved conversion log: {log_path}")
            
#         except Exception as e:
#             print(f"❌ Error saving conversion log: {e}")
        
#         return saved_files

#     def convert_pdf_with_fallbacks(self, file_path: str) -> Optional[Dict]:
#         """Convert PDF with multiple fallback methods"""
#         print(f"🚀 Starting PDF conversion with fallbacks...")
        
#         # Primary method: Full preservation
#         try:
#             print("📋 Attempting full preservation conversion...")
#             results = self.convert_with_full_preservation(file_path)
#             if results:
#                 print("✅ Full preservation conversion successful!")
#                 return results
#         except Exception as e:
#             print(f"❌ Full preservation failed: {e}")
        
#         # Fallback method 1: Basic conversion
#         try:
#             print("📋 Attempting basic conversion fallback...")
#             results = self._basic_conversion_fallback(file_path)
#             if results:
#                 print("✅ Basic conversion successful!")
#                 return results
#         except Exception as e:
#             print(f"❌ Basic conversion failed: {e}")
        
#         # Fallback method 2: Text-only conversion
#         try:
#             print("📋 Attempting text-only conversion fallback...")
#             results = self._text_only_fallback(file_path)
#             if results:
#                 print("✅ Text-only conversion successful!")
#                 return results
#         except Exception as e:
#             print(f"❌ Text-only conversion failed: {e}")
        
#         print("❌ All conversion methods failed!")
#         return None

#     def _basic_conversion_fallback(self, file_path: str) -> Optional[Dict]:
#         """Basic conversion without advanced features"""
#         try:
#             doc = fitz.open(file_path)
            
#             results = {
#                 'metadata': {
#                     'filename': str(Path(file_path).name),
#                     'total_pages': len(doc),
#                     'conversion_method': 'basic_fallback'
#                 },
#                 'pages': [],
#                 'text_extraction': {
#                     'plain_text': '',
#                     'markdown': '',
#                     'html': '<html><body>',
#                     'structured_json': []
#                 },
#                 'images': {},
#                 'tables': [],
#                 'annotations': [],
#                 'fonts': {},
#                 'links': [],
#                 'conversion_stats': self.conversion_stats.copy()
#             }
            
#             # Process pages with basic text extraction only
#             for page_num in range(len(doc)):
#                 try:
#                     page = doc.load_page(page_num)
#                     text = page.get_text()
                    
#                     page_data = {
#                         'page_number': page_num + 1,
#                         'text': str(text),
#                         'images': [],
#                         'tables': [],
#                         'annotations': [],
#                         'fonts': {},
#                         'links': []
#                     }
                    
#                     results['pages'].append(page_data)
#                     results['text_extraction']['plain_text'] += f"\n--- Page {page_num + 1} ---\n{text}\n"
#                     results['text_extraction']['html'] += f"<h2>Page {page_num + 1}</h2><p>{text.replace(chr(10), '<br>')}</p>"
                    
#                     self.conversion_stats['pages_processed'] += 1
                    
#                 except Exception as e:
#                     print(f"Warning: Error processing page {page_num + 1}: {e}")
#                     continue
            
#             results['text_extraction']['html'] += '</body></html>'
#             results['text_extraction']['markdown'] = results['text_extraction']['plain_text']
            
#             doc.close()
#             return results
            
#         except Exception as e:
#             print(f"Basic conversion fallback failed: {e}")
#             return None

#     def _text_only_fallback(self, file_path: str) -> Optional[Dict]:
#         """Minimal text-only conversion"""
#         try:
#             doc = fitz.open(file_path)
            
#             all_text = ""
#             pages_processed = 0
            
#             for page_num in range(len(doc)):
#                 try:
#                     page = doc.load_page(page_num)
#                     text = page.get_text()
#                     all_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
#                     pages_processed += 1
#                 except Exception as e:
#                     print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
#                     all_text += f"\n--- Page {page_num + 1} (Error) ---\nText extraction failed: {e}\n"
            
#             results = {
#                 'metadata': {
#                     'filename': str(Path(file_path).name),
#                     'total_pages': len(doc),
#                     'conversion_method': 'text_only_fallback'
#                 },
#                 'pages': [{'page_number': i+1, 'text': 'See plain_text for content'} for i in range(len(doc))],
#                 'text_extraction': {
#                     'plain_text': all_text,
#                     'markdown': all_text,
#                     'html': f'<html><body><pre>{all_text}</pre></body></html>',
#                     'structured_json': [{'type': 'full_text', 'content': all_text, 'page': 'all'}]
#                 },
#                 'images': {},
#                 'tables': [],
#                 'annotations': [],
#                 'fonts': {},
#                 'links': [],
#                 'conversion_stats': {
#                     'pages_processed': pages_processed,
#                     'images_extracted': 0,
#                     'tables_extracted': 0,
#                     'annotations_found': 0,
#                     'conversion_method': 'text_only_fallback'
#                 }
#             }
            
#             doc.close()
#             return results
            
#         except Exception as e:
#             print(f"Text-only fallback failed: {e}")
#             return None


# def main():
#     """Enhanced main function with comprehensive error handling"""
#     # Try multiple possible file locations
#     possible_paths = [
#         os.path.join(os.getcwd(), 'app', 'utils', 'uploads', 'math for ml.pdf'),
#         os.path.join(os.getcwd(), 'uploads', 'math for ml.pdf'),
#         os.path.join(os.getcwd(), 'math for ml.pdf'),
#     ]
    
#     file_path = None
#     for path in possible_paths:
#         if os.path.exists(path):
#             file_path = path
#             break
    
#     if not file_path:
#         print("🔍 Searching for PDF files in current directory...")
#         pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
#         if pdf_files:
#             file_path = pdf_files[0]
#             print(f"📁 Found PDF file: {file_path}")
#         else:
#             print("❌ No PDF files found. Please ensure a PDF file is available.")
#             print("📍 Searched locations:")
#             for path in possible_paths:
#                 print(f"   - {path}")
#             return
    
#     print("🚀 Enhanced PDF Converter with JSON Serialization Fix")
#     print("=" * 60)
#     print(f"📄 Processing: {file_path}")
    
#     converter = EnhancedPDFConverter()
#     start_time = time.time()
    
#     # Use the fallback conversion method
#     results = converter.convert_pdf_with_fallbacks(file_path)
    
#     if results:
#         end_time = time.time()
#         print(f"✅ Conversion completed in {end_time - start_time:.2f} seconds")
        
#         # Print summary
#         print("\n📊 Conversion Summary:")
#         print(f"   Pages: {results['metadata'].get('total_pages', 'unknown')}")
#         print(f"   Images: {len(results.get('images', {}))}")
#         print(f"   Tables: {len(results.get('tables', []))}")
#         print(f"   Annotations: {len(results.get('annotations', []))}")
#         print(f"   Text length: {len(results['text_extraction'].get('plain_text', ''))} characters")
        
#         if results.get('conversion_stats', {}).get('conversion_method'):
#             print(f"   Method used: {results['conversion_stats']['conversion_method']}")
        
#         # Save results
#         try:
#             saved_files = converter.save_comprehensive_results(results, os.path.basename(file_path))
            
#             print(f"\n📁 All files saved to: {converter.output_dir}/{Path(file_path).stem}/")
#             print("\n🎯 Successfully created:")
#             for format_type, file_path in saved_files.items():
#                 print(f"   ✅ {format_type}: {os.path.basename(file_path)}")
            
#             print("\n🎯 Ready for:")
#             print("   ✅ Interactive web application (JSON data available)")
#             print("   ✅ AI embeddings and search (structured data ready)")
#             print("   ✅ Format-preserved viewing (HTML with embedded images)")
#             print("   ✅ Data extraction and analysis (CSV tables available)")
            
#             # Print any errors encountered
#             if converter.conversion_stats.get('errors'):
#                 print(f"\n⚠️  {len(converter.conversion_stats['errors'])} warnings/errors encountered:")
#                 for error in converter.conversion_stats['errors'][:5]:  # Show first 5
#                     print(f"   • {error}")
#                 if len(converter.conversion_stats['errors']) > 5:
#                     print(f"   • ... and {len(converter.conversion_stats['errors']) - 5} more (see conversion log)")
#             else:
#                 print("\n✨ Conversion completed without errors!")
        
#         except Exception as e:
#             print(f"❌ Error saving results: {e}")
#             print("💾 Conversion completed but file saving failed")
        
#     else:
#         print("❌ All conversion methods failed")
#         print("💡 Possible solutions:")
#         print("   • Check if the PDF file is corrupted")
#         print("   • Ensure the PDF is not password protected")
#         print("   • Try with a different PDF file")
#         print("   • Check file permissions")
    
#     end_time = time.time()
#     processing_time = end_time - start_time
#     print(f"\nTotal processing time: {processing_time:.2f} seconds")

# if __name__ == "__main__":
#     main()



# doc_parser

# #  app/document_parser/docling_converter.py
# import os, json, csv
# from pathlib import Path
# from docling.document_converter import DocumentConverter
# import pdb
# import time

# start_time = time.time() 

# def convert_with_docling(file_path):
#     converter = DocumentConverter()
#     result = converter.convert(file_path)
#     pdb.set_trace()
#     return {
#         'html': result.document.export_to_html(),
#         'markdown': result.document.export_to_markdown(),
#         'json': result.document.export_to_dict(),
#         'structure': result.document.export_to_text(),
#         'tables': result.document.tables,
#         'images': result.document.pictures
#     }

# def save_converted_files(converted_data, original_file_path, output_dir="Conv_files"):
#     """
#     Save converted document data to files in the specified directory
#     """
#     # Create output directory if it doesn't exist
#     Path(output_dir).mkdir(exist_ok=True)
    
#     # Get base filename without extension
#     base_name = Path(original_file_path).stem
    
#     saved_files = {}
    
#     # Save HTML
#     html_path = Path(output_dir) / f"{base_name}.html"
#     with open(html_path, 'w', encoding='utf-8') as f:
#         f.write(converted_data['html'])
#     saved_files['html'] = str(html_path)
    
#     # Save Markdown
#     md_path = Path(output_dir) / f"{base_name}.md"
#     with open(md_path, 'w', encoding='utf-8') as f:
#         f.write(converted_data['markdown'])
#     saved_files['markdown'] = str(md_path)
    
#     # Save JSON
#     json_path = Path(output_dir) / f"{base_name}.json"
#     with open(json_path, 'w', encoding='utf-8') as f:
#         json.dump(converted_data['json'], f, indent=2, ensure_ascii=False)
#     saved_files['json'] = str(json_path)
    
#     # Save structure as text
#     if converted_data['structure']:
#         structure_path = Path(output_dir) / f"{base_name}_structure.txt"
#         with open(structure_path, 'w', encoding='utf-8') as f:
#             f.write(str(converted_data['structure']))
#         saved_files['structure'] = str(structure_path)
    
#     # Save tables as CSV if they exist
#     if converted_data['tables']:
#         tables_dir = Path(output_dir) / f"{base_name}_tables"
#         tables_dir.mkdir(exist_ok=True)
        
#         for i, table in enumerate(converted_data['tables']):
#             csv_path = tables_dir / f"table_{i+1}.csv"
            
#             # Convert table to CSV format
#             try:
#                 # Assuming table has a method to convert to rows/data
#                 # You might need to adjust this based on docling's table structure
#                 if hasattr(table, 'to_csv'):
#                     table.to_csv(csv_path)
#                 else:
#                     # Fallback: save as JSON if direct CSV conversion isn't available
#                     json_table_path = tables_dir / f"table_{i+1}.json"
#                     with open(json_table_path, 'w', encoding='utf-8') as f:
#                         json.dump(str(table), f, indent=2, ensure_ascii=False)
#                     saved_files[f'table_{i+1}'] = str(json_table_path)
#             except Exception as e:
#                 print(f"Error saving table {i+1}: {e}")
        
#         saved_files['tables_dir'] = str(tables_dir)
    
#     # Save images metadata if they exist
#     if converted_data['images']:
#         images_path = Path(output_dir) / f"{base_name}_images.json"
#         with open(images_path, 'w', encoding='utf-8') as f:
#             # Convert images to serializable format
#             images_data = []
#             for img in converted_data['images']:
#                 images_data.append(str(img))  # Convert to string representation
#             json.dump(images_data, f, indent=2, ensure_ascii=False)
#         saved_files['images'] = str(images_path)
    
#     return saved_files

# def process_document(file_path, output_dir="Conv_files"):
#     """
#     Complete pipeline: convert document and save all outputs
#     """
#     print(f"Processing: {file_path}")
    
#     try:
#         # Convert document
#         converted_data = convert_with_docling(file_path)
        
#         # Save converted files
#         saved_files = save_converted_files(converted_data, file_path, output_dir)
        
#         print(f"Conversion completed! Files saved:")
#         for file_type, file_path in saved_files.items():
#             print(f"  {file_type}: {file_path}")
        
#         return saved_files
        
#     except Exception as e:
#         print(f"Error processing {file_path}: {e}")
#         return None

# if __name__ == "__main__":
#     file_path = os.getcwd() + '/uploads/GAN.pdf'
    
#     # Process the document and save files
#     result = process_document(file_path)
    
#     # Calculate and display processing time
#     end_time = time.time()
#     processing_time = end_time - start_time
#     print(f"\nTotal processing time: {processing_time:.2f} seconds")
    
#     if result:
#         print(f"All files saved successfully in Conv_files folder!")
#     else:
#         print("Processing failed!")