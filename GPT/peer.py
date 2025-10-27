#!/usr/bin/env python3
import socket, struct, argparse, os

HDR_FMT = "!QH"  # 8 byte filesize (unsigned long long), 2 byte filename length (unsigned short)
HDR_SZ = struct.calcsize(HDR_FMT)
BUF = 64*1024

def recv_file_from_socket(conn, out_folder="."):
    # read header
    hdr = b""
    while len(hdr) < HDR_SZ:
        part = conn.recv(HDR_SZ - len(hdr))
        if not part:
            raise ConnectionError("Header truncated")
        hdr += part
    filesize, name_len = struct.unpack(HDR_FMT, hdr)
    name = b""
    while len(name) < name_len:
        part = conn.recv(name_len - len(name))
        if not part:
            raise ConnectionError("Filename truncated")
        name += part
    filename = name.decode('utf-8')
    out_path = os.path.join(out_folder, filename)
    with open(out_path, "wb") as f:
        received = 0
        while received < filesize:
            chunk = conn.recv(min(BUF, filesize - received))
            if not chunk:
                raise ConnectionError("Transfer interrupted")
            f.write(chunk)
            received += len(chunk)
    return out_path, filesize

def send_file_over_socket(conn, path):
    filesize = os.path.getsize(path)
    filename = os.path.basename(path).encode('utf-8')
    name_len = len(filename)
    hdr = struct.pack(HDR_FMT, filesize, name_len) + filename
    conn.sendall(hdr)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(BUF)
            if not chunk:
                break
            conn.sendall(chunk)

def act_as_receiver(prev_port, save_folder):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", prev_port))
    sock.listen(1)
    print(f"Dinleniyor -> port {prev_port}. Gelen bekleniyor...")
    conn, addr = sock.accept()
    print("Bağlantı geldi:", addr)
    with conn:
        path, size = recv_file_from_socket(conn, save_folder)
    sock.close()
    print(f"Dosya alındı: {path} ({size} byte)")
    return path

def act_as_sender(next_host, next_port, path):
    print(f"Bağlanıyor -> {next_host}:{next_port} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((next_host, next_port))
    with sock:
        send_file_over_socket(sock, path)
    print("Dosya gönderildi:", path)

def act_as_source(next_host, next_port, send_file):
    if not next_host or not next_port:
        raise ValueError("Kaynak için --next-host ve --next-port gerekli")
    act_as_sender(next_host, next_port, send_file)

def main():
    p = argparse.ArgumentParser(description="Peer: al ve/veya yolla. Zincir içinde kullanılmak üzere.")
    p.add_argument("--prev-port", type=int, help="Önce dosya alacağın port (boşsa alım yok).")
    p.add_argument("--next-host", help="Dosyayı yollanacak sonraki host (boşsa gönderim yok).")
    p.add_argument("--next-port", type=int, help="Dosyayı yollanacak sonraki port.")
    p.add_argument("--send-file", help="Eğer bu makine kaynak ise gönderilecek dosya yolu.")
    p.add_argument("--save-folder", default=".", help="Alınan dosyaların kaydedileceği klasör.")
    args = p.parse_args()

    # Kaynak düğüm: doğrudan gönderim yap
    if args.send_file and args.next_host and args.next_port and not args.prev_port:
        act_as_source(args.next_host, args.next_port, args.send_file)
        return

    # Zincir içi veya son düğüm: önce al. sonra varsa başka yere yolla.
    received_path = None
    if args.prev_port:
        received_path = act_as_receiver(args.prev_port, args.save_folder)
    else:
        print("prev-port belirtilmedi. Alım yapılmayacak.")

    if args.next_host and args.next_port:
        # eğer send_file verilmişse, onu gönder; değilse alınanı gönder
        path_to_send = args.send_file if args.send_file else received_path
        if not path_to_send:
            print("Gönderilecek dosya yok.")
            return
        act_as_sender(args.next_host, args.next_port, path_to_send)
    else:
        print("next-host/next-port belirtilmedi. Gönderim yapılmayacak.")

if __name__ == "__main__":
    main()
