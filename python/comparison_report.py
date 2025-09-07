# comparison.py

import json
import sys

PEOPLE_FILE = "../data/people.json"
ASSET_FILE = "../data/asset_info.json"

def load_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                print(f"Hata: '{file_path}' dosyası boş.")
                return [] if 'people.json' in file_path else {}
            return json.loads(content)
    except FileNotFoundError:
        print(f"Hata: '{file_path}' bulunamadı. Lütfen dosya yolunu kontrol edin.")
        return None
    except json.JSONDecodeError:
        print(f"Hata: '{file_path}' geçerli bir JSON dosyası değil.")
        return None

def select_person(people):
    if not people:
        print("Kayıtlı kişi bulunamadı. Lütfen önce bir kişi ekleyin.")
        return None
    print("\nRaporunu görmek istediğiniz kişiyi seçin:")
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

def calculate_portfolio_risk(portfolio_distribution, asset_info):
    total_risk_score = 0
    if not portfolio_distribution: return 0
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            risk_score = asset_info[asset].get('risk_score', 0)
            total_risk_score += percent * risk_score
    return total_risk_score

def calculate_portfolio_return(portfolio_distribution, asset_info, scenario='base'):
    if not portfolio_distribution: return 0
    scenario_keys = {
        "base": "expected_percentage_return",
        "good": "good_scenario_return",
        "bad": "bad_scenario_return"
    }
    key = scenario_keys.get(scenario, "expected_percentage_return")
    total_return_percent = 0
    # Doların kendi getirisini, 'USD Based Interest' varlığının senaryo getirisinden alıyoruz.
    usd_return_expectation = asset_info.get("USD Based Interest", {}).get(key, 0)
    for asset, percent in portfolio_distribution.items():
        if asset in asset_info:
            asset_return = asset_info[asset].get(key, 0)
            usd_based = asset_info[asset].get('is_usd_based', False)
            if usd_based:
                combined_return = (1 + asset_return) * (1 + usd_return_expectation) - 1
                total_return_percent += percent * combined_return
            else:
                total_return_percent += percent * asset_return
    return total_return_percent

# --- GÜNCELLENDİ: show_scenario_analysis fonksiyonu artık base_dist de alıyor ---
def show_scenario_analysis(principal, current_dist, base_dist, target_dist, asset_info):
    # Tablo genişliği artırıldı
    print("\n" + "-"*130)
    print("SENARYO ANALİZİ (Yıllık TL Bazlı Getiri ve Portföy Değeri)".center(130))
    print("-" * 130)
    print(f"{'SENARYO':<15} | {'MEVCUT PORTFÖY':^35} | {'SABİT PORTFÖY':^35} | {'HEDEF PORTFÖY':^35}")
    print(f"{'':<15} | {'% Getiri':^16} | {'Son Değer (TL)':>16} | {'% Getiri':^16} | {'Son Değer (TL)':>16} | {'% Getiri':^16} | {'Son Değer (TL)':>16}")
    print("-" * 130)

    scenarios = [
        ("Kötü Senaryo", "bad"),
        ("Baz Senaryo", "base"),
        ("İyi Senaryo", "good")
    ]

    for scenario_name, scenario_code in scenarios:
        current_return = calculate_portfolio_return(current_dist, asset_info, scenario=scenario_code)
        current_final = principal * (1 + current_return)
        
        # Sabit portföy için getiri ve son değer hesaplaması
        base_return = calculate_portfolio_return(base_dist, asset_info, scenario=scenario_code)
        # Not: Sabit portföyün ana parası farklı olduğu için, bu getiriyi toplam ana para ile çarpmak yanıltıcı olabilir.
        # Ancak karşılaştırma için toplam ana para üzerinden varsayımsal bir değer hesaplıyoruz.
        base_final = principal * (1 + base_return)

        target_return = calculate_portfolio_return(target_dist, asset_info, scenario=scenario_code)
        target_final = principal * (1 + target_return)
        
        print(
            f"{scenario_name:<15} | "
            f"{current_return*100:^15.2f}% | {current_final:>16,.2f} | "
            f"{base_return*100:^15.2f}% | {base_final:>16,.2f} | "
            f"{target_return*100:^15.2f}% | {target_final:>16,.2f}"
        )

# --- GÜNCELLENDİ: show_comparison_report fonksiyonu artık base_dist de alıyor ---
def show_comparison_report(name, principal, current_dist, base_dist, target_dist, asset_info):
    # Tablo genişliği artırıldı
    table_width = 150
    print("\n" + "="*table_width)
    print(f"Kişi: {name}".center(table_width))
    print(f"Ana Para: {principal:,.2f} TL".center(table_width))
    print("="*table_width)
    print("PORTFÖY DAĞILIM KARŞILAŞTIRMASI".center(table_width))
    print("-" * table_width)
    # Yeni sütun eklendi
    print(f"{'VARLIK':<20} | {'MEVCUT':^30} | {'SABİT (UZUN VADELİ)':^30} | {'HEDEF':^30} | {'DEĞİŞİM (Al/Sat)':^25}")
    print("-" * table_width)

    all_assets = set(current_dist.keys()) | set(base_dist.keys()) | set(target_dist.keys())
    
    for asset in sorted(list(all_assets)):
        current_percent = current_dist.get(asset, 0)
        current_amount = current_percent * principal
        
        base_percent = base_dist.get(asset, 0)
        base_amount = base_percent * principal

        target_percent = target_dist.get(asset, 0)
        target_amount = target_percent * principal
        
        diff_amount = target_amount - current_amount

        current_str = f"{current_amount:,.2f} TL (%{current_percent*100:.1f})"
        base_str = f"{base_amount:,.2f} TL (%{base_percent*100:.1f})" if base_percent > 0 else ""
        target_str = f"{target_amount:,.2f} TL (%{target_percent*100:.1f})"
        diff_str = f"{diff_amount:+,.2f} TL" if abs(diff_amount) > 0.01 else ""
        
        print(f"{asset:<20} | {current_str:>30} | {base_str:>30} | {target_str:>30} | {diff_str:>25}")

    print("-" * table_width)
    
    # Sabit portföy için toplam ve risk hesaplamaları
    base_principal = principal * sum(base_dist.values())
    current_risk = calculate_portfolio_risk(current_dist, asset_info)
    base_risk = calculate_portfolio_risk(base_dist, asset_info)
    target_risk = calculate_portfolio_risk(target_dist, asset_info)

    current_total_str = f"Toplam: {principal:,.2f} TL"
    base_total_str = f"Toplam: {base_principal:,.2f} TL"
    target_total_str = f"Toplam: {principal:,.2f} TL"
    print(f"{'':<20} | {current_total_str:>30} | {base_total_str:>30} | {target_total_str:>30} | {'':>25}")
    
    current_risk_str = f"Ort. Risk: {current_risk:.2f}/10"
    base_risk_str = f"Ort. Risk: {base_risk:.2f}/10"
    target_risk_str = f"Ort. Risk: {target_risk:.2f}/10"
    print(f"{'RİSK SKORU':<20} | {current_risk_str:>30} | {base_risk_str:>30} | {target_risk_str:>30} | {'':>25}")
    
    show_scenario_analysis(principal, current_dist, base_dist, target_dist, asset_info)
    print("=" * table_width)

if __name__ == "__main__":
    people_list = load_file(PEOPLE_FILE)
    asset_info = load_file(ASSET_FILE)
    if people_list is None or asset_info is None:
        sys.exit("Dosya okuma hatası nedeniyle program durduruldu.")

    selected_person = select_person(people_list)
    if selected_person:
        name = selected_person['name']
        principal = selected_person['principal']
        current_dist = selected_person.get('current_portfolio_distribution')
        target_dist = selected_person.get('target_portfolio')
        # YENİ: Sabit portföy dağılımını da JSON'dan al
        base_dist = selected_person.get('base_portfolio_distribution', {})

        if current_dist and target_dist:
            show_comparison_report(
                name,
                principal,
                current_dist,
                base_dist, # Fonksiyona yeni parametre olarak gönder
                target_dist,
                asset_info
            )
        else:
            print("\nMevcut ve/veya hedef portföy bilgileri eksik.")
            print("Karşılaştırma raporu oluşturulamadı.")
            print("Lütfen önce 'current_portfolio.py' betiğini çalıştırdığınızdan emin olun.")