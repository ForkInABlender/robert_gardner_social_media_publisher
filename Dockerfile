FROM python:3
ADD t2.py .
ADD social_media_uploader.sh .
ENV TZ=America/Chicago

RUN python -m pip install rsa git+https://github.com/tokland/youtube-upload.git
RUN python -m pip install google-api-python-client oauth2client progressbar2 facebook-sdk git+https://github.com/b3nab/instapy-cli.git
RUN sed -e 's/\r$//' t2.py
RUN sed -e 's/\r$//' social_media_uploader.sh
RUN chmod +x social_media_uploader.sh
ENTRYPOINT ["./social_media_uploader.sh"]