import socket
import threading
import os
import time

class FileServer:
    def __init__(self, host='0.0.0.0', receive_port=5001, send_port=5002):
        self.host = host
        self.receive_port = receive_port  # Dosya almak için port
        self.send_port = send_port        # Dosya göndermek için port
        self.received_file = "received_file.dat"
        self.file_received = False
        
    def start_receiver(self):
        """Dosya almak için sunucuyu başlat"""
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            receiver_socket.bind((self.host, self.receive_port))
            receiver_socket.listen(1)
            print(f"Dosya alıcı {self.receive_port} portunda dinleniyor...")
            
            while True:
                client_socket, client_address = receiver_socket.accept()
                print(f"Bağlantı kabul edildi: {client_address}")
                
                # Dosya alımını thread'de yap
                thread = threading.Thread(target=self.receive_file, args=(client_socket,))
                thread.start()
                
        except Exception as e:
            print(f"Hata: {e}")
        finally:
            receiver_socket.close()
    
    def receive_file(self, client_socket):
        """Dosya al"""
        try:
            # Önce dosya boyutunu al
            file_size_bytes = client_socket.recv(8)
            file_size = int.from_bytes(file_size_bytes, 'big')
            print(f"Alınacak dosya boyutu: {file_size} bytes")
            
            # Dosyayı al
            with open(self.received_file, 'wb') as file:
                received = 0
                while received < file_size:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    file.write(data)
                    received += len(data)
                    # İlerleme çubuğu
                    progress = (received / file_size) * 100
                    print(f"\rAlınıyor: %{progress:.1f} ({received}/{file_size} bytes)", end='')
            
            self.file_received = True
            print(f"\nDosya başarıyla alındı: {self.received_file}")
            print(f"Toplam alınan veri: {received} bytes")
            
        except Exception as e:
            print(f"\nDosya alım hatası: {e}")
        finally:
            client_socket.close()
    
    def send_file_to_next(self, next_host):
        """Dosyayı zincirdeki bir sonraki bilgisayara gönder"""
        if not os.path.exists(self.received_file):
            print("Gönderilecek dosya bulunamadı!")
            return False
            
        try:
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            send_socket.connect((next_host, self.send_port))
            
            file_size = os.path.getsize(self.received_file)
            print(f"Gönderilecek dosya boyutu: {file_size} bytes")
            
            # Dosya boyutunu gönder
            send_socket.send(file_size.to_bytes(8, 'big'))
            
            # Dosyayı gönder
            with open(self.received_file, 'rb') as file:
                sent = 0
                start_time = time.time()
                
                while True:
                    data = file.read(4096)
                    if not data:
                        break
                    send_socket.send(data)
                    sent += len(data)
                    
                    # İlerleme çubuğu
                    progress = (sent / file_size) * 100
                    print(f"\rGönderiliyor: %{progress:.1f} ({sent}/{file_size} bytes)", end='')
                
                end_time = time.time()
                transfer_time = end_time - start_time
                speed = file_size / transfer_time / 1024 / 1024  # MB/s
                
                print(f"\nDosya başarıyla gönderildi!")
                print(f"Toplam süre: {transfer_time:.2f} saniye")
                print(f"Ortalama hız: {speed:.2f} MB/s")
            
            send_socket.close()
            return True
            
        except Exception as e:
            print(f"\nGönderme hatası: {e}")
            return False
    
    def start(self):
        """Sunucuyu başlat"""
        # Alıcıyı başlat
        receiver_thread = threading.Thread(target=self.start_receiver)
        receiver_thread.daemon = True
        receiver_thread.start()
        
        print("Dosya transfer sunucusu başlatıldı!")
        print(f"Alıcı port: {self.receive_port}")
        print(f"Gönderici port: {self.send_port}")
        
        # Kullanıcı arayüzü
        while True:
            print("\n" + "="*50)
            print("          DOSYA TRANSFER SİSTEMİ")
            print("="*50)
            print("1. Dosyayı zincirdeki bir sonraki bilgisayara gönder")
            print("2. Durumu kontrol et")
            print("3. Çıkış")
            print("-"*50)
            
            choice = input("Seçiminiz (1-3): ").strip()
            
            if choice == '1':
                if self.file_received:
                    next_host = input("Zincirdeki sonraki bilgisayarın IP adresi: ").strip()
                    if next_host:
                        self.send_file_to_next(next_host)
                    else:
                        print("Geçersiz IP adresi!")
                else:
                    print("Henüz dosya alınmadı!")
                    
            elif choice == '2':
                status = "ALINDI" if self.file_received else "BEKLİYOR"
                file_size = os.path.getsize(self.received_file) if os.path.exists(self.received_file) else 0
                print(f"Dosya durumu: {status}")
                print(f"Dosya boyutu: {file_size} bytes")
                print(f"Dosya adı: {self.received_file}")
                
            elif choice == '3':
                print("Program sonlandırılıyor...")
                break
            else:
                print("Geçersiz seçim! Lütfen 1-3 arasında bir sayı girin.")

# Programı başlat
if __name__ == "__main__":
    server = FileServer()
    server.start()
