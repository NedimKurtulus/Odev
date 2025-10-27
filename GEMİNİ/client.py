# Dosya Adı: relay_server.py (Kişi 2'den Kişi 9'a herkes için)

import socket
import os
import time

# --- AYARLAR ---
GELEN_PORT = 65432 # Bu kişi, önceki kişiden bu porttan alacak (Kişi X-1 -> Kişi X)
GELEN_DOSYA_ADI = 'alinan_dosya_relay.bin' # Alınan dosya adı

# --- FONKSİYONLAR (Önceki Server ve Client'tan alındı) ---

def dosya_al(dinleme_port, dosya_adi):
    print(f"\n--- BÖLÜM 1: ALMA (Sunucu Rolü) ---")
    HOST = '0.0.0.0' # Tüm arayüzlerden dinle
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, dinleme_port))
            s.listen()
            print(f"[{HOST}:{dinleme_port}] adresinde dinleniyor... Önceki arkadaştan bağlantı bekleniyor.")

            conn, addr = s.accept()
            with conn:
                print(f"Bağlantı kuruldu: {addr}")
                
                # Dosya boyutunu al
                dosya_boyutu_bayt = conn.recv(1024)
                dosya_boyutu = int(dosya_boyutu_bayt.decode('utf-8').strip())
                print(f"Beklenen Dosya Boyutu: {dosya_boyutu} bayt")

                alinan_bayt = 0
                with open(dosya_adi, 'wb') as f:
                    while alinan_bayt < dosya_boyutu:
                        baytlar = conn.recv(4096)
                        if not baytlar:
                            break
                        f.write(baytlar)
                        alinan_bayt += len(baytlar)
                        print(f"Alınıyor... ({alinan_bayt*100/dosya_boyutu:.2f}%)", end='\r')
                
                print(f"\n[BAŞARILI] '{dosya_adi}' dosyası başarıyla alındı. Boyut: {os.path.getsize(dosya_adi)} bayt")
                return True, os.path.getsize(dosya_adi)

        except Exception as e:
            print(f"[HATA] Alma sırasında bir hata oluştu: {e}")
            return False, 0


def dosya_gonder(hedef_ip, hedef_port, dosya_yolu):
    print(f"\n--- BÖLÜM 2: GÖNDERME (İstemci Rolü) ---")
    
    if not os.path.exists(dosya_yolu):
        print(f"[HATA] Gönderilecek '{dosya_yolu}' dosyası bulunamadı.")
        return False

    dosya_boyutu = os.path.getsize(dosya_yolu)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((hedef_ip, hedef_port))
            print(f"{hedef_ip}:{hedef_port} adresine bağlanıldı.")

            # Dosya boyutunu gönder
            s.sendall(str(dosya_boyutu).encode('utf-8').ljust(1024))
            
            gonderilen_bayt = 0
            with open(dosya_yolu, 'rb') as f:
                while True:
                    baytlar = f.read(4096)
                    if not baytlar:
                        break
                    s.sendall(baytlar)
                    gonderilen_bayt += len(baytlar)
                    print(f"Gönderiliyor... ({gonderilen_bayt*100/dosya_boyutu:.2f}%)", end='\r')

            print(f"\n[BAŞARILI] '{dosya_yolu}' dosyası başarıyla gönderildi.")
            return True

        except Exception as e:
            print(f"[HATA] Gönderme sırasında bir hata oluştu: {e}")
            return False

# --- ANA PROGRAM ZİNCİRİ ---

if __name__ == '__main__':
    
    # Adım 1: Önceki kişiden dosyayı al (Sunucu rolü)
    alindi, dosya_boyutu = dosya_al(GELEN_PORT, GELEN_DOSYA_ADI)
    
    if alindi:
        print("\n--- AKTARIM BİLGİSİ ---")
        print(f"Alınan Dosya Adı: {GELEN_DOSYA_ADI}")
        print(f"Alınan Dosya Boyutu: {dosya_boyutu} bayt")
        
        # Adım 2: Bir sonraki kişiye gönderme (İstemci rolü)
        
        # Kullanıcıdan bir sonraki hedefin IP ve Port bilgisini iste
        hedef_ip = input("Dosyanın gönderileceği **SONRAKİ ARKADAŞIN** IP adresini girin: ")
        hedef_port = int(input("Dosyanın gönderileceği **SONRAKİ ARKADAŞIN** Port numarasını girin (Genellikle 65432): "))
        
        dosya_gonder(hedef_ip, hedef_port, GELEN_DOSYA_ADI)
