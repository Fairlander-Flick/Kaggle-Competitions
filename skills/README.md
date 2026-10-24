# Kaggle araştırma skilli

`kaggle-research`, anlamlı deney seçimi, alternatif yaklaşım keşfi, doğrulama, FAU HPC çalıştırma ve Kaggle submission akışını yönlendirir. Tek kısa giriş dosyası ve yalnız gerektiğinde okunan referanslar içerir.

## Başka bilgisayara kurulum

Linux/macOS terminalinde:

```bash
curl -fL https://raw.githubusercontent.com/Fairlander-Flick/Kaggle-Competitions/main/skills/kaggle-research.tar.gz -o /tmp/kaggle-research.tar.gz
mkdir -p ~/.agents/skills
tar -xzf /tmp/kaggle-research.tar.gz -C ~/.agents/skills
```

Sonra Codex'e:

```text
$kaggle-research kullan. Yarışma: [Kaggle bağlantısı]
FAU kaynaklarını keşfet, güçlü baseline kur ve anlamlı deneylerle ilerle. Kısa raporla.
```

Görünmezse Codex'i yeniden başlat. FAU üzerinde çalışan agent için kurulumu o ortamda yap.

## İçerik

- [SKILL.md](kaggle-research/SKILL.md): ana araştırma döngüsü.
- [Deney seçimi ve keşif](kaggle-research/references/decisions.md): varsayımları sorgulama, prototip ve devam/ölçeklendirme/terfi ayrımı.
- [16 GOLD kaynak kartı](kaggle-research/references/cases.md): mekanizmalar, aktarım koşulları ve olumsuz sonuçlar.
- [Ortam profili](kaggle-research/references/runtime-profile.md): gerçek kaynaklar ve yarışma koşulları.

Yapay saat/GPU limiti veya sandbox kurulumu gerektirmez. Gerçek platform kuralları ve kullanıcı tercihleri geçerlidir. Ücretli dış API kullanımı ayrı harcama iznine bağlıdır. Araştırma veritabanı kurulum için gerekli değildir.

Bu paket talimat içerir; çalışan bir scheduler, evaluator veya kazanma garantisi değildir. Yarışmaya uygun uygulamaları agent görev sırasında oluşturur veya kullanır.
