import psutil
import time
import pandas as pd
from tabulate import tabulate

# Veri tutulacak değişkenler
data = []
columns = ["IP Address", "Download (Bytes)", "Upload (Bytes)"]

# Önceki ölçülen değerler için sözlük
data_counters = {}

# Gerçek zamanlı ağ izleme uygulaması
try:
    while True:
        # Ağ istatistiklerini almak için
        net_io = psutil.net_io_counters(pernic=False)
        connections = psutil.net_connections(kind='inet')
        traffic_info = {}
        
        for conn in connections:
            if conn.raddr:
                raddr_ip = conn.raddr.ip
                # Eğer IP daha önceden eklenmemişse şimdi ekle
                if raddr_ip not in traffic_info:
                    traffic_info[raddr_ip] = [0, 0]  # [download, upload]
                
                # Toplam ağ verilerini kullanarak indirme ve yükleme miktarını ekle 
                download = net_io.bytes_recv # / (1024 * 1024) # # mb cinsinden olmasını sağlıyor
                upload = net_io.bytes_sent # / (1024 * 1024) # # mb cinsinden olmasını sağlıyor
                
                # Önceki ölçümlere göre farkı hesapla
                if raddr_ip not in data_counters:
                    data_counters[raddr_ip] = {
                        'bytes_recv': download,
                        'bytes_sent': upload
                    }
                else:
                    prev_stats = data_counters[raddr_ip]
                    traffic_info[raddr_ip][0] = download - prev_stats['bytes_recv']
                    traffic_info[raddr_ip][1] = upload - prev_stats['bytes_sent']
                    
                    # Şimdiki değerleri kaydet
                    data_counters[raddr_ip]['bytes_recv'] = download
                    data_counters[raddr_ip]['bytes_sent'] = upload
        
        # Yeni gelen bilgileri ekleyip ekranda göster
        data = [[ip, traffic[0], traffic[1]] for ip, traffic in traffic_info.items()]
        df = pd.DataFrame(data, columns=columns)
        print(tabulate(df, headers='keys', tablefmt='psql'))
        time.sleep(1)
except KeyboardInterrupt:
    print("Gerçek zamanlı izleme sona erdi.")
