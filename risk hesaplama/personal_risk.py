import json

def load_data():
    """
    Json dosyasındaki verileri indirir ve buradaki soruları liste halinde döndürür
    """
    try:
        # JSON dosyasını oku ve verileri yükle
        with open('risk_anketi.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            questions = data.get('risk_questions', [])
            return questions

    except FileNotFoundError:
        print("Hata: 'risk_anketi.json' dosyası bulunamadı.")
        print("Lütfen JSON içeriğini bir dosyaya kaydedip tekrar deneyin.")
        return

    except json.JSONDecodeError:
        print("Hata: 'risk_anketi.json' dosyası geçerli bir JSON formatında değil.")
        return
    

def calculate_risk_profile():
    questions = load_data()
    total_score = 0
    num_questions = len(questions)

    print("--- Yatırım Risk Algısı Anketi ---")
    print("Lütfen her soru için size en uygun seçeneğin harfini (A, B, C) girin.")
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
                print("Geçersiz giriş. Lütfen A, B veya C harflerinden birini girin.")

    print("\n" + "-" * 35)
    print(f"Anket Tamamlandı. Toplam Risk Puanınız: {total_score}")
    print(f"Anket Tamamlandı. Toplam Risk Puanınız: {total_score/num_questions}")
    print("-" * 35)

    # Toplam puana göre risk profilini belirle
    if total_score <= 40:
        risk_level = "Düşük Riskli"
        description = "Finansal güvenliği ön planda tutan, risk almaktan kaçınan bir yatırımcısınız. Portföyünüzün büyük bir kısmı risksiz veya düşük riskli araçlardan (vadeli mevduat, devlet tahvilleri vb.) oluşmalıdır."
    elif total_score <= 70:
        risk_level = "Orta Riskli"
        description = "Dengeli bir yaklaşıma sahipsiniz. Hem sermayenizi korumayı hem de orta düzeyde getiri elde etmeyi hedefliyorsunuz. Portföyünüz dengeli fonlar, mavi çipli hisse senetleri gibi araçları içerebilir."
    else:
        risk_level = "Yüksek Riskli"
        description = "Yüksek getiri potansiyeli için yüksek riski göze alabilen bir yatırımcısınız. Dalgalanmalara karşı daha toleranslısınız. Portföyünüzde büyüme hisse senetleri, sektör fonları ve hatta kripto paralar gibi daha riskli araçlara yer verebilirsiniz."

    print(f"Risk Profiliniz: {risk_level}")
    print(f"Açıklama: {description}")
    print("\n*Bu anket sonuçları profesyonel finansal danışmanlığın yerini tutmaz.*")

if __name__ == "__main__":
    calculate_risk_profile()
    

