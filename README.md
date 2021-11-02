# Brain-Download
A GUI for recording raw EEG data from Emotiv Insight headset while displaying images or playing audio clips of multiple stimulus classes

# Installation
1. Install Python >= 3.7
    - I highly recommend installing python with [Anaconda](https://www.anaconda.com).


2. Optional: Create a [virtual environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

    - If you are using anaconda
        > conda create -n ENV_NAME
    - And after creating te environment, activate it by
        >conda activate ENV_NAME

3. Install requirements
        
        conda install pyqt numpy websocket-client 
        pip install playsound
