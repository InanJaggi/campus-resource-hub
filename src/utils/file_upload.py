"""Utility functions for handling file uploads"""
import os
import uuid
from pathlib import Path
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_images_directory():
    """Get the images directory path, handling both Flask app context and direct execution"""
    try:
        # Try to get from Flask app context
        app = current_app._get_current_object()
        root_path = Path(app.root_path)
        static_folder_name = app.static_folder
        
        # If static_folder is absolute, use it directly
        if static_folder_name and os.path.isabs(str(static_folder_name)):
            static_folder = Path(static_folder_name)
        else:
            # Otherwise, it's relative to root_path
            if static_folder_name:
                static_folder = root_path / static_folder_name
            else:
                static_folder = root_path / "static"
    except (RuntimeError, AttributeError, TypeError):
        # Not in app context, use relative path from this file
        static_folder = Path(__file__).parent.parent / "static"
    
    images_dir = static_folder / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir


def save_resource_image(file, resource_id: int) -> str | None:
    """
    Save an uploaded image for a resource.
    
    Args:
        file: The uploaded file from request.files
        resource_id: The ID of the resource
        
    Returns:
        The relative path to the saved image, or None if upload failed
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Get the images directory
    images_dir = _get_images_directory()
    
    # Generate unique filename: resource_{id}_{uuid}.{ext}
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"resource_{resource_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    filepath = images_dir / unique_filename
    
    # Save the file
    try:
        file.save(str(filepath))
        # Return relative path from static folder (always "images/filename")
        return f"images/{unique_filename}"
    except Exception as e:
        print(f"Error saving image: {e}")
        return None


def delete_resource_image(image_path: str) -> bool:
    """
    Delete a resource image file.
    
    Args:
        image_path: The relative path to the image (e.g., "images/resource_1_abc123.jpg")
        
    Returns:
        True if deleted successfully, False otherwise
    """
    if not image_path:
        return False
    
    try:
        images_dir = _get_images_directory()
        # image_path is "images/filename", so we need to get just the filename
        filename = image_path.replace("images/", "")
        filepath = images_dir / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting image: {e}")
        return False
