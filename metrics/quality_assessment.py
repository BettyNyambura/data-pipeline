# Run this AFTER you've manually filled out ground_truth_complex2.md

from metrics import OCRQualityAssessor

def run_assessment():
    """Run quality assessment after ground truth is created"""
    
    # Create assessor
    assessor = OCRQualityAssessor()
    
    # File paths
    ground_truth_file = "metrics/ground_truth_complex2.md"  # Your manually filled file
    ocr_output_file = "metrics/comple2.md"                 # Your OCR result file
    
    print("🔄 Running OCR Quality Assessment...")
    print(f"📄 Ground Truth: {ground_truth_file}")
    print(f"📄 OCR Output: {ocr_output_file}")
    
    try:
        # Generate comprehensive report
        report = assessor.generate_quality_report(ground_truth_file, ocr_output_file)
        
        # Print the report
        assessor.print_quality_report(report)
        
        # Save detailed report to JSON
        import json
        with open("quality_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: quality_report.json")
        
        return report
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\n📝 Make sure you have:")
        print("1. ✅ Filled out ground_truth_complex2.md manually")
        print("2. ✅ Run your OCR to create complex2.md")
        print("3. ✅ Both files exist in current directory")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_assessment()