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
    return toplam_risk_puani

def portfoy_getirisini_hesapla(portfoy_dagilimi, varlik_bilgileri, senaryo='baz'):
    """
    Portföydeki varlıkların getiri beklentilerini belirtilen senaryoya göre hesaplar.
    """
    senaryo_getiri_anahtarlari = {
        "baz": "beklenen_getiri_yuzde",
        "iyi": "iyi_senaryo_beklenen_getiri",
        "kötü": "kötü_senaryo_beklenen_getiri"
    }
    getiri_anahtari = senaryo_getiri_anahtarlari.get(senaryo, "beklenen_getiri_yuzde")
    toplam_getiri_yuzdesi = 0
    usd_kur_beklentisi = varlik_bilgileri.get("USD", {}).get(getiri_anahtari, 0)
    
    for varlik, yuzde in portfoy_dagilimi.items():
        if varlik in varlik_bilgileri:
            varlik_getirisi = varlik_bilgileri[varlik].get(getiri_anahtari, 0)
            dolar_bazli = varlik_bilgileri[varlik]['dolar_bazli']
            
            if dolar_bazli:
                birlesik_getiri = (1 + varlik_getirisi) * (1 + usd_kur_beklentisi) - 1
                toplam_getiri_yuzdesi += yuzde * birlesik_getiri
            else:
                toplam_getiri_yuzdesi += yuzde * varlik_getirisi
    return toplam_getiri_yuzdesi

# YENİ EKLENEN FONKSİYON
def senaryo_analizi_goster(ana_para, guncel_dagilim_yuzde, hedef_dagilim_yuzde, varlik_bilgileri):
    """
    Güncel ve Hedef portföyler için senaryo analizini yan yana gösterir.
    """
    print("\n" + "-"*110)
    print("SENARYO ANALİZİ (Yıllık TL Bazlı Getiri ve Portföy Değeri)".center(110))
    print("-" * 110)
    print(f"{'SENARYO':<20} | {'GÜNCEL PORTFÖY':^42} | {'HEDEF PORTFÖY':^42}")
    print(f"{'':<20} | {'% Getiri':^20} | {'Son Değer (TL)':>20} | {'% Getiri':^20} | {'Son Değer (TL)':>20}")
    print("-" * 110)

    senaryolar = [
        ("Kötü Senaryo", "kötü"),
        ("Baz Senaryo", "baz"),
        ("İyi Senaryo", "iyi")
    ]

    for senaryo_adi, senaryo_kodu in senaryolar:
        # Güncel portföy için hesaplama
        guncel_getiri = portfoy_getirisini_hesapla(guncel_dagilim_yuzde, varlik_bilgileri, senaryo=senaryo_kodu)
        guncel_son_deger = ana_para * (1 + guncel_getiri)

        # Hedef portföy için hesaplama
        hedef_getiri = portfoy_getirisini_hesapla(hedef_dagilim_yuzde, varlik_bilgileri, senaryo=senaryo_kodu)
        hedef_son_deger = ana_para * (1 + hedef_getiri)

        print(
            f"{senaryo_adi:<20} | "
            f"{guncel_getiri*100:^19.2f}% | {guncel_son_deger:>20,.2f} | "
            f"{hedef_getiri*100:^19.2f}% | {hedef_son_deger:>20,.2f}"
        )
    
# GÜNCELLENMİŞ RAPOR FONKSİYONU
def karsilastirmali_rapor_goster(isim, ana_para, guncel_dagilim_yuzde, hedef_dagilim_yuzde, varlik_bilgileri):
    """
    Güncel ve Hedef portföyleri ve senaryo analizlerini yan yana karşılaştırmalı olarak gösterir.
    """
    print("\n" + "="*110)
    print(f"Kişi: {isim}".center(110))
    print(f"Ana Para: {ana_para:,.2f} TL".center(110))
    print("="*110)
    print("PORTFÖY DAĞILIM KARŞILAŞTIRMASI".center(110))
    print("-" * 110)
    
    print(f"{'VARLIK':<20} | {'GÜNCEL DURUM':^30} | {'HEDEF PORTFÖY':^30} | {'DEĞİŞİM (Alım/Satım)':^25}")
    print("-" * 110)

    tum_varliklar = sorted(list(set(guncel_dagilim_yuzde.keys()) | set(hedef_dagilim_yuzde.keys())))

    for varlik in tum_varliklar:
        guncel_yuzde = guncel_dagilim_yuzde.get(varlik, 0)
        guncel_para = guncel_yuzde * ana_para
        guncel_str = f"{guncel_para:,.2f} TL (%{guncel_yuzde*100:.1f})"

        hedef_yuzde = hedef_dagilim_yuzde.get(varlik, 0)
        hedef_para = hedef_yuzde * ana_para
        hedef_str = f"{hedef_para:,.2f} TL (%{hedef_yuzde*100:.1f})"
        
        fark_para = hedef_para - guncel_para
        fark_str = f"{fark_para:+,.2f} TL" if abs(fark_para) > 0.01 else ""

        print(f"{varlik:<20} | {guncel_str:>30} | {hedef_str:>30} | {fark_str:>25}")

    print("-" * 110)

    guncel_risk = portfoy_riskini_hesapla(guncel_dagilim_yuzde, varlik_bilgileri)
    hedef_risk = portfoy_riskini_hesapla(hedef_dagilim_yuzde, varlik_bilgileri)
    
    guncel_toplam_str = f"Toplam: {ana_para:,.2f} TL"
    hedef_toplam_str = f"Toplam: {ana_para:,.2f} TL"
    print(f"{'':<20} | {guncel_toplam_str:>30} | {hedef_toplam_str:>30} | {'':>25}")
    
    guncel_risk_str = f"Ort. Risk: {guncel_risk:.2f}/10"
    hedef_risk_str = f"Ort. Risk: {hedef_risk:.2f}/10"
    print(f"{'RİSK PUANI':<20} | {guncel_risk_str:>30} | {hedef_risk_str:>30} | {'':>25}")

    # SENARYO ANALİZİ BÖLÜMÜNÜ RAPORA EKLİYORUZ
    senaryo_analizi_goster(ana_para, guncel_dagilim_yuzde, hedef_dagilim_yuzde, varlik_bilgileri)
    
    print("=" * 110)

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
        
        guncel_yuzde_dagilimi = secilen_kisi_objesi.get('guncel_portfoy_dagilimi')
        hedef_portfoy_dagilimi = secilen_kisi_objesi.get('hedef_portfoy')

        if guncel_yuzde_dagilimi and hedef_portfoy_dagilimi:
            karsilastirmali_rapor_goster(
                kisi_ismi,
                kisi_ana_para,
                guncel_yuzde_dagilimi,
                hedef_portfoy_dagilimi,
                varlik_bilgileri
            )
        else:
            print("\nGüncel ve/veya hedef portföy bilgileri eksik.")
            print("Karşılaştırmalı rapor oluşturulamadı.")
            print("Lütfen hem 'güncel_portföy.py' hem de 'hedef_belirle.py' betiklerini çalıştırdığınızdan emin olun.")