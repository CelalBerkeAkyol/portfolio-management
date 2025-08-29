import json

# Dosya yolları (değişiklik yok)
PORTFOY_DOSYASI = "../veriler/kisiler.json"
ANKET_DOSYASI = "risk_anketi.json"

# load_portfolios, save_portfolios, load_questions, kisi_sec fonksiyonları öncekiyle aynı...

def load_portfolios(file_path):
    """Kişi portföylerini içeren JSON dosyasını yükler."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Hata: '{file_path}' dosyası bulunamadı.")
        return []
    except json.JSONDecodeError:
        print(f"Hata: '{file_path}' dosyası geçerli bir JSON formatında değil.")
        return []

def save_portfolios(file_path, data):
    """Verileri (güncellenmiş kişi listesi) JSON dosyasına kaydeder."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"\nBilgiler başarıyla '{file_path}' dosyasına kaydedildi.")
    except Exception as e:
        print(f"Dosyayı kaydederken bir hata oluştu: {e}")

def load_questions():
    """Risk anketi sorularını JSON dosyasından yükler."""
    try:
        with open(ANKET_DOSYASI, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('risk_questions', [])
    except FileNotFoundError:
        print(f"Hata: '{ANKET_DOSYASI}' dosyası bulunamadı.")
        return None
    except json.JSONDecodeError:
        print(f"Hata: '{ANKET_DOSYASI}' dosyası geçerli bir JSON formatında değil.")
        return None

def kisi_sec(kisiler):
    """Listeden bir kişi seçilmesini sağlar ve seçilen kişinin tüm bilgisini (dictionary) döndürür."""
    if not kisiler:
        print("Sistemde kayıtlı kişi bulunamadı.")
        return None

    print("\nLütfen risk algısı puanını hesaplamak istediğiniz kişiyi seçin:")
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


# --- BU FONKSİYON GÜNCELLENDİ ---
def calculate_risk_profile():
    """
    Kullanıcıya risk anketi yapar, sonuçları gösterir ve ortalama risk algısı puanını döndürür.
    """
    questions = load_questions()
    if not questions:
        return None

    total_score = 0
    num_questions = len(questions)

    print("\n--- Yatırımcı Risk Profili Anketi ---")
    print("Lütfen her soru için size en uygun seçeneğin harfini (A, B, C...) girin.")
    print("-" * 35)
    for i, question_data in enumerate(questions, 1):
        question_text = question_data['question_text']
        options = question_data['options']

        print(f"\nSoru {i}/{num_questions}: {question_text}")
        option_map = {}
        for option in options:
            print(f"  {option['option_id']}) {option['option_text']}")
            option_map[option['option_id'].upper()] = option['score']

        while True:
            user_input = input("Cevabınız: ").upper()
            if user_input in option_map:
                total_score += option_map[user_input]
                break
            else:
                print(f"Geçersiz giriş. Lütfen geçerli seçeneklerden birini girin: {', '.join(option_map.keys())}")
    
    # Ortalama risk algısı puanını hesapla
    risk_algisi = 0
    if num_questions > 0:
        risk_algisi = total_score / num_questions

    print("\n" + "-" * 35)
    print(f"Anket Tamamlandı. Risk Algısı Puanınız: {risk_algisi:.1f}")
    print("-" * 35)

    # Risk profili eşiklerini ortalama puana göre güncelle
    # Örnek 3 soru için: 40/3=13.3, 70/3=23.3
    if risk_algisi <= 13.3:
        risk_level = "Düşük Riskli"
        description = "Finansal güvenliği ön planda tutan, risk almaktan kaçınan bir yatırımcısınız."
    elif risk_algisi <= 23.3:
        risk_level = "Orta Riskli (Dengeli)"
        description = "Hem sermayenizi korumayı hem de orta düzeyde getiri elde etmeyi hedefliyorsunuz."
    else:
        risk_level = "Yüksek Riskli"
        description = "Yüksek getiri potansiyeli için yüksek riski göze alabilen bir yatırımcısınız."

    print(f"Risk Profiliniz: {risk_level}")
    print(f"Açıklama: {description}")
    
    # Hesaplanan ortalama puanı ana programa göndermek için return ediyoruz
    return risk_algisi

# --- BU FONKSİYON GÜNCELLENDİ ---
def main():
    """Ana program akışını yönetir."""
    kisiler_listesi = load_portfolios(PORTFOY_DOSYASI)
    
    if not kisiler_listesi:
        print("İşlem yapılamadı. Lütfen kişi listesini kontrol edin.")
        return

    secilen_kisi = kisi_sec(kisiler_listesi)

    if secilen_kisi:
        # Risk anketini yap ve ortalama puanı al
        risk_algisi_puani = calculate_risk_profile()
        
        if risk_algisi_puani is not None:
            # Seçilen kişinin sözlüğüne 'risk_algisi' anahtarını ekle/güncelle
            secilen_kisi['risk_algisi'] = round(risk_algisi_puani, 2) # Puanı 2 ondalıkla sınırla
            
            print(f"\n{secilen_kisi['isim']} adlı kişinin yeni risk algısı puanı '{secilen_kisi['risk_algisi']}' olarak güncellendi.")
            
            # Güncellenmiş tüm listeyi dosyaya geri kaydet
            save_portfolios(PORTFOY_DOSYASI, kisiler_listesi)

if __name__ == "__main__":
    main()