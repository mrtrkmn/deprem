# Deprem

Kandilli rasathanesinin yayınladığı verilere göre şehir filtreleyerek, Telegram üzerinden bildirim almanızı sağlayan küçük bir kod parçası. 

- [Github üzerinden nasıl çalıştırılır ?](#github-üzerinden-nasıl-çalıştırılır-)
- [Bilgisayarınız üzerinde nasıl çalıştırılır ?](#bilgisayarınız-üzerinde-nasıl-çalıştırılır-)
- [Telegram entegrasyonu ile nasıl kullanılır ?](#telegram-entegrasyonu-ile-nasıl-kullanılır-)

# Github üzerinden nasıl çalıştırılır ? 

1. Projeyi forkla
2. Workflowları aktifleştir 
3. Actions sekmesinden "Run Deprem Bot" workflow dosyasını çalıştır.

Adımlar aşağıdaki video da gösterilmiştir. 

https://user-images.githubusercontent.com/13614433/226146876-5ce2f393-aecf-4858-baf6-c2791db8f9e3.mov




# Bilgisayarınız üzerinde nasıl çalıştırılır ?

Bilgisayarınızda çalıştırmak için Python 3.8 ve üzeri sürümler gerekmektedir.

Eğer bilgisayarınızda Python 3.8 ve üzeri sürümleri mevcut ise, aşağıdaki komutları çalıştırarak uygulamayı çalıştırabilirsiniz. 

```bash
$ git clone https://github.com/mrtrkmn/deprem.git
$ cd deprem
$ bash sanal_ortam_olustur.sh
$ source venv/bin/activate
$ python deprem.py
```

Daha sonraki adımlar aşağıda verilen örnek video ile anlatılmıştır.


https://user-images.githubusercontent.com/13614433/225782006-ac91464e-a2da-445e-b557-ef2ac656a213.mov


# Telegram Entegrasyonu ile Nasıl kullanılır ?

Bu depoyu (repository) kendi hesabınıza kopyalamanız gerekir (fork). 

- [Kendi Github hesabınıza kopyalamak için tıklayınız](https://github.com/mrtrkmn/deprem/fork)

Kopyaladıktan sonraki adım da Telegram üzerinden "token" almanız gerekmektedir. 

Bunun için telegramdan [@botfather](https://t.me/BotFather) profili bularak aşağıda görüldüğü üzere yeni bir bot bilgisi istediğinizi `/newbot` komutu ile belirtebilirsiniz. Aşağıda belirtilen ekran görüntüsünde olduğu gibi. 

<details>
<summary>Telegram token alma</summary>
<br>
<img width="733" alt="Yeni bot oluşturma" src="https://user-images.githubusercontent.com/13614433/224006707-e7a7b0a0-4427-4f33-808b-7d79a82fdf78.png">
</details>

Daha sonrasında size aşağıdakine benzer bir mesaj gönderecek. 

<details>
<summary>BotFather cevabı</summary>
<br>
<img width="664" alt="Telegram TOKEN" src="https://user-images.githubusercontent.com/13614433/224007385-3e1844f1-ef1b-4e4a-8ce4-876c3dce9691.png">
</details>

Buradaki belirtilen kodu aldıktan sonra Telegram üzerinden chatID yi almamız gerekir. Onu [@RawDataBot](https://t.me/RawDataBot) aracılığı ile alıyoruz. 

`/invite` komutunu gönderdiğimizde bize JSON dosyası verecektir, bu JSON dosyası içerisinde ki chatID değerini alıyoruz aşağıdaki resimde gösterildiği şekilde.

<details>
<summary>Chat ID değerini alma</summary>
<br>
<img width="353" alt="chatID" src="https://user-images.githubusercontent.com/13614433/224008587-8cd068da-e9c1-4f76-b4ae-addbccef477f.png">
</details>

Sonrasında  kendi hesabımıza "fork" oluşturduğumuz projede, "Github secrets" değerlerini ayarlıyoruz. 

- **TELEGRAM_TOKEN**: İlk adımdan alınan değer 
- **TELEGRAM_CHAT_ID**: Son aldığımız değer.


Bunları "Github secrets" üzerinden kaydediyoruz. Bu kaynak Ingilizce olsa da nasıl kaydedildiğini çok basit şekilde açıklıyor: https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-environment

Bu adımları ayarladıktan sonra sadece son olarak Şehir ve Zaman değerini şuradan ayarlamalısınız. 

- Aranan şehiri değiştirmek için: [.github/workflows/run.yaml#L55](.github/workflows/run.yaml#L55)
- Zaman aralığını değiştirmek için: [.github/workflows/run.yaml#L6](.github/workflows/run.yaml#L6) ve [.github/workflows/run.yaml#L56](.github/workflows/run.yaml#L56) değerlerini değiştirmeniz gerekmektedir.

** Not: ** Zaman aralığını değiştirmek için, `cron` formatında değer vermeniz gerekmektedir. Buradan cron formatlarına bakabilirsiniz: https://crontab.guru  Sadece dakika değerini değiştirmek istiyorsanız, `*/5 * * * *` değerinde bulunan `5` değerini değiştirmeniz yeterli olacaktır. 

Burada bulunan değer [.github/workflows/run.yaml#L56](.github/workflows/run.yaml#L56) ile uyumlu olmalıdır. 

--- 
