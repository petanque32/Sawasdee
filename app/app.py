import os
import datetime
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import base64
from sawadee import whisper_call, paligemma_call , sd3_call
from sawadee import WebContentProcessor,run_tool,gen_iamge_prompt,normal_prompt
import json



import asyncio

def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def multi_agent(query,out_1): 
    if out_1['tool'] =='normal' :
        print('process : normal')
        return normal_prompt(query),out_1['tool'] 
    elif out_1['tool'] =='search' :
        print('process : search')
        search = WebContentProcessor(query)
        return search.process(),out_1['tool'] 
    elif out_1['tool'] =='image_gen' :
        print('process : image_gen')
        return gen_iamge_prompt(query),out_1['tool'] 
    
def pipeline_agent(input_text):
    out_1 = run_tool(input_text)
    out = multi_agent(input_text,out_1)
    return out


def save_file(file_bytes, file_extension, file_type):
    """
    Save file bytes to a file with the specified extension.

    :param file_bytes: File data in bytes
    :param file_extension: The extension of the output file
    :param file_type: The type of file (audio or image)
    :return: The name of the saved file
    """
    file_name = f"./upload/{file_type}_sample.{file_extension}"

    with open(file_name, "wb") as f:
        f.write(file_bytes)

    return file_name


def main():
    """
    Main function to run the Whisper Transcription app.
    """
    st.title("Mahasamut")

    with st.sidebar:
        tab1, tab2 = st.tabs(["Record Audio", "Upload Image"])

        # Record Audio tab
        with tab1:
            audio_bytes = audio_recorder()
            if audio_bytes:
                st.audio(audio_bytes, format="audio/wav")
                file_path = save_file(audio_bytes, "mp3", "audio")

        # Upload Image tab
        with tab2:
            image_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
            if image_file:
                file_extension = image_file.type.split('/')[1]
                file_path = save_file(image_file.read(), file_extension, "image")
                st.image(file_path, caption="Uploaded Image", use_column_width=True)

    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Transcribe button action
    with st.sidebar:
        check_lang = st.checkbox("translate")
        if st.button("Transcribe"):
            # print(check_lang)
            transcript_text = whisper_call('./upload/audio_sample.mp3',translate=True)
            # print(transcript_text)
            st.session_state.messages.append({"role": "user", "content": transcript_text['model_output']})
            with st.chat_message("user"):
                st.markdown(transcript_text['model_output'])
            
            if check_lang:
                with st.chat_message("user"):
                    st.markdown(transcript_text['translated_output'])
                
                # Decode the Base64 string
                audio_data = base64.b64decode(transcript_text['translated_output_speech'])

                # Write the decoded bytes to a WAV file
                # with open("./upload/output.wav", "wb") as wav_file:
                #     wav_file.write(audio_data)
                
                st.audio(audio_data, format="audio/wav",)
                

        
    
    # Chat input
    if prompt := st.chat_input("Type your message"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # Initialize run variable
    run = False
    with st.sidebar:
        if st.button('send'):
            run = True 
    
    if run:
        prompt =st.session_state.messages[-1]['content']
        img_path  = './upload/image_sample.jpeg'
        if os.path.exists(img_path):
            response_img=paligemma_call(img_path,prompt)['model_output']
            response_img=json.loads(response_img)
            response_text = response_img["source"] +'\n'+  response_img["target"]
            os.remove(img_path)
            with st.spinner("Thinking..."):
                    response = {"content": response_text}
                    st.markdown(response['content'])
                    st.session_state.messages.append({"role": "assistant", "content": response['content']})

        else:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response_text,type = pipeline_agent(prompt)
                    if type == 'image_gen':
                        image = sd3_call(prompt)
                        st.image(image,caption=response_text)
                    else:
                        response = {"content":response_text }
                        st.markdown(response['content'])
                        st.session_state.messages.append({"role": "assistant", "content": response['content']})

        run = False

if __name__ == "__main__":
    main()
