#!/bin/bash 

# Run python application with the correct environment variables



create_venv(){
    echo "Would you like to create virtual environment? (y/n)"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
}

search_for_earthquake(){
    echo "Enter the name of city you want to search for: "
    read city
    echo "Enter time interval in minutes ( 10: last 10 minute events will be checked) "
    read time_interval 
    TIME_INTERVAL="$time_interval" CITY_TO_BE_CHECKED="$city" python3 deprem.py >> $city.txt
}


# check if virtual environment exists
if [ -d "venv" ]; then
    echo "Virtual environment exists."
    source venv/bin/activate
else
    echo "Virtual environment does not exist."
    create_venv
fi


search_for_earthquake

echo "--------------------------------------------------"

echo "Would you like to deactivate virtual environment? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Deactivating virtual environment..."
    deactivate
fi



echo "Would you like to delete virtual environment? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Deleting virtual environment..."
    rm -rf venv
fi
