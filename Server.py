import socket
import threading
import cv2
import pickle
import struct
import time
from datetime import datetime

class ChatScreenServer:
    def __init__(self, host='localhost', chat_port=9999, screen_port=9998):
        self.host = host
        self.chat_port = chat_port
        self.screen_port = screen_port
        self.clients = {}
        self.screen_clients = []
        self.running = True
        
    def start_server(self):
        # Start chat server
        chat_thread = threading.Thread(target=self.start_chat_server)
        chat_thread.daemon = True
        chat_thread.start()
        
        # Start screen sharing server
        screen_thread = threading.Thread(target=self.start_screen_server)
        screen_thread.daemon = True
        screen_thread.start()
        
        print(f"🚀 Server started!")
        print(f"📱 Chat server: {self.host}:{self.chat_port}")
        print(f"🖥️  Screen server: {self.host}:{self.screen_port}")
        print("Press Ctrl+C to stop the server")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down server...")
            self.running = False
    
    def start_chat_server(self):
        chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        chat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        chat_socket.bind((self.host, self.chat_port))
        chat_socket.listen(5)
        
        while self.running:
            try:
                client_socket, addr = chat_socket.accept()
                print(f"💬 Chat client connected: {addr}")
                
                client_thread = threading.Thread(
                    target=self.handle_chat_client, 
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
            except:
                break
    
    def handle_chat_client(self, client_socket, addr):
        try:
            # Get username
            username = client_socket.recv(1024).decode('utf-8')
            self.clients[username] = client_socket
            
            # Broadcast user joined
            join_msg = f"🟢 {username} joined the chat"
            self.broadcast_message(join_msg, username)
            
            while self.running:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                formatted_msg = f"[{timestamp}] {username}: {message}"
                print(formatted_msg)
                self.broadcast_message(formatted_msg, username)
                
        except Exception as e:
            print(f"Error handling chat client {addr}: {e}")
        finally:
            if username in self.clients:
                del self.clients[username]
                leave_msg = f"🔴 {username} left the chat"
                self.broadcast_message(leave_msg, username)
            client_socket.close()
    
    def broadcast_message(self, message, sender=None):
        disconnected = []
        for username, client_socket in self.clients.items():
            if username != sender:
                try:
                    client_socket.send(message.encode('utf-8'))
                except:
                    disconnected.append(username)
        
        # Clean up disconnected clients
        for username in disconnected:
            if username in self.clients:
                del self.clients[username]
    
    def start_screen_server(self):
        screen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        screen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        screen_socket.bind((self.host, self.screen_port))
        screen_socket.listen(5)
        
        while self.running:
            try:
                client_socket, addr = screen_socket.accept()
                print(f"🖥️  Screen client connected: {addr}")
                
                # Determine if client is sender or receiver
                role = client_socket.recv(1024).decode('utf-8')
                
                if role == "SENDER":
                    screen_thread = threading.Thread(
                        target=self.handle_screen_sender, 
                        args=(client_socket, addr)
                    )
                else:  # RECEIVER
                    screen_thread = threading.Thread(
                        target=self.handle_screen_receiver, 
                        args=(client_socket, addr)
                    )
                
                screen_thread.daemon = True
                screen_thread.start()
                
            except:
                break
    
    def handle_screen_sender(self, client_socket, addr):
        try:
            while self.running:
                # Receive frame size
                data = b""
                payload_size = struct.calcsize("Q")
                
                while len(data) < payload_size:
                    packet = client_socket.recv(4*1024)
                    if not packet:
                        return
                    data += packet
                
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]
                
                # Receive frame data
                while len(data) < msg_size:
                    data += client_socket.recv(4*1024)
                
                frame_data = data[:msg_size]
                
                # Broadcast frame to all receivers
                self.broadcast_screen_frame(frame_data, msg_size)
                
        except Exception as e:
            print(f"Error handling screen sender {addr}: {e}")
        finally:
            client_socket.close()
    
    def handle_screen_receiver(self, client_socket, addr):
        self.screen_clients.append(client_socket)
        try:
            while self.running:
                time.sleep(0.1)  # Keep connection alive
        except:
            pass
        finally:
            if client_socket in self.screen_clients:
                self.screen_clients.remove(client_socket)
            client_socket.close()
    
    def broadcast_screen_frame(self, frame_data, msg_size):
        disconnected = []
        packed_msg_size = struct.pack("Q", msg_size)
        
        for client in self.screen_clients[:]:
            try:
                client.sendall(packed_msg_size + frame_data)
            except:
                disconnected.append(client)
        
        # Clean up disconnected clients
        for client in disconnected:
            if client in self.screen_clients:
                self.screen_clients.remove(client)

if __name__ == "__main__":
    server = ChatScreenServer()
    server.start_server()