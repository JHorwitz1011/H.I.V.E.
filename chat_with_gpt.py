import os
import sys
import queue
from dotenv import load_dotenv

from gtts import gTTS 
from playsound import playsound
from openai import OpenAI
import sounddevice as sd
import soundfile as sf


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", default="Key Not Available")


def generate_answer(client, model_type, prompt, seed = 1):

    message = [{"role": "system", "content": "You are a helpful AI assistant that responds like a magic eight ball. You must answer start your answer with no or yes at the beginning and you must elaborate on your answer."},
               {"role": "user", "content": prompt}]

    response = client.chat.completions.create(model = model_type, 
                                                    messages=message, max_tokens = 100, 
                                                    temperature = 1, top_p = 1, seed = seed)
    
    output = response.choices[0].message.content

    return output

def audio_to_text(client, audio_path):

    audio_file= open(audio_path, "rb")
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

    return transcript.text

def collect_audio():

    samplerate = 44100


    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    try:
        # Make sure the file is opened before recording anything:
        with sf.SoundFile("output.wav", mode='x', samplerate=samplerate,
                        channels=1) as file:
            with sd.InputStream(samplerate=samplerate, device=1,
                                channels=1, callback=callback):
                print('#' * 80)
                print('press Ctrl+C to stop the recording')
                print('#' * 80)
                while True:
                    file.write(q.get())
    except KeyboardInterrupt:
        print('\nRecording finished')


def main():

    collect_audio()

    model_client = OpenAI(api_key = OPENAI_API_KEY)
    model_type = "gpt-3.5-turbo-1106"
    prompt = "Am I going to have a happy new year?"

    prompt = audio_to_text(model_client, "output.wav")
    os.remove("output.wav")
    gpt_response = generate_answer(model_client, model_type, prompt)

    # Save File
    with open("model_response.txt", mode='w') as f:
        f.write(gpt_response)

    # Speak the 
    language = 'en'
    myobj = gTTS(text=gpt_response, lang=language, slow=False) 
    
    myobj.save("model_response.mp3") 
    playsound("model_response.mp3")

if __name__ == '__main__':
    main()

