# MindMaps
Bachelor thesis: Automatic Mind Map generation

The repository contains multiple directories.

*MindMaps* is the experimental version of web application - this prototype was used for all evaluation experiments during thesis.

*MindMapsApp* is the "presentational" version of the application, that could be used by real users.

*Jupyter notebooks* folder contains Jupyter notebooks that were used in evaluation part of thesis. There are both original notebooks and html versions
If you want to run the notebooks in your environment you'll need to download the embeddings from *embeddings* directory as they're the input files for jupyter notebooks.

maps1 and maps2 contains the generated mind maps in json format in the web applications that were used for evaluation - 100+100maps


# Tutorial - Windows Command Line
### Commands Summary:

First download the repository (code -> download zip archive)

Then navigate to *MindMapsApp* or *MindMaps* folder, depending if you want to try the presentational or experimental version of the prototype 

Create a virtual environment
```bash
py -m venv venv
```

Activate the virtual environment

```bash
venv\Scripts\activate
```

Install required packages
```bash
pip install -r requirements.txt
```

Set the Flask app environment variable
```bash
set FLASK_APP=app.py
```

Create .env file
```bash
type nul > .env
notepad .env
OPENAI_API_KEY="your_api_key"
```

Run the Flask application
```bash
flask run

```

# This part includes step-by-step guide on how to run the prototype in Windows command line with pictures. It requires to have Python 3.10+ installed

1.) Download the repository (code -> download zip archive)

2.) Copy the folder with the prototype project, the one that is called MindMaps or MindMapsApp.

3.) Navigate to MindMaps folder and create virtual environment within it. Using "*py -m venv venv*" command
![image](https://github.com/user-attachments/assets/3ecda94a-7d78-432a-bd6c-72a2fbd8eb35)


4.) Once the environment is created run it using command "*venv\Scripts\activate*"
![image](https://github.com/user-attachments/assets/d74eb178-f9f6-4ca0-99ea-d5e59d0c7089)

5.) Install the dependencies. They're in requirements.txt file. Run the command "*pip install -r requirements.txt*"
![image](https://github.com/user-attachments/assets/fc661653-5561-46d1-8c13-0c4b6ead35d0)

6.) Create .env file and setup your OpenAI API key

![image](https://github.com/user-attachments/assets/819355e9-671a-465c-a066-f97ea20dc115)
![image](https://github.com/user-attachments/assets/65261d46-fb1a-4453-8a28-7e23231a5b39)

7.)Set app.py as the main file of the Flask application and run the app. It's gonna run development server on localhost.

Commands are *"set FLASK_APP=app.py*" and "*flask run*"
![image](https://github.com/user-attachments/assets/24cf2488-a9ac-452f-ae3c-ff3d15ecb5b7)
8.) Happy mind mapping


# Tutorial - IDE
This part includes step-by-step guide on how to run the prototype in PyCharm IDE. It requires to have Python 3.10+ installed

1.) Download the repository (code -> download zip archive)

2.) Create a new project in PyCharm - this step is important, because this repository does not include venv folder, which includes interpreter.

![image](https://github.com/user-attachments/assets/e0ff4818-64e5-4abf-b4d5-cdfae5dd3ca8)

![image](https://github.com/user-attachments/assets/c244838d-bf58-483a-9781-8d323f9a5e10)



3.) Copy paste the MindMap folder into new project

![image](https://github.com/user-attachments/assets/d145d15d-eddd-4668-a164-cac1c8353500)


4.) In the 4**app.py** file. Install all required packages (dependencies).

![image](https://github.com/user-attachments/assets/a443aac7-a0d0-44bf-89ff-d3a571733750)


5.) Create .env file in the **MindMap** directory and set up your OpenAI API key.

![image](https://github.com/user-attachments/assets/fae529c1-85e3-4299-8099-86cc73e02247)



6.) That's it, Happy mind mapping!

