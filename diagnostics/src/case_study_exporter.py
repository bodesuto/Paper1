import json
from pathlib import Path

class CaseStudyExporter:
    """Công cụ trích xuất và định dạng ví dụ suy luận cho bài báo Q1."""
    
    def __init__(self):
        self.output_dir = Path("reports/case_studies")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_latex(self, question: str, trace: str, final_answer: str, filename: str):
        """Xuất một tình huống suy luận sang định dạng LaTeX snippet."""
        latex_template = r"""
\begin{tcolorbox}[colback=gray!5,colframe=blue!75!black,title=Case Study: Reasoning Trace]
\textbf{Question:} %s \\
\textbf{Reasoning Traces:}
\begin{itemize}
%s
\end{itemize}
\textbf{Final Answer:} %s
\end{tcolorbox}
"""
        # Format trace steps
        steps = trace.split('\n')
        trace_items = "\n".join([f"    \\item {s.strip()}" for s in steps if s.strip()])
        
        content = latex_template % (question, trace_items, final_answer)
        
        with open(self.output_dir / f"{filename}.tex", "w", encoding="utf-8") as f:
            f.write(content)
        print(f">>> Đã xuất Case Study sang LaTeX: {filename}.tex")

    def export_to_markdown(self, question: str, trace: str, final_answer: str, filename: str):
        """Xuất ra định dạng Markdown đẹp để đưa vào README hoặc báo cáo."""
        md_content = f"""
### 🧪 Case Study: DualMemoryKG Reasoning

**Question:** `{question}`

**Tracing Deep Reasoning:**
> {trace.replace('\n', '\n> ')}

**🎯 Outcome:** **{final_answer}**
"""
        with open(self.output_dir / f"{filename}.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f">>> Đã xuất Case Study sang Markdown: {filename}.md")
