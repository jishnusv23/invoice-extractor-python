import sys
import os 
import json
from pathlib import Path
from datetime import datetime
from dataclasses import asdict
from src.utils.reader.file_reader import (
    read_file_as_buffer,
    validate_file_type,
    is_image,
)
from src.utils.prompt.prompt_buider import build_invoice_prompt
from src.services.openrouter_service import extract_invoice_from_image
from src.validators.invoice_validator import validate_invoice

def main():
    try:
        print("🚀 Invoice Data Extractor")

        
        if len(sys.argv) > 1:
            input_path = Path(sys.argv[1]).resolve()
        else:
            input_path = Path(__file__).parent.parent / "samples" / "invoice_3.jpg"

        print(f"\n📂 Processing file: {input_path}")

        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

 
        validate_file_type(str(input_path))

        if not is_image(str(input_path)):
            raise ValueError("Currently only image files are supported (.jpg, .png, .gif, .webp)")

        print("🖼️ Processing image file...")

        
        file_buffer, mime_type = read_file_as_buffer(str(input_path))

    
        prompt = build_invoice_prompt()
        
    
        extracted_data = extract_invoice_from_image(file_buffer, mime_type, prompt)
        print("✅ Received response from OpenRouter")


        is_valid = validate_invoice(extracted_data)
        if not is_valid:
            print("⚠️ Validation warning detected")
        else:
            print("✅ Validation passed")

      
        print("\n📊 EXTRACTED INVOICE DATA:")
        print("=" * 50)

        timestamp = int(datetime.now().timestamp())
        invoice_number = extracted_data.invoice_number or "unknown"

        
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / f"invoice-{invoice_number}-{timestamp}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(extracted_data), f, indent=2, ensure_ascii=False)

        print(f"\n💾 Output saved to: {output_path}")
        print("\n✅ INVOICE EXTRACTED SUCCESSFULLY!")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
