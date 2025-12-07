# -*- coding: utf-8 -*-
import re

# Dosyayı oku
with open('yerler_veri.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Kısa açıklamaları uzun ve detaylı açıklamalara dönüştürmek için iyileştirmeler
genisletmeler = {
    # ID 5
    '"uzun": "Yılan Kalesi, Adana\'nın Ceyhan ilçesinde bulunan ve tarihi M.Ö. 12. yüzyıla kadar uzanan antik bir kaledir. Kale, Çukurova\'yı savunmak için stratejik bir nokta olarak kullanılmıştır."':
    '"uzun": "Yılan Kalesi, Adana\'nın Ceyhan ilçesinde tarihin derinliklerinden günümüze ulaşan muhteşem bir savunma yapısıdır. M.Ö. 12. yüzyılda inşa edilen bu kale, Çukurova\'nın stratejik önemini koruyan en önemli yapılardan biridir. Kale, yüksek bir tepe üzerinde konumlanmış olup çevreye hakim manzarasıyla bölgenin kontrolünü sağlamıştır. Tarihi boyunca Hititler, Asurlular, Persler, Romalılar ve Bizanslılar tarafından kullanılmış olan kale, her medeniyetin izlerini taşımaktadır. Kalede bulunan surlar, gözetleme kuleleri ve su sarnıçları antik dönem mühendislik bilgisinin göstergesidir. Kalenin adının nereden geldiği konusunda çeşitli rivayetler bulunmakta olup bazı kaynaklara göre kalenin etrafındaki yılanlardan dolayı bu ismi aldığı söylenmektedir."',
    
    # ID 6
    '"uzun": "Adana Ulu Camii, 16. yüzyılda Ramazanoğulları döneminde inşa edilmiş tarihi bir camidir. Caminin taş işçiliği ve çini süslemeleri dikkat çekicidir."':
    '"uzun": "Adana Ulu Camii, 16. yüzyılın ortalarında Ramazanoğulları Beyliği döneminde inşa edilmiş ve Adana\'nın en eski camilerinden biri olarak günümüze kadar ulaşmıştır. Klasik Osmanlı mimarisinin özelliklerini taşıyan cami, siyah-beyaz taş işçiliği ile dikkat çekmektedir. Caminin minaresi zarif hatlarıyla şehrin siluetine katkı sağlarken, iç mekanındaki çini süslemeler ve ahşap işçiliği dönemin sanat anlayışını yansıtmaktadır. Avlusundaki şadırvan ve çeşme de tarihi özellikleri ile korunmuştur. Cami, yüzyıllar boyunca Adana halkının ibadet merkezi olmuş ve pek çok restorasyon geçirerek orijinal özelliklerini korumayı başarmıştır. İçerisindeki hat yazıları ve mihrap süslemeleri Osmanlı sanatının en güzel örneklerindendir."',
    
    # ID 7
    '"uzun": "Misis Köprüsü, Roma döneminden kalma ve hala ayakta olan tarihi bir köprüdür. Ceyhan Nehri üzerinde yer alan köprü, antik ticaret yollarının önemli bir parçasıydı."':
    '"uzun": "Misis Köprüsü, Adana\'nın Misis (Yakapınar) beldesinde Ceyhan Nehri üzerinde yükselen Roma döneminin en etkileyici mühendislik eserlerinden biridir. M.S. 3. yüzyılda inşa edilen köprü, antik çağın önemli ticaret yolu olan Via Tauri\'nin bir parçası olup İpek Yolu güzergahındaki kervanların geçiş noktasıydı. 13 kemerli yapısıyla 150 metre uzunluğunda olan köprü, Roma döneminin taş işçiliği ve mühendislik bilgisinin mükemmel bir örneğidir. Köprü, sadece ticari değil aynı zamanda askeri açıdan da büyük önem taşımıştır. Bizans, Selçuklu ve Osmanlı dönemlerinde de kullanılan köprü, farklı medeniyetler tarafından onarılarak günümüze kadar gelmiştir. Köprünün yakınındaki Misis Mozaik Müzesi\'nde bölgenin zengin tarihi hakkında detaylı bilgi edinmek mümkündür."',
    
    # ID 8
    '"uzun": "Kozan Kalesi, Adana\'nın Kozan ilçesinde yüksek bir tepe üzerinde yer alan tarihi bir kaledir. Kale, Orta Çağ\'da Ermeni Kilikya Krallığı\'nın önemli merkezlerinden biriydi."':
    '"uzun": "Kozan Kalesi, Adana\'nın Kozan ilçesinde 1.200 metre yükseklikte bir tepe üzerinde konumlanan görkemli bir Orta Çağ savunma yapısıdır. Kale, 11. yüzyılda Ermeni Kilikya Krallığı döneminde stratejik bir askeri üs olarak inşa edilmiştir. Kaleye çıkan yol zorlu olmakla birlikte, tepeden görülen panoramik manzara tüm zorluğu unutturmaktadır. Kalede korunmuş surlar, su sarnıçları, saray kalıntıları ve kilise izleri bulunmaktadır. Haçlı Seferleri döneminde önemli bir rol oynayan kale, Kilikya Krallığı\'nın başkenti Sis\'in (bugünkü Kozan) savunmasını sağlamıştır. 13. yüzyılda Memlük saldırılarına karşı direnmiş olan kale, sonrasında Osmanlı hakimiyetine girmiştir. Kalenin içinde bulunan antik yapılar ve tarihi kalıntılar, bölgenin zengin geçmişine tanıklık etmektedir."'
}

# Daha fazla ekleme yapacağım - geri kalan mekanlar için
ek_genisletmeler = {
    # Ankara mekanları
    'Anıtkabir, Mustafa Kemal Atatürk\'ün anıt mezarıdır': 'Anıtkabir, Türkiye Cumhuriyeti\'nin kurucusu Mustafa Kemal Atatürk\'ün anıt mezarı olarak Ankara\'nın Anıttepe semtinde görkemli bir şekilde yükselmektedir. 1944-1953 yılları arasında inşa edilen bu muhteşem yapı, modern Türk mimarisinin en önemli eserlerinden biridir. Mimar Emin Onat ve Orhan Arda tarafından tasarlanan Anıtkabir, 750.000 metrekarelik bir alana yayılmaktadır. Aslan Yolu, Tören Meydanı ve Mozolede yer alan Atatürk\'ün naaşı her yıl milyonlarca ziyaretçi tarafından saygıyla ziyaret edilmektedir. Anıtkabir\'in içinde ayrıca Atatürk\'ün özel eşyaları, belgeleri ve hediyelerinin sergilendiği müze bölümü bulunmaktadır.',
    
    'Kocatepe Camii, Ankara\'nın en büyük camisidir': 'Kocatepe Camii, Ankara\'nın Kızılay semtinde yer alan ve Türkiye\'nin en büyük camilerinden biri olan muhteşem bir ibadethane kompleksidir. 1967-1987 yılları arasında 20 yıl süren bir inşaat sürecinin ardından tamamlanan cami, klasik Osmanlı mimarisi ile modern tekniklerin mükemmel bir sentezini yansıtmaktadır. Mimar Vedat Dalokay\'ın tasarladığı cami, 4 minareli yapısı, dev kubbesi ve 24.000 kişilik kapasitesiyle dikkat çekmektedir. İç mekanında yer alan Kütahya çinileri, hat yazıları ve avizeler Türk-İslam sanatının en güzel örneklerindendir. Caminin altında bulunan alışveriş merkezi ve sosyal tesisler, dini işlevinin yanı sıra modern bir yaşam merkezi özelliği de taşımaktadır.',
}

# Regex ile tüm uzun açıklamaları bul ve güncelle
for eski, yeni in genisletmeler.items():
    content = content.replace(eski, yeni)

for kelime, yeni_cumle in ek_genisletmeler.items():
    # Regex pattern ile "uzun" alanını bul ve güncelle
    pattern = f'("uzun": "[^"]*{re.escape(kelime)}[^"]*")'
    matches = re.findall(pattern, content)
    for match in matches:
        # Eğer zaten uzunsa atla
        if len(match) < 400:
            yeni_deger = f'"uzun": "{yeni_cumle}"'
            content = content.replace(match, yeni_deger)

# Dosyayı kaydet
with open('yerler_veri_yeni.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Açıklamalar genişletildi! yerler_veri_yeni.py dosyası oluşturuldu.")
