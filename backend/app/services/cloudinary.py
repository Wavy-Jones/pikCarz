"""
Cloudinary image upload service
"""
import cloudinary
import cloudinary.uploader
from typing import List
from fastapi import UploadFile, HTTPException
from app.config import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

async def upload_vehicle_image(file: UploadFile, vehicle_id: int) -> str:
    """
    Upload a vehicle image to Cloudinary
    Returns the secure URL of the uploaded image
    """
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Validate file size (max 10MB)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start
    
    if file_size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="File too large. Max size: 10MB")
    
    try:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file.file,
            folder=f"pikcarz/vehicles/{vehicle_id}",
            resource_type="image",
            transformation=[
                {"width": 1200, "height": 800, "crop": "limit"},  # Max dimensions
                {"quality": "auto"},  # Auto quality
                {"fetch_format": "auto"}  # Auto format (WebP when supported)
            ]
        )
        
        return result["secure_url"]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

async def upload_multiple_vehicle_images(
    files: List[UploadFile],
    vehicle_id: int,
    max_images: int = 10
) -> List[str]:
    """
    Upload multiple vehicle images
    Returns list of secure URLs
    """
    
    if len(files) > max_images:
        raise HTTPException(
            status_code=400,
            detail=f"Too many images. Maximum allowed: {max_images}"
        )
    
    uploaded_urls = []
    
    for file in files:
        url = await upload_vehicle_image(file, vehicle_id)
        uploaded_urls.append(url)
    
    return uploaded_urls

def delete_vehicle_images(image_urls: List[str]) -> bool:
    """
    Delete vehicle images from Cloudinary
    Returns True if successful
    """
    
    try:
        for url in image_urls:
            # Extract public_id from URL
            # Format: https://res.cloudinary.com/cloud/image/upload/v123/pikcarz/vehicles/1/image.jpg
            parts = url.split("/")
            if "pikcarz" in parts:
                idx = parts.index("pikcarz")
                public_id = "/".join(parts[idx:-1]) + "/" + parts[-1].split(".")[0]
                cloudinary.uploader.destroy(public_id)
        
        return True
    
    except Exception as e:
        print(f"Error deleting images: {e}")
        return False
