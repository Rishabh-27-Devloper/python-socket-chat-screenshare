import socket
import threading
import cv2
import pickle
import struct
import pyautogui
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import time
from PIL import Image, ImageTk
import numpy as np

class ChatScreenClient:
    def __init__(self):
        self.host = 'localhost'
        self.chat_port = 9999
        self.screen_port = 9998
        self.username = ""
        self.chat_socket = None
        self.screen_socket = None
        self.sharing_screen = False
        self.receiving_screen = False
        self.running = True
        
        # GUI Setup
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Chat & Screen Share")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Chat Tab
        self.setup_chat_tab()
        
        # Screen Share Tab
        self.setup_screen_tab()
        
        # Connection Tab
        self.setup_connection_tab()
        
    def setup_connection_tab(self):
        self.conn_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.conn_frame, text="Connection")
        
        # Connection controls
        conn_control = ttk.LabelFrame(self.conn_frame, text="Server Connection")
        conn_control.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(conn_control, text="Username:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.username_entry = ttk.Entry(conn_control, width=20)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(conn_control, text="Server IP:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.host_entry = ttk.Entry(conn_control, width=20)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=1, column=1, padx=5, pady=5)
        
        self.connect_btn = ttk.Button(conn_control, text="Connect", command=self.connect_to_server)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.status_label = ttk.Label(conn_control, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)
        
    def setup_chat_tab(self):
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat")
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, 
            height=20, 
            state='disabled',
            wrap='word'
        )
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Message input
        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.message_entry = ttk.Entry(input_frame)
        self.message_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_message)
        
        self.send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_btn.pack(side='right')
        
    def setup_screen_tab(self):
        self.screen_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.screen_frame, text="Screen Share")
        
        # Control buttons
        control_frame = ttk.Frame(self.screen_frame)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        self.share_btn = ttk.Button(
            control_frame, 
            text="Start Sharing Screen", 
            command=self.toggle_screen_share
        )
        self.share_btn.pack(side='left', padx=(0, 5))
        
        self.receive_btn = ttk.Button(
            control_frame, 
            text="Start Receiving Screen", 
            command=self.toggle_screen_receive
        )
        self.receive_btn.pack(side='left')
        
        # Screen display
        self.screen_label = ttk.Label(self.screen_frame, text="Screen sharing not active")
        self.screen_label.pack(fill='both', expand=True, padx=10, pady=10)
        
    def connect_to_server(self):
        self.username = self.username_entry.get().strip()
        self.host = self.host_entry.get().strip()
        
        if not self.username:
            messagebox.showerror("Error", "Please enter a username")
            return
            
        try:
            # Connect to chat server
            self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_socket.connect((self.host, self.chat_port))
            self.chat_socket.send(self.username.encode('utf-8'))
            
            # Start receiving messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.status_label.config(text="Status: Connected", foreground="green")
            self.connect_btn.config(text="Disconnect", command=self.disconnect_from_server)
            
            self.display_message("🟢 Connected to server!")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            
    def disconnect_from_server(self):
        self.running = False
        
        if self.chat_socket:
            self.chat_socket.close()
            
        if self.screen_socket:
            self.screen_socket.close()
            
        self.sharing_screen = False
        self.receiving_screen = False
        
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_btn.config(text="Connect", command=self.connect_to_server)
        self.share_btn.config(text="Start Sharing Screen")
        self.receive_btn.config(text="Start Receiving Screen")
        
        self.display_message("🔴 Disconnected from server!")
        
    def receive_messages(self):
        while self.running:
            try:
                message = self.chat_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message)
            except:
                break
                
    def display_message(self, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert('end', message + '\n')
        self.chat_display.config(state='disabled')
        self.chat_display.see('end')
        
    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message and self.chat_socket:
            try:
                self.chat_socket.send(message.encode('utf-8'))
                self.message_entry.delete(0, 'end')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")
                
    def toggle_screen_share(self):
        if not self.sharing_screen:
            self.start_screen_share()
        else:
            self.stop_screen_share()
            
    def start_screen_share(self):
        try:
            self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.screen_socket.connect((self.host, self.screen_port))
            self.screen_socket.send("SENDER".encode('utf-8'))
            
            self.sharing_screen = True
            self.share_btn.config(text="Stop Sharing Screen")
            
            # Start screen capture thread
            share_thread = threading.Thread(target=self.capture_and_send_screen)
            share_thread.daemon = True
            share_thread.start()
            
            self.display_message("🖥️ Started sharing screen")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start screen sharing: {e}")
            
    def stop_screen_share(self):
        self.sharing_screen = False
        if self.screen_socket:
            self.screen_socket.close()
        self.share_btn.config(text="Start Sharing Screen")
        self.display_message("🛑 Stopped sharing screen")
        
    def capture_and_send_screen(self):
        while self.sharing_screen and self.running:
            try:
                # Capture screen
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                
                # Resize frame for better performance
                frame = cv2.resize(frame, (800, 600))
                
                # Encode frame
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                result, frame_encoded = cv2.imencode('.jpg', frame, encode_param)
                data = pickle.dumps(frame_encoded)
                
                # Send frame size then frame data
                message_size = struct.pack("Q", len(data))
                self.screen_socket.sendall(message_size + data)
                
                time.sleep(0.1)  # Control frame rate
                
            except Exception as e:
                print(f"Error capturing screen: {e}")
                break
                
    def toggle_screen_receive(self):
        if not self.receiving_screen:
            self.start_screen_receive()
        else:
            self.stop_screen_receive()
            
    def start_screen_receive(self):
        try:
            self.screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.screen_socket.connect((self.host, self.screen_port))
            self.screen_socket.send("RECEIVER".encode('utf-8'))
            
            self.receiving_screen = True
            self.receive_btn.config(text="Stop Receiving Screen")
            
            # Start screen receive thread
            receive_thread = threading.Thread(target=self.receive_and_display_screen)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.display_message("📺 Started receiving screen")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start screen receiving: {e}")
            
    def stop_screen_receive(self):
        self.receiving_screen = False
        if self.screen_socket:
            self.screen_socket.close()
        self.receive_btn.config(text="Start Receiving Screen")
        self.screen_label.config(image='', text="Screen sharing not active")
        self.display_message("🛑 Stopped receiving screen")
        
    def receive_and_display_screen(self):
        while self.receiving_screen and self.running:
            try:
                # Receive frame size
                data = b""
                payload_size = struct.calcsize("Q")
                
                while len(data) < payload_size:
                    packet = self.screen_socket.recv(4*1024)
                    if not packet:
                        return
                    data += packet
                
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                
                # Receive frame data
                while len(data) < msg_size:
                    data += self.screen_socket.recv(4*1024)
                
                frame_data = data[:msg_size]
                
                # Decode and display frame
                frame_encoded = pickle.loads(frame_data)
                frame = cv2.imdecode(frame_encoded, cv2.IMREAD_COLOR)
                
                # Convert to display format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_pil = Image.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(frame_pil)
                
                # Update display
                self.screen_label.config(image=frame_tk, text="")
                self.screen_label.image = frame_tk  # Keep reference
                
            except Exception as e:
                print(f"Error receiving screen: {e}")
                break
                
    def on_closing(self):
        self.running = False
        self.disconnect_from_server()
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatScreenClient()
    client.run()