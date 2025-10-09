from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import logging

import subprocess
import sys
from typing import Dict, Any
from src.utils.prompt.aircraft_prompt import build_aircraft_prompt
from src.validators.aircraft_validator import validate_aircraft_utilization
from src.services.aircraft_service import extract_aircraft_from_pdf
from src.services.database_service import get_db_service
from src.utils.reader.file_reader import validate_file_type

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create instance 
app = FastAPI(
    title="Aircraft Utilization Data Extractor API",
    description="API for extracting PDF reports",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

db_service = get_db_service()


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup"""
    try:
        
        await db_service.connect()
        logger.info("✅ Application started and database connected")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from database on shutdown"""
    await db_service.disconnect()
    logger.info("👋 Application shutdown and database disconnected")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Aircraft Utilization Data Extractor",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db_service._connected else "disconnected"
    }


@app.post("/extract", response_model=Dict[str, Any])
async def extract_aircraft_data(
    file: UploadFile = File(..., description="PDF file containing aircraft utilization report")
):
    """
    Extract aircraft utilization data from uploaded PDF
    
    Args:
        file: PDF file upload
        
    Returns:
        JSON response with extracted data and database storage status
    """
    temp_file_path = None

    try:
        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported."
            )
        logger.info(f"📂 Received file: {file.filename}")

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name

        # Validate file type
        validate_file_type(temp_file_path)

        # Build prompt
        prompt = build_aircraft_prompt()

        logger.info("🔄 Extracting data from PDF...")
        extracted_data = extract_aircraft_from_pdf(
            file_path=temp_file_path,
            prompt=prompt,
            dpi=450
        )
        logger.info("✅ Data extraction completed")

        # Validate extracted data
        is_valid, warnings = validate_aircraft_utilization(extracted_data)

        if not is_valid:
            logger.warning(f"⚠️ Validation warnings: {len(warnings)}")
        
        # Store data in database 
        logger.info("💾 Storing extracted data in database...")
        record_id, is_new = await db_service.store_aircraft_data(extracted_data)

        # Prepare response
        response_data = {
            "success": True,
            "message": "Data extracted successfully" if is_new else "Duplicate record detected",
            "is_new_record": is_new,
            "record_id": record_id,
            "filename": file.filename,
            "extracted_data": extracted_data.model_dump(),
            "validation": {
                "is_valid": is_valid,
                "warnings": warnings
            },
            "timestamp": datetime.now().isoformat()
        }

        if is_new:
            logger.info(f"✅ New record created with ID: {record_id}")
        else:
            logger.warning(f"⚠️ Duplicate record detected for: {extracted_data.registration}")
        
        return JSONResponse(
            status_code=200 if is_new else 409,
            content=response_data
        )
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error processing file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )
        
    finally:
        # Cleanup temporary file
        if temp_file_path and Path(temp_file_path).exists():
            try:
                Path(temp_file_path).unlink()
                logger.info("🧹 Cleaned up temporary file")
            except Exception as e:
                logger.warning(f"⚠️ Could not delete temporary file: {e}")


@app.get("/aircraft/{record_id}")
async def get_aircraft_by_id(record_id: str):
    """ 
    Retrieve aircraft data by record ID

    Args:
        record_id: Database record ID 
        
    Returns:
        Aircraft data with all components 
    """
    try:
        aircraft_data = await db_service.get_aircraft_by_id(record_id)

        if not aircraft_data:
            raise HTTPException(
                status_code=404,
                detail=f"Aircraft record not found with ID: {record_id}"
            )
        
        return {
            "success": True,
            "data": aircraft_data
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"❌ Error retrieving aircraft data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving data: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )