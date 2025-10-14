from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import logging
import httpx

from typing import Dict, Any
from src.utils.prompt.aircraft_prompt import build_aircraft_prompt
from src.validators.aircraft_validator import validate_aircraft_utilization
from src.services.aircraft_service import extract_aircraft_from_pdf
from src.services.operations_service import get_operations_service
from src.utils.reader.file_reader import validate_file_type
from src.models.operation_models import SaveOperationsRequest, SaveOperationsResponse,ExtractFromUrlRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance 
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

# Initialize services
operations_service = get_operations_service()


@app.on_event("startup")
async def startup_event():
    """Connect to database on startup"""
    try:
        await operations_service.connect()
        logger.info("✅ Application started and database connected")
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from database on shutdown"""
    await operations_service.disconnect()
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
        "database": "connected" if operations_service._connected else "disconnected"
    }


@app.post("/api/save-operations-data", response_model=SaveOperationsResponse)
async def save_operations_data(request: SaveOperationsRequest):
    """
    Save extracted operations data to PostgreSQL database
    
    Args:
        request: SaveOperationsRequest containing lessees, month, and fileName
        
    Returns:
        SaveOperationsResponse with success status and saved data counts
    """
    try:
        logger.info(f"📥 Received request to save data for month: {request.month}")
        logger.info(f"📊 Data contains {len(request.lessees)} lessees")
        
        # Check if data already exists for this month
        exists = await operations_service.check_month_exists(request.month)
        if exists:
            logger.warning(f"⚠️ Data already exists for month: {request.month}")
            return SaveOperationsResponse(
                success=False,
                message=f"Data for month {request.month} already exists. Please delete existing data first or use a different month.",
                data=None
            )
        
        # Save data to database
        result = await operations_service.save_operations_data(
            lessees=request.lessees,
            month=request.month,
            file_name=request.fileName
        )
        
        if result["errors"]:
            logger.error(f"❌ Errors occurred: {result['errors']}")
            return SaveOperationsResponse(
                success=False,
                message="Some errors occurred during save",
                data={
                    "saved_lessees": result["saved_lessees"],
                    "saved_assets": result["saved_assets"],
                    "saved_components": result["saved_components"]
                },
                errors=result["errors"]
            )
        
        logger.info(f"✅ Successfully saved: {result['saved_lessees']} lessees, "
                   f"{result['saved_assets']} assets, {result['saved_components']} components")
        
        return SaveOperationsResponse(
            success=True,
            message="Data saved successfully",
            data={
                "saved_lessees": result["saved_lessees"],
                "saved_assets": result["saved_assets"],
                "saved_components": result["saved_components"],
                "month": request.month,
                "file_name": request.fileName,
                "saved_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"💥 Error saving operations data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save operations data: {str(e)}"
        )
    
@app.post("/api/extract-from-url", response_model=Dict[str, Any])
async def extract_from_url(request: ExtractFromUrlRequest):
    """
    Extract aircraft utilization data from a URL-hosted PDF.
    Checks if airline already exists in database (regardless of month).
    
    Args:
        request: ExtractFromUrlRequest containing fileUrl, fileName, and month
        
    Returns:
        JSON response with either existing airline data from database or message that airline not found
    """
    temp_file_path = None

    try:
        logger.info(f"📥 Downloading PDF from URL: {request.fileUrl}")
        
        # Download file from URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(request.fileUrl)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
        
        

        # Validate file type
        validate_file_type(temp_file_path)

        # Build prompt
        prompt = build_aircraft_prompt()

        
        extracted_data = extract_aircraft_from_pdf(
            file_path=temp_file_path,
            prompt=prompt,
            dpi=150
        )
        logger.info(f"✅ Data extraction completed: {extracted_data}")

        # Get the airline name from extracted data
        airline_name = extracted_data.airline
        

        # Get all data from database
        all_data = await operations_service.get_all_operations()

        # Check if airline exists in the database (case-insensitive)
        airline_data = None
        if all_data:
            for lessee in all_data:
                db_name = lessee.get('name', '').casefold()
                extracted_name = airline_name.casefold()
                if db_name == extracted_name or lessee.get('lessee_name', '').casefold() == extracted_name:
                    airline_data = lessee
                    break

            if airline_data:
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": f"Airline '{airline_name}' already exists in database",
                        "data_source": "database",
                        "airline": airline_name,
                        "data": airline_data,
                        "timestamp": datetime.now().isoformat()
                    }
                )

            

        
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "message": f"Airline '{airline_name}' not found in database",
                "data_source": "database",
                "airline": airline_name,
                "data": [],
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except httpx.HTTPError as e:
        logger.error(f"❌ Error downloading file: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error downloading file from URL: {str(e)}"
        )
        
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


@app.get("/api/operations-data/{month}")
async def get_operations_data(month: str):
    """
    Retrieve operations data for a specific month
    
    Args:
        month: Month string (e.g., "2024-01", "January 2024")
        
    Returns:
        JSON response with operations data for the specified month
    """
    try:
        logger.info(f"📥 Fetching data for month: {month}")
        
        data = await operations_service.get_operations_by_month(month)
        
        if not data:
            return {
            "success": False,
            "data": [],
            "month": month,
            "count": 0
            }
        
        logger.info(f"✅ Found {len(data)} lessees for month: {month}")
        
        return {
            "success": True,
            "data": data,
            "month": month,
            "count": len(data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error fetching operations data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch operations data: {str(e)}"
        )


@app.get("/api/operations-data")
async def get_all_operations_data():
    """
    Retrieve all operations data
    
    Returns:
        JSON response with all operations data
    """
    try:
        logger.info("📥 Fetching all operations data")
        
        data = await operations_service.get_all_operations()
        
        logger.info(f"✅ Found {len(data)} total lessees")
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
        
    except Exception as e:
        logger.error(f"💥 Error fetching all operations data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch operations data: {str(e)}"
        )


@app.delete("/api/operations-data/{month}")
async def delete_operations_data(month: str):
    """
    Delete operations data for a specific month
    
    Args:
        month: Month string to delete
        
    Returns:
        JSON response with deletion status
    """
    try:
        logger.info(f"🗑️ Deleting data for month: {month}")
        
        deleted = await operations_service.delete_operations_by_month(month)
        
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for month: {month}"
            )
        
        logger.info(f"✅ Successfully deleted data for month: {month}")
        
        return {
            "success": True,
            "message": f"Data for month {month} deleted successfully",
            "month": month
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Error deleting operations data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete operations data: {str(e)}"
        )


@app.post("/extract", response_model=Dict[str, Any])
async def extract_aircraft_data(
    file: UploadFile = File(..., description="PDF file containing aircraft utilization report")
):
    """
    Extract aircraft utilization data from uploaded PDF
    
    Args:
        file: PDF file upload
        
    Returns:
        JSON response with extracted data
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
            dpi=150
        )
        logger.info("✅ Data extraction completed")

        # Validate extracted data
        is_valid, warnings = validate_aircraft_utilization(extracted_data)

        if not is_valid:
            logger.warning(f"⚠️ Validation warnings: {len(warnings)}")
        
        # Prepare response
        response_data = {
            "success": True,
            "message": "Data extracted successfully",
            "filename": file.filename,
            "extracted_data": extracted_data.model_dump(),
            "validation": {
                "is_valid": is_valid,
                "warnings": warnings
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return JSONResponse(
            status_code=200,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )