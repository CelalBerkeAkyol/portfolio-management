"""
US Sector Allocation Calculator
Amerika hisse senetleri için sektörel dağılım hesaplama modülü
"""

import json
import sys

SECTOR_CONFIG_FILE = "../data/us_sector_config.json"

def load_sector_config():
    """
    Sektör konfigürasyon dosyasını yükler.
    Returns:
        dict: Sektör bilgilerini içeren dictionary veya None
    """
    try:
        with open(SECTOR_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Hata: '{SECTOR_CONFIG_FILE}' bulunamadı.")
        return None
    except json.JSONDecodeError:
        print(f"Hata: '{SECTOR_CONFIG_FILE}' geçerli bir JSON dosyası değil.")
        return None

def validate_sector_percentages(sector_config):
    """
    Sektör yüzdelerinin toplamının %100 olup olmadığını kontrol eder.
    Args:
        sector_config: Sektör konfigürasyonu
    Returns:
        bool: Geçerliyse True, değilse False
    """
    if not sector_config or 'sectors' not in sector_config:
        return False
    
    sectors = sector_config['sectors']
    total_percent = sum(sector['percentage'] for sector in sectors.values())
    
    if not (0.999 < total_percent < 1.001):
        print(f"\nUYARI: Sektör yüzdeleri toplamı %100 değil!")
        print(f"Hesaplanan Toplam: %{total_percent * 100:.2f}")
        return False
    return True

def calculate_us_sector_allocation(principal, foreign_stocks_allocation, sector_config):
    """
    Kişinin ana parasından Amerika'ya ayrılan kısmı sektörlere dağıtır.
    
    Args:
        principal: Toplam anapara (TL)
        foreign_stocks_allocation: Amerika yatırımına ayrılan yüzde (0-1 arası)
        sector_config: Sektör konfigürasyonu
    
    Returns:
        dict: Her sektör için yatırım miktarı
    """
    if not sector_config or 'sectors' not in sector_config:
        return {}
    
    # Amerika'ya ayrılan toplam miktar
    us_total_amount = principal * foreign_stocks_allocation
    
    # Her sektöre dağıtım
    sector_allocation = {}
    for sector_name, sector_info in sector_config['sectors'].items():
        sector_percent = sector_info['percentage']
        sector_amount = us_total_amount * sector_percent
        sector_allocation[sector_name] = {
            'amount': sector_amount,
            'percentage_of_us': sector_percent,
            'percentage_of_total': foreign_stocks_allocation * sector_percent,
            'description': sector_info['description']
        }
    
    return sector_allocation

def display_us_sector_allocation(name, principal, foreign_stocks_allocation, sector_allocation):
    """
    Amerika sektörel dağılımını ekrana yazdırır.
    
    Args:
        name: Kişi adı
        principal: Toplam anapara
        foreign_stocks_allocation: Amerika'ya ayrılan yüzde
        sector_allocation: Sektörel dağılım dictionary'si
    """
    us_total = principal * foreign_stocks_allocation
    
    print("\n" + "="*70)
    print(f"AMERİKA SEKTÖREL DAĞILIM - {name}")
    print("="*70)
    print(f"Toplam Portföy: {principal:,.2f} TL")
    print(f"Amerika Yatırımı: {us_total:,.2f} TL (%{foreign_stocks_allocation*100:.0f})")
    print("-"*70)
    
    for sector_name, sector_data in sector_allocation.items():
        amount = sector_data['amount']
        pct_of_us = sector_data['percentage_of_us']
        pct_of_total = sector_data['percentage_of_total']
        description = sector_data['description']
        
        print(f"\n{sector_name}:")
        print(f"  Miktar: {amount:>15,.2f} TL")
        print(f"  ABD içinde: %{pct_of_us*100:.0f}")
        print(f"  Toplam portföyde: %{pct_of_total*100:.1f}")
        print(f"  {description}")
    
    print("="*70)

def get_sector_summary_table(sector_allocation):
    """
    Sektörel dağılımı tablo formatında string olarak döndürür.
    
    Args:
        sector_allocation: Sektörel dağılım dictionary'si
    
    Returns:
        str: Tablo formatında sektör özeti
    """
    if not sector_allocation:
        return "Sektörel dağılım bulunamadı."
    
    lines = []
    lines.append("\n" + "-"*60)
    lines.append("SEKTÖR                | MİKTAR (TL)    | ABD İÇİNDE")
    lines.append("-"*60)
    
    for sector_name, sector_data in sector_allocation.items():
        amount = sector_data['amount']
        pct_of_us = sector_data['percentage_of_us']
        lines.append(f"{sector_name:<20} | {amount:>13,.2f} | %{pct_of_us*100:>5.0f}")
    
    lines.append("-"*60)
    
    return "\n".join(lines)

# Test fonksiyonu
def test_sector_calculator():
    """
    Modülü test eder - örnek hesaplama yapar
    """
    sector_config = load_sector_config()
    if not sector_config:
        print("Sektör konfigürasyonu yüklenemedi.")
        return
    
    if not validate_sector_percentages(sector_config):
        print("Sektör yüzdeleri geçersiz!")
        return
    
    # Örnek hesaplama
    test_principal = 200000  # 200 bin TL
    test_us_percent = 0.5     # %50 Amerika
    
    allocation = calculate_us_sector_allocation(test_principal, test_us_percent, sector_config)
    display_us_sector_allocation("Test Kullanıcı", test_principal, test_us_percent, allocation)

if __name__ == "__main__":
    test_sector_calculator()
