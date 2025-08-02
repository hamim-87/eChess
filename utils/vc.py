import cv2
import numpy as np
import time
import os
import glob
from datetime import datetime

# IP Webcam stream URL
stream_url = 'http://172.20.10.6:8080/video'

# Global variables for 4-point selection
points = []
selected_points = []
crop_coords = None
selection_complete = False
selection_window_open = False
cropped_frame = None  # Global variable to hold the latest cropped image

def mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks for 4-point selection"""
    global points, selected_points, crop_coords, selection_complete
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"� Point {len(points)}: ({x}, {y})")
            
            if len(points) == 4:
                # Scale coordinates back to original frame size
                scale_x = param['original_width'] / param['debug_width']
                scale_y = param['original_height'] / param['debug_height']
                
                # Convert points to original frame coordinates
                original_points = [(int(p[0] * scale_x), int(p[1] * scale_y)) for p in points]
                
                # Order points: top-left, top-right, bottom-right, bottom-left
                ordered_points = order_points(np.array(original_points, dtype=np.float32))
                
                # Calculate the dimensions of the output rectangle
                # Use the maximum width and height to preserve aspect ratio
                widthA = np.sqrt(((ordered_points[2][0] - ordered_points[3][0]) ** 2) + 
                                ((ordered_points[2][1] - ordered_points[3][1]) ** 2))
                widthB = np.sqrt(((ordered_points[1][0] - ordered_points[0][0]) ** 2) + 
                                ((ordered_points[1][1] - ordered_points[0][1]) ** 2))
                maxWidth = max(int(widthA), int(widthB))
                
                heightA = np.sqrt(((ordered_points[1][0] - ordered_points[2][0]) ** 2) + 
                                 ((ordered_points[1][1] - ordered_points[2][1]) ** 2))
                heightB = np.sqrt(((ordered_points[0][0] - ordered_points[3][0]) ** 2) + 
                                 ((ordered_points[0][1] - ordered_points[3][1]) ** 2))
                maxHeight = max(int(heightA), int(heightB))
                
                # Create destination points for perspective transform
                dst_points = np.array([
                    [0, 0],
                    [maxWidth - 1, 0],
                    [maxWidth - 1, maxHeight - 1],
                    [0, maxHeight - 1]
                ], dtype=np.float32)
                
                # Store transformation data
                crop_coords = {
                    'src_points': ordered_points,
                    'dst_points': dst_points,
                    'width': maxWidth,
                    'height': maxHeight
                }
                
                selected_points = original_points
                selection_complete = True
                
                print(f"Precision selection complete!")
                print(f"   Output size: {maxWidth}x{maxHeight}")
                print("   Press 'r' to reset and select again")
        else:
            print("⚠️  4 points already selected. Press 'r' to reset.")

def connect_to_stream():
    """Connect to the IP Webcam stream"""
    print("Connecting to IP Webcam...")
    
    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if cap.isOpened():
        for i in range(5):
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                print("✓ Stream connected successfully!")
                return cap
            time.sleep(0.2)
    
    cap.release()
    return None

def order_points(pts):
    """Order points in clockwise order: top-left, top-right, bottom-right, bottom-left"""
    # Initialize list of coordinates
    rect = np.zeros((4, 2), dtype=np.float32)
    
    # Top-left point has smallest sum, bottom-right has largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    # Top-right has smallest difference, bottom-left has largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

def apply_perspective_transform(frame, transform_data):
    """Apply perspective transformation to get precise quadrilateral crop"""
    if not transform_data:
        return None
    
    # Get transformation matrix
    matrix = cv2.getPerspectiveTransform(
        transform_data['src_points'],
        transform_data['dst_points']
    )
    
    # Apply perspective transformation
    warped = cv2.warpPerspective(
        frame, 
        matrix, 
        (transform_data['width'], transform_data['height'])
    )
    
    return warped

def check_image_requests():
    """Check for image capture requests and process them"""
    requests_dir = "image_requests"
    images_dir = "captured_images"
    
    # Create directories if they don't exist
    os.makedirs(requests_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    # Look for request files
    request_files = glob.glob(os.path.join(requests_dir, "request_*.txt"))
    
    return request_files

def process_image_request(request_file, cropped_frame):
    """Process an image request by saving the cropped frame"""
    try:
        # Read the requested filename
        with open(request_file, 'r') as f:
            image_filename = f.read().strip()
        
        # Save the cropped frame
        images_dir = "captured_images"
        image_path = os.path.join(images_dir, image_filename)
        
        success = cv2.imwrite(image_path, cropped_frame)
        
        if success:
            print(f"📸 Image saved: {image_filename}")
            
            # Remove the request file
            os.remove(request_file)
            return True
        else:
            print(f"❌ Failed to save image: {image_filename}")
            return False
            
    except Exception as e:
        print(f"⚠️  Error processing image request: {e}")
        return False

def draw_selection_interface(frame, debug_width=640, debug_height=480):
    """Draw the selection interface with points and instructions"""
    debug_frame = frame.copy()
    
    # Draw existing points
    for i, point in enumerate(points):
        # Scale point to debug frame size
        scaled_x = int(point[0])
        scaled_y = int(point[1])
        
        # Draw point
        cv2.circle(debug_frame, (scaled_x, scaled_y), 8, (0, 255, 255), -1)
        cv2.putText(debug_frame, str(i+1), (scaled_x-5, scaled_y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Draw lines connecting points if we have more than 1
    if len(points) > 1:
        for i in range(len(points)):
            start_point = points[i]
            end_point = points[(i + 1) % len(points)] if len(points) > 2 else points[i-1] if i > 0 else None
            if end_point and i < len(points) - 1:
                cv2.line(debug_frame, start_point, end_point, (255, 0, 0), 2)
    
    # If we have 4 points, draw the complete quadrilateral
    if len(points) == 4:
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(debug_frame, [pts], True, (0, 255, 0), 3)
        
        # Fill with semi-transparent overlay
        overlay = debug_frame.copy()
        cv2.fillPoly(overlay, [pts], (0, 255, 0))
        cv2.addWeighted(debug_frame, 0.8, overlay, 0.2, 0, debug_frame)
    
    # Add instructions
    instruction_text = [
        f"Click {4 - len(points)} more points" if len(points) < 4 else "Selection Complete!",
        "Press 'r' to reset" if len(points) > 0 else "Click 4 corners of chessboard",
        "Press 'Esc' to quit"
    ]
    
    for i, text in enumerate(instruction_text):
        cv2.putText(debug_frame, text, (10, 30 + i * 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Resize for display
    debug_resized = cv2.resize(debug_frame, (debug_width, debug_height))
    return debug_resized

def save_current_cropped_chessboard(filename=None):
    """
    Save the most recent cropped chessboard image to a PNG file.
    If filename is None, use a timestamped default name.
    Returns the filename if successful, None otherwise.
    """
    global cropped_frame
    if cropped_frame is not None:
        if filename is None:
            filename = f"chessboard_{int(time.time())}.png"
        success = cv2.imwrite(filename, cropped_frame)
        if success:
            print(f"✅ Chessboard image saved as {filename}")
            return filename
        else:
            print(f"❌ Failed to save chessboard image as {filename}")
            return None
    else:
        print("❌ No cropped frame available to save.")
        return None

def check_for_save_request():
    """
    If a file named 'save_request.txt' exists, save the current cropped chessboard image
    and remove the request file. The filename can be specified inside the file, otherwise use default.
    """
    request_file = "save_request.txt"
    if os.path.exists(request_file):
        try:
            with open(request_file, 'r') as f:
                filename = f.read().strip()
            if not filename:
                filename = None
        except Exception:
            filename = None
        save_current_cropped_chessboard(filename)
        os.remove(request_file)

def request_chessboard_capture(filename=None):
    """
    Request the running vc.py process to save the current cropped chessboard image.
    If filename is provided, it will be used; otherwise, a default name will be used.
    """
    # Ensure the directory exists if a filename with a path is provided
    if filename:
        dir_name = os.path.dirname(filename)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
    with open("save_request.txt", "w") as f:
        if filename:
            f.write(filename)
        else:
            f.write("")

if __name__ == "__main__":
    # Connect to stream
    cap = connect_to_stream()
    if cap is None:
        print("❌ Could not connect to stream")
        print("Try restarting the IP Webcam app on your phone")
        exit()

    print("🎯 Precision 4-Point Chess Board Selection")
    print("📍 Instructions:")
    print("   1. Click 4 corners of your chessboard in the 'Selection' window")
    print("   2. Perspective correction will create a perfect rectangle")
    print("   3. Handles any angle or distortion automatically")
    print("   4. Press 'r' to reset selection")
    print("   5. Press 'Esc' to quit")
    print("🔥 NEW: Pixel-perfect precision with perspective correction!")
    print("📸 BONUS: Run 'image_capturer.py' to automatically save images!")

    consecutive_failures = 0
    max_failures = 3

    # Get first frame to set up dimensions
    ret, first_frame = cap.read()
    if ret:
        original_height, original_width = first_frame.shape[:2]
        debug_width, debug_height = 640, 480
    else:
        print("❌ Could not get initial frame")
        exit()

    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            consecutive_failures += 1
            print(f"⚠️  Frame read failed ({consecutive_failures}/{max_failures})")
            
            if consecutive_failures >= max_failures:
                print("Too many failures, attempting reconnection...")
                cap.release()
                cap = connect_to_stream()
                if cap is None:
                    print("❌ Reconnection failed, exiting...")
                    break
                consecutive_failures = 0
            
            time.sleep(0.1)
            continue
        
        consecutive_failures = 0
        
        try:
            if selection_complete and crop_coords:
                cropped_frame = apply_perspective_transform(frame, crop_coords)
                if cropped_frame is not None:
                    cv2.imshow("Precision Chess Board", cropped_frame)
                    # Check for image capture requests
                    request_files = check_image_requests()
                    for request_file in request_files:
                        process_image_request(request_file, cropped_frame)
                    # Check for save request from external script
                    check_for_save_request()
                # Once selection is complete, destroy the selection window if it exists
                if selection_window_open:
                    cv2.destroyWindow("Selection")
                    selection_window_open = False
            else:
                # Show selection interface
                debug_frame = draw_selection_interface(frame, debug_width, debug_height)
                cv2.imshow("Selection", debug_frame)
                selection_window_open = True
                # Set mouse callback with frame dimensions
                cv2.setMouseCallback("Selection", mouse_callback, {
                    'original_width': original_width,
                    'original_height': original_height,
                    'debug_width': debug_width,
                    'debug_height': debug_height
                })
        except Exception as e:
            print(f"⚠️  Display error: {e}")
            continue

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # Escape key
            break
        elif key == ord('r'):  # Reset selection
            points = []
            selected_points = []
            crop_coords = None
            selection_complete = False
            # When resetting, make sure the selection window will be shown again
            selection_window_open = False
            print("🔄 Selection reset. Click 4 new points.")
        elif key == ord('s'):
            # Save the current cropped chessboard image instantly using the function
            save_current_cropped_chessboard()

    print("🏁 Closing application...")
    cap.release()
    cv2.destroyAllWindows()
