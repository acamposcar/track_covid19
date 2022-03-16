# Track Covid19

The Track Covid19 website compiled and published the covid19 data available for all countries during 2020.

The source of the data was:
- [Worldometer](https://www.worldometers.info/coronavirus/)
- [European Centre for Disease Prevention and Control](https://opendata.ecdc.europa.eu/covid19/casedistribution/csv)

![Demo](https://media.giphy.com/media/8cPIH5boTpgFgt5cAC/giphy.gif)
## Installation

To set up this project on your computer:

1. Clone the project
    ```python
        git clone https://github.com/acamposcar/track_covid19.git
    ```
2. Install all necessary dependencies
    ```python
        pip3 install -r requirements.txt
    ```
3. Eidt config.json.example with your own SECRET_KEY and save it as config.json
    ```
    "SECRET_KEY" : "some_large_key"
    ```
3. Run flask webserver
    ```python
        flask run
    ```