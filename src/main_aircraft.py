import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from src.utils.prompt.aircraft_prompt import build_aircraft_prompt
from src.utils.reader.file_reader import validate_file_type
from src.services.aircraft_service import extract_aircraft_from_pdf  
from src.services.database_service import get_db_service
from src.validators.aircraft_validator import (
    print_validation_results,
    validate_aircraft_utilization
)

async def main():
    print("✈️ Aircraft Utilization Data Extractor")
    print("=" * 50)
    
    db_service = None
    
    try:
        
        if len(sys.argv) > 1:
            input_path = Path(sys.argv[1]).resolve()
        else:
            input_path = Path(__file__).parent.parent / "samples" / "aircraft_report.pdf"
        
        print(f"\n📂 Processing file: {input_path}")
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        
        validate_file_type(str(input_path))
        if input_path.suffix.lower() != '.pdf':
            raise ValueError("Only PDF files are supported for aircraft reports")
        print("📄 Processing PDF file...")
        
        
        prompt = build_aircraft_prompt()
        
        
        print("\n🔄 Extracting data from PDF...")
        extracted_data = extract_aircraft_from_pdf(
            file_path=str(input_path),
            prompt=prompt,
            dpi=450  
        )
        print("✅ Received response from AI")
        
        
        print("\n🔍 Validating extracted data...")
        is_valid, warnings = validate_aircraft_utilization(extracted_data)
        print_validation_results(is_valid, warnings)
        
        
        print("\n💾 Saving to JSON file...")
        timestamp = int(datetime.now().timestamp())
        registration = extracted_data.registration or "unknown"
        month = extracted_data.month or "unknown"
            
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_filename = f"aircraft-{registration}-{month.replace(' ', '_')}-{timestamp}.json"
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data.model_dump(), f, indent=2, ensure_ascii=False)
        print(f"💾 JSON saved to: {output_path}")
        
        
        
        
        
        print("\n🗄️  Checking database...")
        db_service = get_db_service()
        record_id, is_new = await db_service.store_aircraft_data(extracted_data)
        
        if is_new:
            print(f"✅ Data stored in database with ID: {record_id}")
            
            
            print("\n📊 Verifying stored data...")
            stored_data = await db_service.get_aircraft_by_registration(
                registration=extracted_data.registration,
                month=extracted_data.month
            )
            
            if stored_data:
                print(f"✅ Verification successful!")
                print(f"   Registration: {stored_data.registration}")
              
            
            print("\n✅ AIRCRAFT DATA EXTRACTED AND STORED SUCCESSFULLY!")
        else:
            print(f"\n⚠️  DUPLICATE RECORD DETECTED!")
            print(f"   This data already exists in the database.")
            print(f"   Registration: {extracted_data.registration}")
        
        print("=" * 60)
            
            
           
        
        
        
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        
        if db_service:
            try:
                await db_service.disconnect()
            except Exception as e:
                print(f"⚠️  Warning: Error disconnecting from database: {e}")

if __name__ == "__main__":
    asyncio.run(main())