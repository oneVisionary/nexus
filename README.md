Pawsighnt is an AI-powered veterinary emotion analysis system built as both a software platform and a hardware-integrated solution. It analyzes dog posture, movement, and behavior from video input to determine emotional states such as happiness, stress, activity level, and overall mental well-being. The system presents these insights through a user-friendly interface, AI-generated vet summaries, voice feedback, and visual graphs.

The project demonstrates how computer vision, AI reasoning, and user-centered design can be combined to create an intelligent digital vet assistant.

### **1. Clone the Repository**



### **2. Create Virtual Environment & Install Dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```



### **3. Set Environment Variables**

Create a `.env` file in the root directory and add:

```env
NOVITA_KEY=your_novita_api_key
ELEVAN_LAB=your_elevenlabs_api_key
TAVILY=your_tavily_api_key
```


### **4. Run the Application**

```bash
python app.py
```



### **5. Open in Browser**

```
http://127.0.0.1:5000
```

Upload a dog video and explore emotion analysis, AI vet summary, voice feedback, graphs, and chatbot.

---

## **Minimum Requirements**

* Python 3.8+
* GPU (optional but recommended for YOLO)

