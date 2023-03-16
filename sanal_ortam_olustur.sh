#!/bin/bash 

 # Run python application with the correct environment variables



 create_venv(){
     echo "Sanal ortam oluşturulacak. Devam etmek istiyor musunuz? (y/n)"
     read answer
     if [ "$answer" != "${answer#[Yy]}" ] ;then
        echo "Sanal ortam oluşturuluyor..."
        python3 -m venv venv
        if [ -d "venv" ]; then
            echo "Sanal ortam oluşturuldu."
            source venv/bin/activate 
        else
            echo "Sanal ortam oluşturulamadı."
            exit 1
        fi
        echo "Sanal ortam etkinleştiriliyor..."    
        
        if [ -f "requirements.txt" ]; then
            echo "Gerekli kütüphaneler yükleniyor..."
            pip install  -q  -r requirements.txt
        fi
     fi
     echo "-----------------------------------------------"
     echo "Sanal ortam oluşturuldu ve etkinleştirildi."
     echo " deprem.py dosyasını çalıştırmak için "
     echo "
            'source venv/bin/activate' komutunu kullanabilirsiniz.
            'python deprem.py' komutunu kullanabilirsiniz. "
 }



 # check if virtual environment exists
 if [ -d "venv" ]; then
     echo "Sanal ortam mevcut."
     echo "Mevcut sanal ortamı silmek istiyor musunuz? (e/h)"
     read answer
     if [ "$answer" != "${answer#[Ee]}" ] ;then
         echo "Sanal ortam siliniyor..."
         rm -rf venv
         echo "Sanal ortam silindi."
         echo "Yeniden oluşturmak için 'bash sanal_ortam_olustur.sh' komutunu kullanabilirsiniz.'"
     else 
         source venv/bin/activate
     fi 
 else
     echo "Sanal ortam mevcut değil."
     create_venv

 fi