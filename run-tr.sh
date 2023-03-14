#!/bin/bash 

# Run python application with the correct environment variables



create_venv(){
    echo "Sanal ortam oluşturulacak. Devam etmek istiyor musunuz? (y/n)"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        echo "Sanal ortam oluşturuluyor..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
}

search_for_earthquake(){
    echo "Aramak istediğiniz şehrin adını giriniz: "
    read city
    echo "Kaç dakika aralıklarla kontrol edileceğini giriniz ( 10: son 10 dakika için kontrol edilecek) "
    read time_interval 
    TIME_INTERVAL="$time_interval" CITY_TO_BE_CHECKED="$city" python3 deprem.py
}


# check if virtual environment exists
if [ -d "venv" ]; then
    echo "Sanal ortam mevcut."
    source venv/bin/activate
else
    echo "Sanal ortam mevcut değil."
    create_venv
fi


search_for_earthquake

echo "--------------------------------------------------"

echo "Sanal ortamı kapatmak istiyor musunuz? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Sanal ortam kapatılıyor.."
    deactivate
fi



echo "Sanal ortamı silmek istiyor musunuz? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Sanal ortam siliniyor..."
    rm -rf venv
fi
