import socket
import os
import time

class FileClient:
    def __init__(self, server_host, server_port=5001):
        self.server_host = server_host
        self.server_port = server_port
    
    def send_file(self, file_path):
        """Dosya gönder"""
        if not os.path.exists(file_path):
            print("Dosya bulunamadı!")
            return False
            
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))
            
            file_size = os.path.getsize(file_path)
            print(f"Gönderilecek dosya: {file_path}")
            print(f"Dosya boyutu: {file_size} bytes")
            print(f"Hedef: {self.server_host}:{self.server_port}")
            print("-" * 50)
            
            # Dosya boyutunu gönder
            client_socket.send(file_size.to_bytes(8, 'big'))
            
            # Dosyayı gönder
            with open(file_path, 'rb') as file:
                sent = 0
                start_time = time.time()
                
                while True:
                    data = file.read(4096)
                    if not data:
                        break
                    client_socket.send(data)
                    sent += len(data)
                    
                    # İlerleme çubuğu
                    progress = (sent / file_size) * 100
                    print(f"\rİlerleme: %{progress:.1f} ({sent}/{file_size} bytes)", end='')
                
                end_time = time.time()
                transfer_time = end_time - start_time
                speed = file_size / transfer_time / 1024 / 1024  # MB/s
                
                print(f"\n✓ Dosya başarıyla gönderildi!")
                print(f"⏱️  Toplam süre: {transfer_time:.2f} saniye")
                print(f"🚀 Ortalama hız: {speed:.2f} MB/s")
            
            client_socket.close()
            return True
            
        except Exception as e:
            print(f"\n✗ Gönderme hatası: {e}")
            return False

def main():
    print("="*50)
    print("          DOSYA GÖNDERİCİ")
    print("="*50)
    
    server_ip = input("Dosyayı alacak bilgisayarın IP adresi: ").strip()
    
    if not server_ip:
        print("Geçersiz IP adresi!")
        return
    
    client = FileClient(server_ip)
    
    while True:
        print("\n" + "-"*50)
        print("1. Dosya gönder")
        print("2. IP adresini değiştir")
        print("3. Çıkış")
        print("-"*50)
        
        choice = input("Seçiminiz (1-3): ").strip()
        
        if choice == '1':
            file_path = input("Gönderilecek dosya yolu: ").strip()
            if os.path.exists(file_path):
                client.send_file(file_path)
            else:
                print("Dosya bulunamadı! Lütfen dosya yolunu kontrol edin.")
                
        elif choice == '2':
            new_ip = input("Yeni IP adresi: ").strip()
            if new_ip:
                client.server_host = new_ip
                print(f"IP adresi güncellendi: {new_ip}")
            else:
                print("Geçersiz IP adresi!")
                
        elif choice == '3':
            print("Program sonlandırılıyor...")
            break
        else:
            print("Geçersiz seçim! Lütfen 1-3 arasında bir sayı girin.")

if __name__ == "__main__":
    main()
