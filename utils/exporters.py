from fpdf import FPDF
import json


def export_txt(summary: dict, output_path: str) -> None:
    """ Export summary to plain text file """
    with open(output_path, "w") as f:
        f.write("Meeting Summary\n")
        f.write("\nKey Points:\n")
        for point in summary["key_points"]:
            f.write(f"- {point}\n")
        f.write("\nAction Items:\n")
        for action in summary["action_items"]:
            f.write(f"- {action}\n")

def export_pdf(summary: dict, output_path: str) -> None:
    """ Generate pdf from a text """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Meeting Summary")
    pdf.multi_cell(0, 10, "\nKey Points:")
    for point in summary["key_points"]:
        pdf.multi_cell(0, 10, f"- {point}")
    pdf.multi_cell(0, 10, "\nAction Items:")
    for action in summary["action_items"]:
        pdf.multi_cell(0, 10, f"- {action}")
    pdf.output(output_path)

def export_html(summary: dict, output_path: str) -> None:
    """ Create an HTML summary with key points/actions"""

    html = f"""
    <html>
    <body>
        <h1>Meeting Summary</h1>
        <h2>Key Points</h2>
        <ul>
            {' '.join(f'<li>{point}</li>' for point in summary["key_points"])}
        </ul>
        <h2>Action Items</h2>
        <ul>
            {' '.join(f'<li>{action}</li' for action in summary["action_items"])}
        </ul>
    </body>
    </html>
    """
    with open(output_path, "w") as f:
        f.write(html)