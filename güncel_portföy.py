import json
import sys

# Dosya adlarını sabitleyelim
PORTFOY_DOSYASI = "veriler/kisiler.json"
VARLIK_DOSYASI = "veriler/varlik_bilgileri.json"

def dosyayi_yukle(dosya_yolu):
    """
    Belirtilen JSON dosyasını yükler ve içeriğini döndürür.
    Dosya yoksa veya boşsa, boş bir liste/sözlük döndürür.
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
            if not icerik:
                return [] if 'kisiler.json' in dosya_yolu else {}
            return json.loads(icerik)
    except FileNotFoundError:
        print(f"Bilgi: '{dosya_yolu}' dosyası bulunamadı. Yeni bir dosya oluşturulacak.")
        return [] if 'kisiler.json' in dosya_yolu else {}
    except json.JSONDecodeError:
        print(f"Hata: '{dosya_yolu}' dosyası geçerli bir JSON formatında değil.")
        return None

def dosyaya_kaydet(veri, dosya_yolu):
    """
    Verilen veriyi belirtilen JSON dosyasına kaydeder.
    """
    with open(dosya_yolu, 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)
    print(f"Bilgiler başarıyla '{dosya_yolu}' dosyasına kaydedildi.")

def kisi_sec(kisiler):
    """
    Listeden bir kişi seçilmesini sağlar ve seçilen kişinin tüm bilgisini (dictionary) döndürür.
    """
    if not kisiler:
        print("Sistemde kayıtlı kişi bulunamadı.")
        return None

    print("\nLütfen portföyünü güncellemek istediğiniz kişiyi seçin:")
    for i, kisi in enumerate(kisiler):
        print(f"{i + 1}: {kisi['isim']}")
    
    while True:
        try:
            secim_str = input("\nSeçiminiz (sayı olarak): ")
            secim = int(secim_str)
            if 1 <= secim <= len(kisiler):
                return kisiler[secim - 1]
            else:
                print(f"Lütfen 1 ile {len(kisiler)} arasında bir sayı girin.")
        except ValueError:
            print("Geçersiz giriş. Lütfen bir sayı girin.")

def sayi_al(mesaj):
    """
    Kullanıcıdan geçerli bir sayı (float) alana kadar soruyu tekrar sorar.
    """
    while True:
        try:
            deger = float(input(mesaj))
            return deger
        except ValueError:
            print("Hata: Lütfen sadece sayısal bir değer giriniz.")

# BU KISIMDAKİ DEĞİŞİKLİKLER DİKKATİNİZİ ÇEKSİN
def guncel_portfoy_bilgilerini_al():
    """
    Kullanıcıdan güncel portföy bilgilerini (para miktarları olarak) alır.
    """
    print("\nLütfen güncel varlık miktarlarınızı (TL olarak) giriniz:")
    print("***Tüm değerleri sayısal olarak giriniz***\n")
    
    guncel_portfoy_miktar = {}
    
    # Yeni faiz kategorileri eklendi
    guncel_portfoy_miktar["TL Based Interest"] = sayi_al("TL Bazlı Faiz / Para Piyasası Fonu miktarınız: ")
    guncel_portfoy_miktar["USD Based Interest"] = sayi_al("Dolar Bazlı Faiz / Yabancı Para Piyasası Fonu miktarınız: ")
    
    guncel_portfoy_miktar["Gold"] = sayi_al("Altın miktarınız: ")
    guncel_portfoy_miktar["Silver"] = sayi_al("Gümüş miktarınız: ")
    
    # Türk hisse senetleri ve fonlarını tek kalemde topluyoruz
    turk_hisse = sayi_al("Türk Hisse Senedi miktarınız: ")
    turk_fon = sayi_al("Türk Hisse Senedi Fonu miktarınız: ")
    guncel_portfoy_miktar["Turkish Companies"] = turk_hisse + turk_fon
    
    guncel_portfoy_miktar["Foreign Companies"] = sayi_al("Yabancı Hisse Senedi / Fon miktarınız: ")
    guncel_portfoy_miktar["Crypto Money"] = sayi_al("Kripto Para miktarınız: ")

    return guncel_portfoy_miktar
# DEĞİŞİKLİK BURADA BİTTİ

def portfoy_riskini_hesapla(portfoy_dagilimi, varlik_bilgileri):
    """
    Portföydeki varlıkların risk puanlarına göre toplam riskini hesaplar.
    """
    toplam_risk_puani = 0
    for varlik, yuzde in portfoy_dagilimi.items():
        if varlik in varlik_bilgileri:
            risk_puani = varlik_bilgileri[varlik]['risk_puani']
            toplam_risk_puani += yuzde * risk_puani
        else:
            print(f"UYARI: '{varlik}' adlı varlık bilgisi '{VARLIK_DOSYASI}' dosyasında bulunamadı. Risk hesaplamasına dahil edilmedi.")
            
    return toplam_risk_puani

def portfoy_getirisini_hesapla(portfoy_dagilimi, varlik_bilgileri):
    """
    Portföydeki varlıkların getiri beklentilerine ve kur artışına göre toplam getiri beklentisini hesaplar.
    """
    toplam_getiri_yuzdesi = 0
    usd_kur_beklentisi = varlik_bilgileri.get("USD", {}).get('beklenen_getiri_yuzde', 0)
    
    for varlik, yuzde in portfoy_dagilimi.items():
        if varlik in varlik_bilgileri:
            varlik_getirisi = varlik_bilgileri[varlik]['beklenen_getiri_yuzde']
            dolar_bazli = varlik_bilgileri[varlik]['dolar_bazli']
            
            if dolar_bazli:
                birlesik_getiri = (1 + varlik_getirisi) * (1 + usd_kur_beklentisi) - 1
                toplam_getiri_yuzdesi += yuzde * birlesik_getiri
            else:
                toplam_getiri_yuzdesi += yuzde * varlik_getirisi
        else:
            print(f"UYARI: '{varlik}' adlı varlık bilgisi '{VARLIK_DOSYASI}' dosyasında bulunamadı. Getiri hesaplamasına dahil edilmedi.")
            
    return toplam_getiri_yuzdesi

def portfoy_raporu_goster(isim, baslik, para_dagilimi, yuzde_dagilimi, ana_para, varlik_bilgileri):
    """
    Verilen bilgilere göre yatırım dağılımını, riskini ve getirisini hesaplar ve ekrana yazdırır.
    """
    print("\n" + "="*50)
    print(f"Kişi: {isim}")
    print(f"Portföy Tipi: {baslik}")
    print(f"Ana Para: {ana_para:,.2f} TL")
    print("--- Yatırım Dağılımı ---")

    for varlik, miktar in para_dagilimi.items():
        yuzde = yuzde_dagilimi.get(varlik, 0)
        risk_puani = varlik_bilgileri.get(varlik, {}).get('risk_puani', 'Bilinmiyor')
        beklenen_getiri = varlik_bilgileri.get(varlik, {}).get('beklenen_getiri', 'Bilinmiyor')
        
        print(f"{varlik:<20}: {miktar:>15,.2f} TL (%{yuzde*100:.1f})")
        print(f"{' ':<20} Risk: {risk_puani:<2} / 10 | Getiri: {beklenen_getiri}")

    toplam_portfoy_riski = portfoy_riskini_hesapla(yuzde_dagilimi, varlik_bilgileri)
    toplam_portfoy_getirisi = portfoy_getirisini_hesapla(yuzde_dagilimi, varlik_bilgileri)
    
    print("-" * 50)
    print(f"Portföyün Ağırlıklı Ortalama Riski: {toplam_portfoy_riski:.2f} / 10")
    print(f"Portföyün Yıllık (TL Bazlı) Getiri Beklentisi: %{toplam_portfoy_getirisi * 100:.2f}")
    print("="*50)


# --- Ana Program ---
if __name__ == "__main__":
    kisiler_listesi = dosyayi_yukle(PORTFOY_DOSYASI)
    varlik_bilgileri = dosyayi_yukle(VARLIK_DOSYASI)
    
    if kisiler_listesi is None or varlik_bilgileri is None:
        sys.exit("Dosya okuma hatası nedeniyle program durduruldu.")

    secilen_kisi_objesi = kisi_sec(kisiler_listesi)

    if secilen_kisi_objesi:
        yeni_para_dagilimi = guncel_portfoy_bilgilerini_al()
        
        yeni_ana_para = sum(yeni_para_dagilimi.values())
        
        yeni_yuzde_dagilimi = {varlik: round(miktar / yeni_ana_para, 4) for varlik, miktar in yeni_para_dagilimi.items()}
        
        secilen_kisi_objesi['ana_para'] = yeni_ana_para
        secilen_kisi_objesi['para_dagilimi'] = yeni_para_dagilimi
        secilen_kisi_objesi['guncel_portfoy_dagilimi'] = yeni_yuzde_dagilimi
        
        dosyaya_kaydet(kisiler_listesi, PORTFOY_DOSYASI)
        
        kisi_ismi = secilen_kisi_objesi['isim']
        
        portfoy_raporu_goster(
            kisi_ismi,
            "Güncel Portföy",
            yeni_para_dagilimi,
            yeni_yuzde_dagilimi,
            yeni_ana_para,
            varlik_bilgileri
        )
        
        hedef_portfoy_dagilimi = secilen_kisi_objesi.get('hedef_portfoy', {})
        if hedef_portfoy_dagilimi:
            hedef_para_dagilimi = {varlik: yuzde * yeni_ana_para for varlik, yuzde in hedef_portfoy_dagilimi.items()}
            portfoy_raporu_goster(
                kisi_ismi,
                "Hedef Portföy",
                hedef_para_dagilimi,
                hedef_portfoy_dagilimi,
                yeni_ana_para,
                varlik_bilgileri
            )