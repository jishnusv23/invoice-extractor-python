import sys 
import json 
from pathlib import Path
from datetime import datetime

from src.utils.prompt.aircraft_prompt import build_aircraft_prompt
from src.utils.reader.file_reader import validate_file_type
from src.services.aircraft_service import extract_aircraft_from_pdf
from src.validators.aircraft_validator import (
    print_validation_results,
    validate_aircraft_utilization
)

def main():
    print("✈️ Aircraft Utilization Data Extractor")
    print("=" * 50)

    try:
        # get input file path 
        if len(sys.argv) > 1:
            input_path = Path(sys.argv[1]).resolve()
        else:
            input_path = Path(__file__).parent.parent / "samples" / "aircraft_report.pdf"
        
        print(f"\n Processing file: {input_path}")

        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        validate_file_type(str(input_path))

        if input_path.suffix.lower() != '.pdf':
            raise ValueError("Only PDF files are supported for aircraft reports")

        print("📄 Processing PDF file...")

        prompt = build_aircraft_prompt()

        print("\n🔄 Extracting data from PDF...")
        extracted_data = extract_aircraft_from_pdf(str(input_path), prompt)
        print("✅ Received response from AI")

        
        print("\n🔍 Validating extracted data...")
        is_valid, warnings = validate_aircraft_utilization(extracted_data)
        print_validation_results(is_valid, warnings)

        print("\n💾 Saving to file...")
        timestamp = int(datetime.now().timestamp())
        registration = extracted_data.registration or "unknown"
        month = extracted_data.month or "unknown"
            
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)

        output_filename = f"aircraft-{registration}-{month.replace(' ', '_')}-{timestamp}.json"
        output_path = output_dir / output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data.model_dump(), f, indent=2, ensure_ascii=False)

        print(f"💾 Output saved to: {output_path}")
        print("\n✅ AIRCRAFT DATA EXTRACTED SUCCESSFULLY!")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
