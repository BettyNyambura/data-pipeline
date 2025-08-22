import difflib
import re
from dataclasses import dataclass
from typing import Dict, Tuple, List
import json
from pathlib import Path
import statistics
from tabulate import tabulate

@dataclass
class OCRQualityMetrics:
    character_accuracy: float = 0.0
    character_error_rate: float = 0.0
    word_accuracy: float = 0.0
    word_error_rate: float = 0.0
    line_accuracy: float = 0.0
    line_error_rate: float = 0.0
    edit_distance: int = 0
    insertion_errors: int = 0
    deletion_errors: int = 0
    substitution_errors: int = 0

class OCRQualityAssessor:
    def __init__(self):
        pass

    def load_file(self, file_path: str) -> str:
        return Path(file_path).read_text(encoding='utf-8').strip()

    def normalize_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text).strip().lower()

    def calculate_character_accuracy(self, gt: str, ext: str) -> Tuple[float, int, int, int, int]:
        gt_norm, ext_norm = self.normalize_text(gt), self.normalize_text(ext)
        matcher = difflib.SequenceMatcher(None, gt_norm, ext_norm)
        char_accuracy = matcher.ratio() * 100
        opcodes = matcher.get_opcodes()
        ins = sum(1 for op in opcodes if op[0] == 'insert')
        dels = sum(1 for op in opcodes if op[0] == 'delete')
        subs = sum(1 for op in opcodes if op[0] == 'replace')
        return char_accuracy, 100-char_accuracy, ins, dels, subs

    def calculate_word_accuracy(self, gt: str, ext: str) -> Tuple[float, float]:
        gt_words = self.normalize_text(gt).split()
        ext_words = self.normalize_text(ext).split()
        matcher = difflib.SequenceMatcher(None, gt_words, ext_words)
        acc = matcher.ratio() * 100
        return acc, 100-acc

    def calculate_line_accuracy(self, gt: str, ext: str) -> Tuple[float, float]:
        gt_lines = [self.normalize_text(l) for l in gt.splitlines() if l.strip()]
        ext_lines = [self.normalize_text(l) for l in ext.splitlines() if l.strip()]
        matcher = difflib.SequenceMatcher(None, gt_lines, ext_lines)
        acc = matcher.ratio() * 100
        return acc, 100-acc

    def assess_pair(self, gt_file: str, ocr_file: str) -> Dict:
        gt, ext = self.load_file(gt_file), self.load_file(ocr_file)

        char_acc, cer, ins, dels, subs = self.calculate_character_accuracy(gt, ext)
        word_acc, wer = self.calculate_word_accuracy(gt, ext)
        line_acc, ler = self.calculate_line_accuracy(gt, ext)

        return {
            "file": Path(gt_file).name,
            "character_accuracy": char_acc,
            "character_error_rate": cer,
            "word_accuracy": word_acc,
            "word_error_rate": wer,
            "line_accuracy": line_acc,
            "line_error_rate": ler,
            "insertion_errors": ins,
            "deletion_errors": dels,
            "substitution_errors": subs
        }

def batch_assessment(ground_truth_dir: str, output_dir: str, report_file="quality_report.json"):
    assessor = OCRQualityAssessor()
    gt_dir, out_dir = Path(ground_truth_dir), Path(output_dir)

    reports: List[Dict] = []
    for gt_file in gt_dir.glob("*.md"):
        ocr_file = out_dir / gt_file.name.replace("ground_truth_", "")
        if ocr_file.exists():
            report = assessor.assess_pair(gt_file, ocr_file)
            reports.append(report)
        else:
            print(f"⚠️ No OCR output for {gt_file.name}")

    # Compute averages
    avg_report = {}
    if reports:
        avg_report = {
            "file": "AVERAGE",
            "character_accuracy": statistics.mean(r["character_accuracy"] for r in reports),
            "word_accuracy": statistics.mean(r["word_accuracy"] for r in reports),
            "line_accuracy": statistics.mean(r["line_accuracy"] for r in reports),
        }
        reports.append(avg_report)

    final_report = {"per_file": reports, "averages": avg_report}

    # Save JSON
    with open(report_file, "w") as f:
        json.dump(final_report, f, indent=2)

    # Pretty table
    headers = ["File", "Char Acc (%)", "Word Acc (%)", "Line Acc (%)"]
    table = [
        [
            r["file"],
            f"{r['character_accuracy']:.2f}",
            f"{r['word_accuracy']:.2f}",
            f"{r['line_accuracy']:.2f}"
        ]
        for r in reports
    ]
    print("\n📊 OCR Quality Report:\n")
    print(tabulate(table, headers=headers, tablefmt="pretty"))

    print(f"\n💾 Report saved to {report_file}")
    return final_report

if __name__ == "__main__":
    batch_assessment("ground_truth", "output_files")
