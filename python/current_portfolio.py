import json
import sys

# Dosya yolları
PEOPLE_FILE = "data/people.json"
ASSET_FILE = "data/asset_info.json"

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
    current_portfolio_amount["TRY Based Interest"] = get_number("TL Mevduat / Para Piyasası Fonu tutarı: ")
    current_portfolio_amount["USD Based Interest"] = get_number("USD Mevduat / Yabancı Para Piyasası Fonu tutarı: ")
    current_portfolio_amount["Gold"] = get_number("Altın tutarı: ")
    current_portfolio_amount["Silver"] = get_number("Gümüş tutarı: ")
    current_portfolio_amount["Real Estate"] = get_number("Gayrimenkul / GYO Fonu tutarı: ")
    current_portfolio_amount["Turkish Fund"] = get_number("Türk Fon Sepeti tutarı: ")
    current_portfolio_amount["Turkish Spec Stocks"] = get_number("Türk Spekülatif Hisseleri tutarı: ")
    current_portfolio_amount["Turkish Grow Stocks"] = get_number("Türk Büyüme Hisseleri tutarı: ")
    current_portfolio_amount["Turkish Value Stocks"] = get_number("Türk Değer Hisseleri tutarı: ")  
    current_portfolio_amount["Foreign Stocks"] = get_number("Yabancı Hisseler tutarı: ")
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

# --- İSTEĞİNİZE GÖRE GÜNCELLENMİŞ BİRLEŞİK RAPOR FONKSİYONU ---
def show_combined_report(name, overall_data, base_data, active_data, asset_info):
    """
    Genel, Sabit ve Aktif portföyleri yan yana karşılaştırmalı bir tabloda gösterir.
    Aktif portföy yüzdeleri, Genel Toplam Ana Paraya göre hesaplanır.
    """
    (overall_principal, overall_amount_dist, overall_percent_dist) = overall_data
    (base_principal, base_amount_dist, base_percent_dist) = base_data
    (active_principal, active_amount_dist, active_percent_dist) = active_data

    all_assets = set(overall_amount_dist.keys()) | set(base_amount_dist.keys()) | set(active_amount_dist.keys())
    sorted_assets = sorted(list(all_assets), key=lambda x: overall_amount_dist.get(x, 0), reverse=True)

    # Tablo genişliklerini tanımla
    asset_col_width = 20
    main_col_width = 38
    total_width = asset_col_width + (main_col_width * 3) + 9

    print("\n" + "=" * total_width)
    print(f"PORTFÖY DURUM RAPORU: {name}".center(total_width))
    print("=" * total_width)
    print(f"{'VARLIK':<{asset_col_width}} | {'GENEL PORTFÖY':^{main_col_width}} | {'SABİT PORTFÖY (UZUN VADELİ)':^{main_col_width}} | {'AKTİF PORTFÖY (DEĞİŞKEN)':^{main_col_width}}")
    print(f"{'':<{asset_col_width}} | {'(Ana Para: ' + f'{overall_principal:,.2f} TL)':^{main_col_width}} | {'(Ana Para: ' + f'{base_principal:,.2f} TL)':^{main_col_width}} | {'(Ana Para: ' + f'{active_principal:,.2f} TL)':^{main_col_width}}")
    print("-" * total_width)
    print(f"{'':<{asset_col_width}} | {'Tutar (TL)':>20} | {'%':>15} | {'Tutar (TL)':>20} | {'%':>15} | {'Tutar (TL)':>20} | {'%':>15}")
    print("-" * total_width)

    for asset in sorted_assets:
        overall_amount = overall_amount_dist.get(asset, 0)
        overall_percent = overall_percent_dist.get(asset, 0) * 100
        
        base_amount = base_amount_dist.get(asset, 0)
        base_percent = base_percent_dist.get(asset, 0) * 100
        
        active_amount = active_amount_dist.get(asset, 0)
        
        # --- YÜZDE HESAPLAMA DEĞİŞİKLİĞİ BURADA ---
        # Aktif varlık yüzdesi artık Aktif Ana Paraya göre değil, Genel Ana Paraya göre hesaplanıyor.
        active_percent_display = (active_amount / overall_principal) * 100 if overall_principal != 0 else 0

        if abs(overall_amount) < 0.01 and abs(base_amount) < 0.01 and abs(active_amount) < 0.01:
            continue

        print(f"{asset:<{asset_col_width}} | {overall_amount:>20,.2f} | {f'({overall_percent:6.1f}%)':>15} | "
              f"{base_amount:>20,.2f} | {f'({base_percent:6.1f}%)':>15} | "
              f"{active_amount:>20,.2f} | {f'({active_percent_display:6.1f}%)':>15}") # Değiştirilen değişken kullanıldı

    print("-" * total_width)
    
    # --- TOPLAM SATIRI YÜZDE HESAPLAMA DEĞİŞİKLİĞİ BURADA ---
    # Aktif portföyün toplam yüzdesi, genel portföyün ne kadarlık bir kısmını oluşturduğunu gösterir.
    active_total_percent_display = (active_principal / overall_principal) * 100 if overall_principal != 0 else 0
    
    print(f"{'TOPLAM':<{asset_col_width}} | {overall_principal:>20,.2f} | {f'(100.0%)':>15} | "
          f"{base_principal:>20,.2f} | {f'({sum(base_percent_dist.values())*100:6.1f}%)':>15} | "
          f"{active_principal:>20,.2f} | {f'({active_total_percent_display:6.1f}%)':>15}")
    print("-" * total_width)

    # Risk ve Getiri hesaplamaları için hala orijinal (kendi içinde %100'e tamamlanan) yüzde dağılımı kullanılır.
    # Bu, bu hesaplamaların doğruluğunu korur.
    overall_risk = calculate_portfolio_risk(overall_percent_dist, asset_info)
    base_risk = calculate_portfolio_risk(base_percent_dist, asset_info)
    active_risk = calculate_portfolio_risk(active_percent_dist, asset_info)

    overall_return = calculate_portfolio_return(overall_percent_dist, asset_info) * 100
    base_return = calculate_portfolio_return(base_percent_dist, asset_info) * 100
    active_return = calculate_portfolio_return(active_percent_dist, asset_info) * 100

    print(f"{'Ortalama Risk':<{asset_col_width}} | {f'{overall_risk:.2f} / 10':^{main_col_width}} | {f'{base_risk:.2f} / 10':^{main_col_width}} | {f'{active_risk:.2f} / 10':^{main_col_width}}")
    print(f"{'Yıllık Getiri Bekl.':<{asset_col_width}} | {f'%{overall_return:.2f}':^{main_col_width}} | {f'%{base_return:.2f}':^{main_col_width}} | {f'%{active_return:.2f}':^{main_col_width}}")
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
            
        overall_percent_dist = {asset: amount / overall_principal for asset, amount in overall_amount_dist.items()}
        
        selected_person['principal'] = overall_principal
        selected_person['amount_distribution'] = overall_amount_dist
        selected_person['current_portfolio_distribution'] = overall_percent_dist
        selected_person['current_values'] = overall_amount_dist.copy()
        selected_person['current_portfolio'] = overall_percent_dist.copy()
        save_file(people_list, PEOPLE_FILE)

        person_name = selected_person['name']
        
        base_portfolio_def = selected_person.get('base_portfolio_distribution', {})
        if not base_portfolio_def:
             print("\nBu kişi için bir 'sabit portföy' tanımı bulunmuyor.")
        else:
            base_amount_dist = {asset: overall_principal * percent for asset, percent in base_portfolio_def.items()}
            base_principal = sum(base_amount_dist.values())
            
            active_amount_dist = overall_amount_dist.copy()
            for asset, base_amount in base_amount_dist.items():
                active_amount_dist[asset] = active_amount_dist.get(asset, 0) - base_amount
            
            active_principal = sum(active_amount_dist.values())
            
            # --- BURASI DÜZELTİLDİ ---
            # Hata: Daha önce sadece pozitif değerli varlıklar dahil ediliyordu.
            # Düzeltme: Negatifler de dahil edilerek tüm varlıkların yüzdesi hesaplanıyor.
            active_percent_dist = {}
            if active_principal != 0:
                 active_percent_dist = {asset: amount / active_principal for asset, amount in active_amount_dist.items()}

            show_combined_report(
                person_name,
                (overall_principal, overall_amount_dist, overall_percent_dist),
                (base_principal, base_amount_dist, base_portfolio_def),
                (active_principal, active_amount_dist, active_percent_dist),
                asset_info
            )