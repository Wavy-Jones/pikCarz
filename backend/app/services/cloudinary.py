"""
Cloudinary image upload service
"""
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from typing import List
from app.config import settings

def _configure_cloudinary():
    if not all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
        raise HTTPException(status_code=503, detail="Image upload is not configured on this server.")
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )

async def upload_vehicle_image(file: UploadFile, vehicle_id: int) -> str:
    """
    Upload a single vehicle image to Cloudinary
    Returns the secure URL of the uploaded image
    """
    _configure_cloudinary()
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=f"pikcarz/vehicles/{vehicle_id}",
            resource_type="image",
            transformation=[
                {'width': 1200, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        
        return result['secure_url']
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

async def upload_multiple_vehicle_images(files: List[UploadFile], vehicle_id: int) -> List[str]:
    """
    Upload multiple vehicle images to Cloudinary
    Returns list of secure URLs
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")
    
    urls = []
    for file in files:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image")
        
        url = await upload_vehicle_image(file, vehicle_id)
        urls.append(url)
    
    return urls

async def delete_vehicle_image(image_url: str):
    """Delete an image from Cloudinary"""
    try:
        # Extract public_id from URL
        # URL format: https://res.cloudinary.com/cloud_name/image/upload/v123456/pikcarz/vehicles/1/image_id.jpg
        parts = image_url.split('/')
        public_id = '/'.join(parts[parts.index('pikcarz'):]).split('.')[0]
        
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        # Don't fail if deletion fails - log it instead
        print(f"Failed to delete image: {str(e)}")

async def delete_vehicle_images(image_urls: List[str]):
    """Delete multiple images from Cloudinary"""
    for url in image_urls:
        await delete_vehicle_image(url)
