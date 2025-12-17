import json
import sys

# Dosya yolları
PEOPLE_FILE = "../data/people.json"
ASSET_FILE = "../data/asset_info.json"

def load_file(file_path):
    """
    Belirtilen JSON dosyasını yükler ve içeriğini döndürür.
    Dosya eksik veya boşsa boş bir liste/sözlük döndürür.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return [] if 'people.json' in file_path else {}
            return json.loads(content)
    except FileNotFoundError:
        print(f"Bilgi: '{file_path}' bulunamadı. Yeni bir dosya oluşturulacak.")
        return [] if 'people.json' in file_path else {}
    except json.JSONDecodeError:
        print(f"Hata: '{file_path}' geçerli bir JSON dosyası değil.")
        return None

def save_file(data, file_path):
    """
    Verilen veriyi belirtilen JSON dosyasına kaydeder.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Veri başarıyla '{file_path}' dosyasına kaydedildi.")

def select_person(people):
    """
    Kullanıcının listeden bir kişi seçmesini sağlar ve seçilen kişinin sözlüğünü döndürür.
    """
    if not people:
        print("Sistemde kayıtlı kişi bulunamadı.")
        return None

    print("\nLütfen portföyünü güncellemek istediğiniz kişiyi seçin:")
    for i, person in enumerate(people):
        print(f"{i + 1}: {person['name']}")
    
    while True:
        try:
            selection_str = input("\nSeçiminiz (rakamla): ")
            selection = int(selection_str)
            if 1 <= selection <= len(people):
                return people[selection - 1]
            else:
                print(f"Lütfen 1 ile {len(people)} arasında bir sayı girin.")
        except ValueError:
            print("Geçersiz giriş. Lütfen bir sayı girin.")

def get_number(message):
    """
    Kullanıcıdan geçerli bir float sayı girmesini tekrar tekrar ister.
    """
    while True:
        try:
            value = float(input(message))
            return value
        except ValueError:
            print("Hata: Lütfen sadece sayısal bir değer girin.")

def get_current_portfolio_info():
    """
    Kullanıcıdan mevcut portföy bilgilerini (tutarları) alır.
    """
    print("\nLütfen mevcut varlık tutarlarınızı girin (TL cinsinden):")
    print("***Tüm değerleri sayı olarak giriniz***\n")
    
    current_portfolio_amount = {}
    current_portfolio_amount["USD Based Interest"] = get_number("USD Mevduat / Yabancı Para Piyasası Fonu tutarı: ")
    current_portfolio_amount["TRY Based Interest"] = get_number("TL Mevduat / Para Piyasası Fonu tutarı: ")
    current_portfolio_amount["Gold"] = get_number("Altın tutarı: ")
    current_portfolio_amount["Silver"] = get_number("Gümüş tutarı: ")
    current_portfolio_amount["Foreign Stocks"] = get_number("Yabancı Hisseler tutarı: ")
    current_portfolio_amount["Turkish Fund"] = get_number("Türk Fon Sepeti tutarı: ")
    current_portfolio_amount["Turkish Stocks"] = get_number("Türk Hisseleri tutarı: ")
    current_portfolio_amount["BTC"] = get_number("BTC tutarı: ")
    current_portfolio_amount["Cryptocurrency"] = get_number("Diğer Kripto Varlıklar (Altcoin) tutarı: ")
    
    return current_portfolio_amount

def calculate_portfolio_risk(portfolio_distribution, asset_info):
    """
    Varlık risk puanlarına göre portföyün toplam riskini hesaplar.
    """
    total_risk_score = 0
    if not portfolio_distribution: return 0
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            risk_score = asset_info[asset].get('risk_score', 0)
            total_risk_score += percent * risk_score
    return total_risk_score

def calculate_portfolio_return(portfolio_distribution, asset_info):
    """
    Varlık getirileri ve kur artışına göre portföyün toplam beklenen getirisini hesaplar.
    """
    total_return_percent = 0
    if not portfolio_distribution: return 0
    usd_return_expectation = asset_info.get("USD Based Interest", {}).get('expected_percentage_return', 0)
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            asset_return = asset_info[asset].get('expected_percentage_return', 0)
            usd_based = asset_info[asset].get('is_usd_based', False)
            if usd_based:
                combined_return = (1 + asset_return) * (1 + usd_return_expectation) - 1
                total_return_percent += percent * combined_return
            else:
                total_return_percent += percent * asset_return
    return total_return_percent

def show_portfolio_report(name, overall_data, asset_info):
    """
    Genel portföy durumunu bir tabloda özetler.
    """
    (overall_principal, overall_amount_dist, overall_percent_dist) = overall_data

    sorted_assets = sorted(list(overall_amount_dist.keys()), key=lambda x: overall_amount_dist.get(x, 0), reverse=True)

    asset_col_width = 25
    amount_col_width = 20
    percent_col_width = 15
    total_width = asset_col_width + amount_col_width + percent_col_width + 5

    print("\n" + "=" * total_width)
    print(f"PORTFÖY DURUM RAPORU: {name}".center(total_width))
    print(f"(Ana Para: {overall_principal:,.2f} TL)".center(total_width))
    print("=" * total_width)
    print(f"{'VARLIK':<{asset_col_width}} | {'TUTAR (TL)':>{amount_col_width}} | {'YÜZDE (%)':>{percent_col_width}}")
    print("-" * total_width)

    for asset in sorted_assets:
        amount = overall_amount_dist.get(asset, 0)
        percent = overall_percent_dist.get(asset, 0) * 100
        
        if abs(amount) < 0.01:
            continue

        print(f"{asset:<{asset_col_width}} | {amount:>{amount_col_width},.2f} | {f'{percent:>{percent_col_width-2}.1f}%'}")

    print("-" * total_width)
    print(f"{'TOPLAM':<{asset_col_width}} | {overall_principal:>{amount_col_width},.2f} | {f'100.0%':>{percent_col_width}}")
    print("-" * total_width)

    overall_risk = calculate_portfolio_risk(overall_percent_dist, asset_info)
    overall_return = calculate_portfolio_return(overall_percent_dist, asset_info) * 100

    print(f"{'Ortalama Risk Puanı':<{asset_col_width}}: {overall_risk:.2f} / 10")
    print(f"{'Yıllık Beklenen Getiri':<{asset_col_width}}: %{overall_return:.2f}")
    print("=" * total_width)

# --- Ana Program ---
if __name__ == "__main__":
    people_list = load_file(PEOPLE_FILE)
    asset_info = load_file(ASSET_FILE)
    if people_list is None or asset_info is None:
        sys.exit("Dosya okuma hatası nedeniyle program durduruldu.")

    selected_person = select_person(people_list)
    if selected_person:
        overall_amount_dist = get_current_portfolio_info()
        overall_principal = sum(overall_amount_dist.values())
        
        if overall_principal == 0:
            print("Toplam portföy tutarı sıfır. Hesaplama yapılamıyor.")
            sys.exit()
        
        # Oranlar artık sadece hesaplama için kullanılıyor, kaydedilmiyor.
        overall_percent_dist = {asset: amount / overall_principal for asset, amount in overall_amount_dist.items()}
        
        # --- DEĞİŞİKLİK ---
        # Seçilen kişinin verileri people.json'a kaydetmek için güncelleniyor.
        # Artık sadece ana para ve tutarlar (amount) kaydediliyor.
        selected_person['principal'] = overall_principal
        selected_person['current_portfolio_amount'] = overall_amount_dist
        
        # --- KALDIRILDI ---
        # current_portfolio ve eski anahtarlar artık kaydedilmiyor.
        # selected_person['current_portfolio'] = overall_percent_dist.copy()
        # selected_person['current_values'] = overall_amount_dist
        
        save_file(people_list, PEOPLE_FILE)

        # Raporlama, hesaplanan güncel verilerle yapılıyor.
        show_portfolio_report(
            selected_person['name'],
            (overall_principal, overall_amount_dist, overall_percent_dist),
            asset_info
        )