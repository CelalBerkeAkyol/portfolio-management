import json
import sys

# Dosya yollarını sabitliyoruz
PORTFOY_DOSYASI = "veriler/kisiler.json"
VARLIK_DOSYASI = "veriler/varlik_bilgileri.json"

def dosyayi_yukle(dosya_yolu):
    """
    Belirtilen JSON dosyasını yükler ve içeriğini döndürür.
    """
    try:
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            icerik = f.read()
            if not icerik:
                print(f"Hata: '{dosya_yolu}' dosyası boş.")
                return [] if 'kisiler.json' in dosya_yolu else {}
            return json.loads(icerik)
    except FileNotFoundError:
        print(f"Hata: '{dosya_yolu}' dosyası bulunamadı. Lütfen önce dosyaların doğru konumda olduğundan emin olun.")
        return None
    except json.JSONDecodeError:
        print(f"Hata: '{dosya_yolu}' dosyası geçerli bir JSON formatında değil.")
        return None

def kisi_sec(kisiler):
    """
    Listeden bir kişi seçilmesini sağlar ve seçilen kişinin tüm bilgisini (dictionary) döndürür.
    """
    if not kisiler:
        print("Sistemde kayıtlı kişi bulunamadı. Lütfen önce 'güncel_portföy.py' ile bir kişi ekleyin.")
        return None

    print("\nLütfen raporunu görmek istediğiniz kişiyi seçin:")
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

def portfoy_getirisini_hesapla(portfoy_dagilimi, varlik_bilgileri, senaryo='baz'):
    """
    Portföydeki varlıkların getiri beklentilerini belirtilen senaryoya göre hesaplar.
    Senaryo: 'kötü', 'baz', 'iyi' olabilir.
    """
    senaryo_getiri_anahtarlari = {
        "baz": "beklenen_getiri_yuzde",
        "iyi": "iyi_senaryo_beklenen_getiri",
        "kötü": "kötü_senaryo_beklenen_getiri"
    }
    
    getiri_anahtari = senaryo_getiri_anahtarlari.get(senaryo, "beklenen_getiri_yuzde")
    
    toplam_getiri_yuzdesi = 0
    # Dolar kur beklentisini de senaryoya göre alıyoruz
    usd_kur_beklentisi = varlik_bilgileri.get("USD", {}).get(getiri_anahtari, 0)
    
    for varlik, yuzde in portfoy_dagilimi.items():
        if varlik in varlik_bilgileri:
            # Varlığın kendi getirisini senaryoya göre alıyoruz
            varlik_getirisi = varlik_bilgileri[varlik].get(getiri_anahtari, 0)
            dolar_bazli = varlik_bilgileri[varlik]['dolar_bazli']
            
            if dolar_bazli:
                # Dolar bazlı varlıklar için hem kendi getirisi hem de kur getirisi hesaba katılır
                birlesik_getiri = (1 + varlik_getirisi) * (1 + usd_kur_beklentisi) - 1
                toplam_getiri_yuzdesi += yuzde * birlesik_getiri
            else:
                toplam_getiri_yuzdesi += yuzde * varlik_getirisi
        else:
            print(f"UYARI: '{varlik}' adlı varlık bilgisi '{VARLIK_DOSYASI}' dosyasında bulunamadı. Getiri hesaplamasına dahil edilmedi.")
            
    return toplam_getiri_yuzdesi

def senaryo_analizi_yap_ve_goster(yuzde_dagilimi, varlik_bilgileri, ana_para):
    """
    Tüm senaryolar için portföy getirilerini hesaplar ve sonuçları yazdırır.
    """
    print("-" * 50)
    print("--- SENARYO ANALİZİ (Yıllık TL Bazlı) ---")

    senaryolar = {
        "Kötü Senaryo": "kötü",
        "Baz Senaryo"  : "baz",
        "İyi Senaryo"  : "iyi"
    }

    for senaryo_adi, senaryo_kodu in senaryolar.items():
        getiri = portfoy_getirisini_hesapla(yuzde_dagilimi, varlik_bilgileri, senaryo=senaryo_kodu)
        son_para = ana_para * (1 + getiri)
        print(f"{senaryo_adi:<15}: Getiri: %{getiri * 100:6.2f} | Portföy Değeri: {son_para:15,.2f} TL")


def portfoy_raporu_goster(isim, baslik, para_dagilimi, yuzde_dagilimi, ana_para, varlik_bilgileri):
    """
    Verilen bilgilere göre yatırım dağılımını, riskini ve TÜM SENARYOLARA GÖRE getirisini hesaplar ve ekrana yazdırır.
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
    
    print("-" * 50)
    print(f"Portföyün Ağırlıklı Ortalama Riski: {toplam_portfoy_riski:.2f} / 10")
    
    # Her senaryo için getiri beklentisini hesaplayıp yazdırıyoruz
    senaryo_analizi_yap_ve_goster(yuzde_dagilimi, varlik_bilgileri, ana_para)
    
    print("="*50)


def portfoy_farkini_hesapla_ve_goster(guncel_dagilim, hedef_dagilim, ana_para):
    """
    Güncel portföyü hedef portföye dönüştürmek için gereken değişimleri hesaplar ve raporlar.
    """
    print("\n" + "="*50)
    print("Portföy Değişim Raporu (Güncelden Hedefe)")
    print("-" * 50)

    tum_varliklar = sorted(list(set(guncel_dagilim.keys()) | set(hedef_dagilim.keys())))

    for varlik in tum_varliklar:
        guncel_yuzde = guncel_dagilim.get(varlik, 0)
        hedef_yuzde = hedef_dagilim.get(varlik, 0)
        yuzde_farki = hedef_yuzde - guncel_yuzde
        para_farki = yuzde_farki * ana_para

        if abs(para_farki) > 0.01: # Çok küçük farkları göstermemek için
            print(f"{varlik:<20}: {para_farki:,.2f} TL ({yuzde_farki*100:+.1f}%)")

    print("="*50)


# --- Ana Program ---
if __name__ == "__main__":
    kisiler_listesi = dosyayi_yukle(PORTFOY_DOSYASI)
    varlik_bilgileri = dosyayi_yukle(VARLIK_DOSYASI)
    
    if kisiler_listesi is None or varlik_bilgileri is None:
        sys.exit("Dosya okuma hatası nedeniyle program durduruldu.")

    secilen_kisi_objesi = kisi_sec(kisiler_listesi)

    if secilen_kisi_objesi:
        kisi_ismi = secilen_kisi_objesi['isim']
        kisi_ana_para = secilen_kisi_objesi['ana_para']
        
        # 1. Güncel Portföy raporunu oluştur
        guncel_yuzde_dagilimi = secilen_kisi_objesi.get('guncel_portfoy_dagilimi')
        if guncel_yuzde_dagilimi:
            guncel_para_dagilimi = {varlik: yuzde * kisi_ana_para for varlik, yuzde in guncel_yuzde_dagilimi.items()}
            portfoy_raporu_goster(
                kisi_ismi,
                "Güncel Portföy",
                guncel_para_dagilimi,
                guncel_yuzde_dagilimi,
                kisi_ana_para,
                varlik_bilgileri
            )
        else:
            print("\nGüncel portföy bilgileri bulunamadı. Lütfen 'güncel_portföy.py' dosyasını çalıştırarak portföyünüzü kaydedin.")

        # 2. Hedef Portföy raporunu oluştur
        hedef_portfoy_dagilimi = secilen_kisi_objesi.get('hedef_portfoy')
        if hedef_portfoy_dagilimi:
            hedef_para_dagilimi = {varlik: yuzde * kisi_ana_para for varlik, yuzde in hedef_portfoy_dagilimi.items()}
            portfoy_raporu_goster(
                kisi_ismi,
                "Hedef Portföy",
                hedef_para_dagilimi,
                hedef_portfoy_dagilimi,
                kisi_ana_para,
                varlik_bilgileri
            )
        else:
            print("Hedef portföy bilgileri bulunamadı.")
            
        # 3. Güncel ile Hedef arasındaki fark raporunu oluştur
        if guncel_yuzde_dagilimi and hedef_portfoy_dagilimi:
            portfoy_farkini_hesapla_ve_goster(
                guncel_yuzde_dagilimi,
                hedef_portfoy_dagilimi,
                kisi_ana_para
            )
        else:
            print("\nGüncel ve/veya hedef portföy bilgileri eksik. Değişim raporu oluşturulamadı.")