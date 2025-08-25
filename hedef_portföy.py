import json
import sys
"""
Hedef portföy hesaplamaları için hedef portföy dağılım oranlarını direkt olarak kişiler.json dosyasından oranlarını kendin girmelisin.
Değerleri buradan tek tek alması uzun sürecek oradan değiştirmesi daha kısa sürüyor
"""

# Dosya adlarını sabitle
VARLIK_DOSYASI = "veriler/varlik_bilgileri.json"
KISILER_DOSYASI = "veriler/kisiler.json"


def dosyayi_yukle(dosya_yolu):
    """
    Belirtilen JSON dosyasını yükler.
    
    Returns:
        dict/list: Yüklenen veriyi döndürür.
        None: Hata durumunda None döndürür.
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı. Lütfen önce dosyayı oluşturun.")
        return None
    except json.JSONDecodeError:
        print(f"Hata: '{dosya_yolu}' dosyası geçerli bir JSON formatında değil.")
        return None

def portfoy_yuzdelerini_dogrula(portfoy_sozlugu):
    """
    Verilen bir portföy sözlüğündeki yüzdelerin toplamının 1.0 olup olmadığını kontrol eder.
    
    Returns:
        bool: Toplam %100 ise True, değilse False döner.
    """
    toplam_yuzde = sum(portfoy_sozlugu.values())
    if not (0.999 < toplam_yuzde < 1.001):
        print("\nUYARI: Portföy yüzdelerinin toplamı %100 değil!")
        print(f"Hesaplanan Toplam Yüzde: %{toplam_yuzde * 100:.2f}")
        return False
    return True

def portfoy_riskini_hesapla(hedef_portfoy, varlik_bilgileri):
    """
    Portföydeki varlıkların risk puanlarına göre toplam riskini hesaplar.
    
    Args:
        hedef_portfoy (dict): Kişinin yatırım dağılımı.
        varlik_bilgileri (dict): Varlık sınıflarının risk bilgileri.

    Returns:
        float: Portföyün ortalama risk puanı.
    """
    toplam_risk_puani = 0
    for varlik, yuzde in hedef_portfoy.items():
        if varlik in varlik_bilgileri:
            risk_puani = varlik_bilgileri[varlik]['risk_puani']
            toplam_risk_puani += yuzde * risk_puani
        else:
            print(f"UYARI: '{varlik}' adlı varlık bilgisi '{VARLIK_DOSYASI}' dosyasında bulunamadı. Risk hesaplamasına dahil edilmedi.")
            
    return toplam_risk_puani

def portfoy_getirisini_hesapla(hedef_portfoy, varlik_bilgileri):
    """
    Portföydeki varlıkların getiri beklentilerine ve kur artışına göre toplam getiri beklentisini hesaplar.
    
    Args:
        hedef_portfoy (dict): Kişinin yatırım dağılımı.
        varlik_bilgileri (dict): Varlık sınıflarının getiri bilgileri.
        kur_beklentileri (dict): Döviz kuru artış beklentileri.

    Returns:
        float: Portföyün ortalama getiri beklentisi.
    """
    toplam_getiri_yuzdesi = 0
    usd_kur_beklentisi = varlik_bilgileri["USD"]['beklenen_getiri_yuzde']
    
    for varlik, yuzde in hedef_portfoy.items():
        if varlik in varlik_bilgileri:
            varlik_getirisi = varlik_bilgileri[varlik]['beklenen_getiri_yuzde']
            dolar_bazli = varlik_bilgileri[varlik]['dolar_bazli']
            
            if dolar_bazli:
                # Dolar bazlı varlıklar için hem kendi getirisi hem de kur getirisi hesaplanır
                birlesik_getiri = (1 + varlik_getirisi) * (1 + usd_kur_beklentisi) - 1
                toplam_getiri_yuzdesi += yuzde * birlesik_getiri
            else:
                # TL bazlı varlıklar için sadece kendi getirisi hesaplanır
                toplam_getiri_yuzdesi += yuzde * varlik_getirisi
        else:
            print(f"UYARI: '{varlik}' adlı varlık bilgisi '{VARLIK_DOSYASI}' dosyasında bulunamadı. Getiri hesaplamasına dahil edilmedi.")
            
    return toplam_getiri_yuzdesi

def dagilimi_hesapla_ve_goster(isim, ana_para, hedef_portfoy, varlik_bilgileri):
    """
    Verilen bilgilere göre yatırım dağılımını, riskini ve getirisini hesaplar ve ekrana yazdırır.
    """
    print("\n" + "="*50)
    print(f"Kişi: {isim}")
    print(f"Ana Para: {ana_para:,.2f} TL")
    print("--- Hedef Yatırım Dağılımı ---")

    for varlik, yuzde in hedef_portfoy.items():
        ayrilmasi_gereken_miktar = ana_para * yuzde
        risk_puani = varlik_bilgileri.get(varlik, {}).get('risk_puani', 'Bilinmiyor')
        beklenen_getiri = varlik_bilgileri.get(varlik, {}).get('beklenen_getiri', 'Bilinmiyor')
        
        print(f"{varlik:<20}: {ayrilmasi_gereken_miktar:>15,.2f} TL (%{yuzde*100:.0f})")
        print(f"{' ':<20} Risk: {risk_puani:<2} / 10 | Getiri: {beklenen_getiri}")

    # Portföyün toplam riskini ve getiri beklentisini hesapla
    toplam_portfoy_riski = portfoy_riskini_hesapla(hedef_portfoy, varlik_bilgileri)
    toplam_portfoy_getirisi = portfoy_getirisini_hesapla(hedef_portfoy, varlik_bilgileri)
    
    print("-" * 50)
    print(f"Portföyün Ağırlıklı Ortalama Riski: {toplam_portfoy_riski:.2f} / 10")
    print(f"Portföyün Yıllık (TL Bazlı) Getiri Beklentisi: %{toplam_portfoy_getirisi * 100:.2f}")
    print("="*50)

# --- Ana Program ---
if __name__ == "__main__":
    
    tum_kisiler = dosyayi_yukle(KISILER_DOSYASI)
    varlik_bilgileri = dosyayi_yukle(VARLIK_DOSYASI)

    
    if tum_kisiler is None or varlik_bilgileri is None :
        sys.exit()

    print("Lütfen portföyünü görüntülemek istediğiniz kişiyi seçin:")
    for i, kisi in enumerate(tum_kisiler):
        print(f"{i + 1}: {kisi['isim']}")

    while True:
        try:
            secim_str = input("\nSeçiminiz (sayı olarak): ")
            secim = int(secim_str)
            if 1 <= secim <= len(tum_kisiler):
                secilen_kisi = tum_kisiler[secim - 1]
                break
            else:
                print("Lütfen listedeki sayılardan birini girin.")
        except ValueError:
            print("Geçersiz giriş. Lütfen bir sayı girin.")

    kisi_ismi = secilen_kisi['isim']
    kisi_ana_para = secilen_kisi['ana_para']
    kisi_hedef_portfoy = secilen_kisi['hedef_portfoy']
    
    if portfoy_yuzdelerini_dogrula(kisi_hedef_portfoy):
        dagilimi_hesapla_ve_goster(kisi_ismi, kisi_ana_para, kisi_hedef_portfoy, varlik_bilgileri)
    else:
        print(f"\n{kisi_ismi} adlı kişinin portföy yapılandırması geçersiz olduğu için işlem yapılamadı.")