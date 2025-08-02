import os
import cv2
import time
import serial
import copy

from board import get_move_from_matrices
from stockfish_run import get_stockfish_move

from inference_sdk import InferenceHTTPClient

from vc import request_chessboard_capture


def transpose_matrix(matrix):
    return [[matrix[j][i] for j in range(8)] for i in range(8)]

# chess board

def parse_filename(filename):
    # Remove the .png extension and split by '_'
    base = filename.replace('.png', '')
    row_str, col_str = base.split('_')
    return int(row_str), int(col_str)

prev_board = [[0 for _ in range(8)] for _ in range(8)]
cur_board = [[0 for _ in range(8)] for _ in range(8)]

for row in range(8):
    for col in range(8):
        if row < 2 :
            cur_board[row][col] = 2
            prev_board[row][col] = 2
        elif row >= 2 and row < 6:
            cur_board[row][col] = 1
            prev_board[row][col] = 1
        else:
            cur_board[row][col] = 3
            prev_board[row][col] = 3



def transpose_matrix(matrix):
    return [[matrix[j][i] for j in range(8)] for i in range(8)]

def predict_map(class_id):
    if class_id == "class_1":
        return int(1)
    elif class_id == "class_2":
        return int(2)
    elif class_id == "class_3":
        return int(3)
    else:
        return int(1)


def init_board():
    global prev_board, cur_board

    for row in range(8):
        for col in range(8):
            if row < 2 :
                cur_board[row][col] = 2
                prev_board[row][col] = 2
            elif row >= 2 and row < 6:
                cur_board[row][col] = 1
                prev_board[row][col] = 1
            else:
                cur_board[row][col] = 3
                prev_board[row][col] = 3

    print("Initialized chess board.")

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="YOUR API KEY HERE"
)

def cell_generator(image_path, output_dir="chess_cells"):
    """
    Loads a top-down chessboard image from a file, splits it into 8x8 cells, and saves them as PNG files.
    Args:
        image_path (str): Path to the chessboard image (already perspective-corrected).
        output_dir (str): Directory to save the cell images.
    """
    os.makedirs(output_dir, exist_ok=True)
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    height, width = image.shape[:2]
    cell_height = height // 8
    cell_width = width // 8

    for row in range(8):
        for col in range(8):
            y1 = row * cell_height
            y2 = (row + 1) * cell_height
            x1 = col * cell_width
            x2 = (col + 1) * cell_width
            cell = image[y1:y2, x1:x2]
            cv2.imwrite(f"{output_dir}/{row}_{col}.png", cell)
    print(f"✅ 64 cells saved to: {output_dir}")

def predict_cells(folder="chess_cells"):
    global cur_board
    for filename in os.listdir(folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            path = os.path.join(folder, filename)
            print(path)

            result = client.run_workflow(
                    workspace_name="psydon",
                    workflow_id="custom-workflow-2",
                    images={
                        "image": path
                    },
                    use_cache=True # cache workflow definition for 15 minutes
                )
            print(f"Predicted class for {filename}: {result[0]['predictions']['top']}")
            row, col = parse_filename(filename)
            cur_board[row][7-col] = predict_map(result[0]['predictions']['top'])

    cur_board = transpose_matrix(cur_board)
def print_cur_board():
    print("Current Board State:")
    for row in cur_board:
        print(row)

def print_prev_board():
    print("Previous Board State:")
    for row in prev_board:
        print(row)


def uci_to_custom(uci):
        y1 = ord(uci[0]) - ord('a')
        x1 = 8 - int(uci[1])
        y2 = ord(uci[2]) - ord('a')
        x2 = 8 - int(uci[3])
        return f"{x1}{y1}{x2}{y2}"

def call_for_move():


    global prev_board, cur_board

    print("in call_for_move()")

    request_chessboard_capture("state/current_state.png")

    time.sleep(2)  # Wait for the image to be captured

    cell_generator("state/current_state.png")

    predict_cells()

    print_prev_board()

    print_cur_board()

    move = get_stockfish_move(prev_board, cur_board)

    custom_move = uci_to_custom(move)

    

    prev_board = copy.deepcopy(cur_board)



    return custom_move






def monitor_arduino_and_trigger(port='COM8', baudrate=9600, python_script='Stockfish.py'):
    """Monitor Arduino serial port and trigger Python script when signal received - Fixed version"""
    
    
    
    try:
        while True:  # Keep the main loop running
            # Open serial connection
            arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # Give Arduino time to initialize
            
            print("Connected to Arduino successfully!")
            print("Continuously listening for trigger signals...")
            
            signal_found = False
            
            # Monitor for trigger signal
            while not signal_found:
                # Read line from Arduino
                if arduino.in_waiting > 0:
                    try:
                        line = arduino.readline().decode('utf-8').strip()
                        
                        if line:
                            print(f"📨 Arduino: {line}")
                            
                            # Check for trigger signal
                            if line == "TRIGGER_PYTHON":
                                print("TRIGGER RECEIVED!")
                                signal_found = True
                                

                                move = call_for_move()



                                coordinates_sent = send_coordinates(arduino, move)
                                    
                                if coordinates_sent:
                                    print("COORDINATES SUCCESSFULLY SENT TO ARDUINO!")
                                else:
                                    print("Coordinates sending may have failed")
                                
                                print("Waiting for Arduino to finish motor movement (MOTOR_DONE)...")
                                motor_done = False
                                while not motor_done:
                                    if arduino.in_waiting > 0:
                                        try:
                                            extra_response = arduino.readline().decode().strip()
                                            if extra_response:
                                                print(f"📨 Arduino: {extra_response}")
                                                if "MOTOR_DONE" in extra_response:
                                                    print("Arduino motor movement complete!")
                                                    motor_done = True
                                        except:
                                            pass
                                    time.sleep(0.1)

                                arduino.close()
                               
                    except UnicodeDecodeError:
                        # Skip any garbled serial data
                        pass
                
                time.sleep(0.1)  # Small delay
            
            # If we reach here, we need to reconnect after the break
            if signal_found:
                continue  # Restart the outer loop to reconnect
            
    except serial.SerialException as e:
        print(f"❌ Serial connection error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if Arduino is connected")
        print("2. Verify the correct COM port")
        print("3. Make sure no other program is using the port")
        print("4. Try different baud rate")
        
        # Show available ports
        available_ports = find_arduino_port()
        if available_ports:
            print(f"\n📌 Detected Arduino-like ports: {', '.join(available_ports)}")
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped by user")
        if 'arduino' in locals():
            arduino.close()
        print("👋 Goodbye!")

def find_arduino_port():
    """Try to find the Arduino port automatically"""
    import serial.tools.list_ports
    
    ports = serial.tools.list_ports.comports()
    arduino_ports = []
    
    for port in ports:
        # Look for common Arduino identifiers
        if any(keyword in port.description.lower() for keyword in ['arduino', 'ch340', 'cp210', 'ftdi']):
            arduino_ports.append(port.device)
    
    return arduino_ports

def send_coordinates(arduino, coordinates):
    """Check for coordinate file from Stockfish and send to Arduino"""
 
            
    print(f"Found coordinates from Stockfish: {coordinates}")
    print(f"Sending to Arduino: MOVE:{coordinates}")
    
    # Clear any pending input from Arduino first
    arduino.reset_input_buffer()
    
    # Send to Arduino
    message = f"MOVE:{coordinates}\n"
    arduino.write(message.encode())
    arduino.flush()
    
    print("Waiting for Arduino acknowledgment...")
    
    # Wait longer for Arduino response and read multiple lines if needed
    response_received = False
    attempts = 0
    max_attempts = 10
    
    while not response_received and attempts < max_attempts:
        time.sleep(0.3)  # Wait a bit longer
        attempts += 1
        
        if arduino.in_waiting > 0:
            try:
                response = arduino.readline().decode().strip()
                print(f"Arduino says: {response}")
                
                # Check if this is the acknowledgment we're looking for
                if "ARDUINO_ACK:" in response or "NEW COORDINATE RECEIVED" in response:
                    print("Arduino acknowledged coordinate reception!")
                    response_received = True
                elif response:  # Any other non-empty response
                    print(f"Arduino output: {response}")
                    
            except Exception as e:
                print(f"Error reading Arduino response: {e}")
    
    if not response_received:
        print("No acknowledgment received from Arduino (but coordinate was sent)")
    

    
    return response_received
            





if __name__ == "__main__":
    """Main function with port selection"""
    
    # Try to find Arduino ports automatically
    arduino_ports = find_arduino_port()
    
    if arduino_ports:
        print(f"🔍 Found potential Arduino ports: {', '.join(arduino_ports)}")
        port = arduino_ports[0]  # Use first detected port
        print(f"🎯 Using port: {port}")
    else:
        print("⚠️  No Arduino ports auto-detected")
        port = 'COM8'  # Default port (Windows)
        print(f"🎯 Using default port: {port}")
        print("   (Change this in the code if needed)")
    
    print()
    
    # You can change which Python script to trigger here
    script_to_trigger = 'Stockfish.py'
    
    # Start monitoring
    monitor_arduino_and_trigger(port=port, python_script=script_to_trigger)