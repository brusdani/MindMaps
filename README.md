# MindMaps
Bachelor thesis: Automatic Mind Map generation

The repository contains multiple directories.

*MindMaps* is the main web application

*Jupyter notebooks* folder contains Jupyter notebooks that were used in evaluation part of thesis. There are both original notebooks and html versions
If you want to run the notebooks in your environment you'll need to download the embeddings from *embeddings* directory as they're the input files for jupyter notebooks.

maps1 and maps2 contains the generated mind maps in json format in the web applications that were used for evaluation - 100+100maps



# Tutorial
This part includes step-by-step guide on how to run the prototype in PyCharm IDE. It requires to have Python 3.10+ installed

1.) Download the repository (code -> download zip archive)

2.) Create a new project in PyCharm - this step is important, because this repository does not include venv folder, which includes interpreter.

![image](https://github.com/user-attachments/assets/e0ff4818-64e5-4abf-b4d5-cdfae5dd3ca8)

![image](https://github.com/user-attachments/assets/6f171e0a-ee8f-4fb9-a4cd-47c8aa4f4b2c)


3.) Copy paste the MindMap folder into new project

![image](https://github.com/user-attachments/assets/d145d15d-eddd-4668-a164-cac1c8353500)


4.) In the 4**app.py** file. Install all required packages (dependencies).

![image](https://github.com/user-attachments/assets/a443aac7-a0d0-44bf-89ff-d3a571733750)


5.) Create .env file in the **MindMap** directory and set up your OpenAI API key.

![image](https://github.com/user-attachments/assets/fae529c1-85e3-4299-8099-86cc73e02247)



6.) That's it, Happy mind mapping!

