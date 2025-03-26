import face_recognition
import cv2
import numpy as np
import io
import logging
from typing import List, Optional, Union, Tuple

logger = logging.getLogger(__name__)

def encode_face(image_data: bytes) -> Optional[np.ndarray]:
    """
    Generate face encoding from image data
    
    Args:
        image_data: Binary image data
        
    Returns:
        Face encoding as numpy array or None if no face detected
    """
    try:
        # Read image from binary data
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Find face locations in the image
        face_locations = face_recognition.face_locations(rgb_img)
        
        if not face_locations:
            logger.warning("No face found in the image")
            return None
        
        # Use the first face found
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        if not face_encodings:
            logger.warning("Failed to encode face")
            return None
        
        return face_encodings[0]
    
    except Exception as e:
        logger.error(f"Error encoding face: {str(e)}")
        return None

def compare_faces(face_encoding: np.ndarray, stored_encoding: Union[List[float], np.ndarray], tolerance: float = 0.6) -> bool:
    """
    Compare a face encoding with a stored encoding
    
    Args:
        face_encoding: Face encoding to compare
        stored_encoding: Stored face encoding (from database)
        tolerance: Comparison tolerance (lower is more strict)
        
    Returns:
        True if the faces match, False otherwise
    """
    try:
        # Convert stored encoding to numpy array if it's a list
        if isinstance(stored_encoding, list):
            stored_encoding = np.array(stored_encoding)
        
        # Compare faces
        matches = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=tolerance)
        
        return matches[0]
    
    except Exception as e:
        logger.error(f"Error comparing faces: {str(e)}")
        return False

def detect_faces(image_data: bytes) -> Tuple[np.ndarray, List[Tuple[int, int, int, int]]]:
    """
    Detect faces in an image and return the image with face rectangles drawn
    
    Args:
        image_data: Binary image data
        
    Returns:
        Tuple containing:
        - The image with rectangles drawn around faces
        - List of face locations (top, right, bottom, left)
    """
    try:
        # Read image from binary data
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert BGR to RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Find face locations
        face_locations = face_recognition.face_locations(rgb_img)
        
        # Draw rectangles around faces
        for top, right, bottom, left in face_locations:
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
        
        return img, face_locations
    
    except Exception as e:
        logger.error(f"Error detecting faces: {str(e)}")
        return None, []
