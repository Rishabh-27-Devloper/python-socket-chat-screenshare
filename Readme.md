# Real-time Chat & Screen Sharing Application

A Python application that combines real-time text chatting with screen sharing capabilities using sockets and OpenCV.

## Features

- **Real-time Text Chat**: Multiple users can chat simultaneously
- **Screen Sharing**: Share your screen with other connected users
- **Screen Viewing**: View shared screens from other users
- **User-friendly GUI**: Tabbed interface for easy navigation
- **Multi-threaded**: Handles multiple clients concurrently

## Prerequisites

- Python 3.7 or higher
- Required Python packages (see requirements.txt)

## Installation

1. **Clone or download the files**:
   - `server.py` - The server application
   - `client.py` - The client application
   - `requirements.txt` - Required dependencies

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **For screen capture permissions (macOS)**:
   - Go to System Preferences > Security & Privacy > Privacy > Screen Recording
   - Add your terminal or Python executable to the allowed applications

## Usage

### Starting the Server

1. **Run the server**:
   ```bash
   python server.py
   ```

2. **Server will display**:
   ```
   🚀 Server started!
   📱 Chat server: localhost:9999
   🖥️  Screen server: localhost:9998
   Press Ctrl+C to stop the server
   ```

### Connecting Clients

1. **Run the client**:
   ```bash
   python client.py
   ```

2. **Connect to server**:
   - Go to the "Connection" tab
   - Enter your username
   - Enter server IP (use "localhost" if running locally)
   - Click "Connect"

3. **Start chatting**:
   - Switch to the "Chat" tab
   - Type messages and press Enter or click Send

4. **Screen sharing**:
   - Switch to the "Screen Share" tab
   - Click "Start Sharing Screen" to share your screen
   - Click "Start Receiving Screen" to view shared screens

## How It Works

### Architecture

- **Server**: Manages two separate socket servers
  - Chat Server (port 9999): Handles text messages
  - Screen Server (port 9998): Handles screen frame data

- **Client**: Connects to both servers
  - Chat connection: Sends/receives text messages
  - Screen connection: Sends screen captures or receives frames

### Technical Details

- **Socket Programming**: TCP sockets for reliable communication
- **Threading**: Multi-threaded design for concurrent operations
- **OpenCV**: Image processing and encoding for screen frames
- **PyAutoGUI**: Screen capture functionality
- **Tkinter**: GUI framework for the client interface

### Data Flow

1. **Chat Messages**:
   - Client sends message to server
   - Server broadcasts to all connected clients
   - Messages include timestamps and usernames

2. **Screen Sharing**:
   - Sender captures screen using PyAutoGUI
   - Frame is resized and compressed using OpenCV
   - Frame data is pickled and sent to server
   - Server broadcasts frame to all receivers
   - Receivers decode and display the frame

## Configuration

### Server Settings
You can modify these settings in `server.py`:
- `host`: Server IP address (default: 'localhost')
- `chat_port`: Chat server port (default: 9999)
- `screen_port`: Screen sharing port (default: 9998)

### Performance Tuning
- **Frame Rate**: Adjust `time.sleep(0.1)` in screen capture loop
- **Image Quality**: Modify `cv2.IMWRITE_JPEG_QUALITY` value (0-100)
- **Frame Size**: Change resize dimensions in `cv2.resize(frame, (800, 600))`

## Security Considerations

⚠️ **Important**: This application is designed for local networks or trusted environments:

- No encryption is implemented
- No authentication beyond usernames
- Screen sharing provides full desktop access
- Suitable for educational/development purposes

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure server is running
   - Check firewall settings
   - Verify correct IP and port

2. **Screen Capture Not Working**:
   - Grant screen recording permissions (macOS)
   - Install required dependencies
   - Check PyAutoGUI compatibility

3. **Poor Performance**:
   - Reduce frame rate (increase sleep time)
   - Lower image quality
   - Decrease frame size

### Error Messages

- **"Failed to connect"**: Server not running or incorrect address
- **"Permission denied"**: Screen recording permissions needed
- **"Module not found"**: Install required dependencies

## Extending the Application

### Possible Enhancements

- Add user authentication
- Implement message encryption
- Add file sharing capabilities
- Support for audio/video calls
- Better error handling and reconnection
- User management (kick/ban users)
- Private messaging between users

### Code Structure

- `ChatScreenServer`: Main server class handling both chat and screen
- `ChatScreenClient`: Client class with GUI and networking
- Threading used for concurrent operations
- Pickle for data serialization
- Struct for message framing

## License

This project is provided as-is for educational purposes. Feel free to modify and distribute according to your needs.