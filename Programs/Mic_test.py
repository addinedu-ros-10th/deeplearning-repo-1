import speech_recognition as sr

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("말씀하세요...")
        recognizer.adjust_for_ambient_noise(source)  # 잡음 제거
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language="ko-KR")
        print("인식된 텍스트:", text)
    except sr.UnknownValueError:
        print("음성을 이해하지 못했습니다.")
    except sr.RequestError:
        print("API 요청 에러가 발생했습니다.")

if __name__ == "__main__":
    recognize_speech_from_mic()