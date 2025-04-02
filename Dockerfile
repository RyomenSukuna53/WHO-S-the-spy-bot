FROM python:3.10

WORKDIR /root/SPY

COPY . .

RUN pip3 install --upgrade pip setuptools
RUN pip3 install -U -r requirements.txt

CMD ["python3", "-m", "SPY"]
