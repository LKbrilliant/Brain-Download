# Brain-Download
A GUI for recording raw EEG data from Emotiv Insight headset while displaying images or playing audio clips* of multiple stimulus classes

## Installation
1. Install Python (>= 3.7)
    
    I highly recommend installing python with [Anaconda](https://www.anaconda.com).


2. *Optional*: Create a new [virtual environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) using anaconda.

    ```conda create -n ENV_NAME```
    
    Activate the created environment using,

    ```conda activate ENV_NAME```

3. Install prerequisites
        
    ```conda install pyqt numpy websocket-client```

    ```pip install playsound```

4. Run *Brain-Download*

    Try the program without the EEG headset:
        
    ```python Brain_Download_demo.py```

    Run the program with a license :
        
    ```python Brain_Download.py```
    
    The `demo` mode does not allow you to connect and record eeg data from the EMOTIV Insight headset. For that. you will need a license purchased from EMOTIV, and you will also need to install a companion app called the `EMOTIVE Apps` (or new [EMOTIV Launcher](https://www.emotiv.com)). 

## Datasets
Also, checkout the [Brain download datasets](https://github.com/LKbrilliant/Brain-Download-Datasets)
    
## ToDo
- *fix the audio playing issue